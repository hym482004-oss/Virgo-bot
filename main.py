import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate

# Bot Token ကို ဒီမှာ အသေသတ်မှတ်ထားတယ်
TOKEN = "8759881745:AAEu7PQ3RjOmw-NMk29GQhczEPeT20TZJaQ"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Group ID စစ်တဲ့အပိုင်းကို လုံးဝဖြုတ်လိုက်ပါပြီ
    
    user_text = update.message.text
    if not user_text: return
    text_lower = user_text.lower()

    # 1. "2d" မပါရင် ဘာမှမလုပ်ဘူး (Group ထဲမှာ စကားပြောတာကို မနှောင့်ယှက်ဖို့)
    if "2d" not in text_lower:
        return

    # 2. "2d" ပါလာရင် Market name (Du, Me, Glo, etc.) ပါမပါ အရင်စစ်မယ်
    rate, rate_str = get_market_rate(user_text)
    
    if rate is None:
        # Market name မပါရင် Admin/Owner ကို Mention ခေါ်မယ်
        try:
            admins = await update.effective_chat.get_administrators()
            mention_msg = "ဒါလေးလာစစ်ပေးပါရှင့် "
            for admin in admins:
                if not admin.user.is_bot:
                    mention_msg += f"@{admin.user.username} "
            await update.message.reply_text(mention_msg)
        except:
            # Private Chat မှာဆိုရင် Admin မရှိလို့ mention ခေါ်မရရင် ဒီစာပဲပြန်မယ်
            await update.message.reply_text("Market name (ဥပမာ- Du, Me, Mm) ထည့်ပေးပါဦးရှင့်")
        return

    # 3. Market ပါရင် ဂဏန်းတွက်မယ်
    total_sum = calculate_bets(user_text)
    
    if total_sum == 0:
        await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
        return

    # 4. Result ထုတ်ပြန်မယ်
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
    print("Bot is starting without group restrictions...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
