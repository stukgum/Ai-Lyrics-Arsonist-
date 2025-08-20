import os
import re
from typing import Dict, Any, Optional
import requests
from urllib.parse import urlparse, parse_qs
import yt_dlp
import tempfile

class UniversalURLProcessor:
    """Universal URL processor for extracting audio from any platform"""
    
    # Platform detection patterns
    PLATFORM_PATTERNS = {
        'youtube': [r'youtube\.com', r'youtu\.be', r'm\.youtube\.com'],
        'soundcloud': [r'soundcloud\.com'],
        'spotify': [r'open\.spotify\.com', r'spotify\.com'],
        'bandcamp': [r'\.bandcamp\.com'],
        'vimeo': [r'vimeo\.com'],
        'tiktok': [r'tiktok\.com', r'vm\.tiktok\.com'],
        'instagram': [r'instagram\.com'],
        'twitter': [r'twitter\.com', r'x\.com'],
        'mixcloud': [r'mixcloud\.com'],
        'dailymotion': [r'dailymotion\.com'],
        'twitch': [r'twitch\.tv'],
        'facebook': [r'facebook\.com', r'fb\.watch'],
        'reddit': [r'reddit\.com', r'v\.redd\.it'],
        'voloco': [r'voloco\.co', r'voloco\.com', r'app\.voloco\.co'],
        'rapchat': [r'rapchat\.me', r'rapchat\.com', r'app\.rapchat\.me'],
        'rapfame': [r'rapfame\.com', r'app\.rapfame\.com', r'rapfame\.me'],
        'direct': [r'\.mp3', r'\.wav', r'\.m4a', r'\.aac', r'\.ogg', r'\.flac']
    }
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    
    def detect_platform(self, url: str) -> str:
        """Detect the platform from URL"""
        url_lower = url.lower()
        
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return platform
        
        return 'unknown'
    
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """Extract metadata from any URL"""
        platform = self.detect_platform(url)
        
        try:
            if platform == 'youtube':
                return self._get_youtube_metadata(url)
            elif platform == 'direct':
                return self._get_direct_metadata(url)
            elif platform in ['voloco', 'rapchat', 'rapfame']:
                return self._get_music_app_metadata(url, platform)
            else:
                return self._get_ytdlp_metadata(url, platform)
        except Exception as e:
            return {
                'title': 'Unknown',
                'source': platform,
                'url': url,
                'error': str(e)
            }
    
    def download_audio(self, url: str, output_path: Optional[str] = None) -> str:
        """Download audio from any URL"""
        platform = self.detect_platform(url)
        
        if platform == 'direct':
            return self._download_direct_audio(url, output_path)
        else:
            return self._download_ytdlp_audio(url, output_path)
    
    def _get_youtube_metadata(self, url: str) -> Dict[str, Any]:
        """Get YouTube metadata using official API"""
        if not self.youtube_api_key:
            return self._get_ytdlp_metadata(url, 'youtube')
        
        try:
            video_id = self._extract_youtube_video_id(url)
            if not video_id:
                return self._get_ytdlp_metadata(url, 'youtube')
            
            api_url = f"https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,contentDetails,statistics',
                'id': video_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return self._get_ytdlp_metadata(url, 'youtube')
            
            video = data['items'][0]
            snippet = video['snippet']
            content_details = video['contentDetails']
            statistics = video.get('statistics', {})
            
            duration = self._parse_duration(content_details.get('duration', ''))
            
            return {
                'title': snippet.get('title', 'Unknown'),
                'artist': snippet.get('channelTitle', 'Unknown'),
                'duration': duration,
                'description': snippet.get('description', ''),
                'upload_date': snippet.get('publishedAt', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'source': 'youtube',
                'url': url,
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'platform': 'youtube'
            }
        except:
            return self._get_ytdlp_metadata(url, 'youtube')
    
    def _get_ytdlp_metadata(self, url: str, platform: str) -> Dict[str, Any]:
        """Get metadata using yt-dlp for any platform"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'artist': info.get('uploader', info.get('channel', 'Unknown')),
                    'duration': info.get('duration', 0),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'source': platform,
                    'url': url,
                    'thumbnail': info.get('thumbnail'),
                    'platform': platform,
                    'extractor': info.get('extractor', platform)
                }
        except Exception as e:
            return {
                'title': 'Unknown',
                'source': platform,
                'url': url,
                'error': str(e),
                'platform': platform
            }
    
    def _get_direct_metadata(self, url: str) -> Dict[str, Any]:
        """Get metadata for direct audio URLs"""
        try:
            response = requests.head(url, timeout=10)
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            return {
                'title': filename or 'Direct Audio',
                'source': 'direct',
                'url': url,
                'content_type': response.headers.get('content-type'),
                'content_length': response.headers.get('content-length'),
                'platform': 'direct'
            }
        except Exception as e:
            return {
                'title': 'Direct Audio',
                'source': 'direct',
                'url': url,
                'error': str(e),
                'platform': 'direct'
            }
    
    def _download_ytdlp_audio(self, url: str, output_path: Optional[str] = None) -> str:
        """Download audio using yt-dlp from any supported platform"""
        if not output_path:
            output_path = tempfile.mktemp(suffix='.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'extractaudio': True,
            'audioformat': 'wav',
            'audioquality': '0',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the actual downloaded file
        for ext in ['.wav', '.mp3', '.m4a', '.webm', '.opus']:
            potential_path = output_path.replace('.%(ext)s', ext)
            if os.path.exists(potential_path):
                return potential_path
        
        raise RuntimeError("Downloaded file not found")
    
    def _download_direct_audio(self, url: str, output_path: Optional[str] = None) -> str:
        """Download direct audio file"""
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        if not output_path:
            # Determine extension from content type or URL
            content_type = response.headers.get('content-type', '')
            if 'audio/mpeg' in content_type:
                ext = '.mp3'
            elif 'audio/wav' in content_type:
                ext = '.wav'
            elif 'audio/mp4' in content_type:
                ext = '.m4a'
            else:
                ext = os.path.splitext(urlparse(url).path)[1] or '.mp3'
            
            output_path = tempfile.mktemp(suffix=ext)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return output_path
    
    def _extract_youtube_video_id(self, url: str) -> Optional[str]:
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
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration (PT4M13S) to seconds"""
        if not duration_str:
            return 0
        
        duration_str = duration_str.replace('PT', '')
        hours = minutes = seconds = 0
        
        if 'H' in duration_str:
            hours = int(duration_str.split('H')[0])
            duration_str = duration_str.split('H')[1]
        
        if 'M' in duration_str:
            minutes = int(duration_str.split('M')[0])
            duration_str = duration_str.split('M')[1]
        
        if 'S' in duration_str:
            seconds = int(duration_str.split('S')[0])
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _get_music_app_metadata(self, url: str, platform: str) -> Dict[str, Any]:
        """Get metadata for music creation apps like Voloco, Rapchat, Rapfame"""
        try:
            # Try yt-dlp first as it may support these platforms
            return self._get_ytdlp_metadata(url, platform)
        except Exception as e:
            # Fallback to basic web scraping for metadata
            try:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                # Basic HTML parsing for title
                title_match = re.search(r'<title[^>]*>([^<]+)</title>', response.text, re.IGNORECASE)
                title = title_match.group(1).strip() if title_match else f'{platform.title()} Track'
                
                # Look for common metadata patterns
                artist_patterns = [
                    r'<meta[^>]*name=["\']artist["\'][^>]*content=["\']([^"\']+)["\']',
                    r'<meta[^>]*property=["\']music:musician["\'][^>]*content=["\']([^"\']+)["\']',
                    r'"artist"[:\s]*"([^"]+)"',
                ]
                
                artist = 'Unknown Artist'
                for pattern in artist_patterns:
                    match = re.search(pattern, response.text, re.IGNORECASE)
                    if match:
                        artist = match.group(1).strip()
                        break
                
                return {
                    'title': title,
                    'artist': artist,
                    'source': platform,
                    'url': url,
                    'platform': platform,
                    'description': f'Track from {platform.title()}',
                    'extractor': f'{platform}_custom'
                }
            except Exception as fallback_error:
                return {
                    'title': f'{platform.title()} Track',
                    'artist': 'Unknown Artist',
                    'source': platform,
                    'url': url,
                    'error': str(fallback_error),
                    'platform': platform
                }

# Global instance
url_processor = UniversalURLProcessor()

# Convenience functions for backward compatibility
def get_youtube_metadata(url: str) -> Dict[str, Any]:
    return url_processor.get_metadata(url)

def get_universal_metadata(url: str) -> Dict[str, Any]:
    return url_processor.get_metadata(url)

def download_universal_audio(url: str, output_path: Optional[str] = None) -> str:
    return url_processor.download_audio(url, output_path)
