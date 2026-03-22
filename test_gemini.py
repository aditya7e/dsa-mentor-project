from google import genai

# Create client
client = genai.Client(api_key="AIzaSyBfaCWHvuaPV9mhNmUgaeIB4VaIbdEjsuI")

# Test a simple prompt
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say "Hello, DSA Mentor backend is connected to Gemini!" in one sentence.'
    )
    
    print("✅ Gemini API is working!")
    print("Response:", response.text)
    
except Exception as e:
    print("❌ Gemini API failed:", e)