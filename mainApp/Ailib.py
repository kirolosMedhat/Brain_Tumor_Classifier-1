"""This module is specific to all machine learning tasks. """
import os
import cv2
import pandas as pd
from PIL import Image
import numpy as np
from annoy import AnnoyIndex
from tensorflow import keras
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# loading Machine learning models
bi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                   r'\mlModels\bi_model2.h5')
multi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                      r'\mlModels\multi_model.h5')


class config:
    image_data_with_features_pkl = os.path.join('meta-data-files/', 'image_data_features.pkl')
    image_features_vectors_ann = os.path.join('meta-data-files/', 'image_features_vectors.ann')


class Predictions:
    """This class is specific to predicting tumors."""

    def biModelPrediction(image_path):
        image = cv2.imread(str(image_path))
        image = cv2.resize(image, (224, 224))
        image = np.reshape(image, [1, 224, 224, 3])
        image = np.array(image)
        return bi_model.predict(image)

    def multiModelPrediction(image_path):
        image = cv2.imread(str(image_path))
        image = cv2.resize(image, (224, 224))
        image = np.reshape(image, [1, 224, 224, 3])
        image = np.array(image)
        multi_prediction = multi_model.predict(image)
        return multi_prediction.tolist()

    def multiModelTranslate(multiModelPrediction):
        class_names = ['glioma', 'meningioma', 'ptitutary']
        index = np.argmax(multiModelPrediction)
        return class_names[index]


class FeatureExtractor:
    def __init__(self):
        base_model = multi_model
        # Customize the model to return features from fully-connected layer
        self.model = Model(inputs=base_model.input, outputs=base_model.output)

    def extract(self, img):
        # Resize the image
        img = img.resize((224, 224))
        # Convert the image color space
        img = img.convert('RGB')
        # Reformat the image
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        # Extract Features
        feature = self.model.predict(x)[0]
        return feature / np.linalg.norm(feature)

    def get_feature(self, image_data: list):
        self.image_data = image_data
        # fe = FeatureExtractor()
        features = []
        for img_path in self.image_data:  # Iterate through images
            # Extract Features
            try:
                feature = self.extract(img=Image.open(img_path))
                features.append(feature)
            except:
                features.append(None)
                continue
        return features


class Index:
    def __init__(self, image_list: list):
        self.image_list = image_list
        if 'meta-data-files' not in os.listdir():
            os.makedirs("meta-data-files")
        self.FE = FeatureExtractor()

    def start_feature_extraction(self):
        image_data = pd.DataFrame()
        image_data['images_paths'] = self.image_list
        f_data = self.FE.get_feature(self.image_list)
        image_data['features'] = f_data
        image_data = image_data.dropna().reset_index(drop=True)
        image_data.to_pickle(config.image_data_with_features_pkl)
        print("Image Meta Information Saved: [meta-data-files/image_data_features.pkl]")
        return image_data

    def start_indexing(self, image_data):
        self.image_data = image_data
        f = len(image_data['features'][0])  # Length of item vector that will be indexed
        t = AnnoyIndex(f, 'euclidean')
        for i, v in zip(self.image_data.index, image_data['features']):
            t.add_item(i, v)
        t.build(100)  # 100 trees
        print("Saved the Indexed File:" + "[meta-data-files/image_features_vectors.ann]")
        t.save(config.image_features_vectors_ann)

    def Start(self):
        data = self.start_feature_extraction()
        self.start_indexing(data)


class SearchImage:
    def __init__(self):
        self.image_data = pd.read_pickle(config.image_data_with_features_pkl)
        self.f = len(self.image_data['features'][0])

    def search_by_vector(self, v, n: int):
        self.v = v  # Feature Vector
        self.n = n  # number of output
        u = AnnoyIndex(self.f, 'euclidean')
        u.load(config.image_features_vectors_ann)  # super-fast, will just mmap the file
        index_list = u.get_nns_by_vector(self.v, self.n)  # will find the 10 nearest neighbors
        return dict(zip(index_list, self.image_data.iloc[index_list]['images_paths'].to_list()))

    def get_query_vector(self, image_path: str):
        self.image_path = image_path
        img = Image.open(self.image_path)
        fe = FeatureExtractor()
        query_vector = fe.extract(img)
        return query_vector

    def get_similar_images(self, image_path: str, number_of_images: int):
        self.image_path = image_path
        self.number_of_images = number_of_images
        query_vector = self.get_query_vector(self.image_path)
        img_dict = self.search_by_vector(query_vector, self.number_of_images)
        return img_dict
