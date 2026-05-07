import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    
    total_sum = calculate_bets(user_text)
    if total_sum == 0: return

    user = update.effective_user
    rate, rate_str = get_market_rate(user_text)
    
    # 2D name (du me) မပါရင် mention ခေါ်ခြင်း
    display_name = f"[{user.first_name}](tg://user?id={user.id})" if not rate_str else user.first_name
    
    final_rate = rate_str if rate_str else "7%"
    cashback = int(total_sum * (rate if rate else 0.07))
    net_total = total_sum - cashback
    
    response = (
        f"👤 {display_name}\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{final_rate} Cash Back = {cashback:,} ကျပ်\n"
        f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
