import pytest
from app import home_page

def test_home_page():
    assert home_page('California') == 'Human Resources Management System - State of California'