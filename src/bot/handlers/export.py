from aiogram import types, Router
from aiogram.filters import Command
from src.db.repositories import UserDataRepository
from openpyxl import Workbook
from io import BytesIO
from aiogram.types import BufferedInputFile
export_router = Router()


@export_router.message(Command('export'))
async def export_command(message: types.Message):
    if message.from_user.id == 1070732744:
        data = await UserDataRepository().dump()
        stream = BytesIO()
        wb = Workbook()
        ws = wb.active

        for row_index, row_data in enumerate(data, start=1):
            for col_index, cell_data in enumerate(row_data, start=1):
                ws.cell(row=row_index, column=col_index, value=cell_data)
        wb.save(stream)
        stream.seek(0)
        await message.answer_document(BufferedInputFile(stream.read(), 'export.xlsx'))
