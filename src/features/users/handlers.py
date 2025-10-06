"""
User management handlers
Feature-based architecture
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from telegram.constants import ParseMode
from datetime import datetime, timedelta, timezone
import asyncio

from src.core.logger import log
from src.core.config import settings
from src.middleware.auth import admin_only
from src.services.api import api_client, RemnaWaveAPIError

from . import keyboards as user_kb
from . import formatters as user_fmt

# Conversation states для редактирования пользователя
EDIT_CHOOSING, EDIT_TRAFFIC_LIMIT, EDIT_EXPIRE_DATE, EDIT_STATUS = range(4)

# Conversation states для создания пользователя
CREATE_USERNAME, CREATE_TRAFFIC_LIMIT, CREATE_EXPIRE_DAYS, CREATE_CONFIRM = range(4, 8)

# Conversation states для поиска
SEARCH_INPUT = 8

# Conversation states для массового создания с пресетами
BULK_COUNT, BULK_DURATION, BULK_TRAFFIC, BULK_RESET, BULK_CONFIRM = range(9, 14)


@admin_only
async def users_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users management menu"""
    query = update.callback_query
    await query.answer()
    
    text = """
👥 <b>Управление пользователями</b>

Выберите действие:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=user_kb.users_menu(),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def users_list_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users list with interactive buttons"""
    query = update.callback_query
    await query.answer()
    
    # Extract page from callback data
    page = 1
    if ":" in query.data:
        try:
            page = int(query.data.split(":")[1])
        except (IndexError, ValueError):
            page = 1
    
    try:
        await query.edit_message_text(
            "⏳ Загрузка списка пользователей...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch users
        response = await api_client.get_users(page=page, limit=10)
        data = response.get('response', {})
        users = data.get('users', [])
        total = data.get('total', 0)
        total_pages = (total + 9) // 10
        
        if not users:
            text = "👥 <b>Список пользователей</b>\n\nПользователи не найдены"
            keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")]]
        else:
            text = f"👥 <b>Список пользователей</b> (стр. {page}/{total_pages})\n"
            text += f"<i>Всего: {total} пользователей</i>\n\n"
            text += "Выберите пользователя для управления:"
            
            # Build keyboard with user buttons
            keyboard = []
            for user in users:
                username = user.get('username', 'N/A')
                status = user.get('status', 'unknown').upper()
                uuid = user.get('uuid', '')
                used_traffic = user_fmt.format_bytes(user.get('usedTrafficBytes', 0))
                
                status_emoji = {
                    'ACTIVE': '✅',
                    'DISABLED': '🚫',
                    'LIMITED': '⚠️',
                    'EXPIRED': '⏱️'
                }.get(status, '❓')
                
                button_text = f"{status_emoji} {username} | {used_traffic}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"user_view:{uuid}")])
            
            # Add pagination if needed
            if total_pages > 1:
                pagination_buttons = user_kb.pagination(page, total_pages, "users_page")
                keyboard.append(pagination_buttons)
            
            # Add back button
            keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching users: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при получении списка:</b>\n{str(e)}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in users list")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_view_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed user information"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Загрузка информации...",
            parse_mode=ParseMode.HTML
        )
        
        # Fetch user details
        response = await api_client.get_user(user_uuid)
        user = response.get('response', {})
        
        if not user:
            await query.edit_message_text(
                "❌ Пользователь не найден",
                reply_markup=user_kb.users_menu(),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Get HWID count
        hwid_count = 0
        try:
            hwid_response = await api_client.get_user_devices(user_uuid)
            response_data = hwid_response.get('response', {})
            # API возвращает {'total': N, 'devices': [...]}
            hwid_count = response_data.get('total', 0)
        except Exception as e:
            log.warning(f"Failed to get HWID count: {e}")
        
        # Format user info
        text = user_fmt.format_user_full(user, hwid_count=hwid_count)
        
        await query.edit_message_text(
            text,
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching user: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in user view")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_extend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show subscription extension presets"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    text = """
📅 <b>Продление подписки</b>

Выберите период продления:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=user_kb.extend_presets(user_uuid),
        parse_mode=ParseMode.HTML
    )


@admin_only
async def extend_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute subscription extension"""
    query = update.callback_query
    await query.answer()
    
    try:
        parts = query.data.split(":")
        user_uuid = parts[1]
        days = int(parts[2])
        
        await query.edit_message_text(
            f"⏳ Продление подписки на {days} дней...",
            parse_mode=ParseMode.HTML
        )
        
        result = await api_client.extend_user_subscription(user_uuid, days)
        
        await query.edit_message_text(
            f"✅ <b>Подписка успешно продлена на {days} дней!</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error extending subscription: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка при продлении:</b>\n{str(e)}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in extend user")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )


@admin_only
# OLD PIN-BASED DELETE HANDLERS - REPLACED WITH SMART DELETE IN delete_handlers.py
# user_delete_confirm_callback, user_delete_pin_callback, handle_delete_pin - removed


@admin_only
async def user_reset_traffic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset user traffic"""
    query = update.callback_query
    await query.answer()
    
    try:
        user_uuid = query.data.split(":")[1]
        
        await query.edit_message_text(
            "⏳ Сброс трафика...",
            parse_mode=ParseMode.HTML
        )
        
        await api_client.reset_user_traffic(user_uuid)
        
        await query.edit_message_text(
            "✅ <b>Трафик успешно сброшен!</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error resetting traffic: {e}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b>\n{str(e)}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error in reset traffic")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed user statistics"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    try:
        # Получаем полную информацию о пользователе
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        
        username = user.get('username', 'N/A')
        status = user.get('status', 'unknown').upper()
        
        # Трафик
        used_bytes = user.get('usedTrafficBytes', 0)
        limit_bytes = user.get('trafficLimitBytes', 0)
        used_traffic = user_fmt.format_bytes(used_bytes)
        limit_traffic = user_fmt.format_bytes(limit_bytes) if limit_bytes > 0 else "Не ограничен"
        
        # Процент использования трафика
        if limit_bytes > 0:
            usage_percent = (used_bytes / limit_bytes * 100)
            progress_bar = user_fmt.progress_bar(usage_percent, width=10)
            traffic_info = f"{used_traffic} / {limit_traffic}\n   {progress_bar} {usage_percent:.1f}%"
        else:
            traffic_info = f"{used_traffic} / Безлимит"
        
        # Даты
        created_at = user.get('createdAt')
        expire_at = user.get('expireAt')
        
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_str = created_dt.strftime('%d.%m.%Y %H:%M')
            except:
                created_str = 'N/A'
        else:
            created_str = 'N/A'
        
        if expire_at:
            try:
                expire_dt = datetime.fromisoformat(expire_at.replace('Z', '+00:00'))
                expire_str = expire_dt.strftime('%d.%m.%Y %H:%M')
                
                # Вычисляем оставшееся время
                now = datetime.now(timezone.utc)
                if expire_dt.tzinfo is None:
                    expire_dt = expire_dt.replace(tzinfo=timezone.utc)
                    
                if expire_dt > now:
                    time_left = expire_dt - now
                    days_left = time_left.days
                    hours_left = time_left.seconds // 3600
                    expire_info = f"{expire_str}\n   ⏱️ Осталось: {days_left} дн. {hours_left} ч."
                else:
                    expire_info = f"{expire_str}\n   ⚠️ <b>Истёк</b>"
            except:
                expire_info = 'N/A'
        else:
            expire_info = 'Не установлена'
        
        # Онлайн статус
        online = user.get('online', False)
        online_emoji = "🟢" if online else "⚫"
        online_status = "Онлайн" if online else "Оффлайн"
        
        # Количество устройств
        try:
            devices_response = await api_client.get_user_devices(user_uuid)
            devices_count = len(devices_response.get('response', []))
        except:
            devices_count = 0
        
        text = f"""
📊 <b>Детальная статистика</b>

👤 <b>Пользователь:</b> {username}
🔑 <b>UUID:</b> <code>{user_uuid}</code>

<b>📈 Статус и активность:</b>
   Статус: {user_fmt.status_badge(status)} {status}
   Подключение: {online_emoji} {online_status}
   Устройств: 📱 {devices_count}

<b>📊 Использование трафика:</b>
   {traffic_info}

<b>📅 Временные рамки:</b>
   Создан: {created_str}
   Истекает: {expire_info}

<b>💾 Дополнительная информация:</b>
   ID подписки: <code>{user.get('subscriptionId', 'N/A')}</code>
   Тип трафика: {user.get('trafficLimitStrategy', 'N/A')}
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching user stats: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error fetching user stats")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка при загрузке статистики</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_devices_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user devices with HWID information"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    try:
        # Получаем информацию о пользователе
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        username = user.get('username', 'N/A')
        
        # Получаем устройства пользователя
        devices_response = await api_client.get_user_devices(user_uuid)
        response_data = devices_response.get('response', {})
        # API возвращает {'total': N, 'devices': [...]}
        devices = response_data.get('devices', [])
        total_devices = response_data.get('total', 0)
        
        text = f"📱 <b>Устройства пользователя</b>\n"
        text += f"👤 <b>Пользователь:</b> {username}\n"
        text += f"🔑 <b>UUID:</b> <code>{user_uuid}</code>\n\n"
        
        if not devices or total_devices == 0:
            text += "❌ <b>У пользователя нет зарегистрированных устройств</b>\n\n"
            text += "<i>Устройства появятся после первого подключения к VPN</i>"
        else:
            text += f"<b>Всего устройств:</b> {len(devices)}\n\n"
            
            for idx, device in enumerate(devices, 1):
                hwid = device.get('hwid', 'N/A')
                device_uuid = device.get('uuid', 'N/A')
                created_at = device.get('createdAt')
                
                # Форматируем дату создания
                if created_at:
                    try:
                        created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_str = created_dt.strftime('%d.%m.%Y %H:%M')
                    except:
                        created_str = 'N/A'
                else:
                    created_str = 'N/A'
                
                text += f"<b>🔹 Устройство #{idx}</b>\n"
                text += f"   HWID: <code>{hwid[:32]}...</code>\n"
                text += f"   UUID: <code>{device_uuid}</code>\n"
                text += f"   Добавлено: {created_str}\n\n"
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=total_devices > 0),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching devices: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error fetching devices")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка при загрузке устройств</b>",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_clear_devices_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm clearing all user devices"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    try:
        # Получаем информацию о пользователе и устройствах
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        username = user.get('username', 'N/A')
        
        devices_response = await api_client.get_user_devices(user_uuid)
        response_data = devices_response.get('response', {})
        total_devices = response_data.get('total', 0)
        
        if total_devices == 0:
            await query.edit_message_text(
                "❌ <b>У пользователя нет устройств для удаления</b>",
                reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
                parse_mode=ParseMode.HTML
            )
            return
        
        text = f"""
⚠️ <b>Подтверждение очистки устройств</b>

👤 <b>Пользователь:</b> {username}
📱 <b>Устройств:</b> {total_devices}

<b>Вы уверены, что хотите удалить все зарегистрированные устройства?</b>

<i>Это действие нельзя отменить!</i>
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.clear_devices_confirmation(user_uuid, total_devices),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error confirming device clearing: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error confirming device clearing")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_clear_devices_execute_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute clearing all user devices"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    try:
        # Получаем список устройств
        devices_response = await api_client.get_user_devices(user_uuid)
        response_data = devices_response.get('response', {})
        devices = response_data.get('devices', [])
        total_devices = response_data.get('total', 0)
        
        if not devices or total_devices == 0:
            await query.edit_message_text(
                "❌ <b>У пользователя нет устройств для удаления</b>",
                reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Показываем прогресс
        progress_text = f"🔄 <b>Удаление устройств...</b>\n\nУдалено: 0 / {total_devices}"
        await query.edit_message_text(
            progress_text,
            parse_mode=ParseMode.HTML
        )
        
        # Удаляем каждое устройство
        deleted_count = 0
        failed_count = 0
        
        for idx, device in enumerate(devices, 1):
            hwid = device.get('hwid')
            if hwid:
                try:
                    await api_client.delete_device(user_uuid, hwid)
                    deleted_count += 1
                    
                    # Обновляем прогресс каждые 3 устройства или на последнем
                    if idx % 3 == 0 or idx == total_devices:
                        progress_text = f"🔄 <b>Удаление устройств...</b>\n\nУдалено: {deleted_count} / {total_devices}"
                        if failed_count > 0:
                            progress_text += f"\n❌ Ошибок: {failed_count}"
                        await query.edit_message_text(
                            progress_text,
                            parse_mode=ParseMode.HTML
                        )
                    
                    # Небольшая задержка между запросами
                    await asyncio.sleep(0.1)
                except Exception as e:
                    log.error(f"Failed to delete device {hwid}: {e}")
                    failed_count += 1
        
        # Финальное сообщение
        result_text = f"""
✅ <b>Очистка устройств завершена!</b>

📊 <b>Результаты:</b>
├ Успешно удалено: {deleted_count}
└ Ошибок: {failed_count}

<b>Всего обработано:</b> {total_devices}
        """
        
        await query.edit_message_text(
            result_text.strip(),
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )
        
    except RemnaWaveAPIError as e:
        log.error(f"Error clearing devices: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.exception("Unexpected error clearing devices")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка при удалении устройств</b>",
            reply_markup=user_kb.user_devices_actions(user_uuid, has_devices=False),
            parse_mode=ParseMode.HTML
        )


@admin_only
async def user_edit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user editing conversation"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    
    # Сохраняем UUID пользователя в context
    context.user_data['editing_user_uuid'] = user_uuid
    
    # Получаем текущие данные пользователя
    try:
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        context.user_data['current_user_data'] = user
        
        # Форматируем текущие данные
        username = user.get('username', 'N/A')
        traffic_limit = user.get('trafficLimitBytes', 0)
        traffic_limit_gb = traffic_limit / (1024**3) if traffic_limit else 0
        status = user.get('status', 'N/A')
        expire = user.get('expireAt', 'N/A')
        
        # Клавиатура с опциями редактирования
        keyboard = [
            [InlineKeyboardButton("📊 Лимит трафика", callback_data=f"edit_traffic:{user_uuid}")],
            [InlineKeyboardButton("📅 Дата истечения", callback_data=f"edit_expire:{user_uuid}")],
            [InlineKeyboardButton("🔄 Статус", callback_data=f"edit_status:{user_uuid}")],
            [InlineKeyboardButton("« Назад", callback_data=f"user_view:{user_uuid}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
✏️ <b>Редактирование пользователя</b>

👤 <b>Пользователь:</b> {username}
📊 <b>Текущий лимит:</b> {traffic_limit_gb:.2f} GB
📅 <b>Истекает:</b> {expire}
🔄 <b>Статус:</b> {status}

Выберите, что хотите изменить:
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return EDIT_CHOOSING
        
    except RemnaWaveAPIError as e:
        log.error(f"Error fetching user for editing: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error starting user edit")
        await query.edit_message_text(
            "❌ <b>Произошла неожиданная ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def edit_traffic_limit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for new traffic limit"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    user = context.user_data.get('current_user_data', {})
    username = user.get('username', 'N/A')
    current_limit = user.get('trafficLimitBytes', 0) / (1024**3)
    
    text = f"""
📊 <b>Изменение лимита трафика</b>

👤 <b>Пользователь:</b> {username}
📊 <b>Текущий лимит:</b> {current_limit:.2f} GB

Введите новый лимит трафика в GB:
(0 = безлимитный)
    """
    
    keyboard = [[InlineKeyboardButton("« Отмена", callback_data=f"user_edit:{user_uuid}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    
    return EDIT_TRAFFIC_LIMIT


@admin_only
async def edit_traffic_limit_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process new traffic limit"""
    user_uuid = context.user_data.get('editing_user_uuid')
    
    try:
        # Парсим введённое значение
        traffic_gb = float(update.message.text.strip())
        if traffic_gb < 0:
            await update.message.reply_text(
                "❌ Лимит не может быть отрицательным. Попробуйте снова:",
                parse_mode=ParseMode.HTML
            )
            return EDIT_TRAFFIC_LIMIT
        
        # Конвертируем в байты
        traffic_bytes = int(traffic_gb * (1024**3)) if traffic_gb > 0 else 0
        
        # Обновляем пользователя
        update_data = {
            "trafficLimitBytes": traffic_bytes
        }
        await api_client.update_user(user_uuid, update_data)
        
        # Получаем обновлённые данные
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        
        text = f"""
✅ <b>Лимит трафика обновлён!</b>

👤 <b>Пользователь:</b> {user.get('username', 'N/A')}
📊 <b>Новый лимит:</b> {traffic_gb:.2f} GB
        """
        
        await update.message.reply_text(
            text.strip(),
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введите число (например: 100 или 0):",
            parse_mode=ParseMode.HTML
        )
        return EDIT_TRAFFIC_LIMIT
    except RemnaWaveAPIError as e:
        log.error(f"Error updating traffic limit: {e.message}")
        await update.message.reply_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error updating traffic limit")
        await update.message.reply_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def edit_expire_date_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for new expire date"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    user = context.user_data.get('current_user_data', {})
    username = user.get('username', 'N/A')
    
    # Кнопки с пресетами
    keyboard = [
        [InlineKeyboardButton("7 дней", callback_data=f"set_expire:7:{user_uuid}")],
        [InlineKeyboardButton("30 дней", callback_data=f"set_expire:30:{user_uuid}")],
        [InlineKeyboardButton("90 дней", callback_data=f"set_expire:90:{user_uuid}")],
        [InlineKeyboardButton("180 дней", callback_data=f"set_expire:180:{user_uuid}")],
        [InlineKeyboardButton("365 дней", callback_data=f"set_expire:365:{user_uuid}")],
        [InlineKeyboardButton("« Отмена", callback_data=f"user_edit:{user_uuid}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
📅 <b>Изменение даты истечения</b>

👤 <b>Пользователь:</b> {username}

Выберите срок или введите количество дней:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    
    return EDIT_EXPIRE_DATE


@admin_only
async def edit_expire_date_preset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set expire date from preset"""
    query = update.callback_query
    await query.answer()
    
    _, days_str, user_uuid = query.data.split(":")
    days = int(days_str)
    
    try:
        # Получаем текущего пользователя
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        
        # Вычисляем новую дату
        current_expire_str = user.get('expireAt')
        if current_expire_str:
            # Обработка строки даты (может быть в разных форматах)
            try:
                current_expire = datetime.fromisoformat(str(current_expire_str).replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                current_expire = datetime.now(timezone.utc)
        else:
            current_expire = datetime.now(timezone.utc)
        
        # Если срок уже истёк, начинаем с текущей даты
        if current_expire < datetime.now(timezone.utc):
            new_expire = datetime.now(timezone.utc) + timedelta(days=days)
        else:
            new_expire = current_expire + timedelta(days=days)
        
        # Обновляем пользователя
        update_data = {
            "expireAt": new_expire.isoformat()
        }
        await api_client.update_user(user_uuid, update_data)
        
        text = f"""
✅ <b>Дата истечения обновлена!</b>

👤 <b>Пользователь:</b> {user.get('username', 'N/A')}
📅 <b>Добавлено дней:</b> {days}
📅 <b>Новая дата истечения:</b> {new_expire.strftime('%Y-%m-%d %H:%M')}
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END
        
    except RemnaWaveAPIError as e:
        log.error(f"Error updating expire date: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error updating expire date")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def edit_status_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for new status"""
    query = update.callback_query
    await query.answer()
    
    user_uuid = query.data.split(":")[1]
    user = context.user_data.get('current_user_data', {})
    username = user.get('username', 'N/A')
    current_status = user.get('status', 'N/A')
    
    keyboard = [
        [InlineKeyboardButton("✅ ACTIVE", callback_data=f"set_status:ACTIVE:{user_uuid}")],
        [InlineKeyboardButton("❌ DISABLED", callback_data=f"set_status:DISABLED:{user_uuid}")],
        [InlineKeyboardButton("⏸️ LIMITED", callback_data=f"set_status:LIMITED:{user_uuid}")],
        [InlineKeyboardButton("⏰ EXPIRED", callback_data=f"set_status:EXPIRED:{user_uuid}")],
        [InlineKeyboardButton("« Отмена", callback_data=f"user_edit:{user_uuid}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"""
🔄 <b>Изменение статуса</b>

👤 <b>Пользователь:</b> {username}
🔄 <b>Текущий статус:</b> {current_status}

Выберите новый статус:
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )
    
    return EDIT_STATUS


@admin_only
async def edit_status_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process status change"""
    query = update.callback_query
    await query.answer()
    
    _, new_status, user_uuid = query.data.split(":")
    
    try:
        # Обновляем статус
        update_data = {
            "status": new_status
        }
        await api_client.update_user(user_uuid, update_data)
        
        # Получаем обновлённые данные
        user_response = await api_client.get_user(user_uuid)
        user = user_response.get('response', {})
        
        status_emoji = {
            'ACTIVE': '✅',
            'DISABLED': '❌',
            'LIMITED': '⏸️',
            'EXPIRED': '⏰'
        }
        
        text = f"""
✅ <b>Статус обновлён!</b>

👤 <b>Пользователь:</b> {user.get('username', 'N/A')}
🔄 <b>Новый статус:</b> {status_emoji.get(new_status, '')} {new_status}
        """
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END
        
    except RemnaWaveAPIError as e:
        log.error(f"Error updating status: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка:</b> {e.message}",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error updating status")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка</b>",
            reply_markup=user_kb.user_actions(user_uuid),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def edit_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel editing"""
    query = update.callback_query
    if query:
        await query.answer()
        user_uuid = context.user_data.get('editing_user_uuid')
        if user_uuid:
            await query.edit_message_text(
                "❌ <b>Редактирование отменено</b>",
                reply_markup=user_kb.user_actions(user_uuid),
                parse_mode=ParseMode.HTML
            )
    
    # Очищаем данные
    context.user_data.clear()
    return ConversationHandler.END


@admin_only
async def user_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user creation process"""
    query = update.callback_query
    await query.answer()
    
    # Очищаем данные предыдущего создания
    context.user_data.clear()
    
    text = """
➕ <b>Создание нового пользователя</b>

Шаг 1 из 4: Введите имя пользователя

<i>Требования:</i>
• Только латинские буквы, цифры, дефис и подчёркивание
• Длина от 3 до 32 символов
• Без пробелов

Введите имя пользователя или /cancel для отмены:
    """
    
    await query.edit_message_text(
        text.strip(),
        parse_mode=ParseMode.HTML
    )
    
    return CREATE_USERNAME


@admin_only
async def create_username_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process username input"""
    username = update.message.text.strip()
    
    # Валидация username
    if not username or len(username) < 3 or len(username) > 32:
        await update.message.reply_text(
            "❌ Имя пользователя должно быть от 3 до 32 символов. Попробуйте снова:",
            parse_mode=ParseMode.HTML
        )
        return CREATE_USERNAME
    
    # Проверяем, что username содержит только допустимые символы
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        await update.message.reply_text(
            "❌ Имя пользователя может содержать только латинские буквы, цифры, дефис и подчёркивание. Попробуйте снова:",
            parse_mode=ParseMode.HTML
        )
        return CREATE_USERNAME
    
    # Сохраняем username
    context.user_data['create_username'] = username
    
    text = f"""
➕ <b>Создание пользователя</b>

✅ Имя: <code>{username}</code>

Шаг 2 из 4: Введите лимит трафика в GB

<i>Примеры:</i>
• 100 - установить лимит 100 GB
• 0 - безлимитный трафик

Введите лимит трафика:
    """
    
    await update.message.reply_text(
        text.strip(),
        parse_mode=ParseMode.HTML
    )
    
    return CREATE_TRAFFIC_LIMIT


@admin_only
async def create_traffic_limit_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process traffic limit input"""
    try:
        traffic_gb = float(update.message.text.strip())
        
        if traffic_gb < 0:
            await update.message.reply_text(
                "❌ Лимит не может быть отрицательным. Попробуйте снова:",
                parse_mode=ParseMode.HTML
            )
            return CREATE_TRAFFIC_LIMIT
        
        traffic_bytes = int(traffic_gb * 1024 * 1024 * 1024) if traffic_gb > 0 else 0
        context.user_data['create_traffic_limit'] = traffic_bytes
        
        username = context.user_data.get('create_username')
        traffic_str = f"{traffic_gb:.2f} GB" if traffic_gb > 0 else "Безлимит"
        
        text = f"""
➕ <b>Создание пользователя</b>

✅ Имя: <code>{username}</code>
✅ Лимит трафика: {traffic_str}

Шаг 3 из 4: Введите срок действия в днях

<i>Примеры:</i>
• 30 - подписка на 30 дней
• 365 - подписка на год
• 0 - без ограничения срока

Введите количество дней:
        """
        
        await update.message.reply_text(
            text.strip(),
            parse_mode=ParseMode.HTML
        )
        
        return CREATE_EXPIRE_DAYS
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введите число (например: 100 или 0):",
            parse_mode=ParseMode.HTML
        )
        return CREATE_TRAFFIC_LIMIT


@admin_only
async def create_expire_days_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process expire days input"""
    try:
        days = int(update.message.text.strip())
        
        if days < 0:
            await update.message.reply_text(
                "❌ Количество дней не может быть отрицательным. Попробуйте снова:",
                parse_mode=ParseMode.HTML
            )
            return CREATE_EXPIRE_DAYS
        
        # Вычисляем дату истечения
        if days > 0:
            expire_date = datetime.now(timezone.utc) + timedelta(days=days)
            context.user_data['create_expire_at'] = expire_date.isoformat()
            expire_str = expire_date.strftime('%d.%m.%Y %H:%M')
        else:
            # Для "бессрочных" пользователей устанавливаем дату через 100 лет
            expire_date = datetime.now(timezone.utc) + timedelta(days=36500)
            context.user_data['create_expire_at'] = expire_date.isoformat()
            expire_str = "Без ограничения (~100 лет)"
        
        username = context.user_data.get('create_username')
        traffic_bytes = context.user_data.get('create_traffic_limit', 0)
        traffic_str = user_fmt.format_bytes(traffic_bytes) if traffic_bytes > 0 else "Безлимит"
        
        # Создаём клавиатуру подтверждения
        keyboard = [
            [
                InlineKeyboardButton("✅ Создать", callback_data="create_confirm"),
                InlineKeyboardButton("❌ Отменить", callback_data="create_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
➕ <b>Подтверждение создания пользователя</b>

<b>Проверьте данные:</b>

👤 Имя: <code>{username}</code>
📊 Лимит трафика: {traffic_str}
📅 Срок действия: {expire_str}
🔄 Статус: ACTIVE

Всё верно?
        """
        
        await update.message.reply_text(
            text.strip(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
        return CREATE_CONFIRM
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат. Введите целое число:",
            parse_mode=ParseMode.HTML
        )
        return CREATE_EXPIRE_DAYS


@admin_only
async def create_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and create user"""
    query = update.callback_query
    await query.answer()
    
    try:
        username = context.user_data.get('create_username')
        traffic_limit = context.user_data.get('create_traffic_limit', 0)
        expire_at = context.user_data.get('create_expire_at')
        
        # Создаём пользователя через API
        # expire_at обязательно должен быть в SDK (snake_case!)
        user_data = {
            "username": username,
            "traffic_limit_bytes": traffic_limit,
            "expire_at": expire_at,  # Всегда передаём, так как SDK требует это поле
            "status": "ACTIVE"
        }
        
        await query.edit_message_text(
            "⏳ Создание пользователя...",
            parse_mode=ParseMode.HTML
        )
        
        result = await api_client.create_user(user_data)
        created_user = result.get('response', {})
        
        text = f"""
✅ <b>Пользователь успешно создан!</b>

👤 <b>Имя:</b> {created_user.get('username', 'N/A')}
🔑 <b>UUID:</b> <code>{created_user.get('uuid', 'N/A')}</code>
📊 <b>Лимит трафика:</b> {user_fmt.format_bytes(traffic_limit) if traffic_limit > 0 else 'Безлимит'}
🔄 <b>Статус:</b> {created_user.get('status', 'N/A')}
        """
        
        # Очищаем данные создания
        context.user_data.clear()
        
        await query.edit_message_text(
            text.strip(),
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END
        
    except RemnaWaveAPIError as e:
        log.error(f"Error creating user: {e.message}")
        await query.edit_message_text(
            f"❌ <b>Ошибка создания:</b> {e.message}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error creating user")
        await query.edit_message_text(
            "❌ <b>Произошла ошибка при создании пользователя</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def create_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel user creation"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ <b>Создание пользователя отменено</b>",
        reply_markup=user_kb.users_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END


@admin_only
async def create_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel user creation via /cancel command"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ <b>Создание пользователя отменено</b>",
        reply_markup=user_kb.users_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END


@admin_only
async def user_search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start user search"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔍 <b>Поиск пользователя</b>

Введите один из параметров для поиска:

• <b>Username</b> (имя пользователя)
• <b>UUID</b> (полный или короткий)
• <b>Email</b>
• <b>Telegram ID</b>

Введите значение для поиска или /cancel для отмены:
    """
    
    await query.edit_message_text(
        text.strip(),
        parse_mode=ParseMode.HTML
    )
    
    return SEARCH_INPUT


@admin_only
async def user_search_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process search query"""
    search_query = update.message.text.strip()
    
    if not search_query:
        await update.message.reply_text(
            "❌ Поисковый запрос не может быть пустым. Попробуйте снова:",
            parse_mode=ParseMode.HTML
        )
        return SEARCH_INPUT
    
    try:
        await update.message.reply_text(
            f"🔍 Поиск пользователя: <code>{search_query}</code>...",
            parse_mode=ParseMode.HTML
        )
        
        # Пытаемся найти пользователя
        # Сначала пробуем как UUID
        user = None
        try:
            user_response = await api_client.get_user(search_query)
            user = user_response.get('response')
        except:
            pass
        
        # Если не нашли по UUID, пробуем поиск по имени через список
        if not user:
            try:
                # Получаем всех пользователей и ищем по username/email
                users_response = await api_client.get_users(page=1, limit=1000)
                all_users = users_response.get('response', {}).get('users', [])
                
                # Ищем совпадение по различным полям (с поддержкой поиска по подстроке)
                search_lower = search_query.lower()
                found_users = []
                
                for u in all_users:
                    username = (u.get('username') or '').lower()
                    email = (u.get('email') or '').lower()
                    telegram_id = str(u.get('telegramId') or '')
                    short_uuid = u.get('shortUuid') or ''
                    
                    # Точное совпадение имеет приоритет
                    if (username == search_lower or
                        email == search_lower or
                        telegram_id == search_query or
                        short_uuid == search_query):
                        user = u
                        break
                    
                    # Если точного совпадения нет, ищем по подстроке
                    if (search_lower in username or
                        search_lower in email or
                        search_query in telegram_id or
                        search_query in short_uuid):
                        found_users.append(u)
                
                # Если нашли несколько по подстроке
                if not user and found_users:
                    # Если найден только один, показываем его
                    if len(found_users) == 1:
                        user = found_users[0]
                    else:
                        # Если найдено несколько, показываем список
                        text = f"🔍 <b>Найдено пользователей:</b> {len(found_users)}\n\nЗапрос: <code>{search_query}</code>\n\n"
                        
                        keyboard = []
                        for u in found_users[:10]:  # Показываем максимум 10
                            username = u.get('username', 'N/A')
                            status_emoji = user_fmt.status_badge(u.get('status', ''))
                            short_uuid = u.get('shortUuid', '')[:8]
                            
                            button_text = f"{status_emoji} {username} ({short_uuid})"
                            keyboard.append([
                                InlineKeyboardButton(
                                    button_text,
                                    callback_data=f"user_view_{u.get('uuid')}"
                                )
                            ])
                        
                        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="users_list")])
                        
                        if len(found_users) > 10:
                            text += f"\n<i>Показаны первые 10 из {len(found_users)}. Уточните запрос для более точного поиска.</i>"
                        
                        await update.message.reply_text(
                            text,
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            parse_mode=ParseMode.HTML
                        )
                        return ConversationHandler.END
                    
            except Exception as e:
                log.error(f"Error searching users: {e}")
        
        if user:
            user_uuid = user.get('uuid')
            username = user.get('username', 'N/A')
            status = user.get('status', 'unknown').upper()
            
            # Get HWID count
            hwid_count = 0
            try:
                hwid_response = await api_client.get_user_devices(user_uuid)
                response_data = hwid_response.get('response', {})
                # API возвращает {'total': N, 'devices': [...]}
                hwid_count = response_data.get('total', 0)
            except Exception as e:
                log.warning(f"Failed to get HWID count: {e}")
            
            # Форматируем информацию о найденном пользователе
            text = f"""
✅ <b>Пользователь найден!</b>

{user_fmt.format_user_full(user, hwid_count=hwid_count)}
            """
            
            # Создаём клавиатуру с действиями
            keyboard = user_kb.user_actions(user_uuid)
            
            await update.message.reply_text(
                text.strip(),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                f"❌ <b>Пользователь не найден</b>\n\nЗапрос: <code>{search_query}</code>\n\nПопробуйте другой запрос или /cancel для отмены:",
                reply_markup=user_kb.users_menu(),
                parse_mode=ParseMode.HTML
            )
            return SEARCH_INPUT
            
    except RemnaWaveAPIError as e:
        log.error(f"Error searching user: {e.message}")
        await update.message.reply_text(
            f"❌ <b>Ошибка поиска:</b> {e.message}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    except Exception as e:
        log.exception("Unexpected error searching user")
        await update.message.reply_text(
            "❌ <b>Произошла ошибка при поиске</b>",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


@admin_only
async def search_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel search via /cancel command"""
    await update.message.reply_text(
        "❌ <b>Поиск отменён</b>",
        reply_markup=user_kb.users_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END


# ============================================================================
# BULK USER CREATION WITH PRESETS
# ============================================================================

import random
import string
import asyncio

def generate_random_username(length=12):
    """Generate random username with letters and digits"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@admin_only
async def bulk_create_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bulk user creation with presets"""
    query = update.callback_query
    await query.answer()
    
    max_bulk = settings.max_bulk_create
    
    keyboard = [
        [InlineKeyboardButton(f"{i}", callback_data=f"bulk_count_{i}")]
        for i in [5, 10, 15, max_bulk]
    ]
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="users_list")])
    
    await query.edit_message_text(
        f"<b>📦 Массовое создание пользователей</b>\n\n"
        f"Будут созданы пользователи со случайными именами (12 символов)\n\n"
        f"Выберите количество пользователей (макс. {max_bulk}):",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    return BULK_COUNT


@admin_only
async def bulk_count_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user count selection"""
    query = update.callback_query
    await query.answer()
    
    count = int(query.data.split("_")[2])
    context.user_data['bulk_count'] = count
    
    keyboard = [
        [InlineKeyboardButton("♾️ Безлимит", callback_data="bulk_duration_unlimited")],
        [
            InlineKeyboardButton("1 месяц", callback_data="bulk_duration_1"),
            InlineKeyboardButton("2 месяца", callback_data="bulk_duration_2"),
        ],
        [
            InlineKeyboardButton("3 месяца", callback_data="bulk_duration_3"),
            InlineKeyboardButton("6 месяцев", callback_data="bulk_duration_6"),
        ],
        [InlineKeyboardButton("12 месяцев", callback_data="bulk_duration_12")],
        [InlineKeyboardButton("❌ Отмена", callback_data="users_list")]
    ]
    
    await query.edit_message_text(
        f"<b>📦 Массовое создание: {count} польз.</b>\n\n"
        f"<b>Шаг 1/3:</b> Выберите срок действия:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    return BULK_DURATION


@admin_only
async def bulk_duration_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process duration selection"""
    query = update.callback_query
    await query.answer()
    
    duration_str = query.data.split("_")[2]
    context.user_data['bulk_duration'] = duration_str
    
    count = context.user_data.get('bulk_count')
    
    if duration_str == "unlimited":
        duration_text = "♾️ Безлимит (~100 лет)"
    else:
        months = int(duration_str)
        duration_text = f"{months} мес."
    
    keyboard = [
        [InlineKeyboardButton("♾️ Безлимит", callback_data="bulk_traffic_unlimited")],
        [
            InlineKeyboardButton("100 ГБ", callback_data="bulk_traffic_100"),
            InlineKeyboardButton("400 ГБ", callback_data="bulk_traffic_400"),
        ],
        [
            InlineKeyboardButton("800 ГБ", callback_data="bulk_traffic_800"),
            InlineKeyboardButton("1000 ГБ", callback_data="bulk_traffic_1000"),
        ],
        [InlineKeyboardButton("2000 ГБ", callback_data="bulk_traffic_2000")],
        [InlineKeyboardButton("❌ Отмена", callback_data="users_list")]
    ]
    
    await query.edit_message_text(
        f"<b>📦 Массовое создание: {count} польз.</b>\n\n"
        f"<b>Шаг 2/3:</b> Выберите лимит трафика:\n"
        f"├ Срок: {duration_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    return BULK_TRAFFIC


@admin_only
async def bulk_traffic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process traffic limit selection"""
    query = update.callback_query
    await query.answer()
    
    traffic_str = query.data.split("_")[2]
    context.user_data['bulk_traffic'] = traffic_str
    
    count = context.user_data.get('bulk_count')
    duration_str = context.user_data.get('bulk_duration')
    
    if duration_str == "unlimited":
        duration_text = "♾️ Безлимит"
    else:
        duration_text = f"{duration_str} мес."
    
    if traffic_str == "unlimited":
        traffic_text = "♾️ Безлимит"
        # Если трафик безлимит, сразу переходим к подтверждению
        context.user_data['bulk_reset'] = None
        return await bulk_confirm_show(update, context)
    else:
        traffic_text = f"{traffic_str} ГБ"
    
    # Если трафик ограничен, спрашиваем про период сброса
    keyboard = [
        [InlineKeyboardButton("🚫 Без сброса", callback_data="bulk_reset_NO_RESET")],
        [InlineKeyboardButton("📅 Каждый день", callback_data="bulk_reset_DAY")],
        [InlineKeyboardButton("📅 Каждую неделю", callback_data="bulk_reset_WEEK")],
        [InlineKeyboardButton("📅 Каждый месяц", callback_data="bulk_reset_MONTH")],
        [InlineKeyboardButton("❌ Отмена", callback_data="users_list")]
    ]
    
    await query.edit_message_text(
        f"<b>📦 Массовое создание: {count} польз.</b>\n\n"
        f"<b>Шаг 3/3:</b> Выберите период сброса трафика:\n"
        f"├ Срок: {duration_text}\n"
        f"└ Трафик: {traffic_text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    return BULK_RESET


@admin_only
async def bulk_reset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process reset strategy selection"""
    query = update.callback_query
    await query.answer()
    
    reset_str = query.data.split("_")[2]
    context.user_data['bulk_reset'] = reset_str
    
    return await bulk_confirm_show(update, context)


async def bulk_confirm_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation before bulk creation"""
    query = update.callback_query
    
    count = context.user_data.get('bulk_count')
    duration_str = context.user_data.get('bulk_duration')
    traffic_str = context.user_data.get('bulk_traffic')
    reset_str = context.user_data.get('bulk_reset')
    
    # Форматируем параметры
    if duration_str == "unlimited":
        duration_text = "♾️ Безлимит (~100 лет)"
    else:
        months = int(duration_str)
        duration_text = f"{months} месяц(ев)"
    
    if traffic_str == "unlimited":
        traffic_text = "♾️ Безлимит"
        reset_text = "—"
    else:
        traffic_gb = int(traffic_str)
        traffic_text = f"{traffic_gb} ГБ ({traffic_gb * 1024**3:,} байт)"
        
        reset_names = {
            "NO_RESET": "🚫 Без сброса",
            "DAY": "📅 Каждый день",
            "WEEK": "📅 Каждую неделю",
            "MONTH": "📅 Каждый месяц"
        }
        reset_text = reset_names.get(reset_str, reset_str)
    
    keyboard = [
        [InlineKeyboardButton("✅ Создать", callback_data="bulk_create_confirm")],
        [InlineKeyboardButton("❌ Отмена", callback_data="users_list")]
    ]
    
    text = f"""
<b>📦 Подтверждение массового создания</b>

<b>Количество:</b> {count} пользователей
<b>Имена:</b> Случайные (12 символов)

<b>Параметры:</b>
├ Срок действия: {duration_text}
├ Лимит трафика: {traffic_text}
└ Период сброса: {reset_text}

<b>Статус:</b> ACTIVE

⚠️ Будет создано {count} новых пользователей!
    """
    
    await query.edit_message_text(
        text.strip(),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )
    
    return BULK_CONFIRM


@admin_only
async def bulk_create_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute bulk user creation"""
    query = update.callback_query
    await query.answer()
    
    count = context.user_data.get('bulk_count')
    duration_str = context.user_data.get('bulk_duration')
    traffic_str = context.user_data.get('bulk_traffic')
    reset_str = context.user_data.get('bulk_reset')
    
    await query.edit_message_text(
        f"⏳ <b>Создание {count} пользователей...</b>\n\nЭто может занять некоторое время.",
        parse_mode=ParseMode.HTML
    )
    
    try:
        # Расчёт параметров
        if duration_str == "unlimited":
            expire_date = datetime.now(timezone.utc) + timedelta(days=36500)  # ~100 лет
        else:
            months = int(duration_str)
            expire_date = datetime.now(timezone.utc) + timedelta(days=30 * months)
        
        expire_at = expire_date.isoformat()
        
        if traffic_str == "unlimited":
            traffic_limit = 0
            traffic_strategy = None
        else:
            traffic_gb = int(traffic_str)
            traffic_limit = traffic_gb * 1024**3  # Конвертация в байты
            traffic_strategy = reset_str
        
        # Массовое создание
        created_users = []
        failed_users = []
        
        for i in range(count):
            try:
                username = generate_random_username(12)
                
                user_data = {
                    "username": username,
                    "traffic_limit_bytes": traffic_limit,
                    "expire_at": expire_at,
                    "status": "ACTIVE"
                }
                
                if traffic_strategy:
                    user_data["traffic_limit_strategy"] = traffic_strategy
                
                result = await api_client.create_user(user_data)
                created_user = result.get('response', {})
                created_users.append(created_user.get('username'))
                
                # Небольшая задержка между запросами
                await asyncio.sleep(0.1)
                
            except Exception as e:
                log.error(f"Error creating user {username}: {e}")
                failed_users.append(f"{username}: {str(e)}")
        
        # Формируем отчёт
        success_count = len(created_users)
        failed_count = len(failed_users)
        
        text = f"<b>✅ Массовое создание завершено</b>\n\n"
        text += f"<b>Создано:</b> {success_count}/{count}\n"
        
        if failed_count > 0:
            text += f"<b>Ошибок:</b> {failed_count}\n\n"
        
        if created_users:
            text += f"\n<b>Созданные пользователи:</b>\n"
            # Показываем максимум 20 имён
            shown_users = created_users[:20]
            text += "\n".join([f"• <code>{u}</code>" for u in shown_users])
            
            if len(created_users) > 20:
                text += f"\n\n<i>... и ещё {len(created_users) - 20}</i>"
        
        if failed_users and failed_count <= 5:
            text += f"\n\n<b>Ошибки:</b>\n"
            text += "\n".join([f"• {f}" for f in failed_users])
        
        context.user_data.clear()
        
        await query.edit_message_text(
            text,
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END
        
    except Exception as e:
        log.exception("Error in bulk user creation")
        context.user_data.clear()
        
        await query.edit_message_text(
            f"❌ <b>Ошибка массового создания:</b> {str(e)}",
            reply_markup=user_kb.users_menu(),
            parse_mode=ParseMode.HTML
        )
        
        return ConversationHandler.END


@admin_only
async def bulk_create_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel bulk creation"""
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    
    await query.edit_message_text(
        "❌ <b>Массовое создание отменено</b>",
        reply_markup=user_kb.users_menu(),
        parse_mode=ParseMode.HTML
    )
    
    return ConversationHandler.END


def register_users_handlers(application):
    """Register all user management handlers"""
    
    # ConversationHandler для редактирования пользователя
    edit_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(user_edit_callback, pattern="^user_edit:")
        ],
        states={
            EDIT_CHOOSING: [
                CallbackQueryHandler(edit_traffic_limit_start, pattern="^edit_traffic:"),
                CallbackQueryHandler(edit_expire_date_start, pattern="^edit_expire:"),
                CallbackQueryHandler(edit_status_start, pattern="^edit_status:"),
            ],
            EDIT_TRAFFIC_LIMIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_traffic_limit_process),
                CallbackQueryHandler(edit_cancel, pattern="^user_edit:"),
            ],
            EDIT_EXPIRE_DATE: [
                CallbackQueryHandler(edit_expire_date_preset, pattern="^set_expire:"),
                CallbackQueryHandler(edit_cancel, pattern="^user_edit:"),
            ],
            EDIT_STATUS: [
                CallbackQueryHandler(edit_status_process, pattern="^set_status:"),
                CallbackQueryHandler(edit_cancel, pattern="^user_edit:"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(edit_cancel, pattern="^user_view:"),
        ],
        per_message=False,
        allow_reentry=True
    )
    
    application.add_handler(edit_conv_handler)
    
    # ConversationHandler для создания пользователя
    create_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(user_create_start, pattern="^user_create$")
        ],
        states={
            CREATE_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_username_process),
            ],
            CREATE_TRAFFIC_LIMIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_traffic_limit_process),
            ],
            CREATE_EXPIRE_DAYS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_expire_days_process),
            ],
            CREATE_CONFIRM: [
                CallbackQueryHandler(create_confirm_callback, pattern="^create_confirm$"),
                CallbackQueryHandler(create_cancel_callback, pattern="^create_cancel$"),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^/cancel$"), create_cancel_command),
        ],
        per_message=False,
        allow_reentry=True
    )
    
    application.add_handler(create_conv_handler)
    
    # ConversationHandler для поиска пользователя
    search_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(user_search_start, pattern="^user_search$")
        ],
        states={
            SEARCH_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, user_search_process),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^/cancel$"), search_cancel_command),
        ],
        per_message=False,
        allow_reentry=True
    )
    
    application.add_handler(search_conv_handler)
    
    # ConversationHandler для массового создания пользователей
    bulk_create_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(bulk_create_start, pattern="^user_bulk_create$")
        ],
        states={
            BULK_COUNT: [
                CallbackQueryHandler(bulk_count_callback, pattern="^bulk_count_"),
            ],
            BULK_DURATION: [
                CallbackQueryHandler(bulk_duration_callback, pattern="^bulk_duration_"),
            ],
            BULK_TRAFFIC: [
                CallbackQueryHandler(bulk_traffic_callback, pattern="^bulk_traffic_"),
            ],
            BULK_RESET: [
                CallbackQueryHandler(bulk_reset_callback, pattern="^bulk_reset_"),
            ],
            BULK_CONFIRM: [
                CallbackQueryHandler(bulk_create_confirm, pattern="^bulk_create_confirm$"),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(bulk_create_cancel, pattern="^users_list$"),
        ],
        per_message=False,
        allow_reentry=True
    )
    
    application.add_handler(bulk_create_conv_handler)
    
    # Import delete handlers
    from .delete_handlers import (
        user_delete_start,
        user_delete_confirm_handler,
        user_delete_cancel
    )
    
    # Основные хендлеры
    application.add_handler(CallbackQueryHandler(users_menu_callback, pattern="^users_menu$"))
    application.add_handler(CallbackQueryHandler(users_list_callback, pattern="^users_list$"))
    application.add_handler(CallbackQueryHandler(users_list_callback, pattern="^users_page:"))
    application.add_handler(CallbackQueryHandler(user_view_callback, pattern="^user_view:"))
    application.add_handler(CallbackQueryHandler(user_extend_callback, pattern="^user_extend:"))
    application.add_handler(CallbackQueryHandler(extend_user_callback, pattern="^extend:"))
    
    # Smart delete handlers (replacing old PIN-based delete)
    application.add_handler(CallbackQueryHandler(user_delete_start, pattern="^user_delete_confirm:"))
    application.add_handler(CallbackQueryHandler(user_delete_cancel, pattern="^user_delete_cancel:"))
    
    # Additional feature handlers
    application.add_handler(CallbackQueryHandler(user_reset_traffic_callback, pattern="^user_reset_traffic:"))
    application.add_handler(CallbackQueryHandler(user_stats_callback, pattern="^user_stats:"))
    application.add_handler(CallbackQueryHandler(user_devices_callback, pattern="^user_devices:"))
    application.add_handler(CallbackQueryHandler(user_clear_devices_confirm_callback, pattern="^user_clear_devices_confirm:"))
    application.add_handler(CallbackQueryHandler(user_clear_devices_execute_callback, pattern="^user_clear_devices_execute:"))
    
    # Combined message handler for ConversationHandlers and delete confirmation
    async def combined_text_handler(update, context):
        # Check for delete confirmation first
        if context.user_data.get('delete_user_confirmation'):
            await user_delete_confirm_handler(update, context)
            return
        # Old PIN handler no longer needed - removed
    
    # Message handler (должен быть последним, в группе 1 чтобы не конфликтовать с другими)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, combined_text_handler),
        group=1
    )
    
    log.info("✅ Users feature handlers registered")
