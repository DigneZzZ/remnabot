"""
Pytest configuration and fixtures
"""
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_update():
    """Mock Telegram Update object"""
    update = MagicMock()
    update.effective_user.id = 123456789
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"
    update.message = MagicMock()
    update.callback_query = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    update.callback_query.data = "test_data"
    return update


@pytest.fixture
def mock_context():
    """Mock Telegram Context object"""
    context = MagicMock()
    context.user_data = {}
    context.bot_data = {}
    return context


@pytest.fixture
def mock_api_client():
    """Mock RemnaWave API client"""
    client = MagicMock()
    client.get_users = AsyncMock(return_value={
        'data': [
            {
                'uuid': 'test-uuid-1',
                'username': 'user1',
                'email': 'user1@test.com',
                'status': 'active'
            }
        ],
        'total': 1
    })
    client.get_user = AsyncMock(return_value={
        'uuid': 'test-uuid-1',
        'username': 'user1',
        'email': 'user1@test.com',
        'status': 'active'
    })
    client.get_system_stats = AsyncMock(return_value={
        'totalUsers': 100,
        'activeUsers': 80,
        'totalTraffic': 1024000,
        'nodesCount': 5,
        'hostsCount': 3
    })
    return client
