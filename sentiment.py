# import tensorflow as tf
# from transformers import DistilBertTokenizerFast
# from transformers import TFBertForSequenceClassification
# import pandas as pd
# import numpy as np
# import nltk
# import re
# from nltk.corpus import stopwords
# from nltk.stem.porter import PorterStemmer
# nltk.download('stopwords')
# import tensorflow_datasets as tfds
# from sklearn.model_selection import train_test_split
from transformers import pipeline

class SentimentalAnalysis:
    def __init__(self):
        pass

    def train_data(self):
        classifier = pipeline('sentiment-analysis')
        return classifier.save_pretrained('NewBertModel')

    def analyse_data(self,data):
        c2 = pipeline(task = 'sentiment-analysis', model='NewBertModel')
        outputs = c2(data)
        for output in outputs:
            semtiment_review = output.get('label')
        return  semtiment_review





"""
 def analyse_data(self):
        classifier = pipeline('sentiment-analysis')
        return classifier.save_pretrained('bertModel.h5')
"""