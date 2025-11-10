import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, REMINDER_TIME
from data_handler import DataHandler
from gigachat_module import generate_motivation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

data_handler = DataHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(
        f'Привет! Я бот для отслеживания привычки чтения.\n'
        f'Каждый день выделяй 20 минут на книгу! 📖'
    )
    logger.info(f'User {user_id} started bot')

async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    weekly = data_handler.get_weekly_stats(user_id)
    
    stats_text = "📊 Статистика за неделю:\n"
    for date in weekly:
        stats_text += f"{date}\n"
    
    motivation = generate_motivation(f"Статистика: {len(weekly)} дней чтения на этой неделе")
    if motivation:
        stats_text += f"\n💭 {motivation}"
    
    await update.message.reply_text(stats_text)
    logger.info(f'User {user_id} requested weekly stats')

async def mesyac(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    monthly = data_handler.get_monthly_stats(user_id)
    
    stats_text = "📈 Статистика за месяц:\n"
    for date in monthly:
        stats_text += f"{date}\n"
    
    motivation = generate_motivation(f"Статистика месяца: {len(monthly)} дней чтения")
    if motivation:
        stats_text += f"\n💭 {motivation}"
    
    await update.message.reply_text(stats_text)
    logger.info(f'User {user_id} requested monthly stats')

async def rekord(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    record = data_handler.get_longest_streak(user_id)
    
    record_text = f"🔥 Рекорд: {record} дней"
    
    motivation = generate_motivation(f"Мой рекорд: {record} последовательных дней чтения")
    if motivation:
        record_text += f"\n\n💭 {motivation}"
    
    await update.message.reply_text(record_text)
    logger.info(f'User {user_id} requested record')

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Sending daily reminders...")
    motivation = generate_motivation("Напомни мне про чтение на 20 минут")
    reminder_text = "📖 Время для чтения! Удалось ли сегодня выделить 20 минут на книгу?"
    if motivation:
        reminder_text += f"\n\n{motivation}"
    
    logger.info(f"Reminder: {reminder_text}")

def main() -> None:
    logger.info("Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("statistika", statistika))
    app.add_handler(CommandHandler("mesyac", mesyac))
    app.add_handler(CommandHandler("rekord", rekord))
    
    logger.info("Handlers ready")
    logger.info("Attempting to start...")
    
    scheduler = AsyncIOScheduler()
    #scheduler.add_job(send_reminder, "cron", hour=20, minute=30, timezone="Europe/Moscow", id='send_reminder')
    scheduler.start()
    
    logger.info(f"Sending at {REMINDER_TIME}")
    logger.info("Scheduler started")
    
    app.run_polling()

if __name__ == '__main__':
    main()
