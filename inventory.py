# handlers/inventory.py

import json
import os
from telegram import Update
from telegram.ext import CallbackContext
from menu import main_menu

PLAYERS_FILE = 'data/players.json'


def load_players():
    if not os.path.exists(PLAYERS_FILE):
        return {}
    try:
        with open(PLAYERS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


async def inventory(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()

    if user_id in players:
        player = players[user_id]
        inventory_text = "Ваш инвентарь:\n"
        for item, quantity in player['inventory'].items():
            inventory_text += f"{item}: {quantity}\n"

        # Добавляем информацию о оружии
        if player['weapon']:
            weapon = player['weapon']
            inventory_text += f"\nВаше оружие:\n"
            inventory_text += f"Название: {weapon['name']}\n"
            inventory_text += f"Прочность: {weapon['durability']}\n"
            inventory_text += f"Урон: {weapon['damage']}\n"
            inventory_text += f"Износ: {weapon['wear']}\n"
            inventory_text += f"Шанс: {weapon['chance']}%\n"

        await update.message.reply_text(inventory_text, reply_markup=main_menu())
    else:
        await update.message.reply_text(
            'Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.',
            reply_markup=main_menu()
        )
