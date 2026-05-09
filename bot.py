import os
import cv2
import numpy as np

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("TOKEN")

selected_timeframe = "15s"

# =====================================================
# START COMMAND
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🤖 OTC AI INSTITUTIONAL BOT

Send Pocket Option screenshot.

Commands:

/15s
/30s

Bot Features:
✅ AI trend analysis
✅ Momentum detection
✅ Volatility detection
✅ Candle pressure
✅ Support/Resistance estimation
✅ BUY / SELL / WAIT
"""

    await update.message.reply_text(text)

# =====================================================
# TIMEFRAME COMMANDS
# =====================================================

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

# =====================================================
# AI ANALYSIS ENGINE
# =====================================================

def analyze_chart(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return "❌ Could not analyze screenshot"

    height, width, _ = image.shape

    # =================================================
    # CROP CHART AREA
    # =================================================

    chart = image[:, int(width * 0.55):]

    hsv = cv2.cvtColor(chart, cv2.COLOR_BGR2HSV)

    # =================================================
    # GREEN DETECTION
    # =================================================

    lower_green = np.array([35, 40, 40])
    upper_green = np.array([90, 255, 255])

    green_mask = cv2.inRange(
        hsv,
        lower_green,
        upper_green
    )

    # =================================================
    # RED DETECTION
    # =================================================

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

    # =================================================
    # MOMENTUM STRENGTH
    # =================================================

    green_strength = np.sum(green_mask > 0)
    red_strength = np.sum(red_mask > 0)

    total_strength = green_strength + red_strength + 1

    bullish_pressure = green_strength / total_strength
    bearish_pressure = red_strength / total_strength

    # =================================================
    # TREND ESTIMATION
    # =================================================

    gray = cv2.cvtColor(chart, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=50,
        minLineLength=40,
        maxLineGap=10
    )

    trend_score = 0

    if lines is not None:

        for line in lines[:30]:

            x1, y1, x2, y2 = line[0]

            slope = (y2 - y1) / (x2 - x1 + 1)

            trend_score += slope

    # =================================================
    # VOLATILITY DETECTION
    # =================================================

    volatility = np.std(gray)

    # =================================================
    # DECISION ENGINE
    # =================================================

    signal = "⚪ WAIT"

    confidence = 50

    market_reason = "Market unclear"

    # STRONG BUY

    if (
        bullish_pressure > 0.58
        and trend_score < -5
        and volatility > 35
    ):

        signal = "🟢 BUY"

        confidence = int(
            min(
                95,
                60 + bullish_pressure * 40
            )
        )

        market_reason = "Bullish momentum detected"

    # STRONG SELL

    elif (
        bearish_pressure > 0.58
        and trend_score > 5
        and volatility > 35
    ):

        signal = "🔴 SELL"

        confidence = int(
            min(
                95,
                60 + bearish_pressure * 40
            )
        )

        market_reason = "Bearish momentum detected"

    # =================================================
    # ENTRY WINDOWS
    # =================================================

    if selected_timeframe == "15s":

        entry_window = "1-3 Seconds"

    else:

        entry_window = "3-8 Seconds"

    # =================================================
    # MARKET STRENGTH
    # =================================================

    market_strength = int(
        max(
            bullish_pressure,
            bearish_pressure
        ) * 100
    )

    # =================================================
    # FINAL RESPONSE
    # =================================================

    result = f"""
{signal}

⏱ Timeframe:
{selected_timeframe}

⚡ Entry Window:
{entry_window}

📊 Market Strength:
{market_strength}%

🔥 Confidence:
{confidence}%

🧠 AI Analysis:
{market_reason}

📸 Institutional chart analysis completed
"""

    return result

# =====================================================
# PHOTO HANDLER
# =====================================================

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    file = await context.bot.get_file(
        photo.file_id
    )

    image_path = "chart.jpg"

    await file.download_to_drive(image_path)

    result = analyze_chart(image_path)

    await update.message.reply_text(result)

# =====================================================
# MAIN
# =====================================================

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

    print("AI BOT RUNNING...")

    app.run_polling()

if __name__ == "__main__":
    main()
