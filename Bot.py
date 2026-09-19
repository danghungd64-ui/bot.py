import os
import re
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Lấy token từ biến môi trường Render (KHÔNG viết cứng token vào đây)
BOT_TOKEN = os.environ.get("8934734495:AAGVXUK0muIIPK2XYJhzxwHJoaZNbysc-UY")

# Chat ID của bạn (đã điền sẵn)
MY_CHAT_ID = 8852639183

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

        # ⚙️ TIÊU CHÍ LỌC "NGON, ÍT VIEW" - Chỉnh ở đây nếu muốn
        if view_yeu_cau <= 200 and ratio >= 2.0:
            link_match = re.search(r'(https://thanhtai\.io/r/\S+)', text)
            link = link_match.group(1) if link_match else "Không có link"

            msg = (
                f"🔥 RƯƠNG NGON!\n"
                f"📊 View: {view_hien_tai}/{view_yeu_cau}\n"
                f"📈 Ratio: {ratio}\n"
                f"🔗 {link}"
            )
            await context.bot.send_message(chat_id=MY_CHAT_ID, text=msg)
            logger.info(f"Đã gửi thông báo: {link}")
    except Exception as e:
        logger.error(f"Lỗi xử lý tin nhắn: {e}")

def main():
    if not BOT_TOKEN:
        print("❌ LỖI: Chưa cấu hình BOT_TOKEN trên Render!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot đang chạy và quét tin nhắn...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
