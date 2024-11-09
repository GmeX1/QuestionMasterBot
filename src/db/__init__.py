from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .models import Base

engine = create_async_engine('sqlite+aiosqlite:///database.db')
Session = async_sessionmaker(bind=engine)


async def init_models() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Для пересоздания ДБ
        await conn.run_sync(Base.metadata.create_all)
