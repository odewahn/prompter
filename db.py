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

CURRENT_BLOCKS_SQL = """
select
   b.*
 FROM
   groups g
   join blocks b on b.group_id = g.id
 WHERE
    g.is_current = 1
order by
   b.position
"""


class Groups(Base):
    __tablename__ = "groups"

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
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    position = Column(Integer)
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
        self.block_position = 0

    async def initialize_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        await self.engine.dispose()

    async def close(self):
        await self.engine.dispose()

    async def create_block_group(self, tag, command, task_prompt="", persona_prompt=""):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Set is_current to False for all existing Groups
                await session.execute(
                    text(
                        "UPDATE block_groups SET is_current = False WHERE is_current = True"
                    )
                )
                # Create a new Groups with is_current set to True
                block_group = Groups(
                    tag=tag,
                    command=command,
                    is_current=True,
                    task_prompt=task_prompt,
                    persona_prompt=persona_prompt,
                )
                session.add(block_group)
                await session.flush()  # Ensure the block_group.id is available
                self.block_position = 0  # Reset the block position
                return block_group.id

    async def add_block(self, block_group_id, block_content, tag):
        self.block_position += 1
        async with self.SessionLocal() as session:
            async with session.begin():
                block = Block(
                    block_group_id=block_group_id,
                    block=block_content,
                    tag=tag,
                    token_count=len(block_content.split()),
                    position=self.block_position,
                )
                session.add(block)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_current_blocks(self):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Get all blocks in the current block group
                blocks = await session.execute(text(CURRENT_BLOCKS_SQL))
                return blocks.fetchall()
