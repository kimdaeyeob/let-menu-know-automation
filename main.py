# -*- coding: utf-8 -*-
"""
Main script for Instagram menu crawler and KakaoWork notification system.
"""
import os
import sys
import datetime
from dotenv import load_dotenv

from instagram_crawler import get_todays_menu_post
from cache_manager import save_menu_cache, load_menu_cache
from kakaowork_sender import send_to_kakaowork

# Load environment variables from .env file if it exists
load_dotenv()


def main():
    """Main entry point for the script."""
    # Load environment variables
    env_username = os.environ.get("TARGET_INSTAGRAM_ID")
    
    parser = argparse.ArgumentParser(
        description="Send Instagram menu post to KakaoWork.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl and cache only (no sending)
  python main.py --crawl-only
  
  # Use cache if available, otherwise crawl and send
  python main.py --webhook-env-var KAKAOWORK_WEBHOOK_URL_HAMBAROOM --use-cache
  
  # Send directly with webhook URL
  python main.py --webhook-url https://open.kakaowork.com/v1/webhooks/...
  
  # Use deprecated --room option (backward compatibility)
  python main.py --room 1
        """
    )
    parser.add_argument("--username", type=str, default=env_username, help="Target Instagram ID")
    parser.add_argument("--webhook-url", type=str, default=None, help="Full KakaoWork Webhook URL to use directly.")
    parser.add_argument(
        "--webhook-env-var", 
        type=str, 
        default=None, 
        help="Environment variable name containing the webhook URL (e.g., KAKAOWORK_WEBHOOK_URL_HAMBAROOM)"
    )
    parser.add_argument(
        "--room", 
        type=int, 
        default=None,
        help="[DEPRECATED] Room number to select webhook URL. Use --webhook-env-var instead for better clarity."
    )
    parser.add_argument(
        "--crawl-only",
        action="store_true",
        help="Only crawl and save to cache, do not send message"
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        default=True,
        help="Use cache if available, otherwise crawl (default: True)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force crawl even if cache exists (overrides --use-cache)"
    )
    parser.add_argument(
        "--cache-file",
        type=str,
        default="menu_cache.json",
        help="Cache file path (default: menu_cache.json)"
    )
    
    args = parser.parse_args()
    
    username = args.username
    webhook_url = args.webhook_url
    use_cache = args.use_cache and not args.no_cache
    
    # Get today's date in KST
    kst_offset = datetime.timedelta(hours=9)
    now_kst = datetime.datetime.now(datetime.timezone.utc) + kst_offset
    today_date = now_kst.date()

    # Determine webhook URL from various sources (only if not crawl-only mode)
    if not args.crawl_only:
        if not webhook_url:
            if args.webhook_env_var:
                # New preferred method: directly specify environment variable name
                webhook_url = os.environ.get(args.webhook_env_var)
                if not webhook_url:
                    print(f"Warning: Environment variable '{args.webhook_env_var}' is empty or not set.")
            elif args.room:
                # Deprecated: backward compatibility for --room option
                env_var = f"KAKAOWORK_WEBHOOK_URL_{args.room}"
                webhook_url = os.environ.get(env_var)
                if not webhook_url:
                    print(f"Warning: Environment variable '{env_var}' is empty or not set.")
                print(f"Warning: --room option is deprecated. Use --webhook-env-var {env_var} instead.")
            else:
                # Fallback to the default for backward compatibility
                webhook_url = os.environ.get("KAKAOWORK_WEBHOOK_URL")

        if not webhook_url and not args.crawl_only:
            print("Error: Could not determine webhook URL. Please check your arguments and .env file.")
            print("Usage: python main.py [--username USER] [--webhook-url URL | --webhook-env-var ENV_VAR_NAME]")
            sys.exit(1)

    if not username:
        print("Error: Could not determine username. Please check your arguments and .env file.")
        print("Usage: python main.py [--username USER] [--webhook-url URL | --webhook-env-var ENV_VAR_NAME]")
        sys.exit(1)

    # Try to load from cache first
    image_url = None
    if use_cache:
        cache_data = load_menu_cache(today_date, args.cache_file)
        if cache_data:
            image_url = cache_data.get("image_url")
            print(f"Using cached image URL: {image_url}")

    # If no cache or cache not used, crawl
    if not image_url:
        print(f"Fetching menu post from {username}...")
        post = get_todays_menu_post(username)

        if post:
            image_url = post.url
            
            # Save to cache
            save_menu_cache(today_date, image_url, username, args.cache_file)
        else:
            print("No menu post found for today.")
            sys.exit(1)

    # If crawl-only mode, exit here
    if args.crawl_only:
        print("Crawl-only mode: Cache saved, exiting without sending message.")
        return

    # Send to KakaoWork
    if webhook_url and image_url:
        print("Sending to KakaoWork...")
        success = send_to_kakaowork(webhook_url, image_url)
        if not success:
            sys.exit(1)
    else:
        print("Error: Missing webhook URL or image URL.")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    main()
