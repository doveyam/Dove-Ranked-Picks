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
                    "➖ Удалить врага",
                    callback_data="remove_enemy"
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

    elif data == "add_enemy":

        keyboard = []

        for brawler in sorted(COUNTERS.keys()):

            keyboard.append([
                InlineKeyboardButton(
                    brawler,
                    callback_data=f"enemy:{brawler}"
                    )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Назад",
                callback_data="back_to_draft"
            )
        ])

        await query.edit_message_text(
            "👥 Выберите вражеского бойца:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("enemy:"):

        enemy = data.replace("enemy:", "")

        if user_id in USER_DRAFTS:

            enemies = USER_DRAFTS[user_id]["enemies"]

            if enemy in enemies:

                await query.edit_message_text(
                    f"⚠️ {enemy} уже добавлен."
                )

                return

        if len(enemies) >= 3:

            await query.edit_message_text(
                "❌ Можно выбрать максимум 3 врага."
            )
            return

        enemies.append(enemy)

        await query.edit_message_text(
            f"✅ Добавлен: {enemy}\n\nМожно добавить еще врагов.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "➕ Добавить еще",
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
                ]
            ])
        )

    elif data == "enemy_list":

        draft = USER_DRAFTS.get(user_id)

        if not draft:

            await query.edit_message_text("Нет активного драфта.")
            return

        enemies = draft["enemies"]

        text = "👥 Враги:\n\n"

        if enemies:
            text += "\n".join([f"• {x}" for x in enemies])
        else:
            text += "Пока пусто"

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="back_to_draft"
                    )
                ]
            ])
        )

    elif data == "recommend":

        draft = USER_DRAFTS.get(user_id)

        if not draft:
            await query.edit_message_text("Нет активного драфта.")
            return

        map_name = draft["map"]
        enemies = draft["enemies"]

        if len(enemies) == 0:

            await query.edit_message_text(
                "Добавьте хотя бы одного врага."
            )

            return

        results = get_recommendations(
            enemies,
            MAPS[map_name],
            COUNTERS
        )

        text = "🧠 Лучшие пики:\n\n"

        for brawler, score in results:
            text += f"• {brawler} ({score})\n"

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="back_to_draft"
                    )
                ]
            ])
        )

    elif data == "clear_draft":

        USER_DRAFTS[user_id] = {
            "map": USER_DRAFTS[user_id]["map"],
            "enemies": []
        }

        await query.edit_message_text(
            "🗑 Драфт очищен.",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "⬅️ Назад",
                        callback_data="back_to_draft"
                    )
                ]
            ])
        )

    elif data == "back_to_draft":

        draft = USER_DRAFTS.get(user_id)

        if not draft:
            return

        map_name = draft["map"]

        keyboard = [
            [InlineKeyboardButton("➕ Добавить врага", callback_data="add_enemy")],
            [InlineKeyboardButton("📋 Список врагов", callback_data="enemy_list")],
            [InlineKeyboardButton("➖ Удалить врага", callback_data="remove_enemy")],
            [InlineKeyboardButton("🧠 Получить рекомендацию", callback_data="recommend")],
            [InlineKeyboardButton("🗑 Очистить", callback_data="clear_draft")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]

        await query.edit_message_text(
            f"🗺 Карта: {map_name}\n\nВыберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()