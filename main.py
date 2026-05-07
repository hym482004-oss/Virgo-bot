import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from parser import calculate_bets, get_market_rate


TOKEN = os.getenv("BOT_TOKEN")


def detect_market_name(text):
    t = text.lower()

    if any(x in t for x in ['du', 'dubai', 'ဒူ']):
        return "Dubai"

    if any(x in t for x in ['mega', 'me']):
        return "Mega"

    if any(x in t for x in ['max', 'maxi']):
        return "Max"

    if any(x in t for x in ['lao']):
        return "Laos"

    if any(x in t for x in ['ld', 'london']):
        return "London"

    if any(x in t for x in ['mm']):
        return "Myanmar"

    if any(x in t for x in ['glo', 'global']):
        return "Global"

    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    total_sum = calculate_bets(user_text)

    if total_sum == 0:
        return

    market_name = detect_market_name(user_text)

    # 2D name မပါရင် admin mention
    if not market_name:
        admins = await context.bot.get_chat_administrators(update.effective_chat.id)

        mentions = []
        for admin in admins:
            user = admin.user
            mentions.append(f"[{user.first_name}](tg://user?id={user.id})")

        await update.message.reply_text(
            " ".join(mentions) + "\nဒါလေးလာစစ်ပေးပါရှင့်",
            parse_mode="Markdown"
        )
        return

    user = update.effective_user

    rate, rate_str = get_market_rate(user_text)

    cashback = int(total_sum * rate)
    final_total = total_sum - cashback

    response = (
        f"👤 {user.first_name}\n"
        f"2D name = {market_name}\n"
        f"Total = {total_sum:,} ကျပ်\n"
        f"{rate_str} Cash Back = {cashback:,} ကျပ်\n"
        f"လွဲရမည့်ငွေ = {final_total:,} ကျပ် ဘဲ လွဲပါရှင့်\n"
        f"ကံကောင်းပါစေ 🍀"
    )

    await update.message.reply_text(response)


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            handle_message
        )
    )

    app.run_polling(drop_pending_updates=True)
