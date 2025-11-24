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

# ---------------- CONFIG ----------------
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
    conn = sqlite3.connect
