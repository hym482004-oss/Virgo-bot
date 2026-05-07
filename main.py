async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return

        user_text = update.message.text

        total_sum = calculate_bets(user_text)

        await update.message.reply_text(f"DEBUG TOTAL = {total_sum}")

    except Exception as e:
        await update.message.reply_text(f"ERROR: {str(e)}")
