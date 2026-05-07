async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ID စစ်တဲ့ အပိုင်းကို ခဏ ပိတ်ထားမယ် (ဘယ်နေရာမှာမဆို စမ်းလို့ရအောင်)
    # if update.effective_chat.id not in ALLOWED_GROUPS:
    #     return 

    user_text = update.message.text
    if not user_text: return
    
    # စာထဲမှာ 2d ပါတာနဲ့ တွက်မယ်
    if "2d" in user_text.lower():
        result = calculate_bets(user_text)
        
        if result == "error":
            await update.message.reply_text("ပြန်စစ်ပေးပါရှင့်")
            return

        if isinstance(result, (int, float)) and result > 0:
            cashback = int(result * 0.07)
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
