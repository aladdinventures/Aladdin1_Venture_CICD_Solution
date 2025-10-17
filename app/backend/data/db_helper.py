"""
RenovAI Canada - Database Helper Module
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This module provides helper functions for accessing the pricing and timeline database.
"""

import sqlite3
import os
from typing import Optional, Dict, List

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'pricing_timeline.db')

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn

def get_estimate_data(project_type: str, finish_level: str) -> Optional[Dict]:
    """
    Retrieve estimation data for a specific project type and finish level.
    
    Args:
        project_type: Type of renovation project (kitchen, bathroom, basement, full_home, addition)
        finish_level: Quality level (basic, standard, premium)
    
    Returns:
        Dictionary containing estimation data or None if not found
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT project_type, finish_level, cost_per_sqft, avg_duration_weeks, 
               suggested_materials, description
        FROM pricing_timeline
        WHERE LOWER(project_type) = LOWER(?) AND LOWER(finish_level) = LOWER(?)
    ''', (project_type, finish_level))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'project_type': row['project_type'],
            'finish_level': row['finish_level'],
            'cost_per_sqft': row['cost_per_sqft'],
            'avg_duration_weeks': row['avg_duration_weeks'],
            'suggested_materials': row['suggested_materials'].split(', ') if row['suggested_materials'] else [],
            'description': row['description']
        }
    
    return None

def get_all_project_types() -> List[str]:
    """
    Get a list of all available project types.
    
    Returns:
        List of unique project types
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT project_type FROM pricing_timeline ORDER BY project_type')
    
    project_types = [row['project_type'] for row in cursor.fetchall()]
    conn.close()
    
    return project_types

def get_all_finish_levels() -> List[str]:
    """
    Get a list of all available finish levels.
    
    Returns:
        List of unique finish levels
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT finish_level FROM pricing_timeline ORDER BY finish_level')
    
    finish_levels = [row['finish_level'] for row in cursor.fetchall()]
    conn.close()
    
    return finish_levels

def calculate_estimate(project_type: str, finish_level: str, size_sqft: float) -> Optional[Dict]:
    """
    Calculate cost and timeline estimate for a renovation project.
    
    Args:
        project_type: Type of renovation project
        finish_level: Quality level
        size_sqft: Size of the project in square feet
    
    Returns:
        Dictionary containing the complete estimate or None if data not found
    """
    data = get_estimate_data(project_type, finish_level)
    
    if not data:
        return None
    
    # Calculate total cost
    total_cost = data['cost_per_sqft'] * size_sqft
    
    # Adjust timeline based on project size (larger projects may take proportionally longer)
    base_weeks = data['avg_duration_weeks']
    
    # Size adjustment factor (for very large projects, add extra time)
    if size_sqft > 1000:
        size_factor = 1 + ((size_sqft - 1000) / 5000)  # Add time for large projects
        adjusted_weeks = int(base_weeks * size_factor)
    else:
        adjusted_weeks = base_weeks
    
    return {
        'project_type': data['project_type'],
        'size_sqft': size_sqft,
        'finish_level': data['finish_level'],
        'estimated_cost': round(total_cost, 2),
        'estimated_cost_range': {
            'min': round(total_cost * 0.9, 2),  # -10%
            'max': round(total_cost * 1.15, 2)  # +15%
        },
        'estimated_timeline_weeks': adjusted_weeks,
        'cost_per_sqft': data['cost_per_sqft'],
        'suggested_materials': data['suggested_materials'],
        'description': data['description']
    }

