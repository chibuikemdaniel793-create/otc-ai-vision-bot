import os
import random
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 OTC Signal Bot Active\n\nSend chart screenshot."
    )

# PHOTO HANDLER
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    signals = [
        "🟢 BUY",
        "🔴 SELL",
        "⚪ WAIT"
    ]

    result = random.choice(signals)

    await update.message.reply_text(
        f"""
{result}

📊 Simple Signal Generated
⚡ Bot is responding correctly
"""
    )

# MAIN
def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.PHOTO,
            analyze
        )
    )

    print("BOT STARTED")

    app.run_polling()

if __name__ == "__main__":
    main()
