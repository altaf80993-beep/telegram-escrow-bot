import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ESCROW_GROUP_ID = "@escrow_only_usdt"
ADMIN_USERNAME = "@your_username"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_format(text: str) -> bool:
    pattern = re.compile(
        r"^#Selling\s*[\r\n]+"
        r"Chain:\s*.+[\r\n]+"
        r"Amount\[USDT/USDC\]:\s*.+[\r\n]+"
        r"Amount\[INR\]:\s*.+[\r\n]+"
        r"Rate\[INR/USDT\]:\s*.+[\r\n]+"
        r"Payment Method:\s*.+",
        re.IGNORECASE
    )
    return bool(pattern.match(text.strip()))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Active!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start\n/help\n/escrow @username")

async def escrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seller = update.message.from_user.username or update.message.from_user.full_name
    if update.message.from_user.username:
        seller = "@" + update.message.from_user.username

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /escrow @buyer_username")
        return

    buyer = context.args[0]
    if not buyer.startswith("@"):
        await update.message.reply_text("Buyer username @ se start hona chahiye")
        return

    try:
        link = await context.bot.create_chat_invite_link(
            chat_id=ESCROW_GROUP_ID,
            member_limit=3,
            creates_join_request=False
        )
        msg = (
            f"ESCROW CREATED\n\n"
            f"Buyer: {buyer}\n"
            f"Seller: {seller}\n"
            f"Admin: {ADMIN_USERNAME}\n\n"
            f"Join Link: {link.invite_link}\n\n"
            f"Sirf Buyer, Seller aur Admin join karein."
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.from_user.is_bot:
        return
    try:
        member = await context.bot.get_chat_member(msg.chat_id, msg.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        pass
    text = msg.text or msg.caption or ""
    if text.startswith("/escrow"):
        return
    if not is_valid_format(text):
        try:
            await msg.delete()
        except:
            pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("escrow", escrow_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
    logger.info("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
