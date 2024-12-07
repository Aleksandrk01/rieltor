import logging
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

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Определяем состояния разговора
CHOOSING, TYPING_CONTACT = range(2)

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

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с инлайн-кнопками выбора."""
    user_first_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Здравствуйте, {user_first_name}! Чем я могу вам помочь?",
        reply_markup=reply_markup
    )
    return CHOOSING

# Обработчик нажатий на инлайн-кнопки
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
    """Обрабатывает полученные контактные данные и завершает разговор."""
    user_contact = update.message.text
    choice = context.user_data.get('choice')

    # Здесь вы можете добавить логику обработки данных, например, сохранение в базу

    response_messages = {
        'rent_apartment': "Спасибо! Мы свяжемся с вами по поводу аренды квартиры.",
        'buy_apartment': "Спасибо! Мы свяжемся с вами по поводу покупки квартиры.",
        'rent_house': "Спасибо! Мы свяжемся с вами по поводу аренды дома.",
        'buy_house': "Спасибо! Мы свяжемся с вами по поводу покупки дома."
    }

    response = response_messages.get(choice, "Спасибо за информацию! Мы свяжемся с вами в ближайшее время.")
    await update.message.reply_text(response)

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
    # Вставьте сюда ваш токен
    TOKEN = '7635795563:AAEqNHfskDhKv5dHQssdI66KT3hm7cuJnuU'

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Определяем ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_callback)],
            TYPING_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_contact)],
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
