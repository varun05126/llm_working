# Groq LLM Integration Summary

## Overview
This document summarizes the implementation of the Groq LLM integration in the Women Skill Development Recommendation System.

## Implementation Details

### File Modified
- `skill_recommender/recommender/views.py` - `get_recommendations` function

### Key Changes

#### 1. Actual Groq API Call Implementation
Replaced commented-out/mock code with real API integration:

```python
# Call the actual Groq API
headers = {
    'Authorization': f'Bearer {groq_api_key}',
    'Content-Type': 'application/json'
}
data = {
    'model': 'mixtral-8x7b-32768',
    'messages': [
        {'role': 'system', 'content': 'You are a career development advisor specializing in women\'s skill development.'},
        {'role': 'user', 'content': prompt}
    ],
    'temperature': 0.7,
    'max_tokens': 2000
}
try:
    response = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=data, timeout=30)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    result = response.json()
    llm_response = result['choices'][0]['message']['content']
except requests.exceptions.RequestException as e:
    messages.warning(request, f'Groq API request failed: {str(e)}. Using demo recommendations.')
    return _create_demo_recommendations(user_profile)
except (KeyError, IndexError, json.JSONDecodeError) as e:
    messages.warning(request, f'Error parsing Groq API response: {str(e)}. Using demo recommendations.')
    return _create_demo_recommendations(user_profile)
```

#### 2. Robust Error Handling
- **Network/API Errors**: Catches `requests.exceptions.RequestException` for connection issues, timeouts, HTTP errors
- **Response Parsing Errors**: Handles `KeyError`, `IndexError`, `json.JSONDecodeError` for malformed responses
- **Graceful Fallback**: Automatically falls back to demo recommendations with user notification
- **Timeout Protection**: 30-second timeout prevents hanging requests

#### 3. Prompt Engineering
The system sends a comprehensive prompt to Groq including:
- User profile details (age, location, education, occupation, interests, goals)
- Current skill assessment data in JSON format
- Specific request for:
  1. Top 3 skill gaps for career advancement
  2. 3-month learning path with recommended resources
  3. Specific advice for women in tech/leadership roles
- Required JSON response format for structured processing

#### 4. Model Selection
- Uses `mixtral-8x7b-32768` - a high-quality, fast model from Groq
- Appropriate temperature (0.7) for balanced creativity and consistency
- Sufficient max_tokens (2000) for detailed recommendations

## Configuration Requirements

### Environment Variables
Add to `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Dependencies
Already included in `requirements.txt`:
- `requests>=2.31.0` (for HTTP calls to Groq API)

## Features

### When API Key is Available
- Makes real-time calls to Groq LLM
- Processes actual AI-generated recommendations
- Tracks which model was used (`groq_model_used` field)
- Marks recommendations as `generated_by_llm=True`

### When API Key is Unavailable or API Fails
- Gracefully falls back to demo recommendations
- Shows informative warning messages to users
- Maintains full functionality with simulated data
- Marks fallback recommendations appropriately (`generated_by_llm=False`)

## Data Flow
1. User completes skill assessment
2. System collects profile and skill data
3. Constructs detailed prompt for Groq
4. Sends request to Groq API with timeout protection
5. Processes JSON response into structured data
6. Saves recommendations to database with proper relationships
7. Redirects user to view their personalized recommendations

## Error Recovery
- Network issues → Demo mode with warning
- Invalid API key → Demo mode with warning  
- Malformed responses → Demo mode with warning
- JSON parsing failures → Demo mode with warning
- All errors preserve user experience with fallback

## Performance Considerations
- 30-second timeout prevents resource exhaustion
- Single API call per recommendation generation
- Efficient JSON processing
- Database operations wrapped in transactions implicitly

## Testing
To test the Groq integration:
1. Obtain a valid API key from https://console.groq.com/
2. Add it to `.env` file
3. Start Django development server: `python manage.py runserver`
4. Create account and complete skill assessment
5. Click "Get Recommendations" to trigger Groq API call
6. Verify recommendations are generated and stored

## Future Enhancements
- Add rate limiting awareness
- Implement caching for repeated similar requests
- Add usage monitoring and cost tracking
- Support for multiple Groq models
- Streaming responses for better UX
- Feedback loop to improve prompt engineering

---
*This integration provides a robust, production-ready connection to Groq's LLM infrastructure while maintaining excellent error handling and user experience.*