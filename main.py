import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets

# --- နင့်ဆီကရတဲ့ အချက်အလက်များ ---
TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"
# Group ID က 6023513934 ဆိုရင် Telegram API အရ ရှေ့မှာ -100 ခံပေးရပါတယ်
ALLOWED_GROUPS = [-1006023513934, 6023513934] 
CASHBACK_RATE = 0.07

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. ခွင့်ပြုထားတဲ့ Group ဟုတ်မဟုတ်စစ်ခြင်း
    if update.effective_chat.id not in ALLOWED_GROUPS:
        return 

    user_text = update.message.text
    if not user_text: return
    
    user_name = update.effective_user.first_name

    # 2. 2D Name ပါမပါစစ်ခြင်း (မပါရင် Admin/Owner ကို Mention ခေါ်မည်)
    if "2d" not in user_text.lower():
        try:
            admins = await update.effective_chat.get_administrators()
            mention_msg = "ဒါလေးလာစစ်ပေးပါရှင့် "
            for admin in admins:
                if not admin.user.is_bot:
                    mention_msg += f"@{admin.user.username} "
            await update.message.reply_text(mention_msg)
        except:
            # Private Chat ဖြစ်နေလျှင် သို့မဟုတ် Admin list ယူမရလျှင် ဘာမှမလုပ်ပါ
            pass
        return

    # 3. ဂဏန်းတွက်ချက်ခြင်း
    result = calculate_bets(user_text)

    # ဂဏန်းမပြည့်ခြင်း သို့မဟုတ် Format မှားနေခြင်း
    if result == "error":
        await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
        return

    # တကယ်တွက်လို့ရတဲ့ စာစောင် (Total > 0) ဖြစ်မှသာ reply ပြန်မည်
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
        # Reply function သုံးပြီး မူရင်းစာကို ပြန်ဖြေပေးမည်
        await update.message.reply_text(response)
        
if __name__ == '__main__':
    print("Bot is starting...")
    # Application ကို ဆောက်တဲ့နေရာမှာ အောက်ကအတိုင်း အသေသပ်ပြင်လိုက်ပါ
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Message handler ထည့်ခြင်း
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Error မတက်အောင် run_polling ကို ဒီအတိုင်းပဲ ထားပါ
    app.run_polling(drop_pending_updates=True)

