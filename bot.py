from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os

from data import MODES

TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = []

    for mode_id, mode_data in MODES.items():
        keyboard.append([
            InlineKeyboardButton(
                mode_data["name"],
                callback_data=f"mode:{mode_id}"
            )
        ])

    await update.message.reply_text(
        "🏆 Dove Ranked Picks\n\nВыберите режим:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("mode:"):

        mode_id = data.split(":")[1]

        maps = MODES[mode_id]["maps"]

        keyboard = []

        for map_name in maps:
            keyboard.append([
                InlineKeyboardButton(
                    map_name,
                    callback_data=f"map:{map_name}"
                )
            ])

        await query.edit_message_text(
            f"📍 {MODES[mode_id]['name']}\n\nВыберите карту:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("map:"):

        map_name = data.replace("map:", "")

        await query.edit_message_text(
            f"🗺 Карта: {map_name}\n\nМета подключается..."
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()