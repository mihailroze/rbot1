import json
import logging
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, \
    ConversationHandler
from config import BOT_TOKEN
from handlers import start, explore, attack, ranking, inventory, exchange
from about import about
from helpers import check_subscription
from test_death import simulate_death  # Импортируем новый обработчик

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

CHAT_ID = '@rust_services_chat'  # ID или @username чата

PLAYERS_FILE = 'data/players.json'
ENERGY_REGEN_AMOUNT = 5
HEALTH_RECOVERY_RATE = 1  # Скорость восстановления здоровья: 1 очко в минуту


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


async def regen_energy(context: ContextTypes.DEFAULT_TYPE):
    players = load_players()
    for user_id, player in players.items():
        player['energy'] = min(100, player['energy'] + ENERGY_REGEN_AMOUNT)
    save_players(players)
    logger.info('Energy regenerated for all players.')


async def regen_health(context: ContextTypes.DEFAULT_TYPE):
    players = load_players()
    for user_id, player in players.items():
        if 'last_death' in player:
            time_since_death = datetime.now() - datetime.fromisoformat(player['last_death'])
            recovered_health = int(time_since_death.total_seconds() // 60 * HEALTH_RECOVERY_RATE)
            player['health'] = min(100, recovered_health)
            if player['health'] >= 100:
                del player['last_death']  # Удаляем метку времени смерти, если здоровье полностью восстановлено
    save_players(players)
    logger.info('Health regenerated for all players.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    user_id = str(user.id)
    players = load_players()
    logger.info(f"Loaded players: {players}")
    logger.info(f"Checking registration for user_id: {user_id}")

    if user_id not in players:
        logger.warning(f"User {user_id} not found in players")
        await update.message.reply_text('Пожалуйста, сначала зарегистрируйтесь с помощью команды /start.')
        return

    if not await check_subscription(update, context, CHAT_ID):
        await update.message.reply_text(
            'Для использования бота, пожалуйста, подпишитесь на чат: https://t.me/rust_services_chat')
        return

    text = update.message.text
    logger.info(f"Received message: {text}")

    if text == 'Исследование':
        await explore.explore(update, context)
    elif text == 'Атаковать игрока':
        await attack.attack_button(update, context)
    elif text == 'Рейтинг игроков':
        await ranking.ranking(update, context)
    elif text == 'Инвентарь':
        await inventory.inventory(update, context)
    elif text == 'Обмен компонентов':
        await exchange.exchange(update, context)
    elif text == 'Об игре':
        await about(update, context)
    else:
        logger.info(f"Unhandled message: {text}")


def main() -> None:
    """Run the bot."""
    # Инициализация Application и JobQueue
    application = Application.builder().token(BOT_TOKEN).build()
    job_queue = application.job_queue

    # Регистрация обработчиков команд и кнопок
    application.add_handler(CommandHandler('start', start.start))
    application.add_handler(CallbackQueryHandler(explore.button, pattern='^break|skip$'))
    # Регистрация ConversationHandler для атаки
    attack.add_handlers(application)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Добавление обработчика команды About
    application.add_handler(CommandHandler('about', about))

    # Добавление обработчика для симуляции смерти
    application.add_handler(CommandHandler('simulate_death', simulate_death))

    # Добавление задачи восстановления энергии
    job_queue.run_repeating(regen_energy, interval=timedelta(minutes=5), first=10)

    # Добавление задачи восстановления здоровья
    job_queue.run_repeating(regen_health, interval=timedelta(minutes=1), first=10)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
