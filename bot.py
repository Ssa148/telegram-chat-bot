import os
import time

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)


# =========================================================
# הגדרות
# =========================================================

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# ה-Telegram User ID האישי שלך
# כאן תכניס את המספר שלך
ADMIN_CHAT_ID = 123456789

# אחרי שאתה עונה ידנית:
# הבוט יחזור לאוטומטי אחרי 2 וחצי דקות
MANUAL_TIMEOUT = 150


# =========================================================
# מחירון - כאן אתה משנה לבד
# =========================================================

MENU = {
    "קאלי גדול": 5=400₪
10=600₪
20=1200₪
50=2500₪,
    "קאלי ביטים": 5=350₪
10=600₪
20=1100₪
30=1500₪,
    "רפואי שקיות פתוח":
1=500₪
2=900₪
3=1200₪,
״חממה פרימיום״ 
10=400₪
20=600₪
50=1400₪,
״חשיש חמסה״ 
10=400,
״וייפ עטי אידוי״
1=350₪
2=600₪
3=800
5=1000₪,
״שמן מיצוי רפואי״
משתנה המחיר לפי זנים במלאי,
״מיוחדים אכילים״
תלוי בכמות,
{


# =========================================================
# מילים שהבוט יזהה כאישור
# =========================================================

APPROVAL_WORDS = [
    "סבבה",
    "מצוין",
    "מעולה",
    "תשלח",
    "תשלח לי",
    "יאללה",
    "בסדר",
    "מאשר",
    "קדימה",
]


# =========================================================
# שמירת מצב הלקוחות
# =========================================================

customers = {}


def get_customer(chat_id):
    if chat_id not in customers:
        customers[chat_id] = {
            "step": 0,
            "order": None,
            "product": None,
            "price": None,
            "manual_until": 0,
        }

    return customers[chat_id]


# =========================================================
# בדיקה האם אתה כרגע מנהל את השיחה ידנית
# =========================================================

def is_manual(customer):
    return time.time() < customer["manual_until"]


# =========================================================
# חיפוש מוצר בתוך מה שהלקוח כתב
# =========================================================

def find_product(text):
    text = text.lower().strip()

    for product, price in MENU.items():
        if product.lower() in text:
            return product, price

    return None, None


# =========================================================
# שליחת הודעה דרך החשבון העסקי
# =========================================================

async def business_send(context, message, text):
    await context.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        business_connection_id=message.business_connection_id,
    )


# =========================================================
# הודעות שהלקוח שולח לחשבון העסקי
# =========================================================

async def handle_business_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.business_message

    if not message:
        return

    # כרגע מטפלים רק בטקסט
    if not message.text:
        return

    text = message.text.strip()
    chat_id = message.chat.id

    customer = get_customer(chat_id)

    # -----------------------------------------------------
    # אם אתה כרגע מדבר ידנית עם הלקוח - הבוט שותק
    # -----------------------------------------------------

    if is_manual(customer):
        return

    step = customer["step"]

    # -----------------------------------------------------
    # שלב 0 - הודעה ראשונה
    # -----------------------------------------------------

    if step == 0:

        customer["step"] = 1

        await business_send(
            context,
            message,
            "מה קורה נשמה טוב"
        )

        return

    # -----------------------------------------------------
    # שלב 1 - אחרי שהלקוח ענה
    # -----------------------------------------------------

    if step == 1:

        customer["step"] = 2

        await business_send(
            context,
            message,
            "מה תרצו להזמין ולאיפה?"
        )

        return

    # -----------------------------------------------------
    # שלב 2 - הלקוח כתב מה הוא רוצה ולאיפה
    # -----------------------------------------------------

    if step == 2:

        customer["order"] = text
        customer["step"] = 3

        await business_send(
            context,
            message,
            (
                "שולח תפריט ראשי אחרי אימות !!
זה תפריט זנים לבינתיים אם יש 
שאלות אני פה ❤️
<<לתפריט לחץ עליי>>"
            )
        )

        return

    # -----------------------------------------------------
    # שלב 3 - הלקוח בוחר מוצר מהתפריט
    # -----------------------------------------------------

    if step == 3:

        product, price = find_product(text)

        # מצאנו מוצר
        if product:

            customer["product"] = product
            customer["price"] = price
            customer["step"] = 4

            await business_send(
                context,
                message,
                (
                    f"{product} ❤️\n"
                    f"המחיר הוא {price} ₪\n\n"
                    "מתאים לך?"
                )
            )

            return

        # -------------------------------------------------
        # המוצר לא נמצא במחירון
        # -------------------------------------------------

        await business_send(
            context,
            message,
            "בודק רגע ומעדכן אותך ❤️"
        )

        # שולחים אליך התראה
        if ADMIN_CHAT_ID != 123456789:

            username = (
                f"@{message.from_user.username}"
                if message.from_user and message.from_user.username
                else "אין Username"
            )

            name = (
                message.from_user.full_name
                if message.from_user
                else "לא ידוע"
            )

            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    "⚠️ מוצר לא נמצא במחירון\n\n"
                    f"לקוח: {name}\n"
                    f"Username: {username}\n"
                    f"מה הלקוח כתב:\n{text}\n\n"
                    f"Chat ID: {chat_id}"
                )
            )

        return

    # -----------------------------------------------------
    # שלב 4 - כבר נשלח מחיר
    # מחכים שהלקוח יאשר
    # -----------------------------------------------------

    if step == 4:

        lower_text = text.lower()

        approved = any(
            word in lower_text
            for word in APPROVAL_WORDS
        )

        if approved:

            customer["step"] = 5

            await business_send(
                context,
                message,
                (
                    "מעולה ❤️\n\n"
                    "עכשיו ממשיכים לשלב האימות."
                )
            )

            return

        # אם הוא לא אישר - לא מתקדמים אוטומטית
        await business_send(
            context,
            message,
            "סבבה, תגיד לי אם תרצה להתקדם ❤️"
        )

        return

    # -----------------------------------------------------
    # שלב 5
    # כאן נוסיף בהמשך את תהליך האימות
    # -----------------------------------------------------

    if step == 5:
        return


# =========================================================
# הודעות שאתה שולח בעצמך מהחשבון העסקי
# =========================================================

async def handle_edited_business_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # כרגע לא צריך לעשות כלום בעריכת הודעות
    return


# =========================================================
# MAIN
# =========================================================

def main():

    if not TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing"
        )

    app = Application.builder().token(TOKEN).build()

    # הודעות Business
    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle_business_message
        )
    )

    print("Business bot is running...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
