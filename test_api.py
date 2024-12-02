import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set API key
os.environ['YOUTUBE_API_KEY'] = 'AIzaSyAYQIbzSV_4_wMzUYNhdrqIFIyhR1AMWBo'

def test_youtube_api():
    try:
        # Initialize the YouTube API client
        youtube = build('youtube', 'v3', developerKey=os.environ['YOUTUBE_API_KEY'])
        
        # Test with a sample video ID (using a popular video)
        video_id = 'dQw4w9WgXcQ'  # Rick Astley - Never Gonna Give You Up
        
        # Request video details
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        response = request.execute()
        
        # Print video information
        if response['items']:
            video = response['items'][0]
            print('API Connection Successful!')
            print('Video Title:', video['snippet']['title'])
            print('Channel Name:', video['snippet']['channelTitle'])
            print('View Count:', video['statistics']['viewCount'])
            return True
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred: {e.content}')
        return False
    except Exception as e:
        print(f'An error occurred: {e}')
        return False

if __name__ == '__main__':
    test_youtube_api()
