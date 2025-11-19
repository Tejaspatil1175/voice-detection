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
            stress_data = self._estimate_stress(emotion_data, health_data)
            result['stress_level'] = stress_data['score']
            result['stress_level_category'] = stress_data['level']
            result['stress_components'] = stress_data['components']
            
            # 4. Timeline Analysis
            print("  → Analyzing timeline...")
            timeline_data = self._analyze_timeline(audio_file)
            result['timeline_emotion'] = timeline_data['dominant']
            result['heatmap'] = timeline_data['heatmap']
            result['emotion_timeline'] = timeline_data['timeline']
            result['emotion_distribution'] = timeline_data.get('emotion_distribution', {})
            
            # 5. Trigger Words
            print("  → Detecting keywords...")
            keywords = self._detect_keywords(audio_file)
            result['trigger_word_alert'] = keywords
            
            # 6. Voice Age
            print("  → Estimating voice age...")
            age_data = self._estimate_age(audio_file)
            result['voice_age'] = age_data['age']
            result['age_confidence'] = age_data['confidence']
            result['detected_gender'] = age_data['gender']
            result['age_features'] = age_data.get('features', {})
            
            # 7. Personality Analysis
            print("  → Analyzing personality...")
            personality_data = self._analyze_personality(audio_file)
            result['personality_analysis'] = {
                'extraversion': personality_data['extraversion'],
                'emotional_stability': personality_data['emotional_stability'],
                'openness': personality_data['openness'],
                'agreeableness': personality_data.get('agreeableness', 50),
                'conscientiousness': personality_data.get('conscientiousness', 50)
            }
            result['personality_confidence'] = personality_data.get('confidence', 0.5)
            
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
            
            # Handle NaN values
            if np.isnan(jitter) or np.isinf(jitter):
                jitter = 0.005  # Use typical value
            if np.isnan(shimmer) or np.isinf(shimmer):
                shimmer = 0.03  # Use typical value
            if np.isnan(hnr_mean) or np.isinf(hnr_mean):
                hnr_mean = 15  # Use typical value
            
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
                'score': round(float(health_score), 2) if not np.isnan(health_score) else 0,
                'issues': issues,
                'illness_signals': illness_signals,
                'metrics': {
                    'jitter': round(float(jitter), 4) if not np.isnan(jitter) else 0,
                    'shimmer': round(float(shimmer), 4) if not np.isnan(shimmer) else 0,
                    'hnr': round(float(hnr_mean), 2) if not np.isnan(hnr_mean) else 0,
                    'pitch_mean': round(float(np.mean(pitch_values)), 2) if len(pitch_values) > 0 and not np.isnan(np.mean(pitch_values)) else 0
                }
            }
        except Exception as e:
            print(f"Vocal health error: {e}")
            return {'score': 0, 'issues': ['Analysis failed'], 'illness_signals': [], 'metrics': {}}
    
    def _estimate_stress(self, emotion_data, health_data):
        """Calculate stress level using multiple physiological indicators"""
        
        # Base stress from emotion (0-100)
        stress_map = {
            'angry': 85,
            'fearful': 80,
            'disgusted': 70,
            'sad': 60,
            'surprised': 50,
            'neutral': 30,
            'happy': 20,
            'calm': 15
        }
        
        emotion_stress = stress_map.get(emotion_data['emotion'].lower(), 50)
        
        # Health-based stress indicators
        health_stress = 100 - health_data['score']
        
        # Additional stress indicators from health metrics
        metrics = health_data.get('metrics', {})
        jitter = metrics.get('jitter', 0)
        shimmer = metrics.get('shimmer', 0)
        pitch_mean = metrics.get('pitch_mean', 150)
        
        # Voice tremor indicator (high jitter = high stress)
        tremor_stress = 0
        if jitter > 0.015:
            tremor_stress = min((jitter - 0.015) * 2000, 30)
        
        # Voice instability (high shimmer = stress)
        instability_stress = 0
        if shimmer > 0.05:
            instability_stress = min((shimmer - 0.05) * 500, 25)
        
        # Pitch-based stress (very high or very low can indicate stress)
        pitch_stress = 0
        if pitch_mean > 0:
            # Normal ranges: Male 85-180 Hz, Female 165-255 Hz
            if pitch_mean > 255 or pitch_mean < 85:
                pitch_stress = 15
            elif pitch_mean > 240 or pitch_mean < 100:
                pitch_stress = 10
        
        # Weighted combination of all factors
        total_stress = (
            emotion_stress * 0.35 +      # 35% emotion
            health_stress * 0.25 +        # 25% overall health
            tremor_stress * 0.20 +        # 20% voice tremor
            instability_stress * 0.15 +   # 15% instability
            pitch_stress * 0.05           # 5% pitch abnormality
        )
        
        # Clamp to 0-100 range
        total_stress = np.clip(total_stress, 0, 100)
        
        # Determine stress level category
        if total_stress < 30:
            stress_level = "Low"
        elif total_stress < 55:
            stress_level = "Moderate"
        elif total_stress < 75:
            stress_level = "High"
        else:
            stress_level = "Very High"
        
        return {
            "score": round(total_stress, 2),
            "level": stress_level,
            "components": {
                "emotion": round(emotion_stress * 0.35, 2),
                "health": round(health_stress * 0.25, 2),
                "tremor": round(tremor_stress * 0.20, 2),
                "instability": round(instability_stress * 0.15, 2),
                "pitch": round(pitch_stress * 0.05, 2)
            }
        }
    
    def _analyze_timeline(self, audio_file):
        """Analyze emotion timeline with actual segmentation and analysis"""
        try:
            y, sr = librosa.load(audio_file)
            duration = len(y) / sr
            
            # Dynamic segmentation based on duration
            if duration < 5:
                segments = 3
            elif duration < 15:
                segments = 5
            else:
                segments = min(10, int(duration / 3))  # Max 10 segments
            
            segment_duration = duration / segments
            timeline = []
            emotion_counts = {}
            
            # Create temporary directory for segments
            import tempfile
            temp_dir = tempfile.mkdtemp()
            
            for i in range(segments):
                start_sample = int(i * segment_duration * sr)
                end_sample = int((i + 1) * segment_duration * sr)
                segment_audio = y[start_sample:end_sample]
                
                # Save segment temporarily
                segment_path = os.path.join(temp_dir, f'segment_{i}.wav')
                sf.write(segment_path, segment_audio, sr)
                
                # Analyze emotion for this segment
                try:
                    segment_emotion_results = self.emotion_model(segment_path)
                    segment_emotion = segment_emotion_results[0]['label']
                    segment_confidence = round(segment_emotion_results[0]['score'] * 100, 2)
                except Exception as seg_error:
                    print(f"Segment {i} emotion error: {seg_error}")
                    segment_emotion = 'neutral'
                    segment_confidence = 50
                
                # Count emotions for dominant calculation
                emotion_counts[segment_emotion] = emotion_counts.get(segment_emotion, 0) + 1
                
                timeline.append({
                    'time': f"{i * segment_duration:.1f}s",
                    'emotion': segment_emotion,
                    'confidence': segment_confidence
                })
                
                # Clean up segment file
                try:
                    os.remove(segment_path)
                except:
                    pass
            
            # Clean up temp directory
            try:
                os.rmdir(temp_dir)
            except:
                pass
            
            # Find dominant emotion
            dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else 'neutral'
            
            # Create heatmap data
            heatmap = {
                'times': [t['time'] for t in timeline],
                'emotions': [t['emotion'] for t in timeline],
                'confidences': [t['confidence'] for t in timeline]
            }
            
            return {
                'dominant': dominant_emotion,
                'timeline': timeline,
                'heatmap': heatmap,
                'emotion_distribution': emotion_counts
            }
        except Exception as e:
            print(f"Timeline error: {e}")
            import traceback
            traceback.print_exc()
            return {'dominant': 'neutral', 'timeline': [], 'heatmap': {}, 'emotion_distribution': {}}
    
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
        """Estimate voice age using multiple acoustic features"""
        try:
            # Convert audio to compatible format
            audio_file = self._ensure_compatible_audio(audio_file)
            sound = parselmouth.Sound(audio_file)
            
            # Load with librosa for additional features
            y, sr = librosa.load(audio_file)
            
            # Feature 1: Pitch analysis
            pitch = sound.to_pitch()
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]
            
            if len(pitch_values) == 0:
                return {"age": 30, "confidence": 0.3, "gender": "unknown"}
            
            mean_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            
            # Feature 2: Formant frequencies (vocal tract length indicator)
            formants = sound.to_formant_burg()
            f1_values = []
            f2_values = []
            
            for i in range(formants.get_number_of_frames()):
                f1 = formants.get_value_at_time(1, formants.get_time_from_frame_number(i + 1))
                f2 = formants.get_value_at_time(2, formants.get_time_from_frame_number(i + 1))
                if f1 and not np.isnan(f1):
                    f1_values.append(f1)
                if f2 and not np.isnan(f2):
                    f2_values.append(f2)
            
            mean_f1 = np.mean(f1_values) if f1_values else 500
            mean_f2 = np.mean(f2_values) if f2_values else 1500
            
            # Feature 3: Jitter (voice quality - increases with age)
            point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 600)
            jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            
            # Feature 4: Shimmer (amplitude variation - increases with age)
            shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            
            # Handle NaN values
            if np.isnan(jitter) or np.isinf(jitter):
                jitter = 0.01
            if np.isnan(shimmer) or np.isinf(shimmer):
                shimmer = 0.05
            if np.isnan(mean_pitch) or np.isinf(mean_pitch):
                mean_pitch = 150
            if np.isnan(pitch_std) or np.isinf(pitch_std):
                pitch_std = 30
            
            # Feature 5: Speaking rate approximation
            intensity = sound.to_intensity()
            intensity_values = intensity.values[0]
            intensity_threshold = np.mean(intensity_values) - np.std(intensity_values)
            voiced_frames = np.sum(intensity_values > intensity_threshold)
            speaking_rate = voiced_frames / len(intensity_values) if len(intensity_values) > 0 else 0.5
            
            # Feature 6: Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            
            # Gender estimation (helps with age accuracy)
            if mean_pitch > 165:
                gender = "female"
                gender_factor = 1.0
            elif mean_pitch < 145:
                gender = "male"
                gender_factor = -1.0
            else:
                gender = "unknown"
                gender_factor = 0.0
            
            # Advanced age estimation algorithm
            # Base age from pitch
            if gender == "female":
                if mean_pitch > 220:
                    base_age = 12 + (240 - mean_pitch) / 4  # Children: 12-17
                elif mean_pitch > 200:
                    base_age = 18 + (220 - mean_pitch) / 2  # Young: 18-28
                elif mean_pitch > 180:
                    base_age = 28 + (200 - mean_pitch) / 2  # Adult: 28-38
                else:
                    base_age = 38 + (180 - mean_pitch) / 3  # Older: 38-52
            elif gender == "male":
                if mean_pitch > 200:
                    base_age = 12 + (230 - mean_pitch) / 3  # Children: 12-22
                elif mean_pitch > 130:
                    base_age = 22 + (200 - mean_pitch) / 3  # Young adult: 22-45
                elif mean_pitch > 110:
                    base_age = 45 + (130 - mean_pitch) / 2  # Middle: 45-55
                else:
                    base_age = 55 + (110 - mean_pitch) / 2  # Older: 55-70
            else:
                # Unknown gender - use neutral calculation
                if mean_pitch > 200:
                    base_age = 15
                elif mean_pitch > 160:
                    base_age = 25
                elif mean_pitch > 130:
                    base_age = 35
                else:
                    base_age = 50
            
            # Adjust based on voice quality (jitter/shimmer increase with age)
            quality_age_adjustment = 0
            if jitter > 0.015:
                quality_age_adjustment += 5
            if jitter > 0.025:
                quality_age_adjustment += 8
            if shimmer > 0.06:
                quality_age_adjustment += 5
            if shimmer > 0.10:
                quality_age_adjustment += 8
            
            # Adjust based on pitch variability
            if pitch_std < 20:
                quality_age_adjustment += 5  # Less variation = older
            elif pitch_std > 60:
                quality_age_adjustment -= 3  # More variation = younger
            
            # Adjust based on formants (vocal tract length)
            if gender == "female" and mean_f1 < 700:
                quality_age_adjustment += 5  # Lower formants = larger tract = older
            elif gender == "male" and mean_f1 < 500:
                quality_age_adjustment += 5
            
            # Adjust based on spectral features
            if spectral_centroid < 1500:
                quality_age_adjustment += 3  # Lower brightness = older
            
            # Calculate final age
            estimated_age = base_age + quality_age_adjustment
            
            # Clamp to reasonable range
            estimated_age = np.clip(estimated_age, 10, 80)
            
            # Calculate confidence based on feature consistency
            confidence = 0.5  # Base confidence
            
            # Increase confidence if gender is clear
            if gender in ["male", "female"]:
                confidence += 0.2
            
            # Increase confidence if voice quality is clear
            if 0.005 < jitter < 0.03 and 0.03 < shimmer < 0.12:
                confidence += 0.15
            
            # Increase confidence if pitch is stable
            if 10 < pitch_std < 70:
                confidence += 0.15
            
            confidence = min(confidence, 1.0)
            
            return {
                "age": int(round(float(estimated_age))) if not np.isnan(estimated_age) else 30,
                "confidence": round(float(confidence), 2) if not np.isnan(confidence) else 0.5,
                "gender": gender,
                "features": {
                    "mean_pitch": round(float(mean_pitch), 2) if not np.isnan(mean_pitch) else 0,
                    "pitch_variability": round(float(pitch_std), 2) if not np.isnan(pitch_std) else 0,
                    "jitter": round(float(jitter), 4) if not np.isnan(jitter) else 0,
                    "shimmer": round(float(shimmer), 4) if not np.isnan(shimmer) else 0,
                    "formant_f1": round(float(mean_f1), 2) if not np.isnan(mean_f1) else 0,
                    "formant_f2": round(float(mean_f2), 2) if not np.isnan(mean_f2) else 0
                }
            }
            
        except Exception as e:
            print(f"Age estimation error: {e}")
            return {"age": 30, "confidence": 0.2, "gender": "unknown", "features": {}}
    
    def _analyze_personality(self, audio_file):
        """Enhanced personality analysis using multiple acoustic features"""
        try:
            y, sr = librosa.load(audio_file)
            
            # Feature 1: Speaking rate and energy (Extraversion)
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            except (AttributeError, Exception) as e:
                print(f"Beat tracking failed, using alternative: {e}")
                # Alternative: use zero-crossing rate for tempo estimation
                zcr = librosa.feature.zero_crossing_rate(y)
                tempo = np.mean(zcr) * 1000  # Normalize to tempo-like range
            
            energy = np.mean(librosa.feature.rms(y=y))
            
            # Feature 2: Pitch variation (Emotional expressiveness)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 20
            pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 150
            
            # Feature 3: Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            
            # Feature 4: MFCCs for voice quality
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = np.mean(mfccs, axis=1)
            mfcc_std = np.std(mfccs, axis=1)
            
            # Feature 5: Pause analysis (speaking pattern)
            rms = librosa.feature.rms(y=y)[0]
            silence_threshold = np.mean(rms) * 0.3
            silence_frames = np.sum(rms < silence_threshold)
            speech_frames = len(rms) - silence_frames
            speech_ratio = speech_frames / len(rms) if len(rms) > 0 else 0.5
            
            # Feature 6: Dynamic range
            dynamic_range = np.max(rms) - np.min(rms) if len(rms) > 0 else 0
            
            # EXTRAVERSION (outgoing, energetic, talkative)
            # Higher tempo, energy, speech ratio = more extraverted
            tempo_score = min(tempo / 150 * 40, 40)  # Max 40 points
            energy_score = min(energy * 500, 30)      # Max 30 points
            speech_score = speech_ratio * 30         # Max 30 points
            extraversion = tempo_score + energy_score + speech_score
            extraversion = np.clip(extraversion, 0, 100)
            
            # EMOTIONAL STABILITY (calm, stable, consistent)
            # Lower pitch variation, consistent energy = more stable
            pitch_stability = max(100 - (pitch_std / 50 * 100), 0)
            energy_stability = max(100 - (dynamic_range * 2000), 0)
            mfcc_stability = max(100 - (np.mean(mfcc_std) * 10), 0)
            emotional_stability = (pitch_stability * 0.4 + energy_stability * 0.3 + mfcc_stability * 0.3)
            emotional_stability = np.clip(emotional_stability, 0, 100)
            
            # OPENNESS (creative, curious, expressive)
            # Higher spectral complexity, pitch variation = more open
            spectral_score = min(spectral_centroid / 30, 40)  # Max 40 points
            bandwidth_score = min(spectral_bandwidth / 50, 30)  # Max 30 points
            expressiveness = min(pitch_std / 30 * 30, 30)      # Max 30 points
            openness = spectral_score + bandwidth_score + expressiveness
            openness = np.clip(openness, 0, 100)
            
            # AGREEABLENESS (friendly, warm, cooperative)
            # Moderate pitch, smooth tone, balanced energy
            pitch_warmth = 100 - abs(pitch_mean - 180) / 2  # Optimal around 180Hz
            tone_smoothness = max(100 - (np.mean(mfcc_std[:5]) * 15), 0)
            agreeableness = (pitch_warmth * 0.5 + tone_smoothness * 0.5)
            agreeableness = np.clip(agreeableness, 0, 100)
            
            # CONSCIENTIOUSNESS (organized, careful, deliberate)
            # Consistent speaking rate, controlled energy, clear articulation
            consistency = emotional_stability * 0.6  # Overlaps with stability
            articulation = min(spectral_rolloff / 40, 40)  # Clear high frequencies
            conscientiousness = consistency * 0.6 + articulation * 0.4
            conscientiousness = np.clip(conscientiousness, 0, 100)
            
            return {
                'extraversion': round(float(extraversion), 2),
                'emotional_stability': round(float(emotional_stability), 2),
                'openness': round(float(openness), 2),
                'agreeableness': round(float(agreeableness), 2),
                'conscientiousness': round(float(conscientiousness), 2),
                'confidence': 0.65,  # Moderate confidence for personality
                'acoustic_features': {
                    'tempo': round(float(tempo), 2),
                    'energy': round(float(energy), 4),
                    'pitch_std': round(float(pitch_std), 2),
                    'speech_ratio': round(float(speech_ratio), 2),
                    'spectral_centroid': round(float(spectral_centroid), 2)
                }
            }
        except Exception as e:
            print(f"Personality analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'extraversion': 50,
                'emotional_stability': 50,
                'openness': 50,
                'agreeableness': 50,
                'conscientiousness': 50,
                'confidence': 0.2,
                'acoustic_features': {}
            }
    
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
