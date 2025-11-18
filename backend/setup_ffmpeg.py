"""
FFmpeg Helper - Downloads and sets up FFmpeg for the voice analyzer
Run this script to automatically download and configure FFmpeg
"""

import os
import sys
import urllib.request
import zipfile
import shutil

def download_ffmpeg():
    """Download and extract FFmpeg"""
    
    print("=" * 60)
    print("FFmpeg Setup for Voice Analysis System")
    print("=" * 60)
    
    # FFmpeg download URL (Windows build)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    download_path = "ffmpeg.zip"
    extract_path = "ffmpeg"
    
    print("\n1. Downloading FFmpeg...")
    print(f"   URL: {ffmpeg_url}")
    
    try:
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100 / total_size, 100)
            sys.stdout.write(f'\r   Progress: {percent:.1f}% ({downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB)')
            sys.stdout.flush()
        
        urllib.request.urlretrieve(ffmpeg_url, download_path, show_progress)
        print("\n   ✓ Download complete!")
        
        print("\n2. Extracting FFmpeg...")
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print("   ✓ Extraction complete!")
        
        # Find the bin directory
        print("\n3. Locating FFmpeg binaries...")
        for root, dirs, files in os.walk(extract_path):
            if 'ffmpeg.exe' in files:
                ffmpeg_bin = root
                print(f"   ✓ Found at: {ffmpeg_bin}")
                
                # Add to PATH for current session
                current_path = os.environ.get('PATH', '')
                if ffmpeg_bin not in current_path:
                    os.environ['PATH'] = ffmpeg_bin + os.pathsep + current_path
                    print(f"\n4. FFmpeg added to PATH (current session)")
                    print(f"   Path: {ffmpeg_bin}")
                
                # Clean up
                os.remove(download_path)
                print("\n5. Cleanup complete!")
                
                print("\n" + "=" * 60)
                print("✓ FFmpeg setup successful!")
                print("=" * 60)
                print("\nTo make this permanent, add this to your system PATH:")
                print(f"  {os.path.abspath(ffmpeg_bin)}")
                print("\nOr run this script each time before starting the server.")
                print("\nNow you can start the Flask server:")
                print("  python app.py")
                print("=" * 60)
                
                return os.path.abspath(ffmpeg_bin)
        
        print("   ✗ Could not find ffmpeg.exe in extracted files")
        return None
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease download FFmpeg manually from:")
        print("  https://www.gyan.dev/ffmpeg/builds/")
        print("Extract it and add the 'bin' folder to your PATH")
        return None

if __name__ == "__main__":
    ffmpeg_path = download_ffmpeg()
    
    if ffmpeg_path:
        # Test FFmpeg
        print("\nTesting FFmpeg installation...")
        os.system("ffmpeg -version")
