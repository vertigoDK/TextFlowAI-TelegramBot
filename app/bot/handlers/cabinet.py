from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from typing import Optional

from app.core.services.container import Container
from app.bot.keyboards import CabinetKeyboards


router = Router()


class CabinetMessages:
    """Cabinet interface messages"""
    
    @staticmethod
    def welcome_message(user_name: str) -> str:
        return (
            f"🏠 <b>Personal Cabinet</b>\n\n"
            f"Welcome, {user_name}! 👋\n\n"
            f"Here you can manage your account, view statistics, "
            f"and access your message history.\n\n"
            f"Choose an option below:"
        )
    
    @staticmethod
    def profile_info_message(profile_data: dict) -> str:
        return (
            f"👤 <b>Profile Information</b>\n\n"
            f"📛 <b>Name:</b> {profile_data['full_name']}\n"
            f"🏷️ <b>Username:</b> {profile_data['username']}\n"
            f"🆔 <b>Telegram ID:</b> <code>{profile_data['telegram_id']}</code>\n"
            f"📅 <b>Member since:</b> {profile_data['member_since']}\n"
            f"📊 <b>Account status:</b> {profile_data['account_status']}\n"
        )
    
    @staticmethod
    def daily_usage_message(stats: dict) -> str:
        return (
            f"📊 <b>Daily Usage Statistics</b>\n\n"
            f"🔢 <b>Requests used today:</b> {stats['requests_used']}/{stats['daily_limit']}\n"
            f"⚡ <b>Remaining requests:</b> {stats['remaining_requests']}\n"
            f"📈 <b>Usage percentage:</b> {stats['usage_percentage']}\n"
            f"🚦 <b>Status:</b> {stats['limit_status']}\n\n"
            f"💡 <i>Your daily limit resets at midnight UTC</i>"
        )
    
    @staticmethod
    def weekly_stats_message(stats: dict) -> str:
        return (
            f"📅 <b>Weekly Statistics</b>\n\n"
            f"💬 <b>Total messages:</b> {stats['total_messages']}\n"
            f"👤 <b>Your requests:</b> {stats['user_requests']}\n"
            f"🤖 <b>AI responses:</b> {stats['ai_responses']}\n"
            f"📊 <b>Daily average:</b> {stats['daily_average']} requests\n"
            f"⏰ <b>Period:</b> {stats['period']}\n"
        )
    
    @staticmethod
    def all_time_stats_message(stats: dict) -> str:
        return (
            f"📈 <b>All-Time Statistics</b>\n\n"
            f"💬 <b>Total messages:</b> {stats['total_messages']}\n"
            f"👤 <b>Your requests:</b> {stats['user_requests']}\n"
            f"🤖 <b>AI responses:</b> {stats['ai_responses']}\n"
            f"📅 <b>Days registered:</b> {stats['days_registered']}\n"
            f"📊 <b>Average daily:</b> {stats['avg_daily_requests']} requests\n"
            f"🏆 <b>Most active:</b> {stats['most_active_day']}\n"
        )
    
    @staticmethod
    def message_history_menu() -> str:
        return (
            f"💬 <b>Message History</b>\n\n"
            f"Here you can view, search, export, or clear your message history.\n\n"
            f"Choose an option:"
        )
    
    @staticmethod
    def recent_messages_header(total_count: int, page: int, per_page: int) -> str:
        start = (page - 1) * per_page + 1
        end = min(page * per_page, total_count)
        return (
            f"📝 <b>Recent Messages</b>\n"
            f"Showing {start}-{end} of {total_count} messages\n\n"
        )
    
    @staticmethod
    def format_message_item(msg: dict, index: int) -> str:
        return (
            f"<b>{index}.</b> {msg['role']}\n"
            f"⏰ {msg['timestamp']}\n"
            f"💬 <i>{msg['content']}</i>\n"
        )
    
    @staticmethod
    def settings_menu_message() -> str:
        return (
            f"⚙️ <b>Settings & Information</b>\n\n"
            f"View your account settings and system information.\n\n"
            f"Choose an option:"
        )
    
    @staticmethod
    def account_info_message(settings: dict) -> str:
        return (
            f"ℹ️ <b>Account Information</b>\n\n"
            f"🔢 <b>Daily limit:</b> {settings['daily_limit']} requests\n"
            f"📊 <b>Current usage:</b> {settings['current_usage']}\n"
            f"👤 <b>Account type:</b> {settings['account_type']}\n"
            f"💾 <b>Data retention:</b> {settings['data_retention']}\n"
            f"🔄 <b>Limit reset:</b> {settings['last_reset']}\n"
            f"🆔 <b>Account ID:</b> <code>{settings['account_id']}</code>\n"
        )
    
    @staticmethod
    def usage_patterns_message(patterns: dict) -> str:
        return (
            f"📊 <b>Usage Patterns</b>\n\n"
            f"📈 <b>Today's requests:</b> {patterns['today_requests']}\n"
            f"📊 <b>Yesterday's requests:</b> {patterns['yesterday_requests']}\n"
            f"🔄 <b>Trend:</b> {patterns['trend']}\n"
            f"⏰ <b>Peak usage:</b> {patterns['peak_usage']}\n"
            f"🕐 <b>Preferred time:</b> {patterns['preferred_time']}\n"
            f"👤 <b>User type:</b> {patterns['consistency']}\n"
        )
    
    @staticmethod
    def export_confirmation() -> str:
        return (
            f"📤 <b>Export Message History</b>\n\n"
            f"This will generate a text file with your complete message history.\n\n"
            f"⚠️ <i>Large histories may take a moment to process.</i>\n\n"
            f"Continue with export?"
        )
    
    @staticmethod
    def clear_confirmation() -> str:
        return (
            f"🗑️ <b>Clear Message History</b>\n\n"
            f"⚠️ <b>Warning:</b> This action cannot be undone!\n\n"
            f"All your messages and conversation history will be permanently deleted.\n\n"
            f"Are you sure you want to continue?"
        )
    
    @staticmethod
    def export_success() -> str:
        return (
            f"✅ <b>Export Completed</b>\n\n"
            f"Your message history has been exported successfully!\n"
            f"The file is attached above. 📎\n\n"
            f"💡 <i>You can save this file for your records.</i>"
        )
    
    @staticmethod
    def clear_success(deleted_count: int) -> str:
        return (
            f"✅ <b>History Cleared</b>\n\n"
            f"Successfully deleted {deleted_count} messages from your history.\n\n"
            f"🔄 <i>You can start fresh conversations now!</i>"
        )
    
    @staticmethod
    def error_message() -> str:
        return (
            f"❌ <b>Error</b>\n\n"
            f"Something went wrong while processing your request.\n"
            f"Please try again later."
        )
    
    @staticmethod
    def cabinet_closed() -> str:
        return (
            f"👋 <b>Cabinet Closed</b>\n\n"
            f"Thank you for using the personal cabinet!\n"
            f"Type /cabinet to open it again anytime."
        )


@router.message(Command("cabinet"))
async def open_cabinet(message: Message):
    """Open personal cabinet"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        # Get user profile for welcome message
        profile_data = await cabinet_service.get_profile_info(message.from_user.id)
        welcome_text = CabinetMessages.welcome_message(profile_data['full_name'])
        
        await message.answer(
            welcome_text,
            reply_markup=CabinetKeyboards.main_menu(),
            parse_mode="HTML"
        )
    except Exception:
        await message.answer(
            CabinetMessages.error_message(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "cabinet_main")
async def cabinet_main_menu(callback: CallbackQuery):
    """Show main cabinet menu"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        profile_data = await cabinet_service.get_profile_info(callback.from_user.id)
        welcome_text = CabinetMessages.welcome_message(profile_data['full_name'])
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=CabinetKeyboards.main_menu(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading cabinet", show_alert=True)


@router.callback_query(F.data == "cabinet_profile")
async def show_profile_info(callback: CallbackQuery):
    """Show user profile information"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        profile_data = await cabinet_service.get_profile_info(callback.from_user.id)
        profile_text = CabinetMessages.profile_info_message(profile_data)
        
        await callback.message.edit_text(
            profile_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading profile", show_alert=True)


@router.callback_query(F.data == "cabinet_stats")
async def show_stats_menu(callback: CallbackQuery):
    """Show statistics menu"""
    stats_text = (
        f"📊 <b>Usage Statistics</b>\n\n"
        f"Choose the type of statistics you'd like to view:"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=CabinetKeyboards.stats_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "stats_daily")
async def show_daily_stats(callback: CallbackQuery):
    """Show daily usage statistics"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        stats = await cabinet_service.get_daily_usage_stats(callback.from_user.id)
        stats_text = CabinetMessages.daily_usage_message(stats)
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading statistics", show_alert=True)


@router.callback_query(F.data == "stats_weekly")
async def show_weekly_stats(callback: CallbackQuery):
    """Show weekly usage statistics"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        stats = await cabinet_service.get_weekly_stats(callback.from_user.id)
        stats_text = CabinetMessages.weekly_stats_message(stats)
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading statistics", show_alert=True)


@router.callback_query(F.data == "stats_all_time")
async def show_all_time_stats(callback: CallbackQuery):
    """Show all-time usage statistics"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        stats = await cabinet_service.get_all_time_stats(callback.from_user.id)
        stats_text = CabinetMessages.all_time_stats_message(stats)
        
        await callback.message.edit_text(
            stats_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading statistics", show_alert=True)


@router.callback_query(F.data == "cabinet_history")
async def show_history_menu(callback: CallbackQuery):
    """Show message history menu"""
    history_text = CabinetMessages.message_history_menu()
    
    await callback.message.edit_text(
        history_text,
        reply_markup=CabinetKeyboards.history_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "history_recent")
async def show_recent_messages(callback: CallbackQuery):
    """Show recent messages with pagination"""
    await show_messages_page(callback, page=1)


@router.callback_query(F.data.startswith("history_recent_page_"))
async def show_messages_page_handler(callback: CallbackQuery):
    """Handle message history pagination"""
    page = int(callback.data.split("_")[-1])
    await show_messages_page(callback, page)


async def show_messages_page(callback: CallbackQuery, page: int):
    """Show messages page with pagination"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        per_page = 5
        offset = (page - 1) * per_page
        
        # Get messages and total count
        messages = await cabinet_service.get_recent_messages(
            callback.from_user.id, 
            limit=per_page, 
            offset=offset
        )
        total_count = await cabinet_service.get_message_history_count(callback.from_user.id)
        total_pages = (total_count + per_page - 1) // per_page
        
        if not messages:
            no_messages_text = (
                f"📝 <b>Message History</b>\n\n"
                f"No messages found.\n"
                f"Start a conversation to see your history here!"
            )
            await callback.message.edit_text(
                no_messages_text,
                reply_markup=CabinetKeyboards.back_to_main(),
                parse_mode="HTML"
            )
            await callback.answer()
            return
        
        # Build message text
        header = CabinetMessages.recent_messages_header(total_count, page, per_page)
        message_text = header
        
        for i, msg in enumerate(messages, 1):
            message_text += CabinetMessages.format_message_item(msg, offset + i)
            message_text += "\n"
        
        # Show with pagination keyboard
        keyboard = CabinetKeyboards.pagination_keyboard(
            page, total_pages, "history_recent"
        )
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        
    except Exception:
        await callback.answer("Error loading messages", show_alert=True)


@router.callback_query(F.data == "history_export")
async def confirm_export(callback: CallbackQuery):
    """Confirm message history export"""
    export_text = CabinetMessages.export_confirmation()
    
    await callback.message.edit_text(
        export_text,
        reply_markup=CabinetKeyboards.confirmation_keyboard("export"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_export")
async def export_history(callback: CallbackQuery):
    """Export message history"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        # Export history
        export_text = await cabinet_service.export_message_history(callback.from_user.id)
        
        # Send as document
        from io import BytesIO
        file_content = BytesIO(export_text.encode('utf-8'))
        file_content.name = f"message_history_{callback.from_user.id}.txt"
        
        await callback.message.answer_document(
            document=file_content,
            caption=CabinetMessages.export_success(),
            parse_mode="HTML"
        )
        
        # Return to main menu
        profile_data = await cabinet_service.get_profile_info(callback.from_user.id)
        welcome_text = CabinetMessages.welcome_message(profile_data['full_name'])
        
        await callback.message.edit_text(
            welcome_text,
            reply_markup=CabinetKeyboards.main_menu(),
            parse_mode="HTML"
        )
        await callback.answer("History exported successfully!")
        
    except Exception:
        await callback.answer("Error exporting history", show_alert=True)


@router.callback_query(F.data == "history_clear")
async def confirm_clear(callback: CallbackQuery):
    """Confirm message history clearing"""
    clear_text = CabinetMessages.clear_confirmation()
    
    await callback.message.edit_text(
        clear_text,
        reply_markup=CabinetKeyboards.confirmation_keyboard("clear"),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear")
async def clear_history(callback: CallbackQuery):
    """Clear message history"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        # Get count before clearing
        total_count = await cabinet_service.get_message_history_count(callback.from_user.id)
        
        # Clear history
        success = await cabinet_service.clear_message_history(callback.from_user.id)
        
        if success:
            success_text = CabinetMessages.clear_success(total_count)
            
            await callback.message.edit_text(
                success_text,
                reply_markup=CabinetKeyboards.back_to_main(),
                parse_mode="HTML"
            )
            await callback.answer("History cleared successfully!")
        else:
            await callback.answer("Error clearing history", show_alert=True)
            
    except Exception:
        await callback.answer("Error clearing history", show_alert=True)


@router.callback_query(F.data == "cabinet_settings")
async def show_settings_menu(callback: CallbackQuery):
    """Show settings menu"""
    settings_text = CabinetMessages.settings_menu_message()
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=CabinetKeyboards.settings_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_account")
async def show_account_info(callback: CallbackQuery):
    """Show account information"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        settings = await cabinet_service.get_account_settings(callback.from_user.id)
        account_text = CabinetMessages.account_info_message(settings)
        
        await callback.message.edit_text(
            account_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading account info", show_alert=True)


@router.callback_query(F.data == "settings_limits")
async def show_limits_info(callback: CallbackQuery):
    """Show limits information (redirect to daily stats)"""
    await show_daily_stats(callback)


@router.callback_query(F.data == "settings_patterns")
async def show_usage_patterns(callback: CallbackQuery):
    """Show usage patterns"""
    container = Container()
    cabinet_service = container.get_cabinet_service()
    
    try:
        patterns = await cabinet_service.get_usage_patterns(callback.from_user.id)
        patterns_text = CabinetMessages.usage_patterns_message(patterns)
        
        await callback.message.edit_text(
            patterns_text,
            reply_markup=CabinetKeyboards.back_to_main(),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception:
        await callback.answer("Error loading usage patterns", show_alert=True)


@router.callback_query(F.data == "cabinet_close")
async def close_cabinet(callback: CallbackQuery):
    """Close cabinet"""
    close_text = CabinetMessages.cabinet_closed()
    
    await callback.message.edit_text(
        close_text,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "page_info")
async def page_info_handler(callback: CallbackQuery):
    """Handle page info button (do nothing)"""
    await callback.answer()