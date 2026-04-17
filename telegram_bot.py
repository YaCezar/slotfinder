import os, logging, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
URL = os.getenv('WEBAPP_URL')

# Обработчик для проверок Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    httpd = HTTPServer(('0.0.0.0', port), HealthHandler)
    httpd.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🎰 Открыть SlotFinder", web_app=WebAppInfo(url=URL))]])
    await update.message.reply_text("🎰 Бот готов к работе. Нажми кнопку ниже:", reply_markup=kb)

async def post_init(app: Application):
    await app.bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="🎰 SlotFinder", web_app=WebAppInfo(url=URL)))

def main():
    if not TOKEN or not URL:
        return
    
    threading.Thread(target=run_server, daemon=True).start()
    
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
