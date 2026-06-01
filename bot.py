from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import os

from data import MODES
from maps import MAPS

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

    # ГЛАВНОЕ МЕНЮ РЕЖИМОВ
    if data == "main_menu":

        keyboard = []

        for mode_id, mode_data in MODES.items():
            keyboard.append([
                InlineKeyboardButton(
                    mode_data["name"],
                    callback_data=f"mode:{mode_id}"
                )
            ])

        await query.edit_message_text(
            "🏆 Dove Ranked Picks\n\nВыберите режим:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ВЫБОР РЕЖИМА
    elif data.startswith("mode:"):

        mode_id = data.split(":")[1]

        maps = MODES[mode_id]["maps"]

        keyboard = []

        for map_name in maps:
            keyboard.append([
                InlineKeyboardButton(
                    map_name,
                    callback_data=f"map:{mode_id}:{map_name}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "🏠 Главное меню",
                callback_data="main_menu"
            )
        ])

        await query.edit_message_text(
            f"📍 {MODES[mode_id]['name']}\n\nВыберите карту:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ВЫБОР КАРТЫ
    elif data.startswith("map:"):

        _, mode_id, map_name = data.split(":", 2)

        back_keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ Назад к картам",
                    callback_data=f"mode:{mode_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 Главное меню",
                    callback_data="main_menu"
                )
            ]
        ]

        if map_name in MAPS:

            m = MAPS[map_name]

            text = (
                f"🗺 {map_name}\n\n"
                f"🚫 Приоритетные баны\n"
                + "\n".join([f"• {x}" for x in m["priority_bans"]])

                + "\n\n⚠️ Альтернативные баны\n"
                + "\n".join([f"• {x}" for x in m["alt_bans"]])

                + "\n\n✅ Ферст пики\n"
                + "\n".join([f"• {x}" for x in m["first_picks"]])

                + "\n\n🎯 Ласт пики\n"
                + "\n".join([f"• {x}" for x in m["last_picks"]])
            )

            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(back_keyboard)
            )

        else:

            await query.edit_message_text(
                f"🗺 Карта: {map_name}\n\nНет данных.",
                reply_markup=InlineKeyboardMarkup(back_keyboard)
            )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()