#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SlotFinder Telegram Bot
=======================
Запуск локально:   python telegram_bot.py
Деплой Railway:    см. README_TELEGRAM.md

Переменные окружения:
  BOT_TOKEN   — токен от @BotFather
  WEBAPP_URL  — URL где хостится index.html (твой Railway/GitHub Pages URL)
"""

import os, logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN  = os.getenv('BOT_TOKEN',  'ВСТАВЬ_ТОКЕН_СЮДА')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'ВСТАВЬ_URL_СЮДА')  # например https://slotfinder.up.railway.app

# ── Тексты ────────────────────────────────────────────────────────────────────
WELCOME = """
🎰 *Привет! Я SlotFinder Bot*

Помогу найти идеальный слот из базы 30,000+ игр.

Просто напиши что ищешь:
• Тематику — *«конфеты»*, *«викинги»*, *«вампиры»*
• Механику — *«megaways»*, *«buy bonus»*, *«cluster»*
• Провайдера — *«pragmatic»*, *«nolimit»*
• RTP или потенциал — *«высокий rtp»*, *«x100000»*

Или открой полный каталог кнопкой ниже 👇
"""

HELP = """
*Как искать слоты:*

🎨 *По теме:* конфеты, зомби, космос, пираты, египет...
⚙️ *По механике:* megaways, cluster, buy bonus, hold & spin...
📊 *По RTP:* высокий rtp, rtp 97, rtp 98...
🏆 *По max win:* x50000, x100000, огромный выигрыш...
📦 *По провайдеру:* pragmatic, nolimit, netent, hacksaw...
🔥 *По волатильности:* хайвол, высокая, экстремальная...

*Примеры:*
• `сладкий слот с buy bonus`
• `nolimit высокая волатильность`
• `египет megaways`
• `рыбалка pragmatic`
"""

def webapp_keyboard(text='🎰 Открыть SlotFinder'):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(text, web_app=WebAppInfo(url=WEBAPP_URL))
    ]])

def search_keyboard(query):
    url = f"{WEBAPP_URL}?q={query.replace(' ', '+')}"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('🔍 Смотреть результаты', web_app=WebAppInfo(url=url))
    ], [
        InlineKeyboardButton('📂 Весь каталог', web_app=WebAppInfo(url=WEBAPP_URL))
    ]])

# ── Хендлеры ─────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME,
        parse_mode='Markdown',
        reply_markup=webapp_keyboard()
    )

async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        HELP,
        parse_mode='Markdown',
        reply_markup=webapp_keyboard('🎰 Открыть каталог')
    )

async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(ctx.args) if ctx.args else ''
    if not query:
        await update.message.reply_text(
            '🔍 Напиши что ищешь:\n`/search сладкий слот`\n`/search egypt megaways`',
            parse_mode='Markdown'
        )
        return
    await update.message.reply_text(
        f'🔍 Ищу: *{query}*\n\nОткрой результаты в приложении:',
        parse_mode='Markdown',
        reply_markup=search_keyboard(query)
    )

async def cmd_top(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = f"{WEBAPP_URL}?tab=top"
    await update.message.reply_text(
        '🔥 *Топ слоты* — лучшие релизы прямо сейчас:',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton('🔥 Топ слоты', web_app=WebAppInfo(url=url))
        ]])
    )

async def cmd_new(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = f"{WEBAPP_URL}?tab=new"
    await update.message.reply_text(
        '🆕 *Новинки* — свежие релизы:',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton('🆕 Новинки', web_app=WebAppInfo(url=url))
        ]])
    )

async def cmd_promo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    url = f"{WEBAPP_URL}?tab=promos"
    await update.message.reply_text(
        '🎁 *Промокоды и бонусы*:',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton('🎁 Промокоды', web_app=WebAppInfo(url=url))
        ]])
    )

async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or '').strip()
    if not text or text.startswith('/'):
        return

    # Любое текстовое сообщение = поиск
    await update.message.reply_text(
        f'🔍 Ищу *«{text}»* в базе 30,000+ слотов...',
        parse_mode='Markdown',
        reply_markup=search_keyboard(text)
    )

async def on_webapp_data(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Данные из Web App (если понадобится передавать обратно)"""
    data = update.message.web_app_data.data
    log.info(f'WebApp data: {data}')
    await update.message.reply_text(f'✅ Получено из приложения: {data}')

# ── Настройка при старте ─────────────────────────────────────────────────────
async def post_init(app: Application):
    # Кнопка Menu в чате (открывает Web App)
    await app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text='🎰 SlotFinder',
            web_app=WebAppInfo(url=WEBAPP_URL)
        )
    )
    # Список команд
    await app.bot.set_my_commands([
        BotCommand('start',  'Главная'),
        BotCommand('search', 'Поиск слота'),
        BotCommand('top',    'Топ слоты'),
        BotCommand('new',    'Новинки'),
        BotCommand('promo',  'Промокоды'),
        BotCommand('help',   'Помощь'),
    ])
    log.info(f'Bot started. WebApp URL: {WEBAPP_URL}')

# ── Запуск ────────────────────────────────────────────────────────────────────
def main():
    if BOT_TOKEN == 'ВСТАВЬ_ТОКЕН_СЮДА':
        print('❌ Укажи BOT_TOKEN в переменных окружения или прямо в коде!')
        return
    if WEBAPP_URL == 'ВСТАВЬ_URL_СЮДА':
        print('❌ Укажи WEBAPP_URL — адрес где хостится index.html!')
        return

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler('start',  cmd_start))
    app.add_handler(CommandHandler('help',   cmd_help))
    app.add_handler(CommandHandler('search', cmd_search))
    app.add_handler(CommandHandler('top',    cmd_top))
    app.add_handler(CommandHandler('new',    cmd_new))
    app.add_handler(CommandHandler('promo',  cmd_promo))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_webapp_data))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    print('🤖 Бот запущен. Ctrl+C для остановки.')
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
