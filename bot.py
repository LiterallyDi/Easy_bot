import logging
import random
import psycopg2
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для получения случайной цитаты из базы данных (у меня она локальная)
def get_random_quote(column_name):
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname="valod",
            user="postgres",
            password="your_password",  # тут должны быть ваши данные ребята
            host="localhost",
            port="5433"  #  порт
        )
        cursor = conn.cursor()
        
        # Получение максимального значения Id
        cursor.execute('SELECT MAX("Id") FROM public."valodTable";')
        max_id = cursor.fetchone()[0]

        # Генерация случайного Id
        random_id = random.randint(1, max_id)

        # Логирование выполнения запроса
        query = f'SELECT "{column_name}" FROM public."valodTable" WHERE "Id" = %s;'
        logger.info(f"Выполнение запроса: {query} с Id {random_id}")
        cursor.execute(query, (random_id,))
        quote = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if quote:
            return quote[0]
        else:
            logger.error("Цитата не найдена.")
            return None
    except psycopg2.Error as db_error:
        logger.error(f"Ошибка базы данных: {db_error}")
        return None
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        return None

# Функции обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь нажал /start")
    welcome_message = "Привет! Я Библейские цитаты Бот. Напиши /quote для цитаты на английском языке или /quote_translated для цитаты на русском языке."
    await update.message.reply_text(welcome_message)

async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь запросил цитату на английском языке")
    quote = get_random_quote('EngText')
    if quote:
        await update.message.reply_text(quote)
    else:
        await update.message.reply_text("Ошибка при получении цитаты.")

async def quote_translated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Пользователь запросил цитату на русском языке")
    quote = get_random_quote('RusText')
    if quote:
        await update.message.reply_text(quote)
    else:
        await update.message.reply_text("Ошибка при получении цитаты.")

# Главная функция, запускающая бота, и старайтесь не ставить лишние space ибо на пайтоне это ошибка лол , это вам не xcode
def main() -> None:
    application = Application.builder().token('YOUR_BOT_TOKEN').build()

    start_handler = CommandHandler('start', start)
    quote_handler = CommandHandler('quote', quote)
    quote_translated_handler = CommandHandler('quote_translated', quote_translated)

    application.add_handler(start_handler)
    application.add_handler(quote_handler)
    application.add_handler(quote_translated_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
