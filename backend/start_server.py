"""
Start Voice Analysis Server
This script ensures FFmpeg is available before starting the Flask server
"""

import os
import sys
import subprocess

def find_ffmpeg():
    """Find FFmpeg in common locations"""
    
    # Check if ffmpeg is already in PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg found in PATH")
            return True
    except:
        pass
    
    # Check local ffmpeg folder
    local_paths = [
        os.path.join(os.path.dirname(__file__), 'ffmpeg'),
        'C:\\ffmpeg\\bin',
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links')
    ]
    
    for base_path in local_paths:
        if os.path.exists(base_path):
            # Search for ffmpeg.exe recursively
            for root, dirs, files in os.walk(base_path):
                if 'ffmpeg.exe' in files:
                    ffmpeg_bin = root
                    print(f"✓ Found FFmpeg at: {ffmpeg_bin}")
                    
                    # Add to PATH
                    current_path = os.environ.get('PATH', '')
                    if ffmpeg_bin not in current_path:
                        os.environ['PATH'] = ffmpeg_bin + os.pathsep + current_path
                        print(f"✓ Added FFmpeg to PATH (current session)")
                    
                    return True
    
    return False

def main():
    print("=" * 60)
    print("Starting Voice Analysis Server")
    print("=" * 60)
    
    # Check for FFmpeg
    print("\n1. Checking FFmpeg availability...")
    
    if not find_ffmpeg():
        print("\n✗ FFmpeg not found!")
        print("\nPlease run: python setup_ffmpeg.py")
        print("Or install FFmpeg manually and add to PATH")
        print("\nSee FFMPEG_SETUP.md for detailed instructions")
        sys.exit(1)
    
    # Start Flask server
    print("\n2. Starting Flask server...")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")

if __name__ == "__main__":
    main()
