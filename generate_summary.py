from openai import OpenAI
import requests
import json
import argparse

client = OpenAI()


def get_bearer_token(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

bearer_token = get_bearer_token("bearer_token.txt")

headers = {
    'Authorization': f'Bearer {bearer_token}'
}

def fetch_and_generate_summary(api_url, summary_label, output_file):
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        summary_list = []
        n = 0
        for item in json_data[:10]:
            label_value = item.get("value", f"Unknown {summary_label}")
            n += 1
            title = None
            first_paragraph = None
            for data_item in item.get("data", []):
                for sub_item in data_item.get("data", []):
                    if sub_item.get("key") == "Title":
                        title = sub_item.get("value")
                    for sub2_item in sub_item.get("data", []):
                        if sub2_item.get("key") == "Link":
                            for link_item in sub2_item.get("data", []):
                                if link_item.get("key") == "Emotion":
                                    for emotion_item in link_item.get("data", []):
                                        if emotion_item.get("key") == "Sentiment":
                                            for sentiment_item in emotion_item.get("data", []):
                                                if sentiment_item.get("key") == "Topic":
                                                    first_paragraph = sentiment_item.get("first_paragraph")
        
            title = title if title else "No title found"
            first_paragraph = first_paragraph if first_paragraph else "No paragraph found"
            summary_list.append(f"Berita Selanjutnya, {summary_label}: {label_value}, Title: {title}, First Paragraph: {first_paragraph};")

        combined_summary = ' '.join(summary_list)

        message = {
            "content": f'jelaskan dalam report 1 paragraf: {combined_summary}',
            "role": "system"
        }

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=[message]
    )

    message_object = completion.choices[0].message

    message_dict = {
    "content": message_object.content,
    "role": message_object.role
    }

    json_result = json.dumps(message_dict, indent=4)

    with open(output_file, 'w') as file:
        file.write(json_result)

parser = argparse.ArgumentParser(description='Fetch and summarize news data.')
parser.add_argument('--org', action='store_true', help='Summarize by organization')
parser.add_argument('--nama', action='store_true', help='Summarize by name')
parser.add_argument('--lokasi', action='store_true', help='Summarize by location')

args = parser.parse_args()

if args.org:
    fetch_and_generate_summary('https://apixplore.pustakadata.id/get-rekap-org', 'Organization', 'get-summary-org.json')
elif args.nama:
    fetch_and_generate_summary('https://apixplore.pustakadata.id/get-rekap-nama', 'Person', 'get-summary-nama.json')
elif args.lokasi:
    fetch_and_generate_summary('https://apixplore.pustakadata.id/get-rekap-lokasi', 'Lokasi', 'get-summary-lokasi.json')
else:
    print("Please provide a valid argument: --org, --nama, or --lokasi")
