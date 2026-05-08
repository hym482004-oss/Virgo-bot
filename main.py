import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    total_sum, lines_data = calculate_bets(user_text)
    
    if total_sum == 0: return
    
    user = update.effective_user
    rate, rate_label = get_market_rate(user_text)
    
    cashback = int(total_sum * rate)
    net_total = total_sum - cashback
    
    # Line by line output assembly
    line_report = "\n".join(lines_data)
    
    response = (
        f"👤 {user.first_name}\n"
        f"--------------------\n"
        f"{line_report}\n"
        f"--------------------\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{rate_label} Cashback = {cashback:,} ကျပ်\n"
        f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
