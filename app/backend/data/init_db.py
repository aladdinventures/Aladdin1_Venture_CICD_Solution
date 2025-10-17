#!/usr/bin/env python3
"""
RenovAI Canada - Database Initialization Script
Copyright (c) 2025 Saeed Alaediny. All rights reserved.

This script initializes the SQLite database with sample renovation pricing data
for the Greater Vancouver Area.
"""

import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'pricing_timeline.db')

def init_database():
    """Initialize the database with sample renovation data."""
    
    # Remove existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")
    
    # Create new database connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create pricing_timeline table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pricing_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_type TEXT NOT NULL,
            finish_level TEXT NOT NULL,
            cost_per_sqft REAL NOT NULL,
            avg_duration_weeks INTEGER NOT NULL,
            suggested_materials TEXT,
            description TEXT,
            UNIQUE(project_type, finish_level)
        )
    ''')
    
    # Sample renovation data for Greater Vancouver Area
    renovation_data = [
        # Kitchen Renovations
        ('kitchen', 'basic', 150.0, 4, 'Laminate countertops, Stock cabinets, Standard appliances, Vinyl flooring', 
         'Basic kitchen renovation with functional updates and standard materials'),
        ('kitchen', 'standard', 250.0, 6, 'Granite countertops, Semi-custom cabinets, Mid-range appliances, Ceramic tile flooring', 
         'Standard kitchen renovation with quality materials and modern finishes'),
        ('kitchen', 'premium', 400.0, 8, 'Quartz countertops, Custom cabinets, High-end appliances, Hardwood flooring, LED lighting', 
         'Premium kitchen renovation with luxury materials and custom features'),
        
        # Bathroom Renovations
        ('bathroom', 'basic', 200.0, 3, 'Acrylic tub/shower, Standard vanity, Ceramic tile, Basic fixtures', 
         'Basic bathroom renovation with essential updates'),
        ('bathroom', 'standard', 300.0, 4, 'Fiberglass tub/shower, Custom vanity, Porcelain tile, Mid-range fixtures', 
         'Standard bathroom renovation with modern amenities'),
        ('bathroom', 'premium', 500.0, 6, 'Walk-in shower with glass enclosure, Custom double vanity, Natural stone tile, High-end fixtures, Heated floors', 
         'Premium bathroom renovation with spa-like features'),
        
        # Basement Renovations
        ('basement', 'basic', 80.0, 6, 'Drywall finishing, Laminate flooring, Basic lighting, Paint', 
         'Basic basement finishing for additional living space'),
        ('basement', 'standard', 120.0, 8, 'Drywall with insulation, Engineered hardwood, Recessed lighting, Built-in storage', 
         'Standard basement renovation with comfort features'),
        ('basement', 'premium', 180.0, 10, 'Full insulation, Hardwood flooring, Custom lighting, Wet bar, Home theater setup', 
         'Premium basement renovation with entertainment features'),
        
        # Full Home Renovations
        ('full_home', 'basic', 100.0, 12, 'Paint, Flooring updates, Fixture replacements, Minor repairs', 
         'Basic full home refresh with cosmetic updates'),
        ('full_home', 'standard', 175.0, 16, 'Kitchen and bathroom updates, New flooring throughout, Updated electrical and plumbing, Fresh paint', 
         'Standard full home renovation with major system updates'),
        ('full_home', 'premium', 300.0, 24, 'Complete kitchen and bathroom remodels, Hardwood floors, Smart home integration, High-end finishes throughout', 
         'Premium full home transformation with luxury upgrades'),
        
        # Home Additions
        ('addition', 'basic', 200.0, 12, 'Standard framing, Basic insulation, Drywall, Standard windows and doors', 
         'Basic home addition with functional space'),
        ('addition', 'standard', 300.0, 16, 'Quality framing, Enhanced insulation, Custom windows, Hardwood floors', 
         'Standard home addition with quality construction'),
        ('addition', 'premium', 450.0, 20, 'Premium framing, High-efficiency insulation, Custom windows and doors, Luxury finishes, Integrated HVAC', 
         'Premium home addition with architectural features'),
    ]
    
    # Insert sample data
    cursor.executemany('''
        INSERT INTO pricing_timeline 
        (project_type, finish_level, cost_per_sqft, avg_duration_weeks, suggested_materials, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', renovation_data)
    
    conn.commit()
    
    # Verify data insertion
    cursor.execute('SELECT COUNT(*) FROM pricing_timeline')
    count = cursor.fetchone()[0]
    print(f"Database initialized successfully with {count} records")
    
    # Display sample data
    print("\nSample data:")
    cursor.execute('SELECT project_type, finish_level, cost_per_sqft, avg_duration_weeks FROM pricing_timeline LIMIT 5')
    for row in cursor.fetchall():
        print(f"  {row[0]:15} | {row[1]:10} | ${row[2]:6.2f}/sqft | {row[3]:2} weeks")
    
    conn.close()
    print(f"\nDatabase created at: {DB_PATH}")

if __name__ == '__main__':
    init_database()

