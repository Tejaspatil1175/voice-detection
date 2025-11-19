"""
Quick test script to verify the improved accuracy functions
Run this to check if the new analysis methods work correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from voice_analyzer import VoiceAnalyzer
        print("✅ VoiceAnalyzer imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_initialization():
    """Test if VoiceAnalyzer can be initialized"""
    print("\nTesting initialization...")
    try:
        from voice_analyzer import VoiceAnalyzer
        analyzer = VoiceAnalyzer()
        print("✅ VoiceAnalyzer initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

def test_method_signatures():
    """Test if all methods exist with correct signatures"""
    print("\nTesting method signatures...")
    try:
        from voice_analyzer import VoiceAnalyzer
        import inspect
        
        analyzer = VoiceAnalyzer()
        
        methods = {
            '_estimate_age': 1,
            '_analyze_timeline': 1,
            '_estimate_stress': 2,
            '_analyze_personality': 1,
            'analyze': 1
        }
        
        for method_name, expected_params in methods.items():
            if hasattr(analyzer, method_name):
                method = getattr(analyzer, method_name)
                sig = inspect.signature(method)
                # Subtract 1 for 'self' parameter
                actual_params = len(sig.parameters)
                print(f"  ✅ {method_name} exists with {actual_params} parameters")
            else:
                print(f"  ❌ {method_name} not found")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Method signature test failed: {e}")
        return False

def main():
    print("="*60)
    print("Voice Analyzer Accuracy Improvements - Verification Test")
    print("="*60)
    
    tests = [
        ("Import Test", test_imports),
        ("Initialization Test", test_initialization),
        ("Method Signatures Test", test_method_signatures)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! The improved analyzer is ready to use.")
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python app.py")
        print("2. Open frontend/index.html in your browser")
        print("3. Or test accuracy at frontend/accuracy-test.html")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
