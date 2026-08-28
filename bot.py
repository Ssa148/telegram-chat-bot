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

# כאן תכניס את ה-Telegram User ID האישי שלך
ADMIN_CHAT_ID = 123456789

# הודעה שמפעילה את הבוט
START_MESSAGE = "אשמח להזמין + פינוקים 🎁"

# אחרי שאתה עונה ידנית:
# 150 שניות = 2 וחצי דקות
MANUAL_TIMEOUT = 150


# =========================================================
# מחירון
# אתה יכול להוסיף כמה מוצרים שאתה רוצה
# =========================================================

MENU = {
    "קאלי גדול": 5=400
10=600
20=1200
50=2500,
    "קאלי ביטים": 5=350
10=600
20=1100
30=1500,
    "רפואי שקיות פתוח":
1=500
2=900
3=1200,
"חממה פרימיום"
10=400
20=600
50=1400,
"חשיש חמסה" 
10=400,
"וייפ עטי אידוי"
1=350
2=600
3=800
5=1000,
"שמן מיצוי רפואי"
משתנה המחיר לפי זנים במלאי,
"מיוחדים אכילים"
תלוי בכמות,
{

# =========================================================
# מילים שהבוט מזהה כאישור
# =========================================================

APPROVAL_WORDS = [
    "סבבה",
    "מצוין",
    "מצויין",
    "מעולה",
    "תשלח",
    "תשלח לי",
    "יאללה",
    "בסדר",
    "מאשר",
    "קדימה",
]


# =========================================================
# שמירת מצב של כל לקוח
# =========================================================

customers = {}


def get_customer(chat_id):
    if chat_id not in customers:
        customers[chat_id] = {
            "started": False,
            "step": 0,
            "order": None,
            "product": None,
            "price": None,
            "manual_until": 0,
        }

    return customers[chat_id]


# =========================================================
# בדיקה אם הבוט במצב ידני אצל לקוח
# =========================================================

def is_manual(customer):
    return time.time() < customer["manual_until"]


# =========================================================
# חיפוש מוצר בצורה גמישה
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
# טיפול בהודעות של לקוחות
# =========================================================

async def handle_business_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.business_message

    if not message:
        return

    # כרגע הבוט עובד רק עם הודעות טקסט
    if not message.text:
        return

    text = message.text.strip()
    chat_id = message.chat.id

    customer = get_customer(chat_id)

    # =====================================================
    # לקוח שעוד לא התחיל את התהליך
    # =====================================================

    if not customer["started"]:

        # מתחילים רק אם נשלחה הודעת ההפעלה
        if text != START_MESSAGE:
            return

        customer["started"] = True
        customer["step"] = 1

        await business_send(
            context,
            message,
            "מה קורה נשמה טוב"
        )

        return

    # =====================================================
    # אם אתה כרגע מנהל את השיחה ידנית
    # =====================================================

    if is_manual(customer):
        return

    step = customer["step"]

    # =====================================================
    # שלב 1
    # הלקוח עונה אחרי "מה קורה נשמה טוב"
    # =====================================================

    if step == 1:

        customer["step"] = 2

        await business_send(
            context,
            message,
            "מה תרצו להזמין ולאיפה?"
        )

        return

    # =====================================================
    # שלב 2
    # הלקוח כתב מה רוצה ולאיפה
    # =====================================================

    if step == 2:

        customer["order"] = text
        customer["step"] = 3

        await business_send(
            context,
            message,
            (
                "שולח תפריט ראשי אחרי אימות !!\n\n"
                "זה תפריט לבינתיים אם יש שאלות אני פה ❤️"
            )
        )

        return

    # =====================================================
    # שלב 3
    # הלקוח כותב מוצר מתוך התפריט
    # =====================================================

    if step == 3:

        product, price = find_product(text)

        # ------------------------------
        # נמצא מוצר
        # ------------------------------

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

        # ------------------------------
        # לא נמצא מוצר
        # ------------------------------

        await business_send(
            context,
            message,
            "בודק רגע ומעדכן אותך ❤️"
        )

        # התראה אליך
        if ADMIN_CHAT_ID != 123456789:

            if message.from_user:
                name = message.from_user.full_name

                if message.from_user.username:
                    username = f"@{message.from_user.username}"
                else:
                    username = "אין Username"
            else:
                name = "לא ידוע"
                username = "לא ידוע"

            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=(
                    "⚠️ לקוח כתב משהו שלא נמצא במחירון\n\n"
                    f"שם: {name}\n"
                    f"Username: {username}\n\n"
                    f"הלקוח כתב:\n{text}\n\n"
                    f"Chat ID: {chat_id}"
                )
            )

        return

    # =====================================================
    # שלב 4
    # כבר נשלח מחיר ומחכים לאישור
    # =====================================================

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

        await business_send(
            context,
            message,
            "סבבה, תגיד לי אם תרצה להתקדם ❤️"
        )

        return

    # =====================================================
    # שלב 5
    # כאן נוסיף את המשך האימות
    # =====================================================

    if step == 5:
        return


# =========================================================
# הפעלת הבוט
# =========================================================

def main():

    if not TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is missing"
        )

    app = Application.builder().token(TOKEN).build()

    # רק הודעות Telegram Business
    app.add_handler(
        MessageHandler(
            filters.UpdateType.BUSINESS_MESSAGE,
            handle_business_message
        )
    )

    print("Business bot is running...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
