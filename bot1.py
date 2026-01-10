from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Простые правила без картинок для теста
RULES_SIMPLE = [
    "📖 **Часть 1 из 5**\n\n**Основные правила:**\n• Минимальная ставка: 10 монет\n• Максимальная ставка: 1000 монет\n• Играйте ответственно",
    "📖 **Часть 2 из 5**\n\n**Типы ставок:**\n• На число (x35)\n• На цвет (x2)\n• На чет/нечет (x2)\n• На дюжину (x3)",
    "📖 **Часть 3 из 5**\n\n**Как играть:**\n1. Выберите сумму ставки\n2. Выберите тип ставки\n3. Нажмите 'Крутить'\n4. Получите результат",
    "📖 **Часть 4 из 5**\n\n**Советы:**\n• Начинайте с малого\n• Не гонитесь за потерями\n• Делайте перерывы",
    "📖 **Часть 5 из 5**\n\n**Важно:**\nИгра предназначена только для развлечения!\nУдачи! 🍀"
]

# Список картинок для каждой страницы (5 одинаковых картинок)
RULES_IMAGES = [
    "rules1.jpg",
    "rules2.jpg",
    "rules3.jpg",
    "rules4.jpg",
    "rules5.jpg"
]

# Храним текущие страницы пользователей
user_pages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_pages[user_id] = 0  # Начинаем с первой страницы
    
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", web_app={"url": "https://ruletzreach.github.io/00/"})],
        [InlineKeyboardButton("📖 Правила", callback_data="rules_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать! Выберите действие:", reply_markup=reply_markup)

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE, page_num=None):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Определяем номер страницы
    if page_num is None:
        if user_id in user_pages:
            page_num = user_pages[user_id]
        else:
            page_num = 0
            user_pages[user_id] = page_num
    
    # Обновляем номер страницы пользователя
    user_pages[user_id] = page_num
    
    # Создаем клавиатуру навигации
    nav_buttons = []
    
    # Кнопка "назад" если не первая страница
    if page_num > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"rules_prev_{page_num}"))
    
    # Индикатор страницы
    nav_buttons.append(InlineKeyboardButton(f"{page_num+1}/{len(RULES_SIMPLE)}", callback_data="page_info"))
    
    # Кнопка "вперед" если не последняя страница
    if page_num < len(RULES_SIMPLE) - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data=f"rules_next_{page_num}"))
    
    # Кнопка возврата в меню
    menu_button = [InlineKeyboardButton("🏠 В меню", callback_data="back_menu")]
    
    keyboard = [nav_buttons, menu_button]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Получаем текст и картинку для текущей страницы
    rules_text = RULES_SIMPLE[page_num]
    rules_image = RULES_IMAGES[page_num]
    
    # Отправляем или редактируем сообщение с картинкой
    try:
        if query.message.photo:
            # Если сообщение уже содержит фото, редактируем его
            media = InputMediaPhoto(
                media=rules_image,
                caption=rules_text,
                parse_mode="Markdown"
            )
            await query.edit_message_media(media=media, reply_markup=reply_markup)
        else:
            # Если это первое сообщение с правилами, отправляем новое фото с подписью
            await query.message.reply_photo(
                photo=rules_image,
                caption=rules_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await query.message.delete()  # Удаляем старое сообщение
    except Exception as e:
        logger.error(f"Error sending rules with image: {e}")
        # Если возникла ошибка с фото, отправляем только текст
        await query.edit_message_text(
            text=rules_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()  # Обязательно отвечаем
    
    logger.info(f"User {user_id} pressed: {query.data}")
    
    # Инициализируем страницу пользователя если нужно
    if user_id not in user_pages:
        user_pages[user_id] = 0
    
    if query.data == "rules_start":
        # Начинаем показ правил с первой страницы
        await show_rules(update, context, 0)
    
    elif query.data.startswith("rules_prev_"):
        # Листаем назад
        try:
            current_page = int(query.data.split("_")[-1])
            new_page = current_page - 1
            if new_page >= 0:
                await show_rules(update, context, new_page)
        except:
            await show_rules(update, context, 0)
    
    elif query.data.startswith("rules_next_"):
        # Листаем вперед
        try:
            current_page = int(query.data.split("_")[-1])
            new_page = current_page + 1
            if new_page < len(RULES_SIMPLE):
                await show_rules(update, context, new_page)
        except:
            await show_rules(update, context, 0)
    
    elif query.data == "back_menu":
        # Возвращаемся в главное меню
        keyboard = [
            [InlineKeyboardButton("🎮 Играть", web_app={"url": "https://ruletzreach.github.io/00/"})],
            [InlineKeyboardButton("📖 Правила", callback_data="rules_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.message.delete()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Главное меню:",
            reply_markup=reply_markup
        )
        
        # Сбрасываем страницу пользователя
        user_pages[user_id] = 0
    
    elif query.data == "page_info":
        # Просто показываем информацию о странице
        current_page = user_pages.get(user_id, 0) + 1
        total_pages = len(RULES_SIMPLE)
        await query.answer(f"Страница {current_page} из {total_pages}", show_alert=False)

def main():
    TOKEN = "8540455024:AAGn1_E3Y8wrRmHAhsX4uMaGmgc3nX7eueE"
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("Бот запущен! Отправьте /start")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
