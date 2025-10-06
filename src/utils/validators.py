"""
Validators for user input
"""
import re
from typing import Optional


class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Имя пользователя не может быть пустым"
        
        if len(username) < 3:
            return False, "Имя пользователя должно содержать минимум 3 символа"
        
        if len(username) > 50:
            return False, "Имя пользователя не может превышать 50 символов"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Имя пользователя может содержать только буквы, цифры, '_' и '-'"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """
        Validate email address
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email не может быть пустым"
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Неверный формат email"
        
        return True, None
    
    @staticmethod
    def validate_pin(pin: str, expected_pin: str) -> tuple[bool, Optional[str]]:
        """
        Validate PIN code
        
        Args:
            pin: PIN to validate
            expected_pin: Expected PIN value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not pin:
            return False, "PIN не может быть пустым"
        
        if pin != expected_pin:
            return False, "Неверный PIN код"
        
        return True, None
    
    @staticmethod
    def validate_days(days_str: str) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Validate days input
        
        Args:
            days_str: Days string to validate
            
        Returns:
            Tuple of (is_valid, days_value, error_message)
        """
        try:
            days = int(days_str)
            if days <= 0:
                return False, None, "Количество дней должно быть положительным числом"
            if days > 3650:  # ~10 years
                return False, None, "Количество дней не может превышать 3650"
            return True, days, None
        except ValueError:
            return False, None, "Неверный формат. Введите число"
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> tuple[bool, Optional[str]]:
        """
        Validate UUID format
        
        Args:
            uuid_str: UUID string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not uuid_str:
            return False, "UUID не может быть пустым"
        
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, uuid_str.lower()):
            return False, "Неверный формат UUID"
        
        return True, None
    
    @staticmethod
    def validate_port(port_str: str) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Validate port number
        
        Args:
            port_str: Port string to validate
            
        Returns:
            Tuple of (is_valid, port_value, error_message)
        """
        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                return False, None, "Порт должен быть в диапазоне 1-65535"
            return True, port, None
        except ValueError:
            return False, None, "Неверный формат порта. Введите число"
    
    @staticmethod
    def validate_ip_or_domain(address: str) -> tuple[bool, Optional[str]]:
        """
        Validate IP address or domain name
        
        Args:
            address: Address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not address:
            return False, "Адрес не может быть пустым"
        
        # Check if it's a valid IP
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ip_pattern, address):
            parts = address.split('.')
            if all(0 <= int(part) <= 255 for part in parts):
                return True, None
            return False, "Неверный IP адрес"
        
        # Check if it's a valid domain
        domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if re.match(domain_pattern, address):
            return True, None
        
        return False, "Неверный формат адреса (IP или домен)"
    
    @staticmethod
    def validate_traffic_limit(limit_str: str) -> tuple[bool, Optional[int], Optional[str]]:
        """
        Validate traffic limit in GB
        
        Args:
            limit_str: Limit string to validate (in GB)
            
        Returns:
            Tuple of (is_valid, bytes_value, error_message)
        """
        if limit_str.lower() in ['unlimited', 'inf', '∞', '0']:
            return True, 0, None
        
        try:
            gb = float(limit_str)
            if gb < 0:
                return False, None, "Лимит не может быть отрицательным"
            bytes_value = int(gb * 1024 * 1024 * 1024)
            return True, bytes_value, None
        except ValueError:
            return False, None, "Неверный формат. Введите число (GB) или 'unlimited'"


# Create global validators instance
validators = Validators()
