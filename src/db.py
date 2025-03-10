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
from sqlalchemy.inspection import inspect
import urllib.parse

Base = declarative_base()

CURRENT_BLOCKS_SQL = """
select
   g.tag as group_tag,
   b.id as block_id,
   b.tag as block_tag,
   b.position as position,
   b.created_at as created_at,
   b.content as content,
   b.token_count as token_count
 FROM
   groups g
   join blocks b on b.group_id = g.id
 WHERE
   g.is_current = 1
"""

GROUPS_SQL = """
select
   is_current as is_current,
   tag as group_tag,
   command as command,
   (select count(*) from blocks where group_id = groups.id) as block_count
from
   groups
"""


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_current = Column(Boolean, default=False)
    command = Column(String)
    tag = Column(String, unique=True)
    created_at = Column(DateTime, server_default=func.now())


class Block(Base):
    __tablename__ = "blocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"))
    position = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    content = Column(String)
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

    async def add_group(self, tag, command):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Set is_current to False for all existing Groups
                await session.execute(
                    text("UPDATE groups SET is_current = False WHERE is_current = True")
                )
                # Create a new Groups with is_current set to True
                group = Group(
                    tag=tag,
                    command=urllib.parse.unquote(command),
                    is_current=True,
                )
                session.add(group)
                await session.flush()  # Ensure the block_group.id is available
                self.block_position = 0  # Reset the block position
                return group.id

    async def add_block(self, group_id, block_content, tag):
        self.block_position += 1
        async with self.SessionLocal() as session:
            async with session.begin():
                block = Block(
                    group_id=group_id,
                    content=block_content,
                    tag=tag,
                    token_count=len(block_content.split()),
                    position=self.block_position,
                )
                session.add(block)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def add_group_with_blocks(self, group_data, blocks_data):
        """
        Add a new group and its associated blocks as a single transaction.

        :param group_data: A dictionary containing group details like tag, command, etc.
        :param blocks_data: A list of dictionaries, each containing block details like content and tag.
        :return: The ID of the newly created group.
        """
        async with self.SessionLocal() as session:
            async with session.begin():
                # Set is_current to False for all existing Groups
                await session.execute(
                    text("UPDATE groups SET is_current = False WHERE is_current = True")
                )
                # Create a new Group with is_current set to True
                group = Group(
                    tag=group_data.get("tag"),
                    command=group_data.get("command"),
                    is_current=True,
                )
                session.add(group)
                await session.flush()  # Ensure the group.id is available

                # Add blocks associated with the new group
                for idx, block_data in enumerate(blocks_data):
                    block = Block(
                        group_id=group.id,
                        content=block_data.get("content"),
                        tag=block_data.get("tag"),
                        token_count=len(block_data.get("content", "").split()),
                        position=idx,
                    )
                    session.add(block)

                return group.id

    async def get_current_blocks(self, where_clause=None):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Get all blocks in the current block group
                query = CURRENT_BLOCKS_SQL
                if where_clause:
                    query += f" AND {where_clause}"
                query += " ORDER BY b.position"
                result = await session.execute(text(query))
                blocks = result.fetchall()

                dict_blocks = [block._asdict() for block in blocks]
                # Get column names from the result
                column_names = list(result.keys())
                return dict_blocks, column_names

    async def get_groups(self):
        async with self.SessionLocal() as session:
            async with session.begin():
                result = await session.execute(text(GROUPS_SQL))
                groups = result.fetchall()
                dict_groups = [group._asdict() for group in groups]
                column_names = list(result.keys())
                return dict_groups, column_names

    async def set_current_group(self, tag):
        async with self.SessionLocal() as session:
            async with session.begin():
                # Test if the specified Group exists
                group = await session.execute(
                    text("SELECT tag FROM groups WHERE tag = :tag"), {"tag": tag}
                )
                if not group.scalar():
                    raise Exception(f"Group with tag '{tag}' does not exist")
                # Set is_current to False for all existing Groups
                await session.execute(
                    text("UPDATE groups SET is_current = False WHERE is_current = True")
                )
                # Set is_current to True for the specified Group
                await session.execute(
                    text("UPDATE groups SET is_current = True WHERE tag = :tag"),
                    {"tag": tag},
                )
