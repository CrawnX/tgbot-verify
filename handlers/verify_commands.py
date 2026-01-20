"""Handler Perintah Verifikasi"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# Mencoba mengimpor kontrol konkurensi, jika gagal gunakan implementasi kosong
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    # Jika impor gagal, buat implementasi sederhana
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Link SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong saldo, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"Memulai proses verifikasi Gemini One Pro...\n"
        f"ID Verifikasi: {verification_id}\n"
        f"Saldo dipotong: {VERIFY_COST} poin\n\n"
        "Mohon tunggu, proses ini mungkin memakan waktu 1-2 menit..."
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi Berhasil!\n\n"
            if result.get("pending"):
                result_msg += "Dokumen telah dikirim, menunggu peninjauan manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Link Pengalihan:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi Gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses: {str(e)}\n\n"
            f"Saldo dikembalikan: {VERIFY_COST} poin"
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify2 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Link SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong saldo, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"Memulai proses verifikasi ChatGPT Teacher K12...\n"
        f"ID Verifikasi: {verification_id}\n"
        f"Saldo dipotong: {VERIFY_COST} poin\n\n"
        "Mohon tunggu, proses ini mungkin memakan waktu 1-2 menit..."
    )

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi Berhasil!\n\n"
            if result.get("pending"):
                result_msg += "Dokumen telah dikirim, menunggu peninjauan manual.\n"
            if result.get("redirect_url"):
                result_msg += f"Link Pengalihan:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi Gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan saat verifikasi: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses: {str(e)}\n\n"
            f"Saldo dikembalikan: {VERIFY_COST} poin"
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify3 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parsing verificationId
    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Link SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong saldo, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Memulai proses verifikasi Spotify Student...\n"
        f"Saldo dipotong: {VERIFY_COST} poin\n\n"
        "📝 Sedang membuat informasi mahasiswa...\n"
        "🎨 Sedang membuat PNG Kartu Mahasiswa...\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Menggunakan semaphore untuk kontrol konkurensi
    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id) # INDENTASI DIPERBAIKI DISINI
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi Spotify Student Berhasil!\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen telah dikirim, menunggu audit SheerID\n"
                result_msg += "⏱️ Estimasi waktu audit: dalam beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Link Pengalihan:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi Gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan pada verifikasi Spotify: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses: {str(e)}\n\n"
            f"Saldo dikembalikan: {VERIFY_COST} poin"
        )


async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify4 - Bolt.new Teacher (Versi ambil kode otomatis)"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parsing externalUserId atau verificationId
    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Link SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong saldo, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Memulai proses verifikasi Bolt.new Teacher...\n"
        f"Saldo dipotong: {VERIFY_COST} poin\n\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Menggunakan semaphore untuk kontrol konkurensi
    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # Langkah 1: Kirim dokumen
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            # Kirim gagal, refund
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Gagal mengirim dokumen: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Gagal mendapatkan ID Verifikasi\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
            return
        
        # Update pesan
        await processing_msg.edit_text(
            f"✅ Dokumen telah dikirim!\n"
            f"📋 ID Verifikasi: `{vid}`\n\n"
            f"🔍 Sedang mengambil kode verifikasi otomatis...\n"
            f"(Maksimum menunggu 20 detik)"
        )
        
        # Langkah 2: Ambil kode otomatis (Maks 20 detik)
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)
        
        if code:
            # Berhasil mendapatkan kode
            result_msg = (
                f"🎉 Verifikasi Berhasil!\n\n"
                f"✅ Dokumen terkirim\n"
                f"✅ Audit lolos\n"
                f"✅ Kode verifikasi didapat\n\n"
                f"🎁 Kode Verifikasi: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Link Pengalihan:\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
            
            # Simpan catatan sukses
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            # Jika dalam 20 detik tidak dapat kode, minta user cek nanti
            await processing_msg.edit_text(
                f"✅ Dokumen berhasil dikirim!\n\n"
                f"⏳ Kode verifikasi belum dibuat (mungkin butuh 1-5 menit audit)\n\n"
                f"📋 ID Verifikasi: `{vid}`\n\n"
                f"💡 Silakan gunakan perintah berikut untuk cek nanti:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Catatan: Poin sudah terpotong, cek manual nanti gratis."
            )
            
            # Simpan catatan tertunda
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Menunggu peninjauan",
                vid
            )
            
    except Exception as e:
        logger.error("Terjadi kesalahan pada Bolt.new: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses: {str(e)}\n\n"
            f"Saldo dikembalikan: {VERIFY_COST} poin"
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    """Mengambil kode verifikasi otomatis (Polling ringan, tidak mempengaruhi konkurensi)"""
    import time
    start_time = time.time()
    attempts = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1
            
            # Cek timeout
            if elapsed >= max_wait:
                logger.info(f"Waktu habis ambil kode otomatis ({elapsed} detik), user diminta cek manual")
                return None
            
            try:
                # Cek status verifikasi
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    
                    if current_step == "success":
                        # Ambil kode
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ Sukses ambil kode otomatis: {code} (Waktu {elapsed} detik)")
                            return code
                    elif current_step == "error":
                        # Audit gagal
                        logger.warning(f"Audit gagal: {data.get('errorIds', [])}")
                        return None
                    # else: pending, lanjut tunggu
                
                # Tunggu polling berikutnya
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Kesalahan saat cek kode: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /verify5 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # Parsing verificationId
    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Link SheerID tidak valid, silakan periksa dan coba lagi.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Gagal memotong saldo, silakan coba lagi nanti.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Memulai proses verifikasi YouTube Student Premium...\n"
        f"Saldo dipotong: {VERIFY_COST} poin\n\n"
        "📝 Sedang membuat informasi mahasiswa...\n"
        "🎨 Sedang membuat PNG Kartu Mahasiswa...\n"
        "📤 Sedang mengirim dokumen..."
    )

    # Menggunakan semaphore untuk kontrol konkurensi
    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Verifikasi YouTube Student Premium Berhasil!\n\n"
            if result.get("pending"):
                result_msg += "✨ Dokumen telah dikirim, menunggu audit SheerID\n"
                result_msg += "⏱️ Estimasi waktu audit: dalam beberapa menit\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Link Pengalihan:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Verifikasi Gagal: {result.get('message', 'Kesalahan tidak diketahui')}\n\n"
                f"Saldo dikembalikan: {VERIFY_COST} poin"
            )
    except Exception as e:
        logger.error("Terjadi kesalahan pada verifikasi YouTube: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat memproses: {str(e)}\n\n"
            f"Saldo dikembalikan: {VERIFY_COST} poin"
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Menangani perintah /getV4Code - Mengambil kode verifikasi Bolt.new Teacher"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("Anda telah diblokir, tidak dapat menggunakan fitur ini.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Silakan gunakan /start untuk mendaftar terlebih dahulu.")
        return

    # Cek apakah verification_id disediakan
    if not context.args:
        await update.message.reply_text(
            "Cara penggunaan: /getV4Code <verification_id>\n\n"
            "Contoh: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "ID Verifikasi dikembalikan kepada Anda setelah menggunakan perintah /verify4."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Sedang mengecek kode verifikasi, mohon tunggu..."
    )

    try:
        # Cek SheerID API untuk mendapatkan kode
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Gagal mengecek, kode status: {response.status_code}\n\n"
                    "Silakan coba lagi nanti atau hubungi admin."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ Verifikasi Berhasil!\n\n"
                result_msg += f"🎉 Kode Verifikasi: `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"Link Pengalihan:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Verifikasi masih dalam peninjauan, silakan coba lagi nanti.\n\n"
                    "Biasanya butuh 1-5 menit, mohon bersabar."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    f"❌ Verifikasi Gagal\n\n"
                    f"Pesan kesalahan: {', '.join(error_ids) if error_ids else 'Kesalahan tidak diketahui'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Status saat ini: {current_step}\n\n"
                    "Kode verifikasi belum dibuat, silakan coba lagi nanti."
                )

    except Exception as e:
        logger.error("Gagal mengambil kode Bolt.new: %s", e)
        await processing_msg.edit_text(
            f"❌ Terjadi kesalahan saat mengecek: {str(e)}\n\n"
            "Silakan coba lagi nanti atau hubungi admin."
        )