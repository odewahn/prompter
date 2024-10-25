from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, select

Base = declarative_base()


class User(Base):
    def to_dict(self):
        return {"id": self.id, "username": self.username}

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)


class DatabaseManager:
    def __init__(self, db_url):
        self.engine = create_async_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_user(self, user_id):
        async with self.SessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()

    async def add_user(self, username):
        async with self.SessionLocal() as session:
            new_user = User(username=username)
            session.add(new_user)
            await session.commit()

    async def get_all_users(self):
        async with self.SessionLocal() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def get_all_usernames(self):
        async with self.SessionLocal() as session:
            result = await session.execute(select(User.username))
            return [row[0] for row in result.all()]
