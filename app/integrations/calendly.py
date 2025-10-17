"""
RenovAI Canada - Calendly Integration Module
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This module provides Calendly integration for consultation booking.
"""

import os
from typing import Optional

class CalendlyIntegration:
    """Handler for Calendly consultation booking links."""
    
    def __init__(self, calendly_link: Optional[str] = None):
        """
        Initialize Calendly integration.
        
        Args:
            calendly_link: Direct link to Calendly booking page
        """
        self.calendly_link = calendly_link or os.getenv('CALENDLY_LINK', 'https://calendly.com/renovai-canada/consultation')
    
    def get_booking_link(self, project_type: Optional[str] = None) -> str:
        """
        Get the Calendly booking link.
        
        Args:
            project_type: Optional project type for future dynamic link generation
        
        Returns:
            Calendly booking URL
        """
        # For MVP, we return a static link
        # In future phases, this could be dynamic based on project type
        return self.calendly_link
    
    def get_booking_message(self, project_type: Optional[str] = None) -> str:
        """
        Generate a friendly message with the booking link.
        
        Args:
            project_type: Optional project type for personalized message
        
        Returns:
            Formatted message with booking link
        """
        base_message = (
            "📅 **Ready to discuss your renovation project?**\n\n"
            "Book a free consultation with our renovation experts to get a detailed quote "
            "and discuss your project in depth.\n\n"
            f"👉 [Schedule Your Consultation]({self.calendly_link})\n\n"
            "During the consultation, we'll:\n"
            "- Review your project requirements in detail\n"
            "- Provide a comprehensive cost breakdown\n"
            "- Discuss timeline and scheduling options\n"
            "- Answer all your questions\n\n"
            "We look forward to helping you bring your renovation vision to life!"
        )
        
        return base_message

# Example usage
if __name__ == '__main__':
    calendly = CalendlyIntegration()
    print(calendly.get_booking_message())
    print(f"\nDirect link: {calendly.get_booking_link()}")

