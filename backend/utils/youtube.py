import os
import re
from typing import Dict, Any
import requests
from urllib.parse import urlparse, parse_qs

def get_youtube_metadata(url: str) -> Dict[str, Any]:
    """Extract metadata from YouTube URL using YouTube Data API v3"""
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return {
            'title': 'Unknown',
            'source': 'youtube',
            'url': url,
            'error': 'YouTube API key not configured'
        }
    
    try:
        # Extract video ID from URL
        video_id = extract_video_id(url)
        if not video_id:
            return {
                'title': 'Unknown',
                'source': 'youtube',
                'url': url,
                'error': 'Invalid YouTube URL'
            }
        
        # Call YouTube Data API v3
        api_url = f"https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,contentDetails,statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('items'):
            return {
                'title': 'Unknown',
                'source': 'youtube',
                'url': url,
                'error': 'Video not found or private'
            }
        
        video = data['items'][0]
        snippet = video['snippet']
        content_details = video['contentDetails']
        statistics = video.get('statistics', {})
        
        # Parse duration from ISO 8601 format (PT4M13S -> 253 seconds)
        duration = parse_duration(content_details.get('duration', ''))
        
        return {
            'title': snippet.get('title', 'Unknown'),
            'artist': snippet.get('channelTitle', 'Unknown'),
            'duration': duration,
            'description': snippet.get('description', ''),
            'upload_date': snippet.get('publishedAt', '').replace('-', '').replace('T', '').split('.')[0],
            'view_count': int(statistics.get('viewCount', 0)),
            'source': 'youtube',
            'url': url,
            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url')
        }
            
    except Exception as e:
        return {
            'title': 'Unknown',
            'source': 'youtube',
            'url': url,
            'error': str(e)
        }

def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def parse_duration(duration_str: str) -> int:
    """Parse ISO 8601 duration (PT4M13S) to seconds"""
    
    if not duration_str:
        return 0
    
    # Remove PT prefix
    duration_str = duration_str.replace('PT', '')
    
    # Extract hours, minutes, seconds
    hours = 0
    minutes = 0
    seconds = 0
    
    if 'H' in duration_str:
        hours = int(duration_str.split('H')[0])
        duration_str = duration_str.split('H')[1]
    
    if 'M' in duration_str:
        minutes = int(duration_str.split('M')[0])
        duration_str = duration_str.split('M')[1]
    
    if 'S' in duration_str:
        seconds = int(duration_str.split('S')[0])
    
    return hours * 3600 + minutes * 60 + seconds
