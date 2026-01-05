# -*- coding: utf-8 -*-
"""
KakaoWork message sender module.
"""
import requests


def create_menu_payload(image_url):
    """
    Create payload for menu message to KakaoWork.
    
    Args:
        image_url (str): URL of the menu image
        
    Returns:
        dict: Payload dictionary
    """
    return {
        "text": "오늘의 메뉴 (이미지를 클릭하면 전체보기가 가능합니다)",
        "blocks": [
            {
                "type": "image_link",
                "url": image_url
            },
            {
                "type": "button",
                "text": "이미지 전체보기",
                "style": "default",
                "action_type": "open_system_browser",
                "value": image_url
            }
        ]
    }


def send_to_kakaowork(webhook_url, image_url):
    """
    Sends the image to KakaoWork via Webhook.
    
    Args:
        webhook_url (str): KakaoWork webhook URL
        image_url (str): URL of the menu image
        
    Returns:
        bool: True if successful, False otherwise
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Constructing the payload for KakaoWork
    payload = create_menu_payload(image_url)

    try:
        response = requests.post(webhook_url, json=payload, headers=headers)
        response.raise_for_status()
        print("Successfully sent to KakaoWork.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending to KakaoWork: {e}")
        return False

