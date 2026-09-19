import os
import re
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ✅ Đọc token từ biến môi trường Render
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Chat ID của bạn (Minhle)
MY_CHAT_ID = 8852639183

# Biến toàn cục để bật/tắt bot
IS_ACTIVE = True

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /start - Chào mừng"""
    await update.message.reply_text(
        "👋 Chào bạn! Bot đang hoạt động.\n"
        "Gõ /chaybot để bật quét rương.\n"
        "Gõ /tatbot để tắt quét rương."
    )

async def chaybot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /chaybot - Bật quét rương"""
    global IS_ACTIVE
    IS_ACTIVE = True
    await update.message.reply_text("✅ Đã BẬT quét rương. Bot sẽ thông báo khi có rương ngon!")
    logger.info("Bot đã được BẬT bởi người dùng.")

async def tatbot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lệnh /tatbot - Tắt quét rương"""
    global IS_ACTIVE
    IS_ACTIVE = False
    await update.message.reply_text("🛑 Đã TẮT quét rương. Bot sẽ không thông báo nữa.")
    logger.info("Bot đã bị TẮT bởi người dùng.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn đến từ nhóm"""
    global IS_ACTIVE
    
    # Nếu bot đang tắt, bỏ qua tin nhắn
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

            # Lấy tên user (dòng thứ 2 trong tin nhắn mẫu)
            lines = text.split('\n')
            user_name = "Không rõ"
            if len(lines) > 1:
                user_name = lines[1].strip()

            msg = (
                f"🔥 RƯƠNG NGON!\n"
                f"👤 User: {user_name}\n"
                f"📊 View: {view_hien_tai}/{view_yeu_cau}\n"
                f"📈 Ratio: {ratio}\n"
                f"🔗 Link: {link}"
            )
            # Gửi về chat riêng của bạn (MY_CHAT_ID)
            await context.bot.send_message(chat_id=MY_CHAT_ID, text=msg)
            logger.info(f"Đã gửi thông báo: {link}")

    except Exception as e:
        logger.error(f"Lỗi xử lý tin nhắn: {e}")

def main():
    """Khởi động bot"""
    if not BOT_TOKEN:
        print("❌ LỖI: Chưa cấu hình BOT_TOKEN trên Render!")
        return

    # Tạo event loop mới để tương thích với mọi phiên bản Python
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm các lệnh
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("chaybot", chaybot_command))
    app.add_handler(CommandHandler("tatbot", tatbot_command))
    
    # Thêm handler xử lý tin nhắn thường
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot đang chạy và quét tin nhắn...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
