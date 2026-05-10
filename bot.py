import os
import cv2
import numpy as np

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

TOKEN = os.getenv("TOKEN")

# =========================================
# WEB SERVER FOR RENDER
# =========================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "BOT RUNNING"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)

# =========================================
# SETTINGS
# =========================================

selected_timeframe = "15s"

# =========================================
# START COMMAND
# =========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 OTC AI SIGNAL BOT

Send chart screenshot.

Commands:
/15s
/30s
"""

    await update.message.reply_text(text)

# =========================================
# TIMEFRAME
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
# ANALYSIS ENGINE
# =========================================

def analyze_chart(image_path):

    try:

        image = cv2.imread(image_path)

        if image is None:
            return "❌ Could not read screenshot"

        height, width, _ = image.shape

        chart = image[:, int(width * 0.55):]

        hsv = cv2.cvtColor(chart, cv2.COLOR_BGR2HSV)

        # GREEN

        lower_green = np.array([35, 40, 40])
        upper_green = np.array([90, 255, 255])

        green_mask = cv2.inRange(
            hsv,
            lower_green,
            upper_green
        )

        # RED

        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        red_mask1 = cv2.inRange(
            hsv,
            lower_red1,
            upper_red1
        )

        red_mask2 = cv2.inRange(
            hsv,
            lower_red2,
            upper_red2
        )

        red_mask = red_mask1 + red_mask2

        # STRENGTH

        green_strength = np.sum(green_mask > 0)
        red_strength = np.sum(red_mask > 0)

        total = green_strength + red_strength + 1

        bullish = green_strength / total
        bearish = red_strength / total

        # VOLATILITY

        gray = cv2.cvtColor(chart, cv2.COLOR_BGR2GRAY)

        volatility = int(np.std(gray))

        # MOMENTUM

        momentum = abs(
            green_strength - red_strength
        )

        # SIGNAL

        signal = "⚪ WAIT"
        confidence = 50
        reason = "Market unclear"

        if bullish > 0.58 and momentum > 1500:

            signal = "🟢 BUY"
            confidence = int(
                min(95, 60 + bullish * 40)
            )

            reason = "Bullish pressure detected"

        elif bearish > 0.58 and momentum > 1500:

            signal = "🔴 SELL"
            confidence = int(
                min(95, 60 + bearish * 40)
            )

            reason = "Bearish pressure detected"

        if selected_timeframe == "15s":
            entry = "1-3 Seconds"
        else:
            entry = "3-8 Seconds"

        strength = int(
            max(bullish, bearish) * 100
        )

        return f"""
{signal}

⏱ Timeframe:
{selected_timeframe}

⚡ Entry Window:
{entry}

📊 Market Strength:
{strength}%

🔥 Confidence:
{confidence}%

🧠 Analysis:
{reason}

📈 Volatility:
{volatility}

💥 Momentum:
{momentum}
"""

    except Exception as e:

        return f"❌ Error: {str(e)}"

# =========================================
# PHOTO HANDLER
# =========================================

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        photo = update.message.photo[-1]

        file = await context.bot.get_file(
            photo.file_id
        )

        image_path = "chart.jpg"

        await file.download_to_drive(image_path)

        result = analyze_chart(image_path)

        await update.message.reply_text(result)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Failed: {str(e)}"
        )

# =========================================
# MAIN
# =========================================

def main():

    Thread(target=run_web).start()

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

    print("BOT RUNNING")

    app.run_polling()

if __name__ == "__main__":
    main()
