from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio
import os
from dotenv import load_dotenv

from parser import calculate_bets, get_market_rate

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def detect_market(text):
    text = text.lower()

    names = {
        "du": "Dubai",
        "dubai": "Dubai",
        "ဒူ": "Dubai",

        "mega": "Mega",
        "me": "Mega",

        "max": "Max",
        "maxi": "Max",

        "lao": "Laos",
        "ld": "London",
        "london": "London",

        "mm": "Myanmar",

        "glo": "Global",
        "global": "Global"
    }

    for k, v in names.items():
        if k in text:
            return v

    return None


@dp.message(CommandStart())
async def start(message: Message):
    await message.reply("2D Bot Ready ✅")


@dp.message()
async def handle(message: Message):

    text = message.text

    total = calculate_bets(text)

    if total == 0:
        return

    market_name = detect_market(text)

    # market name မပါရင် admin mention
    if not market_name:
        admins = await bot.get_chat_administrators(message.chat.id)

        mentions = []

        for admin in admins:
            user = admin.user
            if user.username:
                mentions.append(f"@{user.username}")

        if mentions:
            await message.reply(
                " ".join(mentions) +
                "\nဒါလေးလာစစ်ပေးပါရှင့်"
            )
        return

    rate, percent_text = get_market_rate(text)

    cashback = int(total * rate)
    final_total = total - cashback

    username = message.from_user.full_name

    reply_text = (
        f"👤 {username}\n"
        f"2D name = {market_name}\n"
        f"Total = {total:,} ကျပ်\n"
        f"{percent_text} Cash Back = {cashback:,} ကျပ်\n"
        f"လွဲရမည့်ငွေ = {final_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ 🍀"
    )

    await message.reply(reply_text)


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
