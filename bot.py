import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

# Загружаем переменные окружения из .env файла
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Определяем состояния разговора
CHOOSING, TYPING_CONTACT, SELECTING_ROOMS, SELECTING_DISTRICT = range(4)

# Определяем кнопки выбора
keyboard = [
    [
        InlineKeyboardButton("Аренда квартиры", callback_data='rent_apartment'),
        InlineKeyboardButton("Покупка квартиры", callback_data='buy_apartment')
    ],
    [
        InlineKeyboardButton("Аренда дома", callback_data='rent_house'),
        InlineKeyboardButton("Покупка дома", callback_data='buy_house')
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)

# Определяем кнопки для выбора количества комнат
rooms_keyboard = [
    [
        InlineKeyboardButton("1 комната", callback_data='1_room'),
        InlineKeyboardButton("2 комнаты", callback_data='2_rooms')
    ],
    [
        InlineKeyboardButton("3 комнаты", callback_data='3_rooms'),
        InlineKeyboardButton("4 комнаты", callback_data='4_rooms')
    ],
    [
        InlineKeyboardButton("Больше 4 комнат", callback_data='more_rooms')
    ]
]
rooms_markup = InlineKeyboardMarkup(rooms_keyboard)

# Определяем кнопки для выбора района
districts = [
    "Киевский",
    "Суворовский",
    "Комсомольский",
    "Ленинский",
    "Шевченковский",
    "Фрунзенский",
    "Партизанский",
    "Героев Сталинграда",
    "Александровский",
    "Центральный"
]

districts_keyboard = [[InlineKeyboardButton(district, callback_data=district.lower())] for district in districts]
districts_markup = InlineKeyboardMarkup(districts_keyboard)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с инлайн-кнопками выбора."""
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Здравствуйте, {user_first_name}! Чем я могу вам помочь?",
        reply_markup=reply_markup
    )
    return CHOOSING

# Обработчик нажатий на инлайн-кнопки выбора недвижимости
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает нажатия на инлайн-кнопки и запрашивает контактные данные."""
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data['choice'] = choice  # Сохраняем выбор пользователя

    if choice in ['rent_apartment', 'buy_apartment', 'rent_house', 'buy_house']:
        await query.edit_message_text(text="Пожалуйста, оставьте свой контактный номер или напишите, как с вами связаться.")
        return TYPING_CONTACT
    else:
        await query.edit_message_text(text="Извините, я не понимаю ваш выбор.")
        return ConversationHandler.END

# Обработчик получения контактных данных
async def received_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученные контактные данные и запрашивает количество комнат."""
    user_contact = update.message.text
    context.user_data['contact'] = user_contact  # Сохраняем контакт

    await update.message.reply_text(
        "Спасибо! Сколько комнат вам нужно?",
        reply_markup=rooms_markup
    )
    return SELECTING_ROOMS

# Обработчик выбора количества комнат
async def selecting_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор количества комнат и запрашивает район."""
    query = update.callback_query
    await query.answer()

    rooms_choice = query.data
    context.user_data['rooms'] = rooms_choice  # Сохраняем выбор количества комнат

    await query.edit_message_text(text="Выберите район в городе Днепр:")
    return SELECTING_DISTRICT

# Обработчик выбора района
async def selecting_district(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор района и завершает разговор."""
    query = update.callback_query
    await query.answer()

    district_choice = query.data
    context.user_data['district'] = district_choice  # Сохраняем выбор района

    # Здесь вы можете добавить логику обработки данных, например, сохранение в базу или отправку администратору

    choice = context.user_data.get('choice')
    rooms = context.user_data.get('rooms')
    district = context.user_data.get('district')
    contact = context.user_data.get('contact')

    # Формируем сообщение для подтверждения
    choice_mapping = {
        'rent_apartment': "Аренда квартиры",
        'buy_apartment': "Покупка квартиры",
        'rent_house': "Аренда дома",
        'buy_house': "Покупка дома"
    }

    rooms_mapping = {
        '1_room': "1 комната",
        '2_rooms': "2 комнаты",
        '3_rooms': "3 комнаты",
        '4_rooms': "4 комнаты",
        'more_rooms': "Больше 4 комнат"
    }

    district_mapping = {
        district.lower(): district for district in districts
    }

    response = (
        f"**Ваш запрос:**\n"
        f"Тип: {choice_mapping.get(choice, 'Неизвестно')}\n"
        f"Количество комнат: {rooms_mapping.get(rooms, 'Неизвестно')}\n"
        f"Район: {district_mapping.get(district, 'Неизвестно')}\n"
        f"Контакт: {contact}\n\n"
        f"Спасибо! Мы свяжемся с вами в ближайшее время."
    )

    await query.edit_message_text(text=response, parse_mode='Markdown')

    return ConversationHandler.END

# Обработчик команды /cancel для выхода из разговора
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет текущий разговор."""
    await update.message.reply_text('Разговор отменён. Вы можете начать заново, отправив /start.')
    return ConversationHandler.END

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение с инструкциями по использованию бота."""
    help_text = (
        "Я могу помочь вам с выбором:\n"
        "- Аренда квартиры\n"
        "- Покупка квартиры\n"
        "- Аренда дома\n"
        "- Покупка дома\n\n"
        "Пожалуйста, используйте кнопки ниже или отправьте /start для повторного отображения меню."
    )
    await update.message.reply_text(help_text)

def main():
    # Получаем токен из переменных окружения для безопасности
    TOKEN = os.getenv('7635795563:AAEqNHfskDhKv5dHQssdI66KT3hm7cuJnuU')

    if not TOKEN:
        logger.error("Токен бота не найден. Установите переменную окружения TELEGRAM_BOT_TOKEN.")
        return

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Определяем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_callback)],
            TYPING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_contact)],
            SELECTING_ROOMS: [CallbackQueryHandler(selecting_rooms)],
            SELECTING_DISTRICT: [CallbackQueryHandler(selecting_district)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
