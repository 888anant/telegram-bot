
import logging
import json
import os
import uuid
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    CallbackQueryHandler, ContextTypes
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot credentials - Replace with your actual token from BotFather
BOT_TOKEN = "replace_this"  # Replace this with your actual token
ADMIN_ID = replace_this  # Replace with your Telegram user ID (as an integer)

# Channel information
CHANNEL_USERNAME = "hackeddmodz"  # Your channel username without the @ symbol
CHANNEL_ID = -1002404523976  # Replace with your channel ID (as an integer)

# User data file
USER_DATA_FILE = "user_data.json"

# Message templates
WELCOME_MESSAGE = """
🎮 *Welcome to Hacked Modz Bot* 🎮

I'll connect you directly with the admin.

🔹 Send me a message, and I'll forward it.
🔹 You can also send files, photos, or videos.
🔹 The admin will reply to you directly through this bot.

Use /help to see available commands!

Happy Gaming! 🚀
"""

HELP_MESSAGE = """
🔍 *Available Commands* 🔍

/start - Start the bot and get the welcome message
/help - Display this help message
/about - Learn more about Hacked Modz
/checksubscription - Verify if you're subscribed to our channel

📤 To contact admin, simply send your message or file here!
"""

ABOUT_MESSAGE = """
*About Hacked Modz* 🎮

We provide premium mods for free!
Join our channel: @hackeddmodz

Created with ❤️
"""

# Helper Functions
def get_channel_button():
    """Create a button to join the channel"""
    keyboard = [[InlineKeyboardButton("Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
    return InlineKeyboardMarkup(keyboard)

async def is_admin(update: Update) -> bool:
    """Check if the user is an admin"""
    return update.effective_user.id == ADMIN_ID

async def save_user_data(context: ContextTypes.DEFAULT_TYPE):
    """Save user data to a file"""
    try:
        user_data = {}
        
        # Get user data from context
        for user_id, data in context.user_data.items():
            if isinstance(user_id, int):  # Ensure it's a valid user ID
                serializable_data = {}
                for key, value in data.items():
                    # Skip non-serializable items
                    if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        serializable_data[key] = value
                user_data[str(user_id)] = serializable_data
        
        # Save to file
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(user_data, file, indent=2)
            
        logger.info(f"User data saved successfully for {len(user_data)} users")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def load_user_data():
    """Load user data from a file"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        return {}
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {}

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    user = update.effective_user
    
    # Save user information
    context.user_data["registered"] = True
    context.user_data["username"] = user.username or "Unknown"
    context.user_data["first_name"] = user.first_name or "Unknown"
    context.user_data["last_name"] = user.last_name or "Unknown"
    context.user_data["user_id"] = user.id
    await save_user_data(context)
    
    # Notify admin about new user
    if ADMIN_ID:
        admin_notification = (
            f"🆕 New user registered:\n"
            f"ID: {user.id}\n"
            f"Username: @{user.username or 'None'}\n"
            f"Name: {user.first_name or ''} {user.last_name or ''}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_notification)
        except Exception as e:
            logger.error(f"Could not notify admin: {e}")
    
    # Create keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Join Our Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("Request a Mod", callback_data="request_mod")],
        [InlineKeyboardButton("Report an Issue", callback_data="report_issue")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command"""
    if await is_admin(update):
        # Admin help message
        await update.message.reply_text(
            "🛠️ *Admin Commands* 🛠️\n\n"
            "Reply to forwarded messages to respond to users.\n"
            "Use /broadcast [message] to send a message to all users.\n\n"
            "Regular commands also work:\n"
            "/start, /help, /about, /checksubscription",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /about command"""
    reply_markup = get_channel_button()
    await update.message.reply_text(
        ABOUT_MESSAGE,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def channel_subscription_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is subscribed to the channel"""
    user_id = update.effective_user.id
    
    try:
        # Check if user is a member of the channel
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        
        if member.status in ['creator', 'administrator', 'member', 'restricted']:
            await update.message.reply_text(
                "✅ You are subscribed to our channel! Thank you for your support.",
                parse_mode="Markdown"
            )
            return True
        else:
            # Not subscribed
            keyboard = get_channel_button()
            await update.message.reply_text(
                "❌ You are not subscribed to our channel yet. Please join to access all features!",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            return False
    except Exception as e:
        logger.error(f"Error checking channel subscription: {e}")
        keyboard = get_channel_button()
        await update.message.reply_text(
            "❓ Could not verify your subscription status. Please make sure you're subscribed to our channel.",
            reply_markup=keyboard
        )
        return False

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast a message to all users (admin only)"""
    if not await is_admin(update):
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast [message]")
        return
    
    broadcast_message = " ".join(context.args)
    
    # Load user data
    user_data = load_user_data()
    successful = 0
    failed = 0
    
    for user_id_str, data in user_data.items():
        try:
            user_id = int(user_id_str)
            if user_id != ADMIN_ID:  # Don't send to admin
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 *Announcement from Hacked Modz*\n\n{broadcast_message}",
                    parse_mode="Markdown"
                )
                successful += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id_str}: {e}")
            failed += 1
    
    status_message = f"Broadcast completed.\nSuccess: {successful}\nFailed: {failed}"
    await update.message.reply_text(status_message)

# Message handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages"""
    if await is_admin(update):
        await handle_admin_message(update, context)
    else:
        await handle_user_message(update, context)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from regular users"""
    user = update.effective_user
    message = update.message
    
    # Create forwarding message with user info
    user_info = (
        f"💬 Message from user:\n"
        f"ID: {user.id}\n"
        f"Username: @{user.username or 'None'}\n"
        f"Name: {user.first_name or ''} {user.last_name or ''}\n"
        f"-------------------------------------------\n"
    )
    
    # Forward the message to admin
    try:
        # Store conversation tracking info
        msg_id = str(uuid.uuid4())
        context.user_data["last_msg_id"] = msg_id
        
        # Initialize message map if not exists
        if "message_map" not in context.bot_data:
            context.bot_data["message_map"] = {}
        
        # Forward different types of content
        if message.text:
            admin_msg = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"{user_info}{message.text}"
            )
        elif message.photo:
            photo = message.photo[-1]  # Get the largest photo
            caption = f"{user_info}{message.caption or ''}"
            admin_msg = await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo.file_id,
                caption=caption
            )
        elif message.video:
            caption = f"{user_info}{message.caption or ''}"
            admin_msg = await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=message.video.file_id,
                caption=caption
            )
        elif message.document:
            caption = f"{user_info}{message.caption or ''}"
            admin_msg = await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=message.document.file_id,
                caption=caption
            )
        elif message.audio:
            caption = f"{user_info}{message.caption or ''}"
            admin_msg = await context.bot.send_audio(
                chat_id=ADMIN_ID,
                audio=message.audio.file_id,
                caption=caption
            )
        elif message.voice:
            admin_msg = await context.bot.send_voice(
                chat_id=ADMIN_ID,
                voice=message.voice.file_id,
                caption=user_info
            )
        else:
            admin_msg = await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"{user_info}[Unsupported message type]"
            )
        
        # Store the mapping for reply tracking
        context.bot_data["message_map"][admin_msg.message_id] = {
            "user_id": user.id,
            "msg_id": msg_id
        }
        
        # Acknowledge receipt to the user
        await message.reply_text("✅ Your message has been forwarded to the admin. Please wait for a response.")
        
    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        await message.reply_text("❌ There was an error forwarding your message. Please try again later.")

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages from admin"""
    message = update.message
    
    # If not a reply, ignore (admin should reply to forwarded messages)
    if not message.reply_to_message:
        return
    
    replied_msg_id = message.reply_to_message.message_id
    message_map = context.bot_data.get("message_map", {})
    
    # Check if this is a reply to a forwarded message
    if replied_msg_id not in message_map:
        return
    
    # Get the original sender's info
    user_id = message_map[replied_msg_id]["user_id"]
    
    try:
        # Forward different types of content back to the user
        if message.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"💬 *Reply from admin:*\n\n{message.text}",
                parse_mode="Markdown"
            )
        elif message.photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=message.photo[-1].file_id,
                caption=f"💬 Reply from admin:\n\n{message.caption or ''}"
            )
        elif message.video:
            await context.bot.send_video(
                chat_id=user_id,
                video=message.video.file_id,
                caption=f"💬 Reply from admin:\n\n{message.caption or ''}"
            )
        elif message.document:
            await context.bot.send_document(
                chat_id=user_id,
                document=message.document.file_id,
                caption=f"💬 Reply from admin:\n\n{message.caption or ''}"
            )
        elif message.audio:
            await context.bot.send_audio(
                chat_id=user_id,
                audio=message.audio.file_id,
                caption=f"💬 Reply from admin:\n\n{message.caption or ''}"
            )
        elif message.voice:
            await context.bot.send_voice(
                chat_id=user_id,
                voice=message.voice.file_id,
                caption="💬 Reply from admin:"
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="💬 Admin has responded but the message type is not supported."
            )
        
        # Confirm to admin that the message was sent
        await message.reply_text("✅ Your reply has been sent to the user.")
        
    except Exception as e:
        logger.error(f"Error sending admin reply: {e}")
        await message.reply_text(f"❌ Error sending reply: {str(e)}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    
    # Always acknowledge the callback query to stop the loading animation
    await query.answer()
    
    if query.data == "request_mod":
        # Template for mod request
        mod_template = (
            "📱 *MOD REQUEST TEMPLATE*\n\n"
            "Please fill out the following details:\n\n"
            "Game Name: \n"
            "Game Version: \n"
            "Device/Platform: \n"
            "Features Needed: \n"
            "- \n"
            "- \n"
            "Additional Info: "
        )
        await query.message.reply_text(mod_template, parse_mode="Markdown")
        
    elif query.data == "report_issue":
        # Template for issue reporting
        issue_template = (
            "⚠️ *ISSUE REPORT TEMPLATE*\n\n"
            "Please provide the following information:\n\n"
            "Mod Name: \n"
            "Game Version: \n"
            "Device/Platform: \n"
            "Issue Description: \n\n"
            "Steps to Reproduce: \n"
            "1. \n"
            "2. \n"
            "3. "
        )
        await query.message.reply_text(issue_template, parse_mode="Markdown")

async def error_handler(update, context):
    """Log errors caused by Updates."""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("checksubscription", channel_subscription_check))

    # Add callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Add message handler (handles text messages not matching any command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add handlers for different media types
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | 
                                         filters.ATTACHMENT | filters.VOICE | 
                                         filters.VOICE, handle_message))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    print("Starting bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
