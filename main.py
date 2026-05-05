from flask import Flask, request
import processing.processing as processing

app = Flask(__name__) # creates an instance of a Flask app
port = 8000

bucket_name = 'sentiment_analysis_model_app2'
project_name = 'mlops-494715' #this is the project ID

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the Sentiment Analysis Model app'

@app.route('/predict',methods=['POST'])
#def predict(request):
def predict():
    request_data = request.get_json(force=True)
    sample_text = request_data['text']
    predictions_outputs = processing.model_inference(sample_text,bucket_name,project_name)
    outputs = predictions_outputs.tolist()  # this must be a list for the request response
    return outputs

#if __name__ == '__main__':
#    app.run(port=8000,debug=True)
#app.debug=False #don't use when using ngrok or gunicorn when not debugging
#app.run(host='0.0.0.0', port=port,debug=True) # starts the web app at port 8000

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
