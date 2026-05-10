import re
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatMemberStatus

# =========================
# CONFIG — YAHAN APNI VALUES DAALO
# =========================

BOT_TOKEN = "8614020088:AAGCqe2wIIEKimwVzunUIE0JTL3UPzECAH0"
ESCROW_GROUP_ID = "@escrow_only_usdt"
ADMIN_USERNAME = "@crypto_8099"

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =========================
# POST FORMAT CHECK
# =========================

def is_valid_format(text: str) -> bool:
    pattern = re.compile(
        r"^#Selling\s*[\r\n]+"
        r"Chain:\s*.+[\r\n]+"
        r"Amount\[USDT/USDC\]:\s*.+[\r\n]+"
        r"Amount\[INR\]:\s*.+[\r\n]+"
        r"Rate\[INR/USDT\]:\s*.+[\r\n]+"
        r"Payment Method:\s*.+",
        re.IGNORECASE,
    )
    return bool(pattern.match(text.strip()))

# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Escrow Bot Active\n\n"
        "Sirf fixed format posts allowed hain.\n"
        "Usage: /escrow @username"
    )

# =========================
# HELP COMMAND
# =========================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📌 Commands:\n\n"
        "/start - Bot Start\n"
        "/help - Help Menu\n"
        "/escrow @username - Create Escrow Group Link\n\n"
        "Example:\n"
        "Buyer post karega #Selling format mein\n"
        "Seller likhega /escrow @buyer_username\n"
        "Bot dega group link - sirf Buyer, Seller aur Admin join kar sakte hain."
    )
    await update.message.reply_text(help_text)

# =========================
# ESCROW COMMAND
# =========================

async def escrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Jo command likh raha hai = Seller
    seller_username = update.message.from_user.username
    if seller_username:
        seller_username = f"@{seller_username}"
    else:
        seller_username = update.message.from_user.full_name

    if len(context.args) != 1:
        await update.message.reply_text(
            "❌ Usage: /escrow @buyer_username\n"
            "Example: /escrow @rahul_trader"
        )
        return

    buyer_username = context.args[0]

    if not buyer_username.startswith("@"):
        await update.message.reply_text("❌ Buyer username @ se start hona chahiye. Jaise: @rahul_trader")
        return

    try:
        # member_limit=3 → Buyer + Seller + Admin
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=ESCROW_GROUP_ID,
            member_limit=3,
            creates_join_request=False,
        )

        message = (
            "✅ **ESCROW GROUP CREATED**\n\n"
            f"👤 **Buyer:** {buyer_username}\n"
            f"👤 **Seller:** {seller_username}\n"
            f"👨‍💼 **Admin:** {ADMIN_USERNAME}\n\n"
            f"🔗 **Join Link:**\n{invite_link.invite_link}\n\n"
            "⚠️ **Sirf Buyer, Seller aur Admin join karein.**\n"
            "Kisi aur ne join kiya to turant kick hoga."
        )

        await update.message.reply_text(message, parse_mode="Markdown")

    except Exception as e:
        logger.error(e)
        await update.message.reply_text(f"❌ Error creating group link: {e}")

# =========================
# FILTER MESSAGES
# =========================

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or message.from_user.is_bot:
        return

    try:
        member = await context.bot.get_chat_member(
            message.chat_id,
            message.from_user.id,
        )
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        pass

    # Agar /escrow command hai to delete mat karo
    if message.text and message.text.startswith("/escrow"):
        return

    text = message.text or message.caption or ""

    if not is_valid_format(text):
        try:
            await message.delete()
            logger.info(f"Deleted message from {message.from_user.username}")
        except Exception as e:
            logger.error(f"Delete failed: {e}")

# =========================
# MAIN (Python 3.14 compatible)
# =========================

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("escrow", escrow_command))
    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.CAPTION) & ~filters.COMMAND,
            filter_messages,
        )
    )

    logger.info("🚀 Bot Started Successfully")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
