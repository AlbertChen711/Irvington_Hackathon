import openai

# Test with the old openai library
openai.api_key = "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"

print("Testing API key...")
try:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print("✅ API Key WORKS!")
    print(response['choices'][0]['message']['content'])
except Exception as e:
    print(f"❌ API Key FAILED: {str(e)}")
