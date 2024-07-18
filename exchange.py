# handlers/exchange.py

import json
import os
from telegram import Update
from telegram.ext import CallbackContext
from items import ITEMS
from menu import main_menu

PLAYERS_FILE = 'data/players.json'
EXCHANGE_RATE = 1000  # Очки, получаемые за 100 предметов

def load_players():
    if not os.path.exists(PLAYERS_FILE):
        return {}
    try:
        with open(PLAYERS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_players(players):
    with open(PLAYERS_FILE, 'w') as file:
        json.dump(players, file, indent=4)

async def exchange(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()

    if user_id in players:
        player = players[user_id]
        exchange_text = "Вы обменяли:\n"
        points_earned = 0
        for item in ITEMS:
            item_name = item['name']
            if player['inventory'][item_name] >= 100:
                player['inventory'][item_name] -= 100
                points_earned += EXCHANGE_RATE
                exchange_text += f"100 {item_name} на {EXCHANGE_RATE} очков\n"

        if points_earned > 0:
            player['points'] += points_earned
            exchange_text += f"Вы получили {points_earned} очков."
        else:
            exchange_text = "Недостаточно предметов для обмена."

        save_players(players)
        await update.message.reply_text(exchange_text, reply_markup=main_menu())
    else:
        await update.message.reply_text(
            'Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.',
            reply_markup=main_menu()
        )
