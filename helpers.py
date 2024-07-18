# helpers.py

from telegram import Update
from telegram.ext import CallbackContext
import logging

async def check_subscription(update: Update, context: CallbackContext, chat_id: str) -> bool:
    user_id = update.message.from_user.id
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        logging.info(f"User status: {member.status}")
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False
