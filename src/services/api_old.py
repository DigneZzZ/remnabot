"""
Remnawave API service module
"""
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from src.core.config import settings
from src.core.logger import log


class RemnaWaveAPIError(Exception):
    """Base exception for RemnaWave API errors"""
    pass


class RemnaWaveAPIClient:
    """
    Client for interacting with Remnawave API
    Uses httpx for async HTTP requests
    """
    
    def __init__(self):
        self.base_url = settings.remnawave_api_url.rstrip('/')
        self._token: Optional[str] = getattr(settings, 'remnawave_api_token', None)
        self._token_expires_at: Optional[datetime] = None
        self._client: Optional[httpx.AsyncClient] = None
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                follow_redirects=True
            )
        return self._client
    
    async def close(self):
        """Close HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            log.debug("API client closed")
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid authentication token"""
        if not self._token:
            log.error("API token is not configured!")
            raise RemnaWaveAPIError("API token is not configured")
        
        # If token is provided via config, we don't need to authenticate
        if self._token:
            return
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[Any, Any]:
        """
        Make authenticated request to API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response data as dictionary
        """
        await self._ensure_authenticated()
        
        client = await self._get_client()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"
        
        try:
            log.debug(f"Making {method} request to {endpoint}")
            response = await client.request(
                method=method,
                url=endpoint,
                headers=headers,
                **kwargs
            )
            
            if settings.is_debug:
                log.debug(f"Response status: {response.status_code}")
                log.debug(f"Response body: {response.text[:500]}")
            
            response.raise_for_status()
            
            return response.json() if response.text else {}
            
        except httpx.HTTPStatusError as e:
            log.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise RemnaWaveAPIError(f"API error: {e.response.status_code}")
        except httpx.HTTPError as e:
            log.error(f"HTTP error: {e}")
            raise RemnaWaveAPIError(f"HTTP error: {e}")
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            raise RemnaWaveAPIError(f"Request error: {e}")
    
    # ==================== Users API ====================
    
    async def get_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get list of users"""
        log.info(f"Fetching users (page={page}, limit={limit})")
        return await self._make_request(
            "GET",
            f"/api/users?page={page}&limit={limit}"
        )
    
    async def get_user(self, user_uuid: str) -> Dict[str, Any]:
        """Get user by UUID"""
        log.info(f"Fetching user: {user_uuid}")
        return await self._make_request("GET", f"/api/users/{user_uuid}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user"""
        log.info(f"Creating user: {user_data.get('username', 'unknown')}")
        return await self._make_request("POST", "/api/users", json=user_data)
    
    async def update_user(self, user_uuid: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        log.info(f"Updating user: {user_uuid}")
        return await self._make_request("PUT", f"/api/users/{user_uuid}", json=user_data)
    
    async def delete_user(self, user_uuid: str) -> Dict[str, Any]:
        """Delete user"""
        log.warning(f"Deleting user: {user_uuid}")
        return await self._make_request("DELETE", f"/api/users/{user_uuid}")
    
    async def extend_user_subscription(
        self,
        user_uuid: str,
        days: int
    ) -> Dict[str, Any]:
        """Extend user subscription"""
        log.info(f"Extending subscription for {user_uuid} by {days} days")
        return await self._make_request(
            "POST",
            f"/api/users/{user_uuid}/extend",
            json={"days": days}
        )
    
    # ==================== Hosts API ====================
    
    async def get_hosts(self) -> Dict[str, Any]:
        """Get list of hosts"""
        log.info("Fetching hosts")
        return await self._make_request("GET", "/api/hosts")
    
    async def get_host(self, host_uuid: str) -> Dict[str, Any]:
        """Get host by UUID"""
        log.info(f"Fetching host: {host_uuid}")
        return await self._make_request("GET", f"/api/hosts/{host_uuid}")
    
    async def create_host(self, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new host"""
        log.info(f"Creating host: {host_data.get('name', 'unknown')}")
        return await self._make_request("POST", "/api/hosts", json=host_data)
    
    async def update_host(self, host_uuid: str, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update host"""
        log.info(f"Updating host: {host_uuid}")
        return await self._make_request("PUT", f"/api/hosts/{host_uuid}", json=host_data)
    
    async def delete_host(self, host_uuid: str) -> Dict[str, Any]:
        """Delete host"""
        log.warning(f"Deleting host: {host_uuid}")
        return await self._make_request("DELETE", f"/api/hosts/{host_uuid}")
    
    # ==================== Nodes API ====================
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Get list of nodes"""
        log.info("Fetching nodes")
        return await self._make_request("GET", "/api/nodes")
    
    async def get_node(self, node_uuid: str) -> Dict[str, Any]:
        """Get node by UUID"""
        log.info(f"Fetching node: {node_uuid}")
        return await self._make_request("GET", f"/api/nodes/{node_uuid}")
    
    async def get_node_stats(self, node_uuid: str) -> Dict[str, Any]:
        """Get node statistics"""
        log.info(f"Fetching stats for node: {node_uuid}")
        return await self._make_request("GET", f"/api/nodes/{node_uuid}/stats")
    
    async def create_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new node"""
        log.info(f"Creating node: {node_data.get('name', 'unknown')}")
        return await self._make_request("POST", "/api/nodes", json=node_data)
    
    async def update_node(self, node_uuid: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update node"""
        log.info(f"Updating node: {node_uuid}")
        return await self._make_request("PUT", f"/api/nodes/{node_uuid}", json=node_data)
    
    async def delete_node(self, node_uuid: str) -> Dict[str, Any]:
        """Delete node"""
        log.warning(f"Deleting node: {node_uuid}")
        return await self._make_request("DELETE", f"/api/nodes/{node_uuid}")
    
    # ==================== HWID API ====================
    
    async def get_user_devices(self, user_uuid: str) -> Dict[str, Any]:
        """Get devices for user"""
        log.info(f"Fetching devices for user: {user_uuid}")
        return await self._make_request("GET", f"/api/users/{user_uuid}/devices")
    
    async def get_all_devices_stats(self) -> Dict[str, Any]:
        """Get statistics for all devices"""
        log.info("Fetching all devices statistics")
        return await self._make_request("GET", "/api/devices/stats")
    
    async def delete_device(self, device_uuid: str) -> Dict[str, Any]:
        """Delete device"""
        log.warning(f"Deleting device: {device_uuid}")
        return await self._make_request("DELETE", f"/api/devices/{device_uuid}")
    
    # ==================== Squads API ====================
    
    async def get_squads(self) -> Dict[str, Any]:
        """Get list of squads"""
        log.info("Fetching squads")
        return await self._make_request("GET", "/api/squads")
    
    async def get_squad(self, squad_uuid: str) -> Dict[str, Any]:
        """Get squad by UUID"""
        log.info(f"Fetching squad: {squad_uuid}")
        return await self._make_request("GET", f"/api/squads/{squad_uuid}")
    
    async def create_squad(self, squad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new squad"""
        log.info(f"Creating squad: {squad_data.get('name', 'unknown')}")
        return await self._make_request("POST", "/api/squads", json=squad_data)
    
    async def update_squad(self, squad_uuid: str, squad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update squad"""
        log.info(f"Updating squad: {squad_uuid}")
        return await self._make_request("PUT", f"/api/squads/{squad_uuid}", json=squad_data)
    
    async def delete_squad(self, squad_uuid: str) -> Dict[str, Any]:
        """Delete squad"""
        log.warning(f"Deleting squad: {squad_uuid}")
        return await self._make_request("DELETE", f"/api/squads/{squad_uuid}")
    
    async def add_user_to_squad(self, squad_uuid: str, user_uuid: str) -> Dict[str, Any]:
        """Add user to squad"""
        log.info(f"Adding user {user_uuid} to squad {squad_uuid}")
        return await self._make_request(
            "POST",
            f"/api/squads/{squad_uuid}/users/{user_uuid}"
        )
    
    async def remove_user_from_squad(self, squad_uuid: str, user_uuid: str) -> Dict[str, Any]:
        """Remove user from squad"""
        log.info(f"Removing user {user_uuid} from squad {squad_uuid}")
        return await self._make_request(
            "DELETE",
            f"/api/squads/{squad_uuid}/users/{user_uuid}"
        )
    
    # ==================== Statistics API ====================
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        log.info("Fetching system statistics")
        return await self._make_request("GET", "/api/system/stats")
    
    async def get_bandwidth_stats(self) -> Dict[str, Any]:
        """Get bandwidth statistics"""
        log.info("Fetching bandwidth statistics")
        return await self._make_request("GET", "/api/system/stats/bandwidth")
    
    async def get_nodes_statistics(self) -> Dict[str, Any]:
        """Get nodes statistics"""
        log.info("Fetching nodes statistics")
        return await self._make_request("GET", "/api/system/stats/nodes")


# Create global API client instance
api_client = RemnaWaveAPIClient()
