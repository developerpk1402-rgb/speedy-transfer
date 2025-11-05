from django import template
from datetime import datetime
import locale

register = template.Library()

@register.filter
def format_date(value):
    """Format datetime to readable date format"""
    if not value:
        return ""
    
    try:
        if isinstance(value, str):
            # Try to parse the datetime string
            if 'T' in value:
                # Handle ISO format like "2025-08-17T17:20"
                dt = datetime.fromisoformat(value)
            elif ' ' in value:
                # Handle format like "2025-08-17 17:20"
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M')
            else:
                # Try other common formats
                dt = datetime.strptime(value, '%Y-%m-%d')
        else:
            dt = value
        
        # Format as "Monday, January 15, 2025"
        return dt.strftime('%A, %B %d, %Y')
    except Exception:
        return str(value)

@register.filter
def format_time(value):
    """Format datetime to readable time format"""
    if not value:
        return ""
    
    try:
        if isinstance(value, str):
            # Try to parse the datetime string
            if 'T' in value:
                # Handle ISO format like "2025-08-17T17:20"
                dt = datetime.fromisoformat(value)
            elif ' ' in value:
                # Handle format like "2025-08-17 17:20"
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M')
            else:
                # Try other common formats
                dt = datetime.strptime(value, '%Y-%m-%d')
        else:
            dt = value
        
        # Format as "8:00 PM"
        return dt.strftime('%I:%M %p')
    except Exception:
        return str(value)

@register.filter
def format_currency(value, currency="USD"):
    """Format number as currency"""
    if value is None:
        return f"{currency} 0.00"
    
    try:
        amount = float(value)
        return f"{currency} {amount:.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"
