from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
import logging

#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)


RULES_SIMPLE = [
    "Нажмите на квадрат, чтобы открыть его. Число указывает, сколько мин находится вокруг этого квадрата. В этом случае вокруг открытого квадрата находится лишь одна мина",
    "Когда вы найдёте мину, вы можете пометить её флагом. Для этого нажмите правую кнопку мыши (ПКМ) на компьютере или зажмите клетку на телефоне. Также можно использовать значок флага сверху, переключающий режимы «флаг» / «открытие клеток»",
    "Игра заканчивается, когда вы нажимаете на мину. Количество мин на поле указывается сверху. Все мины будут видны, когда игра закончится. Начать заново можно, нажав на кнопку «:)». Найдите все безопасные клетки, чтобы выиграть. Также можно изменить сложность игры",
    "Это стандартный шаблон «1-2», где самая дальняя от единицы клетка всегда безопасна. А самая дальняя клетка от двойки всегда является миной. Такие шаблоны называют «паттернами». Остальные можно найти в интернете или догадаться самому. Иногда игра создаёт ситуации, где нужно угадать расположение мин",
    "На этом всё. Удачи!"
]


RULES_IMAGES = [
    "https://raw.githubusercontent.com/Ruletzreach/00/refs/heads/main/images/rules1.jpg",
    "https://raw.githubusercontent.com/Ruletzreach/00/refs/heads/main/images/rules2.jpg",
    "https://raw.githubusercontent.com/Ruletzreach/00/refs/heads/main/images/rules3.jpg",
    "https://raw.githubusercontent.com/Ruletzreach/00/refs/heads/main/images/rules4.jpg",
    "https://raw.githubusercontent.com/Ruletzreach/00/refs/heads/main/images/rules5.jpg"
]


user_pages = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_pages[user_id] = 0  
    
    keyboard = [
        [InlineKeyboardButton("Начать игру", web_app={"url": "https://ruletzreach.github.io/00/"})],
        [InlineKeyboardButton("А как играть?", callback_data="rules_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать!", reply_markup=reply_markup)

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE, page_num=None):
    query = update.callback_query
    user_id = query.from_user.id
    
    if page_num is None:
        if user_id in user_pages:
            page_num = user_pages[user_id]
        else:
            page_num = 0
            user_pages[user_id] = page_num
    
    user_pages[user_id] = page_num
    
    nav_buttons = []
    
    if page_num > 0:
        nav_buttons.append(InlineKeyboardButton("<--", callback_data=f"rules_prev_{page_num}"))
    
    nav_buttons.append(InlineKeyboardButton(f"{page_num+1}/{len(RULES_SIMPLE)}", callback_data="page_info"))
    
    if page_num < len(RULES_SIMPLE) - 1:
        nav_buttons.append(InlineKeyboardButton("-->️", callback_data=f"rules_next_{page_num}"))
    
    menu_button = [InlineKeyboardButton("В меню", callback_data="back_menu")]
    
    keyboard = [nav_buttons, menu_button]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    rules_text = RULES_SIMPLE[page_num]
    rules_image = RULES_IMAGES[page_num]
    
    try:
        if query.message.photo:
            media = InputMediaPhoto(
                media=rules_image,
                caption=rules_text,
                parse_mode="Markdown"
            )
            await query.edit_message_media(media=media, reply_markup=reply_markup)
        else:
            await query.message.reply_photo(
                photo=rules_image,
                caption=rules_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await query.message.delete()
    except Exception as e:
        #logger.error(f"Error sending rules with image: {e}")
        await query.edit_message_text(
            text=rules_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    #logger.info(f"User {user_id} pressed: {query.data}")
    
    if user_id not in user_pages:
        user_pages[user_id] = 0
    
    if query.data == "rules_start":
        # Начинаем показ правил с первой страницы
        await show_rules(update, context, 0)
    
    elif query.data.startswith("rules_prev_"):
        try:
            current_page = int(query.data.split("_")[-1])
            new_page = current_page - 1
            if new_page >= 0:
                await show_rules(update, context, new_page)
        except:
            await show_rules(update, context, 0)
    
    elif query.data.startswith("rules_next_"):
        try:
            current_page = int(query.data.split("_")[-1])
            new_page = current_page + 1
            if new_page < len(RULES_SIMPLE):
                await show_rules(update, context, new_page)
        except:
            await show_rules(update, context, 0)
    
    elif query.data == "back_menu":
        keyboard = [
            [InlineKeyboardButton("Начать игру", web_app={"url": "https://ruletzreach.github.io/00/"})],
            [InlineKeyboardButton("А как играть?", callback_data="rules_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.message.delete()
        except:
            pass
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Меню:",
            reply_markup=reply_markup
        )
        
        user_pages[user_id] = 0
    
    elif query.data == "page_info":
        current_page = user_pages.get(user_id, 0) + 1
        total_pages = len(RULES_SIMPLE)
        await query.answer(f"Страница {current_page} из {total_pages}", show_alert=False)

def main():
    TOKEN = "8586709039:AAFIakGNHmdxRXOjlO7TgN0uEA7yKS4eONU"
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    #print("Бот запущен! Отправьте /start")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
