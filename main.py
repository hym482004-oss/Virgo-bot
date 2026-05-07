import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets

TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"
# ဒီတစ်ခါ ID စစ်တာကို ခဏပိတ်ထားမယ်၊ ဒါမှ နင် ဘယ် Group ထဲထည့်ထည့် အလုပ်လုပ်မှာ
CASHBACK_RATE = 0.07

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Log ထဲမှာ Group ID ကို ကြည့်လို့ရအောင် print ထုတ်ခိုင်းမယ်
    print(f"Message from Chat ID: {update.effective_chat.id}")

    user_text = update.message.text
    if not user_text: return
    
    user_name = update.effective_user.first_name
    text_lower = user_text.lower()

    # 1. စာထဲမှာ 2d ပါမှ တွက်မယ်
    if "2d" in text_lower:
        result = calculate_bets(user_text)

        if result == "error":
            await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
            return

        if isinstance(result, (int, float)) and result > 0:
            cashback = int(result * CASHBACK_RATE)
            net_total = result - cashback
            
            response = (
                f"👤 {user_name}\n"
                f"Total = {result:,} ကျပ်\n"
                f"7% Cash Back = {cashback:,} ကျပ်\n"
                f"Total = {net_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
                f"ကံကောင်းပါစေ"
            )
            await update.message.reply_text(response)
            return

    # 2. 2D name မပါရင် Admin/Owner Mention ခေါ်မယ်
    # စာလုံးရေ အနည်းဆုံး ၅ လုံးရှိမှ (စကားပြောတာမျိုးမဟုတ်မှ) mention ခေါ်ဖို့
    elif len(user_text) > 10:
        try:
            admins = await update.effective_chat.get_administrators()
            mention_msg = "ဒါလေးလာစစ်ပေးပါရှင့် "
            for admin in admins:
                if not admin.user.is_bot:
                    mention_msg += f"@{admin.user.username} "
            await update.message.reply_text(mention_msg)
        except:
            pass

if __name__ == '__main__':
    print("Bot is starting...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    # drop_pending_updates က bot ပိတ်ထားတုန်းကစာတွေကို ကျော်သွားဖို့
    app.run_polling(drop_pending_updates=True)
