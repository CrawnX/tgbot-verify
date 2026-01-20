"""Alat pemeriksaan izin dan verifikasi"""
import logging
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from config import CHANNEL_USERNAME

logger = logging.getLogger(__name__)


def is_group_chat(update: Update) -> bool:
    """Menentukan apakah ini adalah obrolan grup"""
    chat = update.effective_chat
    return chat and chat.type in ("group", "supergroup")


async def reject_group_command(update: Update) -> bool:
    """Batasan obrolan grup: Hanya mengizinkan /verify /verify2 /verify3 /verify4 /verify5 /qd"""
    if is_group_chat(update):
        await update.message.reply_text("Obrolan grup hanya mendukung /verify /verify2 /verify3 /verify4 /verify5 /qd, silakan gunakan pesan pribadi (PM) untuk perintah lainnya.")
        return True
    return False


async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Memeriksa apakah pengguna telah bergabung dengan channel"""
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error("Gagal memeriksa keanggotaan channel: %s", e)
        return False