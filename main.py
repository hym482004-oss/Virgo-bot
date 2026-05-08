import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8759881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text: return
        user_text = update.message.text
        
        total_sum = calculate_bets(user_text)
        if total_sum == 0: return
        
        user = update.effective_user
        rate, rate_label = get_market_rate(user_text)
        
        # User Mention format
        display_name = f"[{user.first_name}](tg://user?id={user.id})" if not any(x in user_text.lower() for x in ['du', 'me', 'glo']) else user.first_name
        
        cashback = int(total_sum * rate)
        net_total = total_sum - cashback
        
        response = (
            f"👤 {display_name}\n"
            f"Total = {total_sum:,} ကျပ်\n"
            f"{rate_label} Cash Back = {cashback:,} ကျပ်\n"
            f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error occurred: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # drop_pending_updates=True က bot စာမပြန်တာကို ဖြေရှင်းပေးမယ်
    app.run_polling(drop_pending_updates=True)
