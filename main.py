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
    
    # Du/Me မပါရင် Mention ခေါ်မယ်
    display_name = f"[{user.first_name}](tg://user?id={user.id})" if not rate_str else user.first_name
    
    rate_label = rate_str if rate_str else "7%"
    cashback = int(total_sum * (rate if rate else 0.07))
    net_total = total_sum - cashback
    
    # Escape sequence error မတက်အောင် string format ကို ပြင်ထားပါတယ်
    response = (
        "👤 " + str(display_name) + "\n" +
        "Total = " + "{:,}".format(total_sum) + " ကျပ်\n" +
        str(rate_label) + " Cash Back = " + "{:,}".format(cashback) + " ကျပ်\n" +
        "Total = " + "{:,}".format(net_total) + " ကျပ် ဘဲ လွဲပါရှင့်\n" +
        "ကံကောင်းပါစေ"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # Conflict Error အတွက် drop_pending_updates ထည့်ထားသည်
    app.run_polling(drop_pending_updates=True)
