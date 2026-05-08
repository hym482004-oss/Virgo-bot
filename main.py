import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    # parser.py မှ grand_total ကို ယူသည်
    total_sum, _ = calculate_bets(user_text)
    
    if total_sum == 0: return
    
    user = update.effective_user
    rate, rate_label = get_market_rate(user_text)
    
    cashback = int(total_sum * rate)
    net_total = total_sum - cashback
    
    # ရိုးရှင်းသော Output Format
    response = (
        f"👤 {user.first_name}\n"
        f"--------------------\n"
        f"စုစုပေါင်း = {total_sum:,} ကျပ်\n"
        f"{rate_label} Cashback = {cashback:,} ကျပ်\n"
        f"--------------------\n"
        f"လက်ခံရမည့်ငွေ = {net_total:,} ကျပ်\n"
        f"--------------------\n"
        f"ကံကောင်းပါစေ"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
