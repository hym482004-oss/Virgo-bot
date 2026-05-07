import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_text = update.message.text
    text_lower = user_text.lower()

    # "2d" သို့မဟုတ် market name တစ်ခုခုပါမှ အလုပ်လုပ်မယ်
    market_keywords = ['2d', 'mega', 'du', 'mm', 'glo', 'maxi', 'lao', 'ld', 'မီ', 'ဒူ']
    if not any(x in text_lower for x in market_keywords):
        return

    # Market စစ်မယ်
    rate, rate_str = get_market_rate(user_text)
    
    # တွက်မယ်
    total_sum = calculate_bets(user_text)
    
    if total_sum == 0:
        if "2d" in text_lower: # 2d လို့ပါပြီး တွက်မရရင်ပဲ ပြန်စစ်ခိုင်းမယ်
            await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
        return

    # Market name မပါရင် Admin ခေါ်မယ် (Default 7% နဲ့တွက်မယ်)
    if rate_str is None:
        rate_str = "7%"
        try:
            admins = await update.effective_chat.get_administrators()
            mention_msg = "ဒါလေးလာစစ်ပေးပါရှင့် "
            for admin in admins:
                if not admin.user.is_bot:
                    mention_msg += f"@{admin.user.username} "
            await update.message.reply_text(mention_msg)
        except: pass

    # Result ပြမယ်
    cashback_amt = int(total_sum * rate)
    net_total = total_sum - cashback_amt
    user_name = update.effective_user.first_name
    
    response = (
        f"👤 {user_name}\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{rate_str} Cash Back = {cashback_amt:,} ကျပ်\n"
        f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ"
    )
    await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
