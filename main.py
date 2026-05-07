import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    
    total_sum = calculate_bets(user_text)
    if total_sum == 0: return

    # User Name ကို Mention ခေါ်ရန်
    user = update.effective_user
    mention_link = f"[{user.first_name}](tg://user?id={user.id})"

    rate, rate_str = get_market_rate(user_text)
    
    # 2D Name (Du/Me/...) မပါရင် Mention ခေါ်မယ်
    if rate_str is None:
        rate_str = "7%"
        # Mention လင့်ခ်ဖြင့် စာပြန်ခြင်း
        response = (
            f"👤 {mention_link}\n"
            f"Total = {total_sum:,} ကျပ်\n"
            f"{rate_str} Cash Back = {int(total_sum * 0.07):,} ကျပ်\n"
            f"Total = {total_sum - int(total_sum * 0.07):,} ကျပ် ဘဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        # Market Name ပါရင် ပုံမှန်အတိုင်းပြန်မယ်
        cashback = int(total_sum * rate)
        response = (
            f"👤 {user.first_name}\n"
            f"Total = {total_sum:,} ကျပ်\n"
            f"{rate_str} Cash Back = {cashback:,} ကျပ်\n"
            f"Total = {total_sum - cashback:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ"
        )
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
