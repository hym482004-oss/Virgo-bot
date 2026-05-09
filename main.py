import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from parser import calculate_2d, get_market_data

# Bot Configuration
TOKEN = "8159881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ခွင့်ပြုထားတဲ့ Group ID (နင့် Group ID နဲ့ ဒီမှာ အစားထိုးပါ)
ALLOWED_GROUPS = [-1002319409848] 

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Shwethoon 2D Calculator ✨\nစာရင်းများ ရိုက်ထည့်နိုင်ပါပြီ။")

@dp.message(F.text)
async def handle_calc(message: types.Message):
    # Group စစ်ဆေးခြင်း (Optional - နင်တစ်ယောက်တည်း သုံးချင်ရင်)
    # if message.chat.id not in ALLOWED_GROUPS:
    #     return

    user_text = message.text
    
    # တွက်ချက်ခြင်း (parser ဆီကနေ အသေးစိတ် အချက်အလက်တွေ ယူမယ်)
    try:
        result_data = calculate_2d(user_text)
        
        # result_data က 0 ဖြစ်နေရင် (တွက်စရာမရှိရင်) ဘာမှမလုပ်ဘူး
        if not result_data or result_data['total'] == 0:
            return

        total_amount = result_data['total']
        
        # Market & Cashback logic
        rate, rate_label = get_market_data(user_text)
        cashback = int(total_amount * rate)
        net_total = total_amount - cashback
        
        # Output Format (နင်လိုချင်တဲ့ ပုံစံအတိုင်း)
        response = (
            f"👤 {message.from_user.first_name}\n"
            f"--------------------\n"
            f"စုစုပေါင်း = {total_amount:,} ကျပ်\n"
            f"{rate_label} Cashback = {cashback:,} ကျပ်\n"
            f"--------------------\n"
            f"လက်ခံရမည့်ငွေ = {net_total:,} ကျပ်\n"
            f"--------------------\n"
            f"ကံကောင်းပါစေ ✨"
        )
        
        await message.answer(response)

    except Exception as e:
        logging.error(f"Error: {e}")
        # Error တက်ရင် ဘာမှပြန်မပြောဘဲ နေတာက ပိုကောင်းပါတယ် (Bot ရှုပ်မှာစိုးလို့)
        return

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
