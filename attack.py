# handlers/attack.py

import json
import os
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler, MessageHandler, filters
from weapons import WEAPONS
from menu import main_menu
import logging

PLAYERS_FILE = 'data/players.json'
ATTACK_USERNAME = 1
HEALTH_RECOVERY_RATE = 1  # Скорость восстановления здоровья: 1 очко в минуту

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

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

def decrease_weapon_durability(player):
    if player['weapon']:
        weapon_wear = player['weapon']['wear']
        player['weapon']['durability'] -= weapon_wear
        if player['weapon']['durability'] <= 0:
            player['weapon'] = None

async def attack_button(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()
    logger.info(f"Checking registration for user_id: {user_id} in attack_button")

    if user_id not in players:
        logger.warning(f"User {user_id} not found in players")
        await update.message.reply_text('Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.', reply_markup=main_menu())
        return ConversationHandler.END

    await update.message.reply_text("Введите имя пользователя для атаки:", reply_markup=main_menu())
    logger.info("Transitioning to state ATTACK_USERNAME")
    return ATTACK_USERNAME

async def attack_username(update: Update, context: CallbackContext) -> int:
    logger.info("Function attack_username called")
    logger.info(f"Received message for attack_username: {update.message.text}")
    user = update.message.from_user
    attacker_id = str(user.id)
    target_name = update.message.text.strip()
    players = load_players()
    logger.info(f"Checking registration for attacker_id: {attacker_id} in attack_username")
    logger.info(f"Target name entered: {target_name}")

    if target_name == players[attacker_id]['name']:
        await update.message.reply_text('Вы не можете атаковать сами себя.', reply_markup=main_menu())
        return ConversationHandler.END

    target_id = None
    for player_id, player_data in players.items():
        if player_data['name'] == target_name:
            target_id = player_id
            break

    if not target_id:
        logger.warning(f"Target {target_name} not found in players")
        await update.message.reply_text('Пользователь не найден.', reply_markup=main_menu())
        return ConversationHandler.END

    # Проверка времени восстановления здоровья
    if 'last_death' in players[target_id]:
        time_since_death = datetime.now() - datetime.fromisoformat(players[target_id]['last_death'])
        recovered_health = int(time_since_death.total_seconds() // 60 * HEALTH_RECOVERY_RATE)
        players[target_id]['health'] = min(100, players[target_id]['health'] + recovered_health)
        if players[target_id]['health'] < 100:
            await update.message.reply_text(f"{target_name} недавно умер и не может быть атакован до полного восстановления здоровья.", reply_markup=main_menu())
            return ConversationHandler.END

    if attacker_id in players and target_id in players:
        attacker = players[attacker_id]
        target = players[target_id]
        logger.info(f"Attacking {target_name} by {attacker['name']}")

        if attacker['weapon']:
            damage = attacker['weapon']['damage']
            target['health'] -= damage
            result = f"Вы атаковали {target_name} с {attacker['weapon']['name']} и нанесли {damage} урона."
            decrease_weapon_durability(attacker)
        else:
            damage = random.randint(5, 10)
            target['health'] -= damage
            result = f"Вы атаковали {target_name} и нанесли {damage} урона голыми руками."

        if target['health'] <= 0:
            result += f" {target_name} был побежден."
            target['health'] = 0  # Устанавливаем здоровье на 0, чтобы начать восстановление
            target['last_death'] = datetime.now().isoformat()
            attacker['points'] += 100
            target['points'] = max(target['points'] - 100, 0)  # Не позволяем очкам уходить в минус
            attacker['wins'] = attacker.get('wins', 0) + 1
            target['losses'] = target.get('losses', 0) + 1
            for item, quantity in target['inventory'].items():
                attacker['inventory'][item] = min(attacker['inventory'][item] + quantity, 100)
            target['inventory'] = {item: 0 for item in target['inventory']}
            await context.bot.send_message(chat_id=target_id, text="Вы были убиты и потеряли весь свой инвентарь.")

        save_players(players)
        await update.message.reply_text(result, reply_markup=main_menu())
    else:
        logger.warning(f"One of the players is not registered. Attacker ID: {attacker_id}, Target ID: {target_id}")
        await update.message.reply_text('Один из игроков не зарегистрирован. Используйте /start для регистрации.', reply_markup=main_menu())

    logger.info(f"Attack operation completed for attacker_id: {attacker_id} targeting {target_name}")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Команда отменена.', reply_markup=main_menu())
    return ConversationHandler.END

def add_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^(Атаковать игрока)$'), attack_button)],
        states={
            ATTACK_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, attack_username)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, cancel)],
    )

    application.add_handler(conv_handler)
