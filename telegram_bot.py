import os, logging, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Получаем данные из настроек Render
BOT_TOKEN  = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL')

# --- Костыль для Render (чтобы он не убивал процесс) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    httpd.serve_forever()

# --- Тексты и логика ---
WELCOME = "🎰 *Привет! Я SlotFinder Bot*\n\nОткрой каталог кнопкой ниже 👇"

def webapp_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('🎰 Открыть SlotFinder', web_app=WebAppInfo(url=WEBAPP_URL))
    ]])

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME, parse_mode='Markdown', reply_markup=webapp_keyboard())

async def post_init(app: Application):
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text='🎰 SlotFinder', web_app=WebAppInfo(url=WEBAPP_URL))
    )

def main():
    if not BOT_TOKEN or not WEBAPP_URL:
        print("❌ ОШИБКА: Проверь BOT_TOKEN и WEBAPP_URL в настройках Render!")
        return

    # Запускаем проверку порта в фоне
    threading.Thread(target=run_health_check, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_start))
    
    print('🤖 Бот запущен!')
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
