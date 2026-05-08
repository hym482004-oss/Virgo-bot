import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from parser import calculate_2d, get_market_data

# Bot Configuration
TOKEN = "8759881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Shwethoon 2D Calculator Bot မှ ကြိုဆိုပါတယ်ရှင့်။ ✨\nစာရင်းများ ရိုက်ထည့်နိုင်ပါပြီ။")

@dp.message(F.text)
async def handle_calc(message: types.Message):
    user_text = message.text
    
    # တွက်ချက်ခြင်း
    result = calculate_2d(user_text)
    
    if result == "error":
        await message.reply("⚠️ ပြန်စစ်ပေးပါရှင့်")
        return
    
    if result == 0:
        return # ဂဏန်းမပါရင် ဘာမှပြန်မလုပ်ဘူး

    # Market & Cashback logic
    rate, rate_label = get_market_data(user_text)
    cashback = int(result * rate)
    net_total = result - cashback
    
    # Output Format
    response = (
        f"👤 {message.from_user.first_name}\n"
        f"--------------------\n"
        f"စုစုပေါင်း = {result:,} ကျပ်\n"
        f"{rate_label} Cashback = {cashback:,} ကျပ်\n"
        f"--------------------\n"
        f"လက်ခံရမည့်ငွေ = {net_total:,} ကျပ်\n"
        f"--------------------\n"
        f"ကံကောင်းပါစေ"
    )
    
    await message.answer(response)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
