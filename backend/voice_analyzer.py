"""
Voice Analysis Module
Analyzes audio files for emotion, vocal health, stress, personality, etc.
"""

from transformers import pipeline
import parselmouth
import librosa
import soundfile as sf
import numpy as np
import warnings
import os
import tempfile
warnings.filterwarnings('ignore')

class VoiceAnalyzer:
    def __init__(self):
        print("Loading AI models...")
        try:
            self.emotion_model = pipeline("audio-classification", model="Hatman/audio-emotion-detection")
            self.keyword_model = pipeline("audio-classification", model="superb/wav2vec2-base-superb-ks")
            print("Models loaded successfully!")
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def analyze(self, audio_file):
        """Main analysis function"""
        try:
            print(f"Starting analysis of: {audio_file}")
            
            # Initialize result structure
            result = {
                "vocal_health_score": 0,
                "emotion": "",
                "stress_level": 0,
                "timeline_emotion": "",
                "issues_detected": [],
                "early_illness_signals": [],
                "personality_analysis": {},
                "voice_age": 0,
                "trigger_word_alert": [],
                "suggestions": [],
                "heatmap": {},
                "live_analysis": {},
                "raw": {}
            }
            
            # 1. Emotion Detection
            print("  → Analyzing emotion...")
            emotion_data = self._analyze_emotion(audio_file)
            result['emotion'] = emotion_data['emotion']
            result['raw']['emotion'] = emotion_data
            
            # 2. Vocal Health Analysis
            print("  → Analyzing vocal health...")
            health_data = self._analyze_vocal_health(audio_file)
            result['vocal_health_score'] = health_data['score']
            result['issues_detected'] = health_data['issues']
            result['early_illness_signals'] = health_data['illness_signals']
            result['raw']['health'] = health_data
            
            # 3. Stress Level
            print("  → Calculating stress level...")
            result['stress_level'] = self._estimate_stress(emotion_data, health_data)
            
            # 4. Timeline Analysis
            print("  → Analyzing timeline...")
            timeline_data = self._analyze_timeline(audio_file)
            result['timeline_emotion'] = timeline_data['dominant']
            result['heatmap'] = timeline_data['heatmap']
            
            # 5. Trigger Words
            print("  → Detecting keywords...")
            keywords = self._detect_keywords(audio_file)
            result['trigger_word_alert'] = keywords
            
            # 6. Voice Age
            print("  → Estimating voice age...")
            result['voice_age'] = self._estimate_age(audio_file)
            
            # 7. Personality Analysis
            print("  → Analyzing personality...")
            result['personality_analysis'] = self._analyze_personality(audio_file)
            
            # 8. Suggestions
            print("  → Generating suggestions...")
            result['suggestions'] = self._generate_suggestions(result)
            
            # 9. Live Analysis
            result['live_analysis'] = {
                "status": "completed",
                "duration": self._get_duration(audio_file),
                "quality": "good" if result['vocal_health_score'] > 70 else "needs improvement"
            }
            
            print("✓ Analysis complete!")
            return result
            
        except Exception as e:
            print(f"Analysis error: {e}")
            raise
    
    def _analyze_emotion(self, audio_file):
        """Detect emotion from audio"""
        try:
            results = self.emotion_model(audio_file)
            return {
                'emotion': results[0]['label'],
                'confidence': round(results[0]['score'] * 100, 2),
                'all_emotions': [{'label': r['label'], 'score': round(r['score'] * 100, 2)} for r in results[:3]]
            }
        except Exception as e:
            print(f"Emotion analysis error: {e}")
            return {'emotion': 'neutral', 'confidence': 0, 'all_emotions': []}
    
    def _analyze_vocal_health(self, audio_file):
        """Analyze vocal health metrics"""
        try:
            # Convert audio to compatible format for parselmouth
            audio_file = self._ensure_compatible_audio(audio_file)
            sound = parselmouth.Sound(audio_file)
            
            # Pitch analysis
            pitch = sound.to_pitch()
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]
            
            # Harmonics-to-Noise Ratio
            harmonicity = sound.to_harmonicity()
            hnr_values = harmonicity.values[harmonicity.values != -200]
            hnr_mean = np.mean(hnr_values) if len(hnr_values) > 0 else 0
            
            # Jitter and Shimmer
            point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 600)
            jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            
            # Calculate health score (0-100)
            hnr_score = np.clip((hnr_mean + 10) / 30 * 100, 0, 100)
            jitter_score = np.clip((1 - jitter * 100) * 100, 0, 100)
            shimmer_score = np.clip((1 - shimmer * 10) * 100, 0, 100)
            health_score = (hnr_score + jitter_score + shimmer_score) / 3
            
            # Detect issues
            issues = []
            illness_signals = []
            
            if jitter > 0.01:
                issues.append("High jitter - vocal strain detected")
                illness_signals.append("Possible vocal cord tension")
            
            if shimmer > 0.05:
                issues.append("High shimmer - voice instability")
                illness_signals.append("Potential hoarseness or fatigue")
            
            if hnr_mean < 10:
                issues.append("Low HNR - rough or breathy voice")
                illness_signals.append("Possible respiratory issue")
            
            if len(pitch_values) > 0:
                pitch_std = np.std(pitch_values)
                if pitch_std > 50:
                    issues.append("High pitch variation - emotional stress")
            
            return {
                'score': round(health_score, 2),
                'issues': issues,
                'illness_signals': illness_signals,
                'metrics': {
                    'jitter': round(jitter, 4),
                    'shimmer': round(shimmer, 4),
                    'hnr': round(hnr_mean, 2),
                    'pitch_mean': round(np.mean(pitch_values), 2) if len(pitch_values) > 0 else 0
                }
            }
        except Exception as e:
            print(f"Vocal health error: {e}")
            return {'score': 0, 'issues': ['Analysis failed'], 'illness_signals': [], 'metrics': {}}
    
    def _estimate_stress(self, emotion_data, health_data):
        """Calculate stress level (0-100)"""
        stress_map = {
            'angry': 85,
            'fearful': 75,
            'disgusted': 65,
            'sad': 55,
            'surprised': 45,
            'neutral': 25,
            'happy': 15
        }
        
        emotion_stress = stress_map.get(emotion_data['emotion'].lower(), 50)
        health_stress = 100 - health_data['score']
        
        return round((emotion_stress + health_stress) / 2, 2)
    
    def _analyze_timeline(self, audio_file):
        """Analyze emotion timeline"""
        try:
            y, sr = librosa.load(audio_file)
            duration = len(y) / sr
            
            # Simple segmentation
            segments = 5
            segment_duration = duration / segments
            timeline = []
            
            for i in range(segments):
                start_time = i * segment_duration
                timeline.append({
                    'time': f"{start_time:.1f}s",
                    'emotion': 'neutral'  # Simplified for now
                })
            
            # Create heatmap data
            heatmap = {
                'times': [t['time'] for t in timeline],
                'emotions': [t['emotion'] for t in timeline]
            }
            
            return {
                'dominant': 'neutral',
                'timeline': timeline,
                'heatmap': heatmap
            }
        except Exception as e:
            print(f"Timeline error: {e}")
            return {'dominant': 'neutral', 'timeline': [], 'heatmap': {}}
    
    def _detect_keywords(self, audio_file):
        """Detect trigger words"""
        try:
            results = self.keyword_model(audio_file)
            keywords = [r['label'] for r in results if r['score'] > 0.5]
            return keywords[:5]  # Top 5
        except Exception as e:
            print(f"Keyword detection error: {e}")
            return []
    
    def _estimate_age(self, audio_file):
        """Estimate voice age"""
        try:
            # Convert audio to compatible format for parselmouth
            audio_file = self._ensure_compatible_audio(audio_file)
            sound = parselmouth.Sound(audio_file)
            pitch = sound.to_pitch()
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]
            
            if len(pitch_values) == 0:
                return 30
            
            mean_pitch = np.mean(pitch_values)
            
            # Simple heuristics
            if mean_pitch > 200:
                return 15  # Child/Teen
            elif mean_pitch > 180:
                return 25  # Young female
            elif mean_pitch > 140:
                return 30  # Adult female/Young male
            elif mean_pitch > 110:
                return 40  # Middle-aged
            else:
                return 55  # Older adult
        except Exception as e:
            print(f"Age estimation error: {e}")
            return 30
    
    def _analyze_personality(self, audio_file):
        """Basic personality analysis"""
        try:
            y, sr = librosa.load(audio_file)
            
            # Extract features with fallbacks
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            except (AttributeError, Exception) as e:
                # Fallback if beat tracking fails (e.g., scipy.signal.hann issue)
                print(f"Beat tracking failed, using fallback: {e}")
                tempo = 120  # Default tempo
            
            energy = np.mean(librosa.feature.rms(y=y))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Calculate traits (0-100) - ensure they're Python floats, not numpy types
            extraversion = float(min((tempo / 200 * 50) + (energy * 1000), 100))
            emotional_stability = float(max(100 - (energy * 500), 0))
            openness = float(min(spectral_centroid / 40, 100))
            
            return {
                'extraversion': round(extraversion, 2),
                'emotional_stability': round(emotional_stability, 2),
                'openness': round(openness, 2)
            }
        except Exception as e:
            print(f"Personality analysis error: {e}")
            return {'extraversion': 50, 'emotional_stability': 50, 'openness': 50}
    
    def _generate_suggestions(self, result):
        """Generate health suggestions"""
        suggestions = []
        
        if result['vocal_health_score'] < 50:
            suggestions.append("Consider vocal rest and stay hydrated")
        
        if result['stress_level'] > 70:
            suggestions.append("High stress detected - try relaxation exercises")
        
        if 'High jitter' in str(result['issues_detected']):
            suggestions.append("Practice gentle vocal warm-ups")
        
        if result['emotion'] in ['angry', 'sad', 'fearful']:
            suggestions.append("Consider stress management techniques")
        
        if not suggestions:
            suggestions.append("Voice health is good - keep it up!")
        
        return suggestions
    
    def _get_duration(self, audio_file):
        """Get audio duration in seconds"""
        try:
            y, sr = librosa.load(audio_file)
            return round(len(y) / sr, 2)
        except:
            return 0
    
    def _ensure_compatible_audio(self, audio_file):
        """Convert audio to format compatible with parselmouth (16-bit PCM WAV)"""
        try:
            # Try to load with parselmouth first
            parselmouth.Sound(audio_file)
            return audio_file
        except Exception as e:
            print(f"Converting audio format for compatibility: {e}")
            try:
                # Load with librosa and convert
                y, sr = librosa.load(audio_file, sr=16000)
                
                # Check if audio was actually loaded
                if len(y) == 0:
                    raise ValueError("Audio file is empty or unreadable")
                
                # Create temporary WAV file
                temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_wav_path = temp_wav.name
                temp_wav.close()
                
                # Save as 16-bit PCM WAV
                sf.write(temp_wav_path, y, sr, subtype='PCM_16')
                
                print(f"✓ Audio converted successfully: {len(y)} samples at {sr}Hz")
                return temp_wav_path
            except Exception as conv_error:
                print(f"✗ Audio conversion failed: {conv_error}")
                print(f"  File: {audio_file}")
                print(f"  Tip: Ensure the audio file is valid and not corrupted")
                raise ValueError(f"Could not process audio file: {conv_error}")
