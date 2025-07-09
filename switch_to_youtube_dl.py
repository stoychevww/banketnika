#!/usr/bin/env python3
"""
Script to switch from yt-dlp to youtube-dl-nightly (latest version)
"""
import subprocess
import sys

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Main function to switch to youtube-dl-nightly"""
    print("🔄 Switching from yt-dlp to youtube-dl-nightly (latest version)...")
    print("=" * 60)
    
    # Step 1: Uninstall yt-dlp
    print("1. Uninstalling yt-dlp...")
    success, stdout, stderr = run_command("pip uninstall yt-dlp -y")
    if success:
        print("✅ yt-dlp uninstalled successfully")
    else:
        print(f"⚠️  Warning: Could not uninstall yt-dlp: {stderr}")
    
    # Step 2: Install youtube-dl-nightly
    print("\n2. Installing youtube-dl-nightly (latest version)...")
    success, stdout, stderr = run_command("pip install youtube-dl-nightly>=2025.5.5")
    if success:
        print("✅ youtube-dl-nightly installed successfully")
    else:
        print(f"❌ Error installing youtube-dl-nightly: {stderr}")
        return False
    
    # Step 3: Verify installation
    print("\n3. Verifying installation...")
    success, stdout, stderr = run_command("python -c \"import youtube_dl; print(f'youtube-dl version: {youtube_dl.version.__version__}')\"")
    if success:
        print("✅ youtube-dl-nightly is working correctly")
        print(stdout.strip())
    else:
        print(f"❌ Error verifying youtube-dl-nightly: {stderr}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Successfully switched to youtube-dl-nightly (latest version)!")
    print("This version is actively maintained and includes the latest fixes.")
    print("You can now run your bot with the updated configuration.")
    print("\nTo test the search functionality, run:")
    print("python debug_search.py \"your search query\"")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 