import os
import asyncio
import logging
import datetime
import io
from recogniser import recognize_audio, recognize_video
from dotenv import load_dotenv
from aiogram import Bot, types, Router, Dispatcher
from aiogram.filters import Command
import time

load_dotenv()
bot = Bot(os.getenv("TOKEN"))
__file_path__ = 'files/'
dp = Dispatcher()
r = Router()


def recognize_file(file_path: str, is_audio=False, audio_type=None) -> str:
    if is_audio:
        text = recognize_audio(file_path, audio_type)
    else:
        text = recognize_video(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)

    return text


async def send_file(message: types.message, text = 'Ответ'):
    answer_file = f'files/{message.from_user.id}-TRANSRIPTION.txt'

    with open(answer_file, 'w') as file:
        file.write(text)

    await message.reply_document(types.FSInputFile(answer_file))

    if os.path.exists(answer_file):
        os.remove(answer_file)


@r.message(lambda message: message.video)
async def stt_video(message: types.Message):
    await message.reply('Видео')
    file_type = str(message.video.mime_type).split('/')[-1]
    file_id = message.video.file_id
    temp = io.BytesIO()
    file_path = __file_path__ + f'{message.from_user.id}-FILE.' + file_type
    await bot.download(file_id, temp)

    with open(file_path, 'wb') as file:
        file.write(temp.read())

    text = recognize_file(file_path, False, None)
    await send_file(message, text)


@r.message(lambda message: message.voice)
async def stt_voice(message: types.Message):
    await message.reply('Голосовое')
    file_type = 'ogg'
    file_id = message.voice.file_id
    temp = io.BytesIO()
    await bot.download(file_id, temp)
    file_path = __file_path__ + f'{message.from_user.id}-FILE.' + file_type

    print(file_path)

    with open(file_path, 'wb') as file:
        file.write(temp.read())

    text = recognize_file(file_path, True, 'ogg')
    await send_file(message, text)


@r.message(lambda message: message.document)
async def stt_document(message: types.Message):
    await message.reply('Документ')
    file_name = message.file_name.split('.')[0].lower()

    video_types = ['mov', 'avi', 'mp4']
    audio_types = ['mp3', 'ogg', 'flv', 'wav']

    file_path = __file_path__ + file_name

    file_type = str(file_name).split('.')[-1]

    if file_type in video_types:
        file_id = message.document.file_id
        temp = io.BytesIO()
        await bot.download(file_id, temp)
        is_audio = False
    elif file_type in audio_types:
        file_id = message.document.file_id
        temp = io.BytesIO()
        await bot.download(file_id, temp)
        is_audio = True
    else:
        await message.reply('Мне не знаком этот формат файла')
        return

    with open(file_path, 'wb') as file:
        file.write(temp.read())

    text = recognize_file(file_path, is_audio, file_type)
    await send_file(message, text)


async def start() -> None:
    logging.info(f'{datetime.datetime.now()} START BOT')
    dp.include_router(r)
    await dp.start_polling(bot)


@r.message(Command('start', 'id'))
async def start_function(message: types.Message) -> None:
    text = f'{message.from_user.first_name}, ваш уникальный ID: {message.chat.id}'
    await message.answer(text)


if __name__ == "__main__":
    print('Бот-расшифровщик запущен')
    asyncio.run(start())
