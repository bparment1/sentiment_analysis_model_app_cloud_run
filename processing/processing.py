
'''
def clean_text(data):
    # download the necessary files
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')

    # 1. Removing URLS
    data = re.sub('http\S+', '', data).strip()
    data = re.sub('www\S+', '', data).strip()

    # 2. Removing Tags
    data = re.sub('#\S+', '', data).strip()

    # 3. Removing Mentions
    data = re.sub('@\S+', '', data).strip()

    # 4. Removing upper brackets to keep negative auxiliary verbs in text
    data = data.replace("'", "")

    # 5. Tokenize
    text_tokens = word_tokenize(data.lower())

    # 6. Remove Puncs and number
    tokens_without_punc = [w for w in text_tokens if w.isalpha()]

    # 7. Removing Stopwords
    stop_words = stopwords.words('english')
    for i in ["not", "no"]:
        stop_words.remove(i)
    tokens_without_sw = [t for t in tokens_without_punc if t not in stop_words]

    # 8. lemma
    text_cleaned = [WordNetLemmatizer().lemmatize(t) for t in tokens_without_sw]

    # joining
    return " ".join(text_cleaned)


def model_inference(sample):
    #assuming we have pickle objects in the models directory
    # Loading model to compare the results
    model = pickle.load(open('./models/model_rf.pkl', 'rb'))
    tfidf_vectorizer = pickle.load(open('./models/tfidf_vectorizer.pkl', 'rb'))

    sample_cleaned = clean_text(sample)
    #sample_cleaned = sample
    sample_vectorized = tfidf_vectorizer.transform([sample_cleaned])
    y_pred = model.predict(sample_vectorized)

    return y_pred

'''

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
        text = re.sub(r'http\S+', '', text).strip()
        text = re.sub(r'www\S+', '', text).strip()
        text = re.sub(r'#\S+', '', text).strip()
        text = re.sub(r'@\S+', '', text).strip()
        text = text.replace("'", "")

        tokens = word_tokenize(text.lower())
        tokens = [w for w in tokens if w.isalpha()]
        tokens = [t for t in tokens if t not in self.stop_words]
        tokens = [self.lemmatizer.lemmatize(t) for t in tokens]

        return " ".join(tokens)

    def clean(self, data):
        if not isinstance(data, pd.Series):
          data = pd.Series(data)
        return data.apply(self.clean_single)

'''
def model_inference(sample):
    #assuming we have pickle objects in the models directory
    # Loading model to compare the results
    model = pickle.load(open('./models/model_rf.pkl', 'rb'))
    tfidf_vectorizer = pickle.load(open('./models/tfidf_vectorizer.pkl', 'rb'))

    sample_cleaned = clean_text(sample)
    #sample_cleaned = sample
    sample_vectorized = tfidf_vectorizer.transform([sample_cleaned])
    y_pred = model.predict(sample_vectorized)

    return y_pred
'''

'''
def model_inference(sample):
    pipe = joblib.load('./models/pipeline.joblib')
    y_pred = pipe.predict([sample])
    return y_pred
'''


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
