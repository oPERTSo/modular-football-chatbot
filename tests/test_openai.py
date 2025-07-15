import openai

openai.api_key = "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"

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, who are you?"}]
    )
    print("SUCCESS! Your key works. Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("ERROR: ", e)
