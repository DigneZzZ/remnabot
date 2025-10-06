"""
Remnawave API service using official SDK
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger as log

from remnawave import RemnawaveSDK
from remnawave.exceptions import ApiError, ForbiddenError
from remnawave.models import (
    UsersResponseDto,
    UserResponseDto,
    GetStatsResponseDto,
    GetAllConfigProfilesResponseDto,
    GetAllNodesResponseDto,
    GetAllHostsResponseDto,
    UpdateUserRequestDto,
)

from src.core.config import settings


class RemnaWaveAPIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RemnaWaveAPIClient:
    """
    Async API client for Remnawave using official SDK
    Wrapper around RemnawaveSDK for compatibility with existing code
    """
    
    def __init__(self):
        self.base_url = settings.remnawave_api_url.rstrip('/')
        self.token = settings.remnawave_api_token
        self._sdk: Optional[RemnawaveSDK] = None
    
    @property
    def sdk(self) -> RemnawaveSDK:
        """Get or create SDK instance"""
        if self._sdk is None:
            self._sdk = RemnawaveSDK(
                base_url=self.base_url,
                token=self.token
            )
            log.info(f"Remnawave SDK initialized with base_url={self.base_url}")
        return self._sdk
    
    async def close(self):
        """Close SDK client"""
        if self._sdk and self._sdk._client:
            await self._sdk._client.aclose()
            log.debug("API SDK client closed")
    
    # ======================
    # USERS API
    # ======================
    
    async def get_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get paginated list of users"""
        try:
            log.info(f"Fetching users (page={page}, limit={limit})")
            
            # SDK использует start/size вместо page/limit
            start = (page - 1) * limit
            response: UsersResponseDto = await self.sdk.users.get_all_users_v2(
                start=start,
                size=limit
            )
            
            # Возвращаем в формате, совместимом со старым API
            return {
                "response": {
                    "users": [user.model_dump(by_alias=True) for user in response.users],
                    "total": response.total
                }
            }
        except ApiError as e:
            log.error(f"SDK API error: {e}")
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Unexpected error fetching users: {e}")
            raise RemnaWaveAPIError(f"Error fetching users: {str(e)}")
    
    async def get_user(self, user_uuid: str) -> Dict[str, Any]:
        """Get user by UUID"""
        try:
            log.info(f"Fetching user {user_uuid}")
            response: UserResponseDto = await self.sdk.users.get_user_by_uuid(uuid=user_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching user: {e}")
            raise RemnaWaveAPIError(f"Error fetching user: {str(e)}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            log.info(f"Creating user: {user_data.get('username')}")
            from remnawave.models import CreateUserRequestDto
            
            # Создаём DTO из словаря
            create_dto = CreateUserRequestDto(**user_data)
            response: UserResponseDto = await self.sdk.users.create_user(body=create_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error creating user: {e}")
            raise RemnaWaveAPIError(f"Error creating user: {str(e)}")
    
    async def update_user(self, user_uuid: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user - создаём DTO с uuid внутри"""
        try:
            log.info(f"Updating user {user_uuid}")
            # DTO ТРЕБУЕТ uuid внутри себя - добавляем его в данные
            user_data_with_uuid = {**user_data, "uuid": str(user_uuid)}
            update_dto = UpdateUserRequestDto(**user_data_with_uuid)
            # Вызываем SDK метод - uuid уже внутри DTO
            response: UserResponseDto = await self.sdk.users.update_user(
                body=update_dto
            )
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error updating user: {e}")
            raise RemnaWaveAPIError(f"Error updating user: {str(e)}")
    
    async def delete_user(self, user_uuid: str) -> Dict[str, Any]:
        """Delete user"""
        try:
            log.info(f"Deleting user {user_uuid}")
            response = await self.sdk.users.delete_user(uuid=user_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error deleting user: {e}")
            raise RemnaWaveAPIError(f"Error deleting user: {str(e)}")
    
    async def extend_user_subscription(
        self,
        user_uuid: str,
        days: int,
        traffic_limit_bytes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Extend user subscription by N days"""
        try:
            log.info(f"Extending subscription for user {user_uuid} by {days} days")
            
            # Получаем текущего пользователя
            user = await self.sdk.users.get_user_by_uuid(uuid=user_uuid)
            
            # Используем UTC timezone для корректного сравнения
            from datetime import timezone
            now = datetime.now(timezone.utc)
            
            # Вычисляем новую дату истечения
            current_expire = user.expire_at if user.expire_at else now
            
            # Убедимся что current_expire имеет timezone
            if current_expire.tzinfo is None:
                from datetime import timezone
                current_expire = current_expire.replace(tzinfo=timezone.utc)
            
            if current_expire < now:
                new_expire = now + timedelta(days=days)
            else:
                new_expire = current_expire + timedelta(days=days)
            
            # Обновляем пользователя - передаём словарь, а не DTO
            update_data = {
                "expireAt": new_expire.isoformat(),
                "trafficLimitBytes": traffic_limit_bytes if traffic_limit_bytes is not None else user.traffic_limit_bytes
            }
            
            # update_user сам создаст DTO из словаря
            response_dict = await self.update_user(user_uuid, update_data)
            return response_dict
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error extending subscription: {e}")
            raise RemnaWaveAPIError(f"Error extending subscription: {str(e)}")
    
    async def reset_user_traffic(self, user_uuid: str) -> Dict[str, Any]:
        """Reset user traffic to 0"""
        try:
            log.info(f"Resetting traffic for user {user_uuid}")
            # SDK ожидает строку, а не UUID объект
            uuid_str = str(user_uuid) if not isinstance(user_uuid, str) else user_uuid
            response = await self.sdk.users.reset_user_traffic(uuid=uuid_str)
            return {"response": response.model_dump(by_alias=True) if hasattr(response, 'model_dump') else {"success": True}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error resetting traffic: {e}")
            raise RemnaWaveAPIError(f"Error resetting traffic: {str(e)}")
    
    # ======================
    # HOSTS API
    # ======================
    
    async def get_hosts(self) -> Dict[str, Any]:
        """Get all hosts"""
        try:
            log.info("Fetching hosts")
            response: GetAllHostsResponseDto = await self.sdk.hosts.get_all_hosts()
            # GetAllHostsResponseDto имеет поле root вместо hosts
            return {"response": [host.model_dump(by_alias=True) for host in response.root]}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching hosts: {e}")
            raise RemnaWaveAPIError(f"Error fetching hosts: {str(e)}")
    
    async def get_host(self, host_uuid: str) -> Dict[str, Any]:
        """Get host by UUID"""
        try:
            log.info(f"Fetching host {host_uuid}")
            response = await self.sdk.hosts.get_one_host(host_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching host: {e}")
            raise RemnaWaveAPIError(f"Error fetching host: {str(e)}")
    
    async def create_host(self, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new host"""
        try:
            log.info("Creating host")
            from remnawave.models import CreateHostRequestDto
            create_dto = CreateHostRequestDto(**host_data)
            response = await self.sdk.hosts.create_host(body=create_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error creating host: {e}")
            raise RemnaWaveAPIError(f"Error creating host: {str(e)}")
    
    async def update_host(self, host_uuid: str, host_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update host"""
        try:
            log.info(f"Updating host {host_uuid}")
            from remnawave.models import UpdateHostRequestDto
            # UUID должен быть включен в DTO
            host_data['uuid'] = host_uuid
            update_dto = UpdateHostRequestDto(**host_data)
            response = await self.sdk.hosts.update_host(body=update_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error updating host: {e}")
            raise RemnaWaveAPIError(f"Error updating host: {str(e)}")
    
    async def delete_host(self, host_uuid: str) -> Dict[str, Any]:
        """Delete host"""
        try:
            log.info(f"Deleting host {host_uuid}")
            # Метод принимает uuid как позиционный аргумент
            response = await self.sdk.hosts.delete_host(host_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error deleting host: {e}")
            raise RemnaWaveAPIError(f"Error deleting host: {str(e)}")
    
    async def create_host(self, create_data: "CreateHostRequestDto") -> Dict[str, Any]:
        """Create new host"""
        try:
            log.info(f"Creating host with remark: {create_data.remark}")
            response = await self.sdk.hosts.create_host(body=create_data)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error creating host: {e}")
            raise RemnaWaveAPIError(f"Error creating host: {str(e)}")
    
    # ======================
    # INBOUNDS API
    # ======================
    
    async def get_inbounds(self) -> Dict[str, Any]:
        """Fetch all inbounds"""
        try:
            log.info("Fetching inbounds")
            response = await self.sdk.inbounds.get_all_inbounds()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching inbounds: {e}")
            raise RemnaWaveAPIError(f"Error fetching inbounds: {str(e)}")
    
    # ======================
    # NODES API
    # ======================
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Get all nodes"""
        try:
            log.info("Fetching nodes")
            response: GetAllNodesResponseDto = await self.sdk.nodes.get_all_nodes()
            # GetAllNodesResponseDto имеет поле root вместо nodes
            return {"response": [node.model_dump(by_alias=True) for node in response.root]}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching nodes: {e}")
            raise RemnaWaveAPIError(f"Error fetching nodes: {str(e)}")
    
    async def get_node(self, node_uuid: str) -> Dict[str, Any]:
        """Get node by UUID"""
        try:
            log.info(f"Fetching node {node_uuid}")
            response = await self.sdk.nodes.get_one_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching node: {e}")
            raise RemnaWaveAPIError(f"Error fetching node: {str(e)}")
    
    async def get_node_stats(self, node_uuid: str) -> Dict[str, Any]:
        """Get node statistics"""
        try:
            log.info(f"Fetching stats for node {node_uuid}")
            # SDK пока не имеет этого метода, используем базовую информацию
            response = await self.sdk.nodes.get_one_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching node stats: {e}")
            raise RemnaWaveAPIError(f"Error fetching node stats: {str(e)}")
    
    async def create_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new node"""
        try:
            log.info("Creating node")
            from remnawave.models import CreateNodeRequestDto
            create_dto = CreateNodeRequestDto(**node_data)
            response = await self.sdk.nodes.create_node(body=create_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error creating node: {e}")
            raise RemnaWaveAPIError(f"Error creating node: {str(e)}")
    
    async def update_node(self, update_data) -> Dict[str, Any]:
        """Update node"""
        try:
            log.info(f"Updating node {update_data.uuid}")
            response = await self.sdk.nodes.update_node(body=update_data)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error updating node: {e}")
            raise RemnaWaveAPIError(f"Error updating node: {str(e)}")
    
    async def enable_node(self, node_uuid: str) -> Dict[str, Any]:
        """Enable node"""
        try:
            log.info(f"Enabling node {node_uuid}")
            response = await self.sdk.nodes.enable_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True) if hasattr(response, 'model_dump') else {}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error enabling node: {e}")
            raise RemnaWaveAPIError(f"Error enabling node: {str(e)}")
    
    async def disable_node(self, node_uuid: str) -> Dict[str, Any]:
        """Disable node"""
        try:
            log.info(f"Disabling node {node_uuid}")
            response = await self.sdk.nodes.disable_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True) if hasattr(response, 'model_dump') else {}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error disabling node: {e}")
            raise RemnaWaveAPIError(f"Error disabling node: {str(e)}")
    
    async def restart_node(self, node_uuid: str) -> Dict[str, Any]:
        """Restart node"""
        try:
            log.info(f"Restarting node {node_uuid}")
            response = await self.sdk.nodes.restart_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True) if hasattr(response, 'model_dump') else {}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error restarting node: {e}")
            raise RemnaWaveAPIError(f"Error restarting node: {str(e)}")
    
    async def delete_node(self, node_uuid: str) -> Dict[str, Any]:
        """Delete node"""
        try:
            log.info(f"Deleting node {node_uuid}")
            response = await self.sdk.nodes.delete_node(uuid=node_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error deleting node: {e}")
            raise RemnaWaveAPIError(f"Error deleting node: {str(e)}")
    
    # ======================
    # DEVICES (HWID) API
    # ======================
    
    async def get_devices(self) -> Dict[str, Any]:
        """Get all devices (HWID)"""
        try:
            log.info("Fetching all devices")
            response = await self.sdk.hwid.get_hwid_users()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching devices: {e}")
            raise RemnaWaveAPIError(f"Error fetching devices: {str(e)}")
    
    async def get_user_devices(self, user_uuid: str) -> Dict[str, Any]:
        """Get user devices (HWID)"""
        try:
            log.info(f"Fetching devices for user {user_uuid}")
            # SDK принимает позиционный аргумент, не keyword
            response = await self.sdk.hwid.get_hwid_user(user_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching devices: {e}")
            raise RemnaWaveAPIError(f"Error fetching devices: {str(e)}")
    
    async def get_all_devices_stats(self) -> Dict[str, Any]:
        """Get statistics for all devices"""
        try:
            log.info("Fetching all devices statistics")
            response = await self.sdk.hwid.get_hwid_stats()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching device stats: {e}")
            raise RemnaWaveAPIError(f"Error fetching device stats: {str(e)}")
    
    async def delete_device(self, user_uuid: str, hwid: str) -> Dict[str, Any]:
        """Delete device"""
        try:
            log.info(f"Deleting device {hwid} for user {user_uuid}")
            from uuid import UUID
            from remnawave.models.hwid import DeleteUserHwidDeviceRequestDto
            
            # Создаём DTO объект для удаления устройства
            # DTO ожидает UUID объект, а не строку
            delete_dto = DeleteUserHwidDeviceRequestDto(
                user_uuid=UUID(user_uuid),
                hwid=str(hwid)
            )
            
            response = await self.sdk.hwid.delete_hwid_to_user(body=delete_dto)
            return {"response": response.model_dump(by_alias=True) if hasattr(response, 'model_dump') else {"success": True}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error deleting device: {e}")
            raise RemnaWaveAPIError(f"Error deleting device: {str(e)}")
    
    # ======================
    # SQUADS API
    # ======================
    
    async def get_squads(self) -> Dict[str, Any]:
        """Get all squads"""
        try:
            log.info("Fetching squads")
            # Используем get_internal_squads вместо get_all_internal_squads
            response = await self.sdk.internal_squads.get_internal_squads()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching squads: {e}")
            raise RemnaWaveAPIError(f"Error fetching squads: {str(e)}")
    
    async def get_squad(self, squad_uuid: str) -> Dict[str, Any]:
        """Get squad by UUID"""
        try:
            log.info(f"Fetching squad {squad_uuid}")
            response = await self.sdk.internal_squads.get_internal_squad_by_uuid(uuid=squad_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching squad: {e}")
            raise RemnaWaveAPIError(f"Error fetching squad: {str(e)}")
    
    async def create_squad(self, squad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new squad"""
        try:
            log.info("Creating squad")
            from remnawave.models import CreateInternalSquadRequestDto
            create_dto = CreateInternalSquadRequestDto(**squad_data)
            response = await self.sdk.internal_squads.create_internal_squad(body=create_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error creating squad: {e}")
            raise RemnaWaveAPIError(f"Error creating squad: {str(e)}")
    
    async def update_squad(self, squad_uuid: str, squad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update squad"""
        try:
            log.info(f"Updating squad {squad_uuid}")
            from remnawave.models import UpdateInternalSquadRequestDto
            update_dto = UpdateInternalSquadRequestDto(**squad_data)
            response = await self.sdk.internal_squads.update_internal_squad(uuid=squad_uuid, body=update_dto)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error updating squad: {e}")
            raise RemnaWaveAPIError(f"Error updating squad: {str(e)}")
    
    async def delete_squad(self, squad_uuid: str) -> Dict[str, Any]:
        """Delete squad"""
        try:
            log.info(f"Deleting squad {squad_uuid}")
            response = await self.sdk.internal_squads.delete_internal_squad(uuid=squad_uuid)
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error deleting squad: {e}")
            raise RemnaWaveAPIError(f"Error deleting squad: {str(e)}")
    
    # ======================
    # SYSTEM API
    # ======================
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            log.info("Fetching system statistics")
            response: GetStatsResponseDto = await self.sdk.system.get_stats()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching system stats: {e}")
            raise RemnaWaveAPIError(f"Error fetching system stats: {str(e)}")
    
    async def get_bandwidth_stats(self) -> Dict[str, Any]:
        """Get bandwidth statistics"""
        try:
            log.info("Fetching bandwidth statistics")
            response = await self.sdk.system.get_bandwidth_stats()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching bandwidth stats: {e}")
            raise RemnaWaveAPIError(f"Error fetching bandwidth stats: {str(e)}")
    
    async def get_nodes_statistics(self) -> Dict[str, Any]:
        """Get nodes statistics"""
        try:
            log.info("Fetching nodes statistics")
            response = await self.sdk.system.get_nodes_statistics()
            return {"response": response.model_dump(by_alias=True)}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error fetching nodes statistics: {e}")
            raise RemnaWaveAPIError(f"Error fetching nodes statistics: {str(e)}")
    
    async def restart_xray(self) -> Dict[str, Any]:
        """Restart Xray service"""
        try:
            log.info("Restarting Xray service")
            response = await self.sdk.system.restart_xray()
            return {"response": {"success": True, "message": "Xray restarted"}}
        except ApiError as e:
            raise RemnaWaveAPIError(f"API error: {e.error.code}", e.error.status)
        except Exception as e:
            log.exception(f"Error restarting Xray: {e}")
            raise RemnaWaveAPIError(f"Error restarting Xray: {str(e)}")
    
    # ======================
    # MASS OPERATIONS
    # ======================
    
    async def mass_activate_users(self) -> Dict[str, Any]:
        """Activate all users"""
        try:
            log.info("Mass activating users")
            # Get all users first
            response = await self.get_users(page=1, limit=1000)
            users = response.get('response', {}).get('users', [])
            
            success_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    uuid = user.get('uuid')
                    if uuid:
                        await self.update_user(uuid, {"status": "ACTIVE"})
                        success_count += 1
                except Exception:
                    failed_count += 1
            
            return {
                "response": {
                    "successCount": success_count,
                    "failedCount": failed_count
                }
            }
        except Exception as e:
            log.exception(f"Error in mass activate: {e}")
            raise RemnaWaveAPIError(f"Error in mass activate: {str(e)}")
    
    async def mass_deactivate_users(self) -> Dict[str, Any]:
        """Deactivate all users"""
        try:
            log.info("Mass deactivating users")
            response = await self.get_users(page=1, limit=1000)
            users = response.get('response', {}).get('users', [])
            
            success_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    uuid = user.get('uuid')
                    if uuid:
                        await self.update_user(uuid, {"status": "DISABLED"})
                        success_count += 1
                except Exception:
                    failed_count += 1
            
            return {
                "response": {
                    "successCount": success_count,
                    "failedCount": failed_count
                }
            }
        except Exception as e:
            log.exception(f"Error in mass deactivate: {e}")
            raise RemnaWaveAPIError(f"Error in mass deactivate: {str(e)}")
    
    async def mass_reset_traffic(self) -> Dict[str, Any]:
        """Reset traffic for all users"""
        try:
            log.info("Mass resetting traffic")
            response = await self.get_users(page=1, limit=1000)
            users = response.get('response', {}).get('users', [])
            
            success_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    uuid = user.get('uuid')
                    if uuid:
                        await self.reset_user_traffic(uuid)
                        success_count += 1
                except Exception:
                    failed_count += 1
            
            return {
                "response": {
                    "successCount": success_count,
                    "failedCount": failed_count
                }
            }
        except Exception as e:
            log.exception(f"Error in mass reset traffic: {e}")
            raise RemnaWaveAPIError(f"Error in mass reset traffic: {str(e)}")
    
    async def mass_extend_users(self, days: int) -> Dict[str, Any]:
        """Extend all users subscription by N days"""
        try:
            log.info(f"Mass extending users by {days} days")
            response = await self.get_users(page=1, limit=1000)
            users = response.get('response', {}).get('users', [])
            
            success_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    uuid = user.get('uuid')
                    if uuid:
                        await self.extend_user_subscription(uuid, days)
                        success_count += 1
                except Exception:
                    failed_count += 1
            
            return {
                "response": {
                    "successCount": success_count,
                    "failedCount": failed_count
                }
            }
        except Exception as e:
            log.exception(f"Error in mass extend: {e}")
            raise RemnaWaveAPIError(f"Error in mass extend: {str(e)}")


# Создаём глобальный экземпляр клиента
api_client = RemnaWaveAPIClient()
