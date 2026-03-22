from google import genai

# Create client
client = genai.Client(api_key="AIzaSyBfaCWHvuaPV9mhNmUgaeIB4VaIbdEjsuI")

# List all available models
try:
    print("Fetching available models...\n")
    
    models = client.models.list()
    
    print("Available models:")
    print("-" * 50)
    
    for model in models:
        print(f"✓ {model.name}")
    
    print("-" * 50)
    
except Exception as e:
    print("❌ Failed to list models:", e)