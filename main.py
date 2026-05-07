import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets

# --- SETTINGS ---
TOKEN = "နင့်ရဲ့_BOT_TOKEN_ဒီမှာထည့်"
ALLOWED_GROUPS = [-100123456789, -100987654321] # နင်ခွင့်ပြုမယ့် Group ID တွေပဲ ဒီမှာထည့်
CASHBACK_RATE = 0.07

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. ခွင့်ပြုထားတဲ့ Group ဟုတ်မဟုတ်စစ်
    if update.effective_chat.id not in ALLOWED_GROUPS:
        return 

    user_text = update.message.text
    if not user_text: return
    
    # 2. 2D Name ပါမပါစစ် (မပါရင် Admin/Owner Mention ခေါ်)
    if "2d" not in user_text.lower():
        try:
            admins = await update.effective_chat.get_administrators()
            mention_msg = "ဒါလေးလာစစ်ပေးပါရှင့် "
            for admin in admins:
                if not admin.user.is_bot:
                    mention_msg += f"@{admin.user.username} "
            await update.message.reply_text(mention_msg)
        except: pass
        return

    # 3. တွက်ချက်ခြင်း
    result = calculate_bets(user_text)

    # ဂဏန်းမပြည့်လို့ အမှားတက်ရင်
    if result == "error":
        await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
        return

    # တကယ်တွက်လို့ရတဲ့ စာစောင်ဆိုရင်ပဲ reply ပြန်မယ်
    if isinstance(result, int) and result > 0:
        cashback = int(result * CASHBACK_RATE)
        net_total = result - cashback
        user_name = update.effective_user.first_name
        
        response = (
            f"👤 {user_name}\n"
            f"Total = {result:,} ကျပ်\n"
            f"7% Cash Back = {cashback:,} ကျပ်\n"
            f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
            f"ကံကောင်းပါစေ"
        )
        await update.message.reply_text(response)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is started...")
    app.run_polling()
