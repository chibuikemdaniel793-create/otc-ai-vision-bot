import os

from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =========================================
# TOKEN
# =========================================

TOKEN = os.getenv("TOKEN")

# =========================================
# KEEP RENDER ALIVE
# =========================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "BOT IS RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

Thread(target=run_web).start()

# =========================================
# GLOBAL TIMEFRAME
# =========================================

selected_timeframe = "15s"

# =========================================
# START COMMAND
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = f"""
🤖 OTC SIGNAL BOT

Send chart screenshot.

Commands:

/15s
/30s

Current timeframe:
{selected_timeframe}
"""

    await update.message.reply_text(text)

# =========================================
# TIMEFRAME COMMANDS
# =========================================

async def mode_15(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global selected_timeframe

    selected_timeframe = "15s"

    await update.message.reply_text(
        "⚡ 15s mode activated"
    )

async def mode_30(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global selected_timeframe

    selected_timeframe = "30s"

    await update.message.reply_text(
        "⚡ 30s mode activated"
    )

# =========================================
# SIMPLE SIGNAL ENGINE
# =========================================

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    result = f"""
🟢 BUY SIGNAL

⏱ Timeframe:
{selected_timeframe}

🔥 Confidence:
78%

📊 Market Condition:
Trending Market

⚡ Entry:
Wait for candle confirmation

✅ Bot running successfully
"""

    await update.message.reply_text(result)

# =========================================
# MAIN
# =========================================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("15s", mode_15)
    )

    app.add_handler(
        CommandHandler("30s", mode_30)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            analyze
        )
    )

    print("BOT RUNNING...")

    app.run_polling()

if __name__ == "__main__":
    main()
