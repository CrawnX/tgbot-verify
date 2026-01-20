"""Konfigurasi Global"""
import os
from dotenv import load_dotenv

# Memuat berkas .env
load_dotenv()

# Konfigurasi Telegram Bot
BOT_TOKEN = os.getenv(“BOT_TOKEN”, “YOUR_BOT_TOKEN_HERE”)
CHANNEL_USERNAME = os.getenv(“CHANNEL_USERNAME”, “pk_oa”)
CHANNEL_URL = os.getenv(“CHANNEL_URL”, “https://t.me/pk_oa”)

# Konfigurasi Administrator
ADMIN_USER_ID = int(os.getenv(“ADMIN_USER_ID”, “123456789”))

# Konfigurasi Poin
VERIFY_COST = 5  # Poin yang dikonsumsi untuk verifikasi
CHECKIN_REWARD = 1  # Poin hadiah untuk check-in
INVITE_REWARD = 2  # Poin hadiah undangan
REGISTER_REWARD = 1  # Poin hadiah pendaftaran

# Tautan bantuan
HELP_NOTION_URL = “https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc”