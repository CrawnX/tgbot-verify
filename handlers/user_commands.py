"""Handler Perintah Pengguna"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command
from utils.messages import (
    get_welcome_message,
    get_about_message,
    get_help_message,
)

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /start"""
    if await reject_group_command(update):
        return

    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    full_name = user.full_name or ""

    # Jika user sudah terdaftar, langsung kirim pesan selamat datang kembali
    if db.user_exists(user_id):
        await update.message.reply_text(
            f"Selamat datang kembali, {full_name}！\n"
            "Anda sudah terdaftar dalam sistem.\n"
            "Kirim /help untuk melihat perintah yang tersedia."
        )
        return

    # Menangani undangan (referral)
    invited_by: Optional[int] = None
    if context.args:
        try:
            invited_by = int(context.args[0])
            if not db.user_exists(invited_by):
                invited_by = None
        except Exception:
            invited_by = None

    # Membuat akun user baru
    if db.create_user(user_id, username, full_name, invited_by):
        welcome_msg = get_welcome_message(full_name, bool(invited_by))
        await update.message.reply_text(welcome_msg)
    else:
        await update.message.reply_text("Pendaftaran gagal, silakan coba lagi nanti.")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /about"""
    if await reject_group_command(update):
        return

    await update.message.reply_text(get_about_message())


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /help"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    is_admin = user_id == ADMIN_USER_ID
    await update.message.reply_text(get_help_message(is_admin))


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /balance"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    await update.message.reply_text(
        f"💰 Saldo Poin\n\nPoin saat ini: {user['balance']} poin"
    )


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /qd (Absen Harian) - Saat ini dinonaktifkan sementara"""
    user_id = update.effective_user.id

    # Fitur absen dinonaktifkan sementara (dalam perbaikan bug)
    # await update.message.reply_text(
    #     "⚠️ Fitur Absen sedang dalam pemeliharaan sementara\n\n"
    #     "Karena ditemukan bug, fitur ini ditutup sementara untuk perbaikan.\n"
    #     "Akan segera kembali. Mohon maaf atas ketidaknyamanannya.\n\n"
    #     "💡 Anda bisa mendapatkan poin dengan cara berikut:\n"
    #     "• Undang teman /invite (+2 poin)\n"
    #     "• Gunakan kode voucher /use <kode_voucher>"
    # )
    # return
    
    # ===== Kode di bawah ini dinonaktifkan sementara =====
    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    # Cek tahap 1: Di level handler perintah
    if not db.can_checkin(user_id):
        await update.message.reply_text("❌ Anda sudah absen hari ini, silakan kembali besok.")
        return

    # Cek tahap 2: Di level database (Operasi SQL Atomik)
    if db.checkin(user_id):
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"✅ Absen berhasil!\nMendapatkan poin: +1\nTotal poin saat ini: {user['balance']} poin"
        )
    else:
        # Jika database mengembalikan False, berarti sudah absen hari ini (keamanan ganda)
        await update.message.reply_text("❌ Anda sudah absen hari ini, silakan kembali besok.")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /invite untuk mengundang teman"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    bot_username = context.bot.username
    invite_link = f"https://t.me/{bot_username}?start={user_id}"

    await update.message.reply_text(
        f"🎁 Link Undangan Spesial Anda:\n{invite_link}\n\n"
        "Setiap 1 orang yang berhasil mendaftar melalui link ini, Anda akan mendapatkan 2 poin."
    )


async def use_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /use untuk menggunakan kode voucher/card key"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /use <kode_voucher>\n\nContoh: /use voucher123"
        )
        return

    key_code = context.args[0].strip()
    result = db.use_card_key(key_code, user_id)

    if result is None:
        await update.message.reply_text("Kode voucher tidak ditemukan, silakan periksa dan coba lagi.")
    elif result == -1:
        await update.message.reply_text("Batas penggunaan kode voucher ini telah tercapai.")
    elif result == -2:
        await update.message.reply_text("Kode voucher ini telah kedaluwarsa.")
    elif result == -3:
        await update.message.reply_text("Anda sudah pernah menggunakan kode voucher ini.")
    else:
        user = db.get_user(user_id)
        await update.message.reply_text(
            f"Kode voucher berhasil digunakan!\n"
            f"Mendapatkan poin: {result}\n"
            f"Total poin saat ini: {user['balance']}"
        )