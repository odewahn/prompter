from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func

Base = declarative_base()


class BlockGroup(Base):
    __tablename__ = "block_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_current = Column(Boolean, default=False)
    command = Column(String)
    tag = Column(String)
    task_prompt = Column(String)
    persona_prompt = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    block_group_id = Column(Integer, ForeignKey("block_groups.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
    block = Column(String)
    token_count = Column(Integer)


class DatabaseManager:
    current_db_url = None

    def __init__(self, db_url):
        DatabaseManager.current_db_url = db_url
        self.engine = create_async_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.engine.dispose()

    async def close(self):
        await self.engine.dispose()

    async def create_block_group(self, tag, command, task_prompt="", persona_prompt=""):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Set is_current to False for all existing BlockGroups
                await session.execute(
                    text(
                        "UPDATE block_groups SET is_current = False WHERE is_current = True"
                    )
                )
                # Create a new BlockGroup with is_current set to True
                block_group = BlockGroup(
                    tag=tag,
                    command=command,
                    is_current=True,
                    task_prompt=task_prompt,
                    persona_prompt=persona_prompt,
                )
                session.add(block_group)
                await session.flush()  # Ensure the block_group.id is available
                return block_group.id

    async def add_block(self, block_group_id, block_content, tag):
        async with self.SessionLocal() as session:
            async with session.begin():
                block = Block(
                    block_group_id=block_group_id,
                    block=block_content,
                    tag=tag,
                    token_count=len(block_content.split()),
                )
                session.add(block)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
