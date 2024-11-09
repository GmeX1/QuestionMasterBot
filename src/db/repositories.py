from sqlalchemy import select

from src.bot.schemas.register_schemas import RegProfile
from src.db import Session
from src.db.models import UserData


class UserDataRepository:
    def __init__(self):
        self.db = Session

    async def add_data(self, data: RegProfile):
        async with self.db() as session:
            new_data = UserData(
                tg_id=data.tg_id,
                name=data.full_name,
                phone=data.phone_number,
                client_type=data.client_type,
                organization_name=data.organization_name if data.organization_name else None
            )
            session.add(new_data)
            await session.commit()
        return new_data

    async def check_user(self, tg_id: int):
        async with self.db() as session:
            result = (await session.execute(select(UserData).where(UserData.tg_id == tg_id))).one_or_none()
        return True if result else False

    async def dump(self):
        async with self.db() as session:
            result = (await session.execute(select(
                UserData.id,
                UserData.name,
                UserData.phone,
                UserData.client_type,
                UserData.organization_name))).fetchall()
            result.insert(0, ('id', 'name', 'phone', 'client type', 'organization name'))
        return result
