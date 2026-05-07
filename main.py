import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    
    rate, rate_str = get_market_rate(user_text)
    total_sum = calculate_bets(user_text)
    
    if total_sum == 0:
        if any(x in user_text.lower() for x in ['2d', 'du', 'me', 'mm', 'glo']):
            await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
        return

    if rate_str is None:
        rate_str = "7%"

    cashback = int(total_sum * rate)
    net_total = total_sum - cashback
    
    response = (
        f"👤 {update.effective_user.first_name}\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{rate_str} Cash Back = {cashback:,} ကျပ်\n"
        f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ"
    )
    await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # Error တက်နေတဲ့ parameter ကို ပြင်ထားတယ်
    app.run_polling(drop_pending_updates=True)
