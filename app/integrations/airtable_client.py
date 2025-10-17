"""
RenovAI Canada - Airtable Integration Module
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This module provides integration with Airtable for lead storage.
For MVP, this uses mock responses. Real API integration will be added in Beta.
"""

import os
from typing import Dict, Optional
from datetime import datetime
import json

class AirtableClient:
    """Client for interacting with Airtable API."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None, table_name: str = "Leads"):
        """
        Initialize Airtable client.
        
        Args:
            api_key: Airtable API key (from environment variable)
            base_id: Airtable base ID (from environment variable)
            table_name: Name of the table to store leads
        """
        self.api_key = api_key or os.getenv('AIRTABLE_API_KEY', '')
        self.base_id = base_id or os.getenv('AIRTABLE_BASE_ID', '')
        self.table_name = table_name
        self.use_mock = not (self.api_key and self.base_id)
        
        if self.use_mock:
            print("⚠️  Using mock Airtable integration (no API key/base ID provided)")
            # Create a local JSON file to simulate lead storage
            self.mock_file = os.path.join(os.path.dirname(__file__), 'mock_leads.json')
            if not os.path.exists(self.mock_file):
                with open(self.mock_file, 'w') as f:
                    json.dump([], f)
    
    def create_lead(self, lead_data: Dict) -> Dict:
        """
        Create a new lead record in Airtable.
        
        Args:
            lead_data: Dictionary containing lead information
        
        Returns:
            Dictionary with creation status and record ID
        """
        if self.use_mock:
            return self._mock_create_lead(lead_data)
        
        # Real Airtable API integration would go here
        # For MVP, we use mock implementation
        return self._mock_create_lead(lead_data)
    
    def _mock_create_lead(self, lead_data: Dict) -> Dict:
        """
        Mock implementation of lead creation for MVP testing.
        
        Args:
            lead_data: Dictionary containing lead information
        
        Returns:
            Dictionary with creation status and mock record ID
        """
        # Add timestamp and generate mock ID
        lead_record = {
            'id': f"rec{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'fields': lead_data
        }
        
        # Store in local JSON file
        try:
            with open(self.mock_file, 'r') as f:
                leads = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            leads = []
        
        leads.append(lead_record)
        
        with open(self.mock_file, 'w') as f:
            json.dump(leads, f, indent=2)
        
        print(f"✅ Mock lead created: {lead_record['id']}")
        
        return {
            'success': True,
            'record_id': lead_record['id'],
            'message': 'Lead stored successfully (mock mode)',
            'created_at': lead_record['created_at']
        }
    
    def get_all_leads(self) -> list:
        """
        Retrieve all leads (mock implementation for testing).
        
        Returns:
            List of all lead records
        """
        if self.use_mock:
            try:
                with open(self.mock_file, 'r') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                return []
        
        # Real Airtable API would be called here
        return []

# Example usage and testing
if __name__ == '__main__':
    client = AirtableClient()
    
    # Test lead creation
    test_lead = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1-604-555-0123',
        'project_type': 'kitchen',
        'size_sqft': 200,
        'finish_level': 'premium',
        'postal_code': 'V6B 1A1',
        'estimated_cost': 80000,
        'project_notes': 'Looking to renovate kitchen with modern appliances'
    }
    
    result = client.create_lead(test_lead)
    print(f"\nTest Result: {result}")
    
    # Display all leads
    all_leads = client.get_all_leads()
    print(f"\nTotal leads stored: {len(all_leads)}")

