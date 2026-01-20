"""Template Pesan"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Mendapatkan pesan selamat datang"""
    msg = (
        f"🎉 Selamat datang, {full_name}!\n"
        "Anda telah berhasil mendaftar dan mendapatkan 1 poin.\n"
    )
    if invited_by:
        msg += "Terima kasih telah bergabung melalui link undangan, pengundang Anda telah mendapatkan 2 poin.\n"

    msg += (
        "\nBot ini dapat membantu Anda menyelesaikan verifikasi SheerID secara otomatis.\n"
        "Mulai cepat:\n"
        "/about - Pelajari fungsi bot\n"
        "/balance - Cek saldo poin\n"
        "/help - Lihat daftar perintah lengkap\n\n"
        "Dapatkan lebih banyak poin:\n"
        "/qd - Absen harian\n"
        "/invite - Undang teman\n"
        f"Gabung ke Channel: {CHANNEL_URL}"
    )


def get_about_message() -> str:
    """Mendapatkan pesan tentang bot"""
    return (
        "🤖 Bot Verifikasi Otomatis SheerID\n"
        "\n"
        "Pengenalan Fitur:\n"
        "- Menyelesaikan verifikasi Siswa/Guru SheerID secara otomatis\n"
        "- Mendukung verifikasi Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student, dan Bolt.new Teacher\n"
        "- Proses cepat, aman, dan tanpa campur tangan manusia (kecuali audit manual dari SheerID)\n"
        "\n"
        "Cara Penggunaan:\n"
        "1. Dapatkan link verifikasi SheerID dari situs resmi\n"
        "2. Gunakan perintah verifikasi yang sesuai di bot ini\n"
        "3. Tunggu sistem memproses dan mengunggah dokumen otomatis\n"
        )


def get_help_message(is_admin: bool = False) -> str:
    """Mendapatkan daftar perintah bantuan"""
    msg = (
        "📖 Daftar Perintah Pengguna:\n"
        "/start - Daftar/Mulai bot\n"
        "/about - Tentang bot ini\n"
        "/balance - Cek saldo poin Anda\n"
        "/qd - Absen harian untuk dapat poin\n"
        "/invite - Dapatkan link undangan Anda\n"
        "/use <kode> - Gunakan kode voucher poin\n"
        f"/verify <link> - Verifikasi Gemini One Pro (-{VERIFY_COST} poin)\n"
        f"/verify2 <link> - Verifikasi ChatGPT Teacher K12 (-{VERIFY_COST} poin)\n"
        f"/verify3 <link> - Verifikasi Spotify Student (-{VERIFY_COST} poin)\n"
        f"/verify4 <link> - Verifikasi Bolt.new Teacher (-{VERIFY_COST} poin)\n"
        f"/verify5 <link> - Verifikasi YouTube Student Premium (-{VERIFY_COST} poin)\n"
        "/getV4Code <id_verifikasi> - Ambil kode verifikasi Bolt.new\n"
        "/help - Lihat pesan bantuan ini\n"
        f"Panduan jika gagal: {HELP_NOTION_URL}\n"
    )
    if is_admin:
        msg += (
            "\n👑 Perintah Admin:\n"
            "/addbalance <ID_User> <poin> - Tambah poin pengguna\n"
            "/block <ID_User> - Blokir pengguna\n"
            "/white <ID_User> - Hapus blokir\n"
            "/blacklist - Lihat daftar blokir\n"
            "/genkey <kode> <poin> [kali] [hari] - Buat kode voucher\n"
            "/listkeys - Lihat daftar voucher\n"
            "/broadcast <teks> - Kirim pesan massal ke semua user\n"
    )
    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Mendapatkan pesan poin tidak cukup"""
    return (
        f"Poin tidak cukup (Saldo saat ini: {current_balance} poin).\n\n"
        f"Setiap verifikasi membutuhkan {VERIFY_COST} poin.\n"
        "Anda bisa mendapatkan poin dengan cara:\n"
        "1. Absen harian /qd\n"
        "2. Undang teman /invite\n"
        "3. Gunakan kode voucher /use"
        )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Mendapatkan pesan cara penggunaan verifikasi"""
    return (
        f"Cara penggunaan: {command} <link_sheerid>\n\n"
        f"Contoh: {command} https://offers.sheerid.com/p/verified/xxxx/\n\n"
        f"Layanan: {service_name}\n"
        f"Biaya: {VERIFY_COST} poin"
        )