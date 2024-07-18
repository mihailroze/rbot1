# menu.py

from telegram import ReplyKeyboardMarkup

def main_menu():
    keyboard = [
        ['Исследование', 'Атаковать игрока'],
        ['Рейтинг игроков', 'Инвентарь', 'Обмен компонентов'],
        ['Об игре']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
