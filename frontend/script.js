// API Configuration
const API_URL = 'http://localhost:5000';

console.log('Voice Analysis Script Loaded - Version 3.1');
console.log('API URL:', API_URL);

// Global state
let selectedFile = null;
let recordedBlob = null;
let mediaRecorder = null;
let audioChunks = [];
let volumeMeterInterval = null;
let audioContext = null;
let analyser = null;
let microphone = null;

// DOM Elements
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const recordBtn = document.getElementById('recordBtn');
const recordInfo = document.getElementById('recordInfo');
const analyzeBtn = document.getElementById('analyzeBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');

// File Upload Handler
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedFile = file;
        recordedBlob = null;
        fileInfo.textContent = `Selected: ${file.name}`;
        analyzeBtn.disabled = false;
    }
});

// Recording Handler
recordBtn.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        // Stop recording
        mediaRecorder.stop();
        recordBtn.textContent = 'Start Recording';
        recordBtn.classList.remove('recording');
        recordInfo.textContent = 'Recording stopped';
        document.getElementById('volumeMeter').style.display = 'none';
    } else {
        // Start recording
        try {
            // Request high-quality audio with echo cancellation and noise suppression
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    sampleRate: 44100
                }
            });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            
            // Setup volume meter
            setupVolumeMeter(stream);

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                // Create blob from recorded chunks
                const mimeType = mediaRecorder.mimeType || 'audio/webm';
                const rawBlob = new Blob(audioChunks, { type: mimeType });
                
                // Convert to WAV using Web Audio API
                try {
                    const arrayBuffer = await rawBlob.arrayBuffer();
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                    
                    // Normalize audio to boost quiet recordings
                    const normalizedBuffer = await normalizeAudio(audioBuffer, audioContext);
                    
                    // Convert AudioBuffer to WAV
                    recordedBlob = audioBufferToWav(normalizedBuffer);
                    
                    selectedFile = null;
                    fileInfo.textContent = 'No file selected';
                    recordInfo.textContent = 'Recording ready for analysis';
                    analyzeBtn.disabled = false;
                } catch (error) {
                    console.error('Error converting audio:', error);
                    // Fallback: use original blob
                    recordedBlob = rawBlob;
                    selectedFile = null;
                    fileInfo.textContent = 'No file selected';
                    recordInfo.textContent = 'Recording ready (may need conversion)';
                    analyzeBtn.disabled = false;
                }
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
                
                // Stop volume meter
                stopVolumeMeter();
            };

            mediaRecorder.start();
            recordBtn.textContent = 'Stop Recording';
            recordBtn.classList.add('recording');
            recordInfo.textContent = 'Recording... Click to stop';
            document.getElementById('volumeMeter').style.display = 'block';
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    }
});

// Analyze Button Handler
analyzeBtn.addEventListener('click', async (e) => {
    e.preventDefault(); // Prevent default button behavior
    e.stopPropagation(); // Stop event from bubbling
    e.stopImmediatePropagation(); // Stop all propagation
    
    console.log('=== ANALYZE BUTTON CLICKED ===');
    console.log('Selected file:', selectedFile);
    console.log('Recorded blob:', recordedBlob);
    
    if (!selectedFile && !recordedBlob) {
        alert('Please select a file or record audio first');
        return false;
    }

    // Show loading
    analyzeBtn.disabled = true;
    loadingSpinner.style.display = 'inline-block';
    resultsSection.style.display = 'none';

    try {
        // Prepare form data
        const formData = new FormData();
        
        if (selectedFile) {
            formData.append('audio', selectedFile);
        } else if (recordedBlob) {
            formData.append('audio', recordedBlob, 'recording.wav');
        }

        // Send to API
        console.log('Sending request to:', `${API_URL}/analyze`);
        console.log('FormData contents:', {
            hasFile: formData.has('audio'),
            fileName: selectedFile ? selectedFile.name : 'recording.wav'
        });
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            body: formData,
            mode: 'cors',
            credentials: 'omit'
        });

        console.log('Response received!');
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        console.log('Response headers:', {
            contentType: response.headers.get('content-type'),
            corsOrigin: response.headers.get('access-control-allow-origin')
        });
        
        if (!response.ok) {
            const contentType = response.headers.get('content-type');
            let errorMessage = 'Analysis failed';
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    const error = await response.json();
                    console.error('Server error:', error);
                    errorMessage = error.error || errorMessage;
                } catch (e) {
                    console.error('Could not parse error response:', e);
                }
            } else {
                const textError = await response.text();
                console.error('Non-JSON error response:', textError);
                errorMessage = textError || errorMessage;
            }
            throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('Analysis result received!');
        console.log('Result success:', result.success);
        console.log('Result data keys:', result.data ? Object.keys(result.data) : 'no data');
        
        if (result.success) {
            displayResults(result.data);
        } else {
            throw new Error(result.error || 'Unknown error');
        }

    } catch (error) {
        console.error('=== ANALYSIS ERROR ===');
        console.error('Error message:', error.message);
        console.error('Error name:', error.name);
        console.error('Error stack:', error.stack);
        
        let errorMsg = error.message;
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            errorMsg = 'Connection failed. Please ensure:\n' +
                      '1. Backend server is running (http://localhost:5000)\n' +
                      '2. No firewall is blocking the connection\n' +
                      '3. CORS is properly configured';
        }
        
        alert('Error analyzing audio: ' + errorMsg);
    } finally {
        console.log('Analysis request completed');
        analyzeBtn.disabled = false;
        loadingSpinner.style.display = 'none';
    }
    
    return false; // Explicitly return false to prevent any default action
});

// Display Results
function displayResults(data) {
    console.log('Displaying results:', data);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Check and display quality warnings
    displayQualityWarnings(data);

    // Quick Stats
    document.getElementById('emotionValue').textContent = capitalizeFirst(data.emotion);
    document.getElementById('healthValue').textContent = data.vocal_health_score.toFixed(1) + '%';
    document.getElementById('stressValue').textContent = data.stress_level.toFixed(1) + '%';
    document.getElementById('ageValue').textContent = data.voice_age + ' years';

    // Personality Traits
    updatePersonalityBar('extraversion', data.personality_analysis.extraversion);
    updatePersonalityBar('stability', data.personality_analysis.emotional_stability);
    updatePersonalityBar('openness', data.personality_analysis.openness);
    updatePersonalityBar('agreeableness', data.personality_analysis.agreeableness || 50);
    updatePersonalityBar('conscientiousness', data.personality_analysis.conscientiousness || 50);

    // Issues Detected
    const issuesList = document.getElementById('issuesList');
    issuesList.innerHTML = '';
    if (data.issues_detected.length > 0) {
        data.issues_detected.forEach(issue => {
            const li = document.createElement('li');
            li.textContent = issue;
            issuesList.appendChild(li);
        });
    } else {
        issuesList.innerHTML = '<li>No issues detected</li>';
    }

    // Trigger Words
    const triggersList = document.getElementById('triggersList');
    triggersList.innerHTML = '';
    if (data.trigger_word_alert.length > 0) {
        data.trigger_word_alert.forEach(word => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = word;
            triggersList.appendChild(tag);
        });
    } else {
        triggersList.innerHTML = '<span style="color: #999;">No trigger words detected</span>';
    }

    // Suggestions
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    data.suggestions.forEach(suggestion => {
        const li = document.createElement('li');
        li.textContent = suggestion;
        suggestionsList.appendChild(li);
    });

    // Early Illness Signals
    const illnessList = document.getElementById('illnessList');
    illnessList.innerHTML = '';
    if (data.early_illness_signals.length > 0) {
        data.early_illness_signals.forEach(signal => {
            const li = document.createElement('li');
            li.textContent = signal;
            illnessList.appendChild(li);
        });
    } else {
        illnessList.innerHTML = '<li>No health concerns detected</li>';
    }

    // Timeline
    const timelineChart = document.getElementById('timelineChart');
    if (data.heatmap && data.heatmap.times) {
        displayTimeline(data.heatmap.times, data.heatmap.emotions);
    } else {
        timelineChart.innerHTML = '<p style="color: #999;">Timeline data not available</p>';
    }

    // Raw Data
    document.getElementById('rawData').textContent = JSON.stringify(data, null, 2);
}

function updatePersonalityBar(trait, value) {
    const bar = document.getElementById(`${trait}Bar`);
    const valueSpan = document.getElementById(`${trait}Value`);
    bar.style.width = value + '%';
    valueSpan.textContent = value.toFixed(1) + '%';
}

function displayTimeline(times, emotions) {
    const timelineChart = document.getElementById('timelineChart');
    timelineChart.innerHTML = '';
    
    const timelineContainer = document.createElement('div');
    timelineContainer.style.display = 'flex';
    timelineContainer.style.justifyContent = 'space-between';
    timelineContainer.style.alignItems = 'flex-end';
    timelineContainer.style.height = '100px';
    timelineContainer.style.padding = '20px 0';
    
    times.forEach((time, index) => {
        const bar = document.createElement('div');
        bar.style.flex = '1';
        bar.style.margin = '0 5px';
        bar.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        bar.style.borderRadius = '5px 5px 0 0';
        bar.style.height = '80%';
        bar.style.position = 'relative';
        bar.title = `${time}: ${emotions[index]}`;
        
        const label = document.createElement('div');
        label.textContent = time;
        label.style.textAlign = 'center';
        label.style.fontSize = '0.8rem';
        label.style.marginTop = '5px';
        
        const wrapper = document.createElement('div');
        wrapper.style.flex = '1';
        wrapper.appendChild(bar);
        wrapper.appendChild(label);
        
        timelineContainer.appendChild(wrapper);
    });
    
    timelineChart.appendChild(timelineContainer);
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Convert AudioBuffer to WAV format
function audioBufferToWav(buffer) {
    const numberOfChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numberOfChannels * bytesPerSample;
    
    const data = [];
    for (let i = 0; i < buffer.numberOfChannels; i++) {
        data.push(buffer.getChannelData(i));
    }
    
    const interleaved = interleave(data);
    const dataLength = interleaved.length * bytesPerSample;
    const headerLength = 44;
    const totalLength = headerLength + dataLength;
    
    const arrayBuffer = new ArrayBuffer(totalLength);
    const view = new DataView(arrayBuffer);
    
    // Write WAV header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, totalLength - 8, true);
    writeString(view, 8, 'WAVE');
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // fmt chunk size
    view.setUint16(20, format, true);
    view.setUint16(22, numberOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);
    
    // Write audio data
    floatTo16BitPCM(view, 44, interleaved);
    
    return new Blob([arrayBuffer], { type: 'audio/wav' });
}

function interleave(channelData) {
    const length = channelData[0].length;
    const numberOfChannels = channelData.length;
    const result = new Float32Array(length * numberOfChannels);
    
    let offset = 0;
    for (let i = 0; i < length; i++) {
        for (let channel = 0; channel < numberOfChannels; channel++) {
            result[offset++] = channelData[channel][i];
        }
    }
    return result;
}

function floatTo16BitPCM(view, offset, input) {
    for (let i = 0; i < input.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, input[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// Normalize audio to boost quiet recordings
async function normalizeAudio(audioBuffer, audioContext) {
    const offlineContext = new OfflineAudioContext(
        audioBuffer.numberOfChannels,
        audioBuffer.length,
        audioBuffer.sampleRate
    );
    
    const source = offlineContext.createBufferSource();
    source.buffer = audioBuffer;
    
    // Find peak amplitude
    let peak = 0;
    for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
        const data = audioBuffer.getChannelData(channel);
        for (let i = 0; i < data.length; i++) {
            const abs = Math.abs(data[i]);
            if (abs > peak) peak = abs;
        }
    }
    
    // If audio is too quiet, boost it
    if (peak < 0.1 && peak > 0) {
        const targetPeak = 0.7; // Target 70% of max volume
        const gain = offlineContext.createGain();
        gain.gain.value = targetPeak / peak;
        
        source.connect(gain);
        gain.connect(offlineContext.destination);
        source.start();
        
        console.log(`Audio normalized: peak ${peak.toFixed(3)} -> gain ${gain.gain.value.toFixed(2)}x`);
        return await offlineContext.startRendering();
    }
    
    // Audio is fine, return original
    console.log(`Audio peak: ${peak.toFixed(3)} (no normalization needed)`);
    return audioBuffer;
}

// Setup volume meter for recording
function setupVolumeMeter(stream) {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        microphone = audioContext.createMediaStreamSource(stream);
        
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        microphone.connect(analyser);
        
        const volumeBar = document.getElementById('volumeBar');
        const volumeText = document.getElementById('volumeText');
        
        volumeMeterInterval = setInterval(() => {
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength;
            const percentage = Math.min(100, (average / 128) * 100);
            
            volumeBar.style.width = percentage + '%';
            
            if (percentage < 5) {
                volumeText.textContent = '⚠️ Very quiet - speak louder!';
                volumeText.style.color = '#f44336';
            } else if (percentage < 20) {
                volumeText.textContent = '⚠️ Too quiet - increase volume';
                volumeText.style.color = '#ff9800';
            } else if (percentage > 85) {
                volumeText.textContent = '⚠️ Too loud - reduce volume';
                volumeText.style.color = '#ff9800';
            } else {
                volumeText.textContent = '✓ Good level - keep speaking';
                volumeText.style.color = '#4caf50';
            }
        }, 100);
    } catch (error) {
        console.error('Volume meter setup failed:', error);
    }
}

// Stop volume meter
function stopVolumeMeter() {
    if (volumeMeterInterval) {
        clearInterval(volumeMeterInterval);
        volumeMeterInterval = null;
    }
    if (microphone) {
        microphone.disconnect();
        microphone = null;
    }
    if (analyser) {
        analyser = null;
    }
}

// Display quality warnings based on analysis results
function displayQualityWarnings(data) {
    const warningDiv = document.getElementById('qualityWarning');
    const issuesList = document.getElementById('qualityIssues');
    const issues = [];
    
    // Check duration
    if (data.live_analysis && data.live_analysis.duration < 5) {
        issues.push(`Recording too short (${data.live_analysis.duration}s) - at least 5 seconds recommended for accurate results`);
    }
    
    // Check vocal health score as quality indicator
    if (data.vocal_health_score < 30) {
        issues.push('Very low audio quality detected - results may be inaccurate');
    }
    
    // Check if age features are missing
    if (data.age_features && Object.keys(data.age_features).length === 0) {
        issues.push('Insufficient audio data for age estimation - recording may be too short or too quiet');
    }
    
    // Check age confidence
    if (data.age_confidence < 0.5) {
        issues.push(`Low confidence in age estimation (${Math.round(data.age_confidence * 100)}%) - audio quality may be poor`);
    }
    
    // Check emotion confidence
    if (data.raw && data.raw.emotion && data.raw.emotion.confidence < 50) {
        issues.push(`Low confidence in emotion detection (${data.raw.emotion.confidence}%) - try speaking more expressively`);
    }
    
    // Check HNR (Harmonics-to-Noise Ratio)
    if (data.raw && data.raw.health && data.raw.health.metrics) {
        const hnr = data.raw.health.metrics.hnr;
        if (hnr < 10 && hnr > 0) {
            issues.push(`Poor audio signal quality (HNR: ${hnr.toFixed(1)} dB) - background noise or microphone issues detected`);
        } else if (hnr <= 0) {
            issues.push('Very poor audio quality - check microphone and reduce background noise');
        }
        
        // Check pitch
        if (data.raw.health.metrics.pitch_mean === 0) {
            issues.push('No voice pitch detected - microphone may not be capturing audio properly');
        }
    }
    
    // Display warnings if any issues found
    if (issues.length > 0) {
        issuesList.innerHTML = issues.map(issue => `<li>${issue}</li>`).join('');
        warningDiv.style.display = 'block';
    } else {
        warningDiv.style.display = 'none';
    }
}

// Check API Health on Load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            console.log('API is healthy and ready');
        } else {
            console.warn('API health check failed');
        }
    } catch (error) {
        console.error('Could not connect to API:', error);
        alert('Warning: Could not connect to backend API. Make sure the server is running on http://localhost:5000');
    }
});
