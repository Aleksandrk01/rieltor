import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
import requests
from bs4 import BeautifulSoup

# Загрузка переменных окружения из .env
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Определяем состояния разговора
CHOOSING, TYPING_ROOMS, TYPING_DISTRICT, TYPING_RENOVATION, TYPING_BUDGET, TYPING_PAYMENT, TYPING_CONTACT = range(7)

# Определяем кнопки выбора категории
category_keyboard = [
    [
        InlineKeyboardButton("Аренда квартиры", callback_data='rent_apartment'),
        InlineKeyboardButton("Покупка квартиры", callback_data='buy_apartment')
    ],
    [
        InlineKeyboardButton("Аренда дома", callback_data='rent_house'),
        InlineKeyboardButton("Покупка дома", callback_data='buy_house')
    ]
]
category_markup = InlineKeyboardMarkup(category_keyboard)

# Определяем кнопки выбора количества комнат
rooms_keyboard = [
    [
        InlineKeyboardButton("1 комната", callback_data='1_room'),
        InlineKeyboardButton("2 комнаты", callback_data='2_rooms')
    ],
    [
        InlineKeyboardButton("3 комнаты", callback_data='3_rooms'),
        InlineKeyboardButton("4 и более комнат", callback_data='4_plus_rooms')
    ]
]
rooms_markup = InlineKeyboardMarkup(rooms_keyboard)

# Определяем кнопки выбора района города Днепр
district_keyboard = [
    [
        InlineKeyboardButton("Центральный", callback_data='central_district'),
        InlineKeyboardButton("Днепропетровский", callback_data='dnepropetrovsk_district')
    ],
    [
        InlineKeyboardButton("Жовтневый", callback_data='zhovtnevyi_district'),
        InlineKeyboardButton("Соборный", callback_data='sobornyi_district')
    ],
    [
        InlineKeyboardButton("Ломоносовский", callback_data='lomonosovskyi_district'),
        InlineKeyboardButton("Партизанский", callback_data='partyzanskyi_district')
    ]
]
district_markup = InlineKeyboardMarkup(district_keyboard)

# Определяем кнопки выбора типа ремонта
renovation_keyboard = [
    [
        InlineKeyboardButton("Косметический", callback_data='cosmetic_renovation'),
        InlineKeyboardButton("Капитальный", callback_data='capital_renovation')
    ],
    [
        InlineKeyboardButton("Дизайнерский", callback_data='designer_renovation'),
        InlineKeyboardButton("Не требуется", callback_data='no_renovation')
    ]
]
renovation_markup = InlineKeyboardMarkup(renovation_keyboard)

# Определяем кнопки выбора бюджета
budget_keyboard = [
    [
        InlineKeyboardButton("До 10 000$", callback_data='budget_under_10k'),
        InlineKeyboardButton("10 000$ - 20 000$", callback_data='budget_10k_20k')
    ],
    [
        InlineKeyboardButton("20 000$ - 30 000$", callback_data='budget_20k_30k'),
        InlineKeyboardButton("Более 30 000$", callback_data='budget_over_30k')
    ]
]
budget_markup = InlineKeyboardMarkup(budget_keyboard)

# Определяем кнопки выбора способа оплаты
payment_keyboard = [
    [
        InlineKeyboardButton("Наличные", callback_data='payment_cash'),
        InlineKeyboardButton("Рассрочка", callback_data='payment_installment')
    ],
    [
        InlineKeyboardButton("Ипотека", callback_data='payment_mortgage'),
        InlineKeyboardButton("Не определился", callback_data='payment_unsure')
    ]
]
payment_markup = InlineKeyboardMarkup(payment_keyboard)

# Определяем кнопку для запроса контакта
contact_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Отправить контакт", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

def fetch_olx_listings(category, transaction, rooms, district, budget_min, budget_max):
    """
    Функция для получения объявлений с OLX на основе заданных параметров.
    """
    # Здесь должен быть ваш код скрейпинга OLX
    # Для примера вернём пустой список
    return []

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с инлайн-кнопками выбора категории."""
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Здравствуйте, {user_first_name}! Чем я могу вам помочь?",
        reply_markup=category_markup
    )
    return CHOOSING

# Обработчик нажатий на инлайн-кнопки категории
async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор категории и запрашивает количество комнат."""
    query = update.callback_query
    await query.answer()

    choice = query.data
    context.user_data['choice'] = choice  # Сохраняем выбор пользователя

    # Отправляем вопрос о количестве комнат с соответствующими кнопками
    await query.edit_message_text(text="Сколько комнат вас интересует?", reply_markup=rooms_markup)
    return TYPING_ROOMS

# Обработчик нажатий на инлайн-кнопки количества комнат
async def rooms_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор количества комнат и запрашивает район."""
    query = update.callback_query
    await query.answer()

    rooms_choice = query.data
    context.user_data['rooms'] = rooms_choice  # Сохраняем выбор пользователя

    # Отправляем вопрос о районе с соответствующими кнопками
    await query.edit_message_text(text="Укажите, пожалуйста, район города Днепр:", reply_markup=district_markup)
    return TYPING_DISTRICT

# Обработчик нажатий на инлайн-кнопки района
async def district_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор района и запрашивает тип ремонта."""
    query = update.callback_query
    await query.answer()

    district_choice = query.data
    context.user_data['district'] = district_choice  # Сохраняем выбор пользователя

    # Отправляем вопрос о типе ремонта с соответствующими кнопками
    await query.edit_message_text(text="Какой тип ремонта вас интересует?", reply_markup=renovation_markup)
    return TYPING_RENOVATION

# Обработчик нажатий на инлайн-кнопки типа ремонта
async def renovation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор типа ремонта и запрашивает бюджет."""
    query = update.callback_query
    await query.answer()

    renovation_choice = query.data
    context.user_data['renovation'] = renovation_choice  # Сохраняем выбор пользователя

    # Отправляем вопрос о бюджете с соответствующими кнопками
    await query.edit_message_text(text="Какой ваш бюджет на проект?", reply_markup=budget_markup)
    return TYPING_BUDGET

# Обработчик нажатий на инлайн-кнопки бюджета
async def budget_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор бюджета и запрашивает способ оплаты."""
    query = update.callback_query
    await query.answer()

    budget_choice = query.data
    context.user_data['budget'] = budget_choice  # Сохраняем выбор пользователя

    # Отправляем вопрос о способе оплаты с соответствующими кнопками
    await query.edit_message_text(
        text="Какой способ оплаты вы предпочитаете?",
        reply_markup=payment_markup
    )
    return TYPING_PAYMENT

# Обработчик нажатий на инлайн-кнопки способа оплаты
async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор способа оплаты и запрашивает контактные данные."""
    query = update.callback_query
    await query.answer()

    payment_choice = query.data
    context.user_data['payment'] = payment_choice  # Сохраняем выбор пользователя

    # Отправляем новое сообщение с кнопкой для отправки контакта
    await query.message.reply_text(
        text="Пожалуйста, отправьте свой контактный номер или напишите, как с вами связаться.",
        reply_markup=contact_keyboard
    )
    return TYPING_CONTACT

# Обработчик получения контактных данных
async def received_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает полученные контактные данные и завершает разговор."""
    contact = update.message.contact
    if contact:
        user_contact = contact.phone_number
    else:
        user_contact = update.message.text  # На случай, если пользователь пишет текст

    context.user_data['contact'] = user_contact
    choice = context.user_data.get('choice')
    rooms = context.user_data.get('rooms', 'не указано')
    district = context.user_data.get('district', 'не указан')
    renovation = context.user_data.get('renovation', 'не указан')
    budget = context.user_data.get('budget', 'не указан')
    payment = context.user_data.get('payment', 'не указан')

    # Преобразуем данные для удобного отображения
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
        '4_plus_rooms': "4 и более комнат"
    }
    district_mapping = {
        'central_district': "Центральный",
        'dnepropetrovsk_district': "Днепропетровский",
        'zhovtnevyi_district': "Жовтневый",
        'sobornyi_district': "Соборный",
        'lomonosovskyi_district': "Ломоносовский",
        'partyzanskyi_district': "Партизанский"
    }
    renovation_mapping = {
        'cosmetic_renovation': "Косметический",
        'capital_renovation': "Капитальный",
        'designer_renovation': "Дизайнерский",
        'no_renovation': "Не требуется"
    }
    budget_mapping = {
        'budget_under_10k': "До 10 000$",
        'budget_10k_20k': "10 000$ - 20 000$",
        'budget_20k_30k': "20 000$ - 30 000$",
        'budget_over_30k': "Более 30 000$"
    }
    payment_mapping = {
        'payment_cash': "Наличные",
        'payment_installment': "Рассрочка",
        'payment_mortgage': "Ипотека",
        'payment_unsure': "Не определился"
    }

    selected_choice = choice_mapping.get(choice, "Неизвестный выбор")
    selected_rooms = rooms_mapping.get(rooms, "Не указано")
    selected_district = district_mapping.get(district, "Не указан")
    selected_renovation = renovation_mapping.get(renovation, "Не указан")
    selected_budget = budget_mapping.get(budget, "Не указан")
    selected_payment = payment_mapping.get(payment, "Не указан")

    # Получаем объявления с OLX
    listings = fetch_olx_listings(
        category='apartment' if 'apartment' in choice else 'house',
        transaction='rent' if 'rent' in choice else 'buy',
        rooms=rooms,
        district=district,
        budget_min=budget_min_val(budget),
        budget_max=budget_max_val(budget)
    )

    if not listings:
        olx_message = "К сожалению, не удалось найти подходящие объявления на OLX."
    else:
        olx_message = "Вот некоторые подходящие объявления с OLX:\n\n"
        for listing in listings[:5]:  # Ограничиваем до 5 объявлений
            olx_message += f"• *{listing['title']}*\n  Цена: {listing['price']}\n  [Подробнее]({listing['link']})\n\n"

    final_response = (
        f"Спасибо за предоставленную информацию!\n\n"
        f"**Категория:** {selected_choice}\n"
        f"**Количество комнат:** {selected_rooms}\n"
        f"**Район:** {selected_district}\n"
        f"**Тип ремонта:** {selected_renovation}\n"
        f"**Бюджет:** {selected_budget}\n"
        f"**Способ оплаты:** {selected_payment}\n"
        f"**Контакт:** {user_contact}\n\n"
        f"{olx_message}"
        f"Мы свяжемся с вами в ближайшее время."
    )

    # Отправляем итоговое сообщение
    await update.message.reply_text(final_response, parse_mode='Markdown', disable_web_page_preview=True, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

# Обработчик ошибок
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Логирует ошибку и отправляет сообщение пользователю."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # Отправляем сообщение пользователю
    if isinstance(update, Update) and update.effective_user:
        await update.effective_user.send_message(
            text="Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."
        )

# Обработчик команды /cancel для выхода из разговора
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отменяет текущий разговор."""
    await update.message.reply_text('Разговор отменён. Вы можете начать заново, отправив /start.', reply_markup=ReplyKeyboardRemove())
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
        "Пожалуйста, используйте кнопки или команду /start для отображения меню."
    )
    await update.message.reply_text(help_text)

def budget_min_val(budget_key):
    """Возвращает минимальную цену на основе выбранного бюджета."""
    budget_min_map = {
        'budget_under_10k': '0',
        'budget_10k_20k': '10000',
        'budget_20k_30k': '20000',
        'budget_over_30k': '30000'
    }
    return budget_min_map.get(budget_key, '0')

def budget_max_val(budget_key):
    """Возвращает максимальную цену на основе выбранного бюджета."""
    budget_max_map = {
        'budget_under_10k': '10000',
        'budget_10k_20k': '20000',
        'budget_20k_30k': '30000',
        'budget_over_30k': '1000000'  # Большое число для верхней границы
    }
    return budget_max_map.get(budget_key, '1000000')

def main():
    # Получаем токен из переменных окружения
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    if not TOKEN:
        logger.error("Не удалось найти переменную окружения TELEGRAM_BOT_TOKEN")
        return

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Определяем ConversationHandler с последовательными шагами
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(category_callback)],
            TYPING_ROOMS: [CallbackQueryHandler(rooms_callback)],
            TYPING_DISTRICT: [CallbackQueryHandler(district_callback)],
            TYPING_RENOVATION: [CallbackQueryHandler(renovation_callback)],
            TYPING_BUDGET: [CallbackQueryHandler(budget_callback)],
            TYPING_PAYMENT: [CallbackQueryHandler(payment_callback)],
            TYPING_CONTACT: [
                MessageHandler(filters.CONTACT, received_contact),
                MessageHandler(filters.TEXT & ~filters.COMMAND, received_contact)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Добавляем обработчики
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))

    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
