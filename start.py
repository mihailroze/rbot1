# handlers/start.py

import json
import os
import uuid
from telegram import Update
from telegram.ext import CallbackContext
from items import ITEMS
from menu import main_menu
from helpers import check_subscription

PLAYERS_FILE = 'data/players.json'
CHAT_ID = '@rust_services_chat'

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

def initialize_inventory():
    return {item['name']: 0 for item in ITEMS}

def generate_unique_username(existing_usernames):
    while True:
        username = f"user_{uuid.uuid4().hex[:8]}"
        if username not in existing_usernames:
            return username

async def start(update: Update, context: CallbackContext) -> None:
    if not await check_subscription(update, context, CHAT_ID):
        await update.message.reply_text('Для использования бота, пожалуйста, подпишитесь на чат: https://t.me/rust_services_chat')
        return

    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()

    if user_id in players:
        await update.message.reply_text('Вы уже зарегистрированы.')
        return

    existing_usernames = {player['name'] for player in players.values()}
    if user.username:
        username = user.username
    else:
        username = generate_unique_username(existing_usernames)

    players[user_id] = {
        'name': username,
        'id': user_id,
        'health': 100,
        'points': 0,
        'energy': 100,
        'weapon': None,
        'rustcoin': 0,
        'last_loot': None,
        'inventory': initialize_inventory(),
        'wins': 0,  # Инициализация количества побед
        'losses': 0,  # Инициализация количества поражений
    }
    save_players(players)
    await update.message.reply_text(f'Добро пожаловать в Rust Adventure, {username}!')

    commands_description = """
Добро пожаловать в Rust Adventure!

Вот список доступных команд:

1. `Исследование` - Исследуйте мир и находите различные предметы и оружие.
2. `Атаковать игрока` - Атакуйте другого игрока по его имени.
3. `Рейтинг игроков` - Просмотрите рейтинг всех игроков.
4. `Инвентарь` - Посмотрите содержимое вашего инвентаря.
5. `Обмен компонентов` - Обменивайте предметы на очки опыта.

Пример использования команды атаки:
`Атаковать игрока username`

Если у вас есть вопросы или проблемы, свяжитесь с поддержкой.

Удачи и приятной игры!
"""
    await update.message.reply_text(commands_description, reply_markup=main_menu())
