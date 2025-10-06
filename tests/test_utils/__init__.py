"""
Tests for validators
"""
import pytest
from src.utils.validators import validators


def test_validate_username_valid():
    """Test valid username"""
    is_valid, error = validators.validate_username("testuser123")
    assert is_valid is True
    assert error is None


def test_validate_username_too_short():
    """Test username too short"""
    is_valid, error = validators.validate_username("ab")
    assert is_valid is False
    assert "минимум 3 символа" in error


def test_validate_username_invalid_chars():
    """Test username with invalid characters"""
    is_valid, error = validators.validate_username("test user!")
    assert is_valid is False
    assert "может содержать только" in error


def test_validate_email_valid():
    """Test valid email"""
    is_valid, error = validators.validate_email("test@example.com")
    assert is_valid is True
    assert error is None


def test_validate_email_invalid():
    """Test invalid email"""
    is_valid, error = validators.validate_email("invalid-email")
    assert is_valid is False
    assert "Неверный формат" in error


def test_validate_pin_correct():
    """Test correct PIN"""
    is_valid, error = validators.validate_pin("1234", "1234")
    assert is_valid is True
    assert error is None


def test_validate_pin_incorrect():
    """Test incorrect PIN"""
    is_valid, error = validators.validate_pin("0000", "1234")
    assert is_valid is False
    assert "Неверный PIN" in error


def test_validate_days_valid():
    """Test valid days"""
    is_valid, days, error = validators.validate_days("30")
    assert is_valid is True
    assert days == 30
    assert error is None


def test_validate_days_negative():
    """Test negative days"""
    is_valid, days, error = validators.validate_days("-5")
    assert is_valid is False
    assert error is not None


def test_validate_port_valid():
    """Test valid port"""
    is_valid, port, error = validators.validate_port("8080")
    assert is_valid is True
    assert port == 8080
    assert error is None


def test_validate_port_out_of_range():
    """Test port out of range"""
    is_valid, port, error = validators.validate_port("70000")
    assert is_valid is False
    assert "диапазоне 1-65535" in error
