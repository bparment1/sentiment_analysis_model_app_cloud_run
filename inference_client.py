import json
import requests
import argparse

#url = 'http://localhost:8000/predict'
#API_URL = 'http://127.0.0.1:8000/predict'
API_URL = "https://sentiment-api-524111024198.us-east1.run.app"

def create_parser():
    parser_agent = argparse.ArgumentParser(description='Sentiment analysis')
    parser_agent.add_argument('--input_text', type=str, help='Text for which sentiment is generated', default='',required=True)
    parser_agent.add_argument('--url', type=str, help='API endpoint url', default='',required=True)

    return parser_agent

def predict(text, url=API_URL):
    payload = json.dumps({'text': text})
    try:
        response = requests.post(url, 
                                 data=payload, 
                                 headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print(f"Error: could not connect to {url}. Is the server running?")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e} — {response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")
 
 
def main():
    parser = create_parser()
    args = parser.parse_args()
 
    print(f"Sending request to {args.url}")
    print(f"Text: {args.input_text}")
 
    result = predict(args.input_text, args.url)
    if result:
        print(f"Prediction: {result}")
 
 
if __name__ == "__main__":
    main()
 
 
'''
python inference_client.py \
--input_text "The meal service was not very good and we didn't get water" \
--url "http://127.0.0.1:8000/predict"
'''