import json
import requests

## Call the local test function:

#url = 'http://localhost:8501/predict'
#url = 'http://127.0.0.1:5555/predict' #same as localhost
url = 'http://127.0.0.1:8000/predict' #same as localhost
#http://127.0.0.1:8000

#request_data = json.dumps({'text': 'rf'})
sample="The meal service was not very good and we didn't get water"
request_data = json.dumps({'text': sample})

response = requests.post(url,request_data)
print(response)
print(response.text)

