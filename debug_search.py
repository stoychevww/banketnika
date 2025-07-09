#!/usr/bin/env python3
"""
Debug script to test YouTube search functionality with youtube-dl
"""
import asyncio
import sys
from utils.music_utils import YouTubeDownloader

async def test_search(query):
    """Test search functionality"""
    print(f"=" * 60)
    print(f"Testing search for: {query}")
    print(f"=" * 60)
    
    downloader = YouTubeDownloader()
    
    try:
        result = await downloader.search_youtube(query)
        
        if result:
            print("✅ Search successful!")
            print(f"Title: {result.get('title', 'N/A')}")
            print(f"ID: {result.get('id', 'N/A')}")
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"Webpage URL: {result.get('webpage_url', 'N/A')}")
            print(f"Duration: {result.get('duration', 'N/A')}")
            print(f"Uploader: {result.get('uploader', 'N/A')}")
        else:
            print("❌ Search returned None")
            
    except Exception as e:
        print(f"❌ Search failed with error: {e}")
    
    print(f"=" * 60)

async def main():
    """Main test function"""
    test_queries = [
        "test song",
        "popular music",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "eminem lose yourself",
        "classical music"
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument as query
        test_queries = [" ".join(sys.argv[1:])]
    
    for query in test_queries:
        await test_search(query)
        await asyncio.sleep(2)  # Wait between tests

if __name__ == "__main__":
    asyncio.run(main()) 