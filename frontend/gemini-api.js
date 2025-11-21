// Gemini API Integration for Voice Analysis Chatbot

async function callGeminiAPI(question, analysisData, apiKey) {
    try {
        const contextData = {
            emotion: analysisData.emotion,
            confidence: analysisData.emotion_confidence.toFixed(1),
            vocalHealth: analysisData.vocal_health_score.toFixed(1),
            stress: analysisData.stress_level.toFixed(1),
            duration: analysisData.live_analysis.duration.toFixed(2),
            personality: {
                openness: analysisData.personality_traits.openness.toFixed(1),
                conscientiousness: analysisData.personality_traits.conscientiousness.toFixed(1),
                extraversion: analysisData.personality_traits.extraversion.toFixed(1),
                agreeableness: analysisData.personality_traits.agreeableness.toFixed(1),
                neuroticism: analysisData.personality_traits.neuroticism.toFixed(1)
            },
            issues: analysisData.issues_detected.join(', ') || 'None',
            suggestions: analysisData.suggestions.join(', ')
        };

        const prompt = `You are an AI assistant for a voice analysis system. The user analyzed their voice and got these results:

Emotion: ${contextData.emotion} (${contextData.confidence}% confidence)
Vocal Health: ${contextData.vocalHealth}%
Stress Level: ${contextData.stress}%
Recording Duration: ${contextData.duration} seconds

Personality Traits:
- Openness: ${contextData.personality.openness}%
- Conscientiousness: ${contextData.personality.conscientiousness}%
- Extraversion: ${contextData.personality.extraversion}%
- Agreeableness: ${contextData.personality.agreeableness}%
- Neuroticism: ${contextData.personality.neuroticism}%

Issues: ${contextData.issues}
Suggestions: ${contextData.suggestions}

User Question: ${question}

Provide a helpful, friendly response in 2-3 sentences. Be supportive and informative.`;

        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }]
            })
        });

        if (!response.ok) {
            const error = await response.json();
            console.error('Gemini API error:', error);
            return null;
        }

        const data = await response.json();
        const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (aiResponse) {
            return aiResponse.trim();
        }
        
        return null;
    } catch (error) {
        console.error('Gemini API call failed:', error);
        return null;
    }
}
