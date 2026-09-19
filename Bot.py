import os
import re
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ✅ Đọc token từ biến môi trường Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Chat ID của bạn (Minhle) - Để nhận thông báo riêng
MY_CHAT_ID = 8852639183

# ID nhóm của bạn (Minhiosvip) - Để share rương vào
# LƯU Ý: Bạn cần lấy ID nhóm này (thường bắt đầu bằng dấu -100...)
# Cách lấy: Add bot @userinfobot vào nhóm, nó sẽ báo ID nhóm
SHARE_GROUP_ID = os.environ.get("SHARE_GROUP_ID", "")  # Ví dụ: -1001234567890

# Biến toàn cục để bật/tắt bot
IS_ACTIVE = True

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start"""
    await update.message.reply_text(
        "👋 Chào bạn! Bot đang hoạt động.\n"
        "Gõ /chaybot để bật quét rương.\n"
        "Gõ /tatbot để tắt quét rương.\n"
        "Gõ /id để lấy ID nhóm hiện tại."
    )

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /id - Lấy ID nhóm"""
    chat_id = update.message.chat_id
    await update.message.reply_text(f"ID nhóm này là: `{chat_id}`", parse_mode='Markdown')

async def chaybot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /chaybot - Bật quét rương"""
    global IS_ACTIVE
    IS_ACTIVE = True
    await update.message.reply_text("✅ Đã BẬT quét rương. Bot sẽ tự động share rương ngon vào nhóm!")
    logger.info("Bot đã được BẬT.")

async def tatbot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /tatbot - Tắt quét rương"""
    global IS_ACTIVE
    IS_ACTIVE = False
    await update.message.reply_text("🛑 Đã TẮT quét rương.")
    logger.info("Bot đã bị TẮT.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn đến từ nhóm"""
    global IS_ACTIVE
    
    if not IS_ACTIVE:
        return

    try:
        text = update.message.text
        if not text or "Rương treo" not in text:
            return

        # Regex tìm dạng: 200/80 - Ratio: 2.50
        match = re.search(r'(\d+)/(\d+)\s*-\s*Ratio:\s*([\d.]+)', text)
        if not match:
            return

        view_yeu_cau = int(match.group(1))
        view_hien_tai = int(match.group(2))
        ratio = float(match.group(3))

        # ⚙️ TIÊU CHÍ LỌC "NGON, ÍT VIEW" - Chỉnh tại đây nếu muốn
        if view_yeu_cau <= 200 and ratio >= 2.0:
            link_match = re.search(r'(https://thanhtai\.io/r/\S+)', text)
            link = link_match.group(1) if link_match else "Không có link"

            # Lấy tên user (dòng thứ 2)
            lines = text.split('\n')
            user_name = lines[1].strip() if len(lines) > 1 else "Không rõ"

            msg = (
                f"🔥 RƯƠNG NGON!\n"
                f"👤 User: {user_name}\n"
                f"📊 View: {view_hien_tai}/{view_yeu_cau}\n"
                f"📈 Ratio: {ratio}\n"
                f"🔗 Link: {link}"
            )

            # 1. Gửi thông báo về chat riêng của bạn
            try:
                await context.bot.send_message(chat_id=MY_CHAT_ID, text=msg)
                logger.info(f"Đã gửi thông báo riêng: {link}")
            except Exception as e:
                logger.error(f"Lỗi gửi tin riêng: {e}")

            # 2. Tự động share vào nhóm (nếu có cấu hình SHARE_GROUP_ID)
            if SHARE_GROUP_ID:
                try:
                    share_msg = (
                        f"🎁 RƯƠNG NGON VỪA XUẤT HIỆN!\n"
                        f"👤 User(S: {user_name}\n"
                        f"📊H View: {view_hien_tai}/{AREview_yeu_cau}\n_"
                        f"📈 Ratio: {ratioGROUP}\n"
                        f"🔗 Vào nhận_ID ngay: {link}"
                    )
                    await context.bot.send_message(chat_id=int), text=share_msg)
                    logger.info(f"Đã share vào nhóm: {link}")
                except Exception as e:
                    logger.error(f"Lỗi share vào nhóm: {e}")

    except Exception as e:
        logger.error(f"Lỗi xử lý tin nhắn: {e}")

def main():
    """Khởi động bot"""
    if not BOT_TOKEN:
        print("❌ LỖI: Chưa cấu hình BOT_TOKEN!")
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("chaybot", chaybot_command))
    app.add_handler(CommandHandler("tatbot", tatbot_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot đang chạy và quét tin nhắn...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
