import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = 1

    await update.message.reply_text(
        "מה קורה אחי הגעת 😎\n"
        "שלח לי הודעה ונמשיך..."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step", 0)

    if step == 0:
        await update.message.reply_text(
            "לחץ קודם /start כדי להתחיל 👇"
        )
        return

    if step == 1:
        context.user_data["step"] = 2
        await update.message.reply_text("מאיפה אתה? 📍")
        return

    if step == 2:
        context.user_data["city"] = text
        context.user_data["step"] = 3
        await update.message.reply_text("בן כמה אתה? 👤")
        return

    if step == 3:
        context.user_data["age"] = text
        context.user_data["step"] = 4
        await update.message.reply_text("איך קוראים לך?")
        return

    if step == 4:
        context.user_data["name"] = text
        context.user_data["step"] = 5
        await update.message.reply_text(
            f"נעים מאוד {text} 😎\n"
            "מה אתה מחפש?"
        )
        return

    if step == 5:
        context.user_data["looking_for"] = text
        context.user_data["step"] = 6

        await update.message.reply_text(
            "קיבלתי אחי ✅\n"
            "עוד מעט נחזור אליך."
        )
        return

    await update.message.reply_text(
        "כבר סיימנו 😎\n"
        "להתחלה מחדש לחץ /start"
    )


def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
