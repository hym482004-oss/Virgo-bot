import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

# နင်နောက်ဆုံးပေးထားတဲ့ Token
TOKEN = "8759881745:AAF29kI14jlV6oIP771xK5-GtUfHfH0YqDU"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_text = update.message.text
    total_sum = calculate_bets(user_text)
    if total_sum == 0: return
    user = update.effective_user
    
    # rate က None ဖြစ်မနေအောင် parser ထဲမှာရော ဒီမှာရော handle လုပ်ထားသည်
    rate, rate_label = get_market_rate(user_text)
    rate_val = rate if rate is not None else 0.07
    
    display_name = f"[{user.first_name}](tg://user?id={user.id})" if "7%" not in str(rate_label) else user.first_name
    cashback = int(total_sum * rate_val)
    net_total = total_sum - cashback
    
    # f-string ထဲမှာ backslash escape sequence များ မသုံးတော့ဘဲ SyntaxWarning ရှင်းလင်းသည်
    response = (
        f"👤 {display_name}\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{rate_label} Cash Back = {cashback:,} ကျပ်\n"
        f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ"
    )
    await update.message.reply_text(response, parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # Conflict Error (Bot ထပ်နေခြင်း) ကို ဖြေရှင်းရန်
    app.run_polling(drop_pending_updates=True)
