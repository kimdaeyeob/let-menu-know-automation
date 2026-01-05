# -*- coding: utf-8 -*-
"""
Instagram crawler module for fetching menu posts.
"""
import datetime
import instaloader


def get_todays_menu_post(username):
    """
    Fetches posts and finds the one that matches TODAY's date in the CAPTION.
    Prioritizes images that look like text (Menu) over food photos.
    
    Args:
        username (str): Instagram username to crawl
        
    Returns:
        Post object if found, None otherwise
    """
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Get today's date in KST
        kst_offset = datetime.timedelta(hours=9)
        now_kst = datetime.datetime.now(datetime.timezone.utc) + kst_offset
        today_date = now_kst.date()
        
        # Format date string to look for in caption (e.g., "12월 1일", "12월1일")
        # We'll check for both "M월 D일" and "M월D일" to be safe
        date_str_1 = f"{today_date.month}월 {today_date.day}일"
        date_str_2 = f"{today_date.month}월{today_date.day}일"
        
        print(f"Looking for posts with caption containing '{date_str_1}' or '{date_str_2}'...")

        candidates = []
        
        # Iterate through recent 5 posts
        count = 0
        for post in profile.get_posts():
            if count >= 5:
                break
            
            caption = post.caption if post.caption else ""
            
            # Check if the caption mentions today's date
            if date_str_1 in caption or date_str_2 in caption:
                print(f"Found candidate post from {post.date}: {caption[:30]}...")
                
                # Score the candidate to pick the best one (Menu Text > Food Photo)
                score = 0
                
                # Priority 1: Accessibility Caption indicates text
                acc_caption = post.accessibility_caption if post.accessibility_caption else ""
                if "text" in acc_caption.lower() or "says" in acc_caption.lower():
                    score += 10
                    print("  -> High probability: Accessibility caption mentions text.")
                
                # Priority 2: Single Image (GraphImage) is usually the menu text
                # Food photos are often carousels (GraphSidecar)
                if post.typename == 'GraphImage':
                    score += 5
                    print("  -> Medium probability: Single image type.")
                
                candidates.append((score, post))
            
            count += 1
            
        if not candidates:
            print("No posts found matching today's date in the caption.")
            return None
        
        # Sort candidates by score (descending)
        # If scores are tied, the sort is stable (preserves original order, which is Newest->Oldest).
        # But we usually want the "Menu Text" which might be older or newer?
        # Actually, based on user feedback, the Menu Text is often uploaded *before* the food photo.
        # But with the scoring, the "Text" image should win regardless of order.
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        best_match = candidates[0][1]
        print(f"Selected best match with score {candidates[0][0]}")
        return best_match

    except Exception as e:
        print(f"Error fetching post: {e}")
        return None


def find_menu_post_by_date(username, target_date):
    """
    Fetches posts and finds the one that matches a specific date in the CAPTION.
    This function allows querying past or future dates for extensibility.
    
    Args:
        username (str): Instagram username to crawl
        target_date (datetime.date): Target date to search for
        
    Returns:
        Post object if found, None otherwise
    """
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Format date string to look for in caption (e.g., "12월 1일", "12월1일")
        date_str_1 = f"{target_date.month}월 {target_date.day}일"
        date_str_2 = f"{target_date.month}월{target_date.day}일"
        
        print(f"Looking for posts with caption containing '{date_str_1}' or '{date_str_2}'...")

        candidates = []
        
        # Iterate through recent posts (extend search range for past dates)
        count = 0
        max_posts = 20 if target_date < datetime.date.today() else 5
        
        for post in profile.get_posts():
            if count >= max_posts:
                break
            
            caption = post.caption if post.caption else ""
            
            # Check if the caption mentions the target date
            if date_str_1 in caption or date_str_2 in caption:
                print(f"Found candidate post from {post.date}: {caption[:30]}...")
                
                # Score the candidate to pick the best one (Menu Text > Food Photo)
                score = 0
                
                # Priority 1: Accessibility Caption indicates text
                acc_caption = post.accessibility_caption if post.accessibility_caption else ""
                if "text" in acc_caption.lower() or "says" in acc_caption.lower():
                    score += 10
                    print("  -> High probability: Accessibility caption mentions text.")
                
                # Priority 2: Single Image (GraphImage) is usually the menu text
                if post.typename == 'GraphImage':
                    score += 5
                    print("  -> Medium probability: Single image type.")
                
                candidates.append((score, post))
            
            count += 1
            
        if not candidates:
            print(f"No posts found matching {target_date} in the caption.")
            return None
        
        # Sort candidates by score (descending)
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        best_match = candidates[0][1]
        print(f"Selected best match with score {candidates[0][0]}")
        return best_match

    except Exception as e:
        print(f"Error fetching post: {e}")
        return None

