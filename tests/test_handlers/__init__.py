"""
Tests for start handlers
"""
import pytest
from unittest.mock import patch, AsyncMock

from src.handlers.start import start_command, main_menu_callback, stats_callback


@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test /start command"""
    await start_command(mock_update, mock_context)
    
    # Verify reply was sent
    mock_update.message.reply_text.assert_called_once()
    
    # Verify message contains welcome text
    call_args = mock_update.message.reply_text.call_args
    assert "Добро пожаловать" in call_args[0][0]


@pytest.mark.asyncio
async def test_main_menu_callback(mock_update, mock_context):
    """Test main menu callback"""
    await main_menu_callback(mock_update, mock_context)
    
    # Verify callback was answered
    mock_update.callback_query.answer.assert_called_once()
    
    # Verify message was edited
    mock_update.callback_query.edit_message_text.assert_called_once()
    
    # Verify message contains menu text
    call_args = mock_update.callback_query.edit_message_text.call_args
    assert "Главное меню" in call_args[0][0]


@pytest.mark.asyncio
@patch('src.handlers.start.api_client')
async def test_stats_callback(mock_api, mock_update, mock_context):
    """Test statistics callback"""
    # Mock API response
    mock_api.get_system_stats = AsyncMock(return_value={
        'totalUsers': 100,
        'activeUsers': 80,
        'totalTraffic': 1024000,
        'nodesCount': 5,
        'hostsCount': 3
    })
    
    await stats_callback(mock_update, mock_context)
    
    # Verify callback was answered
    mock_update.callback_query.answer.assert_called_once()
    
    # Verify API was called
    mock_api.get_system_stats.assert_called_once()
    
    # Verify message was edited
    assert mock_update.callback_query.edit_message_text.call_count >= 1
