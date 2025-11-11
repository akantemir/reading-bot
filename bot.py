import logging
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request, jsonify
from config import TELEGRAM_TOKEN, REMINDER_TIME
from data_handler import DataHandler
from gigachat_module import generate_motivation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

data_handler = DataHandler()

# Flask app for webhooks
flask_app = Flask(__name__)

# Telegram bot application
app = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(
        f'Привет! Я бот для отслеживания прибычки чтения.\n'
        f'Каждый день вделай 20 минут на книгу! '
    )
    logger.info(f'User {user_id} started bot')

async def statistika(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    weekly = data_handler.get_weekly_stats(user_id)
    await update.message.reply_text(
        f"Статистика на неделю:\n"
        f"Всего прочитано: {weekly['total_sessions']} сеансов\n"
        f"Минут: {weekly['total_minutes']} минут\n"
        f"Средний сеанс: {weekly['avg_session_length']:.0f} минут"
    )

async def mesyac(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    monthly = data_handler.get_monthly_stats(user_id)
    await update.message.reply_text(
        f"Статистика на месяц:\n"
        f"Всего сеансов: {monthly['total_sessions']}\n"
        f"Всего минут: {monthly['total_minutes']}\n"
        f"Среднее за день: {monthly['daily_average']:.1f} минут"
    )

async def rekord(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    record = data_handler.get_record(user_id)
    await update.message.reply_text(
        f"Ваш рекорд: {record['max_session']} минут\n"
        f"Дата: {record['date']}"
    )

async def send_reminder(application: Application, user_id: int) -> None:
    """Send reminder message to user"""
    try:
        motivation = generate_motivation()
        await application.bot.send_message(
            chat_id=user_id,
            text=f"Напоминание! Пора читать!\n\n{motivation}"
        )
    except Exception as e:
        logger.error(f"Failed to send reminder to {user_id}: {e}")

async def scheduler_job(application: Application) -> None:
    """Run scheduled reminders"""
    logger.info(f"Running scheduled reminders at {REMINDER_TIME}")
    # Get all active users and send reminders
    active_users = data_handler.get_active_users()
    for user_id in active_users:
        await send_reminder(application, user_id)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({'status': 'error', 'message': 'No data'}), 400
        
        # Create Update object from JSON
        update = Update.de_json(update_data, app.bot)
        
        # Process the update asynchronously
        asyncio.run(app.process_update(update))
        
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@flask_app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

def create_app() -> Application:
    """Create and configure the Telegram bot application"""
    global app
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stat', statistika))
    app.add_handler(CommandHandler('mesyac', mesyac))
    app.add_handler(CommandHandler('rekord', rekord))
    
    logger.info("Handlers ready")
    
    # Setup scheduler for reminders
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduler_job,
        'cron',
        args=(app,),
        hour=20,
        minute=30,
        timezone='Europe/Moscow',
        id='send_reminder'
    )
    scheduler.start()
    
    logger.info(f"Sending at {REMINDER_TIME}")
    logger.info("Scheduler started")
    
    return app

def main() -> None:
    """Start the Flask webhook server"""
    create_app()
    
    # Start Flask server on 0.0.0.0:5000
    logger.info("Starting webhook server...")
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    main()
