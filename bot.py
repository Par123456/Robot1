import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Admin user ID (replace with actual admin ID)
ADMIN_ID = 6508600903

# List of banned users (in-memory, will be lost if bot restarts)
banned_users = []

# In-memory storage for user subcriptions
user_subscriptions = {}

# In-memory storage for user support messages
support_requests = []

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    keyboard = [
        [KeyboardButton("/help"), KeyboardButton("/design_logo")],
        [KeyboardButton("/dns"), KeyboardButton("/vpn")],
        [KeyboardButton("/support"), KeyboardButton("/games")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome! Use the menu below to interact with the bot.", reply_markup=reply_markup)

# Help command handler
def help_command(update: Update, context: CallbackContext) -> None:
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/design_logo <text> - Design a logo with the given text\n"
        "/dns - DNS services\n"
        "/vpn - VPN services\n"
        "/support - Contact support\n"
        "/games - Play games\n"
        "/admin - Admin panel (admin only)\n"
    )
    update.message.reply_text(help_text)

# Design logo command handler
def design_logo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    if not context.args:
        update.message.reply_text("Please provide text for the logo.")
        return

    text = ' '.join(context.args)
    logo_path = create_logo(text)
    update.message.reply_photo(photo=open(logo_path, 'rb'))

def create_logo(text: str) -> str:
    img = Image.new('RGB', (500, 150), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    d.text((10, 10), text, font=fnt, fill=(255, 255, 0))
    logo_path = 'logo.png'
    img.save(logo_path)
    return logo_path

# DNS services command handler
def dns_services(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    keyboard = [
        [InlineKeyboardButton("Free DNS", callback_data='free_dns')],
        [InlineKeyboardButton("Premium DNS", callback_data='premium_dns')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('DNS Services:', reply_markup=reply_markup)

# VPS services command handler
def vps_services(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    keyboard = [
        [InlineKeyboardButton("Free VPN", callback_data='free_vpn')],
        [InlineKeyboardButton("Premium VPN", callback_data='premium_vpn')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('VPN Services:', reply_markup=reply_markup)

# Support command handler
def support(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    update.message.reply_text("Please describe your issue:")
    context.user_data['awaiting_support'] = True

# Games command handler
def games(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        update.message.reply_text("You are banned from using this bot.")
        return

    update.message.reply_text("Game feature coming soon!")

# Admin panel command handler
def admin_panel(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        update.message.reply_text("You are not authorized to use this command.")
        return

    keyboard = [
        [InlineKeyboardButton("Ban User", callback_data='ban_user')],
        [InlineKeyboardButton("Unban User", callback_data='unban_user')],
        [InlineKeyboardButton("View Support Requests", callback_data='view_support')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Admin Panel:', reply_markup=reply_markup)

# Callback query handler for admin actions
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        query.answer("You are not authorized to perform this action.")
        return

    query.answer()
    action = query.data

    if action == 'ban_user':
        query.message.reply_text("Please send the user ID to ban.")
        context.user_data['action'] = 'ban_user'
    elif action == 'unban_user':
        query.message.reply_text("Please send the user ID to unban.")
        context.user_data['action'] = 'unban_user'
    elif action == 'view_support':
        support_text = "\n".join(support_requests) if support_requests else "No support requests."
        query.message.reply_text(support_text)

# Handle messages for admin and support actions
def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in banned_users:
        return

    if 'awaiting_support' in context.user_data and context.user_data['awaiting_support']:
        support_requests.append(update.message.text)
        update.message.reply_text("Your support request has been sent.")
        context.user_data['awaiting_support'] = False
        return

    if user_id != ADMIN_ID:
        return

    if 'action' not in context.user_data:
        return

    action = context.user_data['action']
    target_user_id = int(update.message.text)

    if action == 'ban_user':
        banned_users.append(target_user_id)
        update.message.reply_text(f"User {target_user_id} has been banned.")
    elif action == 'unban_user':
        if target_user_id in banned_users:
            banned_users.remove(target_user_id)
            update.message.reply_text(f"User {target_user_id} has been unbanned.")
        else:
            update.message.reply_text(f"User {target_user_id} is not banned.")

    del context.user_data['action']

def main() -> None:
    updater = Updater("7305678243:AAEGUtqt56DQH8ZiegNmHrbUAOMIaZyxaQA")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("design_logo", design_logo))
    dispatcher.add_handler(CommandHandler("dns", dns_services))
    dispatcher.add_handler(CommandHandler("vpn", vps_services))
    dispatcher.add_handler(CommandHandler("support", support))
    dispatcher.add_handler(CommandHandler("games", games))
    dispatcher.add_handler(CommandHandler("admin", admin_panel))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()