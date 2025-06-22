from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    """Handle /start command"""
    welcome_text = (
        f"🤖 <b>Welcome to TextFlow AI Bot!</b>\n\n"
        f"Hello, {message.from_user.first_name}! 👋\n\n"
        f"I'm your AI assistant powered by Google Gemini. I can help you with:\n"
        f"• 💬 Answering questions\n"
        f"• 📝 Writing and editing text\n"
        f"• 🔍 Research and analysis\n"
        f"• 💡 Creative tasks\n"
        f"• 🧮 Problem solving\n\n"
        f"<b>Available commands:</b>\n"
        f"• /cabinet - 🏠 Open your personal cabinet\n"
        f"• /help - ❓ Get help information\n\n"
        f"Just send me any message to start chatting! 🚀\n\n"
        f"<i>You have {20} free requests per day.</i>"
    )
    
    await message.answer(welcome_text, parse_mode="HTML")


@router.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    help_text = (
        f"❓ <b>Help & Information</b>\n\n"
        f"<b>How to use the bot:</b>\n"
        f"1. Simply send any text message\n"
        f"2. I'll respond with AI-generated answers\n"
        f"3. Continue the conversation naturally\n\n"
        f"<b>Available commands:</b>\n"
        f"• /start - 🏠 Welcome message\n"
        f"• /cabinet - 📊 Personal cabinet with stats\n"
        f"• /help - ❓ This help message\n\n"
        f"<b>Features:</b>\n"
        f"• 📈 Usage statistics\n"
        f"• 💬 Message history\n"
        f"• 📤 Export conversations\n"
        f"• ⚙️ Account settings\n\n"
        f"<b>Limits:</b>\n"
        f"• 20 requests per day (resets at midnight UTC)\n"
        f"• Message length: up to 1000 characters\n\n"
        f"Need more help? Use /cabinet to check your stats!"
    )
    
    await message.answer(help_text, parse_mode="HTML")
