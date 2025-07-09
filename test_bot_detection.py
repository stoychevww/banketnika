#!/usr/bin/env python3
"""
Test script to check YouTube bot detection bypass
"""
import asyncio
from utils.music_utils import YouTubeDownloader

async def test_bot_detection():
    """Test if we can bypass YouTube bot detection"""
    downloader = YouTubeDownloader()
    
    test_queries = [
        "popular song",
        "music",
        "test",
        "never gonna give you up",
        "despacito"
    ]
    
    print("Testing YouTube bot detection bypass...")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/{len(test_queries)}: '{query}'")
        print("-" * 30)
        
        try:
            result = await downloader.search_youtube(query)
            
            if result:
                print(f"✅ SUCCESS: Found '{result.get('title', 'Unknown')}'")
                print(f"   ID: {result.get('id', 'N/A')}")
                print(f"   Duration: {result.get('duration', 'N/A')} seconds")
            else:
                print("❌ FAILED: No results returned")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Wait between tests to avoid rate limiting
        if i < len(test_queries):
            print("   Waiting 3 seconds...")
            await asyncio.sleep(3)
    
    print("\n" + "=" * 50)
    print("Bot detection test completed.")

if __name__ == "__main__":
    asyncio.run(test_bot_detection()) 