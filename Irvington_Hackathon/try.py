import openai

openai.api_key = "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"

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}]
)

print(response['choices'][0]['message']['content'])