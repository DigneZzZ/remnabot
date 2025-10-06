"""
Tests for API client
"""
import pytest
from unittest.mock import AsyncMock, patch

from src.services.api import RemnaWaveAPIClient, RemnaWaveAPIError


@pytest.mark.asyncio
async def test_authenticate():
    """Test authentication"""
    client = RemnaWaveAPIClient()
    
    with patch.object(client, '_get_client') as mock_get_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'accessToken': 'test-token'}
        
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_get_client.return_value = mock_http_client
        
        await client._authenticate()
        
        assert client._token == 'test-token'
        assert client._token_expires_at is not None


@pytest.mark.asyncio
async def test_authenticate_failure():
    """Test authentication failure"""
    client = RemnaWaveAPIClient()
    
    with patch.object(client, '_get_client') as mock_get_client:
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        
        mock_http_client = AsyncMock()
        mock_http_client.post.return_value = mock_response
        mock_get_client.return_value = mock_http_client
        
        with pytest.raises(RemnaWaveAPIError):
            await client._authenticate()


@pytest.mark.asyncio
async def test_get_users():
    """Test get users"""
    client = RemnaWaveAPIClient()
    client._token = 'test-token'
    
    with patch.object(client, '_make_request') as mock_request:
        mock_request.return_value = {
            'data': [{'username': 'test'}],
            'total': 1
        }
        
        result = await client.get_users()
        
        assert 'data' in result
        assert len(result['data']) == 1
        mock_request.assert_called_once()
