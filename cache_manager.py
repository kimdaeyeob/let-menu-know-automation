# -*- coding: utf-8 -*-
"""
Cache manager module for storing and loading menu data.
"""
import json
import os
import datetime
from pathlib import Path


def get_cache_file_path(cache_file='menu_cache.json'):
    """
    Get the full path to the cache file.
    
    Args:
        cache_file (str): Cache file name
        
    Returns:
        str: Full path to cache file
    """
    return os.path.join(os.getcwd(), cache_file)


def save_menu_cache(date, image_url, username, cache_file='menu_cache.json'):
    """
    Save menu data to cache file.
    
    Args:
        date (datetime.date): Date of the menu
        image_url (str): URL of the menu image
        username (str): Instagram username
        cache_file (str): Cache file name
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cache_path = get_cache_file_path(cache_file)
        cache_data = {}
        
        # Load existing cache if it exists
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not read existing cache file: {e}")
                cache_data = {}
        
        # Update cache with new data
        date_str = date.isoformat() if isinstance(date, datetime.date) else str(date)
        cache_data[date_str] = {
            "image_url": image_url,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "username": username
        }
        
        # Save cache
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"Cache saved for date {date_str}")
        return True
        
    except Exception as e:
        print(f"Error saving cache: {e}")
        return False


def load_menu_cache(date, cache_file='menu_cache.json'):
    """
    Load menu data from cache file.
    
    Args:
        date (datetime.date): Date to load from cache
        cache_file (str): Cache file name
        
    Returns:
        dict: Cache data with 'image_url', 'timestamp', 'username' if found, None otherwise
    """
    try:
        cache_path = get_cache_file_path(cache_file)
        
        if not os.path.exists(cache_path):
            print(f"Cache file not found: {cache_path}")
            return None
        
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        date_str = date.isoformat() if isinstance(date, datetime.date) else str(date)
        
        if date_str in cache_data:
            print(f"Cache found for date {date_str}")
            return cache_data[date_str]
        else:
            print(f"No cache found for date {date_str}")
            return None
            
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading cache: {e}")
        return None

