"""全局配置文件"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# Telegram Bot 配置
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "pk_oa")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/pk_oa")

# 管理员配置
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))

VERIFY_COST = 5  # Poin yang dikonsumsi untuk verifikasi
CHECKIN_REWARD = 1  # Poin hadiah untuk check-in
INVITE_REWARD = 2  # Poin hadiah undangan
REGISTER_REWARD = 1  # Poin hadiah pendaftaran

# 帮助链接
HELP_NOTION_URL = "https://rhetorical-era-3f3.notion.site/dd78531dbac745af9bbac156b51da9cc"
