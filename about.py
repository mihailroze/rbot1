# about.py

from telegram import Update
from telegram.ext import CallbackContext
from menu import main_menu

async def about(update: Update, context: CallbackContext) -> None:
    description = """
    Добро пожаловать в Rust Adventure!

    Rust Adventure - это текстовая игра, в которой игроки исследуют мир, сражаются с другими игроками, собирают предметы и оружие, обменивают найденные ресурсы на очки опыта и повышают свои ранги.

    Команды игры:
    1. `Исследование` - Исследуйте мир и находите различные предметы и оружие.
    2. `Атаковать игрока <username>` - Атакуйте другого игрока по его имени.
    3. `Рейтинг игроков` - Просмотрите рейтинг всех игроков.
    4. `Инвентарь` - Посмотрите содержимое вашего инвентаря.
    5. `Обмен компонентов` - Обменивайте предметы на очки опыта.

    Пример использования команды атаки:
    `Атаковать игрока username`

    Если у вас есть вопросы или проблемы, свяжитесь с поддержкой - @huligan17

    Удачи и приятной игры!
    """
    await update.message.reply_text(description, reply_markup=main_menu())