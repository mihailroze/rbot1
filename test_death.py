# handlers/test_death.py

import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext
from menu import main_menu

PLAYERS_FILE = 'data/players.json'
HEALTH_RECOVERY_TIME = timedelta(seconds=20)  # Время восстановления здоровья для тестирования

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

async def simulate_death(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()

    if user_id not in players:
        await update.message.reply_text('Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.')
        return

    player = players[user_id]
    player['health'] = 0
    player['last_death'] = datetime.now().isoformat()
    player['points'] = max(player['points'] - 100, 0)  # Не позволяем очкам уходить в минус
    player['losses'] = player.get('losses', 0) + 1
    player['inventory'] = {item: 0 for item in player['inventory']}
    save_players(players)

    await update.message.reply_text('Вы были убиты для тестирования. Ваше здоровье восстанавливается через 20 секунд, инвентарь утерян.', reply_markup=main_menu())
