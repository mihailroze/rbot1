# handlers/ranking.py

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


async def ranking(update: Update, context: CallbackContext) -> None:
    players = load_players()
    sorted_players = sorted(players.values(), key=lambda p: p.get('points', 0), reverse=True)

    ranking_text = "Рейтинг игроков:\n"
    for player in sorted_players:
        name = player['name']
        points = player.get('points', 0)
        wins = player.get('wins', 0)
        losses = player.get('losses', 0)
        ranking_text += f"{name}: {points} очков, Победы: {wins}, Поражения: {losses}\n"

    await update.message.reply_text(ranking_text, reply_markup=main_menu())
