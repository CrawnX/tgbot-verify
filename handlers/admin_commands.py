"""Handler Perintah Admin"""
import asyncio
import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_ID
from database_mysql import Database
from utils.checks import reject_group_command

logger = logging.getLogger(__name__)


async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /addbalance - Admin menambahkan poin ke pengguna"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /addbalance <ID_User> <Jumlah_Poin>\n\nContoh: /addbalance 123456789 10"
        )
        return

    try:
        target_user_id = int(context.args[0])
        amount = int(context.args[1])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.add_balance(target_user_id, amount):
            user = db.get_user(target_user_id)
            await update.message.reply_text(
                f"✅ Berhasil menambahkan {amount} poin untuk pengguna {target_user_id}.\n"
                f"Total poin saat ini: {user['balance']} poin"
            )
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan angka yang valid.")


async def block_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /block - Admin memblokir pengguna"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /block <ID_User>\n\nContoh: /block 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.block_user(target_user_id):
            await update.message.reply_text(f"✅ Pengguna {target_user_id} telah diblokir.")
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan ID User yang valid.")


async def white_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /white - Admin menghapus blokir (unblock)"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /white <ID_User>\n\nContoh: /white 123456789"
        )
        return

    try:
        target_user_id = int(context.args[0])

        if not db.user_exists(target_user_id):
            await update.message.reply_text("Pengguna tidak ditemukan.")
            return

        if db.unblock_user(target_user_id):
            await update.message.reply_text(f"✅ Pengguna {target_user_id} telah dihapus dari daftar blokir.")
        else:
            await update.message.reply_text("Operasi gagal, silakan coba lagi nanti.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan ID User yang valid.")


async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /blacklist - Melihat daftar blokir"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    blacklist = db.get_blacklist()

    if not blacklist:
        await update.message.reply_text("Daftar blokir kosong.")
        return

    msg = "📋 Daftar Pengguna yang Diblokir:\n\n"
    for user in blacklist:
        msg += f"ID Pengguna: {user['user_id']}\n"
        msg += f"Username: @{user['username']}\n"
        msg += f"Nama Lengkap: {user['full_name']}\n"
        msg += "---\n"

    await update.message.reply_text(msg)


async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /genkey - Admin membuat kode voucher"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Cara penggunaan: /genkey <Kode_Voucher> <Poin> [Batas_Penggunaan] [Hari_Kadaluarsa]\n\n"
            "Contoh:\n"
            "/genkey voucher20 20 - Buat voucher 20 poin (1x pakai, selamanya)\n"
            "/genkey vip100 50 10 - Buat voucher 50 poin (10x pakai, selamanya)\n"
            "/genkey promo 30 1 7 - Buat voucher 30 poin (1x pakai, kadaluarsa 7 hari)"
        )
        return

    try:
        key_code = context.args[0].strip()
        balance = int(context.args[1])
        max_uses = int(context.args[2]) if len(context.args) > 2 else 1
        expire_days = int(context.args[3]) if len(context.args) > 3 else None

        if balance <= 0:
            await update.message.reply_text("Jumlah poin harus lebih dari 0.")
            return

        if max_uses <= 0:
            await update.message.reply_text("Batas penggunaan harus lebih dari 0.")
            return

        if db.create_card_key(key_code, balance, user_id, max_uses, expire_days):
            msg = (
                "✅ Kode Voucher berhasil dibuat!\n\n"
                f"Voucher: {key_code}\n"
                f"Poin: {balance}\n"
                f"Batas Penggunaan: {max_uses} kali\n"
            )
            if expire_days:
                msg += f"Masa Berlaku: {expire_days} hari\n"
            else:
                msg += "Masa Berlaku: Selamanya\n"
            msg += f"\nCara penggunaan user: /use {key_code}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Kode voucher sudah ada atau gagal dibuat, silakan gunakan nama lain.")
    except ValueError:
        await update.message.reply_text("Format parameter salah, silakan masukkan angka yang valid.")


async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /listkeys - Admin melihat daftar voucher"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id

    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    keys = db.get_all_card_keys()

    if not keys:
        await update.message.reply_text("Belum ada kode voucher.")
        return

    msg = "📋 Daftar Kode Voucher:\n\n"
    for key in keys[:20]:  # Hanya menampilkan 20 pertama
        msg += f"Voucher: {key['key_code']}\n"
        msg += f"Poin: {key['balance']}\n"
        msg += f"Penggunaan: {key['current_uses']}/{key['max_uses']}\n"

        if key["expire_at"]:
            expire_time = datetime.fromisoformat(key["expire_at"])
            if datetime.now() > expire_time:
                msg += "Status: Kadaluarsa\n"
            else:
                days_left = (expire_time - datetime.now()).days
                msg += f"Status: Aktif (Sisa {days_left} hari)\n"
        else:
            msg += "Status: Aktif Selamanya\n"

        msg += "---\n"

    if len(keys) > 20:
        msg += f"\n(Hanya menampilkan 20 voucher pertama dari total {len(keys)})"

    await update.message.reply_text(msg)


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /broadcast - Admin mengirim pesan massal"""
    if await reject_group_command(update):
        return

    user_id = update.effective_user.id
    if user_id != ADMIN_USER_ID:
        await update.message.reply_text("Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    text = " ".join(context.args).strip() if context.args else ""
    if not text and update.message.reply_to_message:
        text = update.message.reply_to_message.text or ""

    if not text:
        await update.message.reply_text("Cara penggunaan: /broadcast <teks>, atau balas sebuah pesan lalu kirim /broadcast")
        return

    user_ids = db.get_all_user_ids()
    success, failed = 0, 0

    status_msg = await update.message.reply_text(f"📢 Memulai siaran (broadcast) ke {len(user_ids)} pengguna...")

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=text)
            success += 1
            await asyncio.sleep(0.05)  # Jeda sedikit untuk menghindari limit API Telegram
        except Exception as e:
            logger.warning("Gagal mengirim siaran ke %s: %s", uid, e)
            failed += 1

    await status_msg.edit_text(f"✅ Siaran (Broadcast) selesai!\nBerhasil: {success}\nGagal: {failed}")