import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatMemberStatus

BOT_TOKEN = "8614020088:AAGCqe2wIIEKimwVzunUIE0JTL3UPzECAH0"
ESCROW_GROUP_ID = "@escrow_only_usdt"

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

async def escrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /escrow @username")
        return
    target_user = context.args[0]
    if not target_user.startswith("@"):
        await update.message.reply_text("Username @ se start hona chahiye, jaise @trader")
        return
    try:
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=ESCROW_GROUP_ID,
            member_limit=1,
            creates_join_request=False
        )
        await update.message.reply_text(
            f"Escrow created for {target_user}\n"
            f"Link: {invite_link.invite_link}\n"
            f"Sirf {target_user} join kar sakta hai."
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def filter_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or message.from_user.is_bot:
        return
    try:
        member = await context.bot.get_chat_member(message.chat_id, message.from_user.id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except:
        pass
    text = message.text or message.caption or ""
    if not is_valid_format(text):
        try:
            await message.delete()
            logger.info(f"Deleted message from {message.from_user.username}")
        except Exception as e:
            logger.error(f"Delete failed: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Active! Sirf fixed format posts allowed hain.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("escrow", escrow_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_messages))
    logger.info("Bot is LIVE now...")
    app.run_polling()

if __name__ == "__main__":
    main()
