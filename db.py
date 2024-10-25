from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.sql import func

Base = declarative_base()

class BlockGroup(Base):
    __tablename__ = "block_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_current = Column(Boolean, default=False)
    command = Column(String)
    tag = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    block_group_id = Column(Integer, ForeignKey("block_groups.id", ondelete="CASCADE"))
    created_at = Column(DateTime, server_default=func.now())
    block = Column(String)
    token_count = Column(Integer)

class CompletionGroup(Base):
    __tablename__ = "completion_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_fn = Column(String)
    persona_fn = Column(String)
    prompt = Column(String)
    command = Column(String)
    tag = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class Completion(Base):
    __tablename__ = "completions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    completion_group_id = Column(Integer, ForeignKey("completion_groups.id", ondelete="CASCADE"))
    block_id = Column(Integer)
    response = Column(String)
    elapsed_time_in_seconds = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def close(self):
        await self.engine.dispose()

    async def create_block_group(self, tag):
        async with self.SessionLocal() as session:
            async with session.begin():
                block_group = BlockGroup(tag=tag)
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
                    token_count=len(block_content.split())
                )
                session.add(block)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
