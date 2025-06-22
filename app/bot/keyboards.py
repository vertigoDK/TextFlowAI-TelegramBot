from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CabinetKeyboards:
    """Keyboards for personal cabinet navigation"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main cabinet menu keyboard"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="👤 Profile Info",
                callback_data="cabinet_profile"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="📊 Usage Statistics", 
                callback_data="cabinet_stats"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="💬 Message History",
                callback_data="cabinet_history"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="⚙️ Settings",
                callback_data="cabinet_settings"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        builder.adjust(2, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Back to main menu button"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="🔙 Back to Menu",
                callback_data="cabinet_main"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        builder.adjust(1, 1)
        return builder.as_markup()
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Statistics submenu keyboard"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="📈 Daily Usage",
                callback_data="stats_daily"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="📅 Weekly Stats",
                callback_data="stats_weekly"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="📊 All Time Stats",
                callback_data="stats_all_time"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🔙 Back to Menu",
                callback_data="cabinet_main"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        builder.adjust(2, 1, 1, 1)
        return builder.as_markup()
    
    @staticmethod
    def history_menu() -> InlineKeyboardMarkup:
        """Message history submenu keyboard"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="📝 Recent Messages",
                callback_data="history_recent"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🔍 Search History",
                callback_data="history_search"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="📤 Export History",
                callback_data="history_export"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🗑️ Clear History",
                callback_data="history_clear"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🔙 Back to Menu",
                callback_data="cabinet_main"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        builder.adjust(2, 2, 1, 1)
        return builder.as_markup()
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings submenu keyboard"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="ℹ️ Account Info",
                callback_data="settings_account"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🔢 Limits Info",
                callback_data="settings_limits"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="📊 Usage Patterns",
                callback_data="settings_patterns"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="🔙 Back to Menu",
                callback_data="cabinet_main"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        builder.adjust(2, 1, 1, 1)
        return builder.as_markup()
    
    @staticmethod
    def confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
        """Confirmation keyboard for destructive actions"""
        builder = InlineKeyboardBuilder()
        
        builder.add(
            InlineKeyboardButton(
                text="✅ Yes, Continue",
                callback_data=f"confirm_{action}"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cabinet_main"
            )
        )
        
        builder.adjust(1, 1)
        return builder.as_markup()
    
    @staticmethod
    def pagination_keyboard(
        current_page: int,
        total_pages: int,
        callback_prefix: str
    ) -> InlineKeyboardMarkup:
        """Pagination keyboard for lists"""
        builder = InlineKeyboardBuilder()
        
        if current_page > 1:
            builder.add(
                InlineKeyboardButton(
                    text="⬅️ Previous",
                    callback_data=f"{callback_prefix}_page_{current_page - 1}"
                )
            )
        
        builder.add(
            InlineKeyboardButton(
                text=f"📄 {current_page}/{total_pages}",
                callback_data="page_info"
            )
        )
        
        if current_page < total_pages:
            builder.add(
                InlineKeyboardButton(
                    text="➡️ Next",
                    callback_data=f"{callback_prefix}_page_{current_page + 1}"
                )
            )
        
        builder.add(
            InlineKeyboardButton(
                text="🔙 Back to Menu",
                callback_data="cabinet_main"
            )
        )
        builder.add(
            InlineKeyboardButton(
                text="❌ Close Cabinet",
                callback_data="cabinet_close"
            )
        )
        
        # Adjust layout based on number of pagination buttons
        if current_page == 1:
            builder.adjust(2, 1, 1)  # No previous button
        elif current_page == total_pages:
            builder.adjust(2, 1, 1)  # No next button
        else:
            builder.adjust(3, 1, 1)  # All buttons
            
        return builder.as_markup()