import asyncio
import sqlite3
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8467867383:AAGrCYHbRJqxZwPm2rS8YCjb5Wf_ulLVG_o"
ADMIN_ID = 7085347092
SHOPS = ["Ц. Рынок", "ТЦ Апельсин", "Базар"]
DB = "data.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS employees (user_id INTEGER PRIMARY KEY)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS cash_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        shop TEXT,
        cash TEXT,
        datetime TEXT
    )""")
    conn.commit()
    conn.close()

def add_employee(user_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO employees (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def save_cash(user_id, shop, cash):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cash_reports (user_id, shop, cash, datetime) VALUES (?, ?, ?, ?)",
        (user_id, shop, cash, datetime.now().strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

def get_employees():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM employees")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_all_reports():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT user_id, shop, cash, datetime FROM cash_reports ORDER BY datetime DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

# ---------------- BOT HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_employee(update.effective_user.id)
    await update.message.reply_text("Вы подключены. Ожидайте уведомления.")

async def report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(shop, callback_data=f"shop|{shop}")] for shop in SHOPS]
    await update.message.reply_text("Выберите магазин:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Недостаточно прав.")
        return
    reports = get_all_reports()
    if not reports:
        await update.message.reply_text("Нет данных.")
        return
    text = "Все отчёты:\n\n"
    for user_id, shop, cash, dt in reports:
        text += f"👤 {user_id}\n🏬 {shop}\n💰 {cash}\n⏱ {dt}\n\n"
    await update.message.reply_text(text)

async def choose_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, shop = update.callback_query.data.split("|")
    context.user_data["shop"] = shop
    await update.callback_query.message.reply_text(f"Введите кассу для: {shop}")
    await update.callback_query.answer()

async def cash_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "shop" not in context.user_data:
        return
    shop = context.user_data["shop"]
    cash = update.message.text
    save_cash(update.effective_user.id, shop, cash)
    await update.message.reply_text("Сохранено.")
    context.user_data.clear()

# ---------------- REMINDERS ----------------
async def send_reminders(app):
    target_times = {"11:00", "13:00", "15:00", "18:00"}
    while True:
        now = datetime.now().strftime("%H:%M")
        if now in target_times:
            employees = get_employees()
            for emp in employees:
                try:
                    await app.bot.send_message(emp, "Пора отправить кассу! Нажмите /report")
                except:
                    pass
            await asyncio.sleep(70)
        await asyncio.sleep(1)

# ---------------- MAIN ----------------
def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", report_menu))
    app.add_handler(CommandHandler("all", admin_all))
    app.add_handler(CallbackQueryHandler(choose_shop, pattern="shop"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cash_input))
    asyncio.ensure_future(send_reminders(app))
    print("Bot started on Render")
    app.run_polling()

if __name__ == "__main__":
    main()

