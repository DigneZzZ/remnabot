"""
Data schemas and models for Remnawave API
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: Optional[str] = None
    status: str = "active"
    traffic_limit: Optional[int] = None
    expires_at: Optional[datetime] = None


class UserCreate(UserBase):
    """User creation model"""
    password: str


class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None
    traffic_limit: Optional[int] = None
    expires_at: Optional[datetime] = None


class UserResponse(UserBase):
    """User response model"""
    uuid: str
    used_traffic: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HostBase(BaseModel):
    """Base host model"""
    name: str
    address: str
    port: int
    remark: Optional[str] = None


class HostCreate(HostBase):
    """Host creation model"""
    pass


class HostUpdate(BaseModel):
    """Host update model"""
    name: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None
    remark: Optional[str] = None


class HostResponse(HostBase):
    """Host response model"""
    uuid: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NodeBase(BaseModel):
    """Base node model"""
    name: str
    address: str
    port: int


class NodeCreate(NodeBase):
    """Node creation model"""
    pass


class NodeUpdate(BaseModel):
    """Node update model"""
    name: Optional[str] = None
    address: Optional[str] = None
    port: Optional[int] = None


class NodeResponse(NodeBase):
    """Node response model"""
    uuid: str
    status: str
    users_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NodeStatsResponse(BaseModel):
    """Node statistics response"""
    total_traffic: int = 0
    upload_traffic: int = 0
    download_traffic: int = 0
    users_online: int = 0
    total_users: int = 0


class DeviceResponse(BaseModel):
    """Device (HWID) response model"""
    uuid: str
    user_uuid: str
    device_id: str
    device_name: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SquadBase(BaseModel):
    """Base squad model"""
    name: str
    description: Optional[str] = None


class SquadCreate(SquadBase):
    """Squad creation model"""
    pass


class SquadUpdate(BaseModel):
    """Squad update model"""
    name: Optional[str] = None
    description: Optional[str] = None


class SquadResponse(SquadBase):
    """Squad response model"""
    uuid: str
    members_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    """System statistics model"""
    total_users: int = 0
    active_users: int = 0
    total_traffic: int = 0
    nodes_count: int = 0
    hosts_count: int = 0


class DeviceStats(BaseModel):
    """Device statistics model"""
    total_devices: int = 0
    active_devices: int = 0
    top_users: List[dict] = []


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[dict]
    total: int
    page: int
    limit: int
    total_pages: int
