# handlers/explore.py

import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from weapons import get_random_weapon
from items import get_random_item, ITEMS
from menu import main_menu

PLAYERS_FILE = 'data/players.json'
ENERGY_COST = 10
RUSTCOIN_CHANCE = 0.05  # Шанс нахождения rustcoin в процентах

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

async def explore(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()

    if user_id in players:
        loot = random.choice(["бочка", "ящик", "ничего"])
        if loot == "ничего":
            await update.message.reply_text("Вы ничего не нашли.", reply_markup=main_menu())
        else:
            players[user_id]['last_loot'] = loot
            save_players(players)

            keyboard = [
                [InlineKeyboardButton("Разбить", callback_data='break')],
                [InlineKeyboardButton("Пропустить", callback_data='skip')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"Перед вами {loot}. Что вы хотите сделать?", reply_markup=reply_markup)
    else:
        await update.message.reply_text('Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.', reply_markup=main_menu())

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)
    players = load_players()
    player = players.get(user_id, None)

    if not player:
        await query.answer("Сначала зарегистрируйтесь с помощью команды /start.")
        return

    choice = query.data
    loot = player.get('last_loot', None)

    if not loot:
        await query.answer("Произошла ошибка, попробуйте снова.")
        return

    if choice == 'break':
        if player['energy'] < ENERGY_COST:
            await query.answer("Недостаточно энергии для лутания. Подождите некоторое время для восстановления энергии.")
            return

        player['energy'] -= ENERGY_COST
        if loot == "бочка":
            points = random.randint(5, 15)
        else:
            points = random.randint(10, 25)
        player['points'] += points
        result = f"Вы разбили {loot} и получили {points} очков опыта."

        # Вероятность найти оружие
        if random.random() < 0.3:
            weapon = get_random_weapon()
            if weapon:
                if player['weapon']:
                    old_weapon = player['weapon']
                    if weapon['damage'] > old_weapon['damage']:
                        player['weapon'] = weapon
                        player['rustcoin'] += 1
                        result += f" Вы также нашли {weapon['name']} и заменили старое оружие {old_weapon['name']}. Вы получили 1 rustcoin за замену."
                    else:
                        result += f" Вы также нашли {weapon['name']}, но оно хуже вашего текущего {old_weapon['name']}."
                else:
                    player['weapon'] = weapon
                    result += f" Вы также нашли {weapon['name']} с прочностью {weapon['durability']}."

        # Вероятность найти предмет
        item = get_random_item()
        item_name = item['name']
        if player['inventory'][item_name] < item['max_quantity']:
            player['inventory'][item_name] += 1
            result += f" Вы нашли {item_name}."

        if random.random() < RUSTCOIN_CHANCE:
            rustcoin_amount = random.randint(1, 5)
            player['rustcoin'] += rustcoin_amount
            result += f" Вы также нашли {rustcoin_amount} rustcoin."

        decrease_weapon_durability(player)
        await query.edit_message_text(f'{result} Ваша энергия: {player["energy"]}.')
    elif choice == 'skip':
        await query.edit_message_text(f"Вы пропустили {loot}. Ваша энергия: {player['energy']}.")

    player['last_loot'] = None
    save_players(players)
    await query.answer()
