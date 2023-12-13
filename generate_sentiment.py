from openai import OpenAI

client = OpenAI()

import json

with open('get-rekap-org.json', 'r') as file:
    json_data = json.load(file)

organization = json_data["value"]
title = json_data["data"][0]["data"][0]["value"]

message = {
    "role": "system",
    "content": f'analisa sentimen dan emosi dari berita dgn format ["sentimen","emosi"]:{title}'
}

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[message]
)

print(completion.choices[0].message.content)
