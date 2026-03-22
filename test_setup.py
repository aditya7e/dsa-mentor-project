# Test all imports
try:
    from flask import Flask, jsonify, request
    print("✅ Flask imported successfully")
except Exception as e:
    print("❌ Flask import failed:", e)

try:
    from flask_cors import CORS
    print("✅ Flask-CORS imported successfully")
except Exception as e:
    print("❌ Flask-CORS import failed:", e)

try:
    import requests
    print("✅ Requests imported successfully")
except Exception as e:
    print("❌ Requests import failed:", e)

try:
    import google.genai as genai
    print("✅ Google Generative AI imported successfully")
except Exception as e:
    print("❌ Google Generative AI import failed:", e)

print("\n🎉 All packages are ready!")