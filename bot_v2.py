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
from counters import COUNTERS
from storage import USER_DRAFTS
from draft_engine import get_recommendations

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


def get_main_keyboard():

    keyboard = []

    for mode_id, mode_data in MODES.items():
        keyboard.append([
            InlineKeyboardButton(
                mode_data["name"],
                callback_data=f"mode:{mode_id}"
            )
        ])

    return InlineKeyboardMarkup(keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "main_menu":

        await query.edit_message_text(
            "🏆 Dove Ranked Picks\n\nВыберите режим:",
            reply_markup=get_main_keyboard()
        )

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

    elif data.startswith("map:"):

        _, mode_id, map_name = data.split(":", 2)

        USER_DRAFTS[user_id] = {
            "map": map_name,
            "enemies": []
        }

        keyboard = [
            [
                InlineKeyboardButton(
                    "➕ Добавить врага",
                    callback_data="add_enemy"
                )
            ],
            [
                InlineKeyboardButton(
                    "📋 Список врагов",
                    callback_data="enemy_list"
                )
            ],
            [
                InlineKeyboardButton(
                    "🧠 Получить рекомендацию",
                    callback_data="recommend"
                )
            ],
            [
                InlineKeyboardButton(
                    "🗑 Очистить",
                    callback_data="clear_draft"
                )
            ],
            [
                InlineKeyboardButton(
                    "⬅️ Назад к картам",
                    callback_data=f"mode:{mode_id}"
                )
            ]
        ]

        await query.edit_message_text(
            f"🗺 Карта: {map_name}\n\nВыберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )