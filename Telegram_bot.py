from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from auth_google import token
from All_code import alg
from aiofiles import os
import os

bot = Bot(token=token)
dp = Dispatcher(bot)


spreadsheet_id = "1pgCuZb0PkXHUASb4u0xGp27zJnLO0zli50aK8R6kDc8"


temp_dir = 'temp'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Отправьте файл")


@dp.message_handler(content_types=['document'])
async def get_pdf(message: types.Message):
    if message.document.mime_type == "application/pdf":
        await message.reply('Вы отправили pdf файл\nОжидайте...')
        file_path = os.path.join(os.getcwd(), temp_dir, message.document.file_name)
        await message.document.download(destination_file=file_path)
        pdf_file = alg(spreadsheet_id, file_path, message.document.file_name)
        await bot.send_document(message.chat.id, document=open(pdf_file, "rb"))
    else:
        await message.reply('Пожалуйста, отправьте pdf файл')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
