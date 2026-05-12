import pickle
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd
from google.cloud import storage
import os

# download the necessary files
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

class TextCleaner:
    def __init__(self):
        sw = stopwords.words('english')
        for i in ["not", "no"]:
            sw.remove(i)
        self.stop_words = sw
        self.lemmatizer = WordNetLemmatizer()

    def clean_single(self, text):
        text = re.sub(r'http\S+', '', text).strip() # removes URLs:"check http://example.com" → "check"
        text = re.sub(r'www\S+', '', text).strip() # removes www links: "visit www.site.com" → "visit"
        text = re.sub(r'#\S+', '', text).strip() # removes hashtags:  "#great movie" → "movie"
        text = re.sub(r'@\S+', '', text).strip() # removes mentions:  "@user loved it" → "loved it"
        text = text.replace("'", "") # removes apostrophes: "didn't" → "didnt"

        tokens = word_tokenize(text.lower()) # splits into tokens: "Great Movie" → ["great", "movie"]
        tokens = [w for w in tokens if w.isalpha()] # removes numbers/punctuation
        tokens = [t for t in tokens if t not in self.stop_words] # removes English stopwords: "the", "is", "at"
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens] # "movies" → "movie", "loved" → "love"

        return " ".join(tokens)

    def clean(self, data):
        if not isinstance(data, pd.Series):
          data = pd.Series(data)
        return data.apply(self.clean_single)

# Currently: downloads model from GCS on EVERY API call → slow! We need to rewrite this.

def model_inference(sample,bucket_name,project_name):
    #assuming we have pickle objects in the models directory in GCP bucket

    # Loading model to predict
    storage_client = storage.Client(project=project_name)
    # client = storage.Client(project='your-project-id')
    bucket = storage_client.get_bucket(bucket_name)
    blob_model = bucket.blob('models/pipeline.joblib')
    #print(type(blob_model))
    # Ensure tmp directory exists
    os.makedirs('./tmp', exist_ok=True)
    blob_model.download_to_filename('./tmp/pipeline.joblib')
    pipe = joblib.load('./tmp/pipeline.joblib')
    #print(type(pipe))
    y_pred = pipe.predict([sample])

    return y_pred
