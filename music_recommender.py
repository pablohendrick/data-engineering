from pyspark.ml.feature import VectorAssembler

encoded_data_vector = VectorAssembler(inputCols=X, outputCol='features').transform(df_data)
encoded_data_vector.select('features').show(truncate=False, n=5)

from pyspark.ml.feature import StandardScaler

scaler = StandardScaler(inputCol='features', outputCol='features_scaled')
model_scaler = scaler.fit(encoded_data_vector)
scaled_music_data = model_scaler.transform(encoded_data_vector)

scaled_music_data.select('features_scaled').show(truncate=False, n=5)

k = len(X)
k

from pyspark.ml.feature import PCA

pca = PCA(k=k, inputCol='features_scaled', outputCol='pca_features')
model_pca = pca.fit(scaled_music_data)
music_data_pca = model_pca.transform(scaled_music_data)

model_pca.explainedVariance

sum(model_pca.explainedVariance) * 100

values_list = [sum(model_pca.explainedVariance[0:i+1]) for i in range(k)]
values_list

import numpy as np

k = sum(np.array(values_list) <= 0.7)
k

pca = PCA(k=k, inputCol='features_scaled', outputCol='pca_features')
model_pca = pca.fit(scaled_music_data)
final_music_data_pca = model_pca.transform(scaled_music_data)

final_music_data_pca.select('pca_features').show(truncate=False, n=5)

from pyspark.ml import Pipeline

pca_pipeline = Pipeline(stages=[VectorAssembler(inputCols=X, outputCol='features'),
                                StandardScaler(inputCol='features', outputCol='features_scaled'),
                                PCA(k=6, inputCol='features_scaled', outputCol='pca_features')])

model_pca_pipeline = pca_pipeline.fit(df_data)

projection = model_pca_pipeline.transform(df_data)

projection.select('pca_features').show(truncate=False, n=5)

from pyspark.ml.clustering import KMeans

SEED = 1224

kmeans = KMeans(k=50, featuresCol='pca_features', predictionCol='cluster_pca', seed=SEED)

kmeans_model = kmeans.fit(projection)

projection_kmeans = kmeans_model.transform(projection) 

projection_kmeans.select(['pca_features','cluster_pca']).show()

from pyspark.ml.functions import vector_to_array

projection_kmeans = projection_kmeans.withColumn('x', vector_to_array('pca_features')[0])\
                                     .withColumn('y', vector_to_array('pca_features')[1])

projection_kmeans.select(['x', 'y', 'cluster_pca', 'artists_song']).show()

import plotly.express as px

fig = px.scatter(projection_kmeans.toPandas(), x='x', y='y', color='cluster_pca', hover_data=['artists_song'])
fig.show()

song_name = 'Taylor Swift - Style'

cluster = projection_kmeans.filter(projection_kmeans.artists_song == song_name).select('cluster_pca').collect()[0][0]
cluster

recommended_songs = projection_kmeans.filter(projection_kmeans.cluster_pca == cluster)\
                                    .select('artists_song', 'id', 'pca_features')
recommended_songs.show()

song_components = recommended_songs.filter(recommended_songs.artists_song == song_name)\
                                  .select('pca_features').collect()[0][0]
song_components   

from scipy.spatial.distance import euclidean
from pyspark.sql.types import FloatType
import pyspark.sql.functions as f

def calculate_distance(value):
    return euclidean(song_components, value)

udf_calculate_distance = f.udf(calculate_distance, FloatType())

recommended_songs_distance = recommended_songs.withColumn('Dist', udf_calculate_distance('pca_features'))

recommended = spark.createDataFrame(recommended_songs_distance.sort('Dist').take(10)).select(['artists_song', 'id', 'Dist'])

recommended.show()

def song_recommender(song_name):
    cluster = projection_kmeans.filter(projection_kmeans.artists_song == song_name).select('cluster_pca').collect()[0][0]
    recommended_songs = projection_kmeans.filter(projection_kmeans.cluster_pca == cluster)\
                                         .select('artists_song', 'id', 'pca_features')
    song_components = recommended_songs.filter(recommended_songs.artists_song == song_name)\
                                       .select('pca_features').collect()[0][0]

    def calculate_distance(value):
        return euclidean(song_components, value)

    udf_calculate_distance = f.udf(calculate_distance, FloatType())

    recommended_songs_distance = recommended_songs.withColumn('Dist', udf_calculate_distance('pca_features'))

    recommended = spark.createDataFrame(recommended_songs_distance.sort('Dist').take(10)).select(['artists_song', 'id', 'Dist'])

    return recommended

df_recommended = song_recommender('Taylor Swift - Style')
df_recommended.show()

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

scope = "user-library-read playlist-modify-private"

OAuth = SpotifyOAuth(
        scope=scope,         
        redirect_uri='http://localhost:5000/callback',
        client_id = '76384hdh4nd33939jnd893923204j8f9',
        client_secret = 'dj439fgj93492309jf93jf848fjj')

client_credentials_manager = SpotifyClientCredentials(client_id = '76384hdh4nd33939jnd893923204j8f9', 
                                                      client_secret = 'dj439fgj93492309jf93jf848fjj') #non-existing tokens

sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

id = projection_kmeans.filter(projection_kmeans.artists_song == song_name).select('id').collect()[0][0]
id

sp.track(id)

playlist_id = df_recommended.select('id').collect()

playlist_track = []
for id in playlist_id:
    playlist_track.append(sp.track(id[0]))

def song_recommender(song_name):
    cluster = projection_kmeans.filter(projection_kmeans.artists_song == song_name).select('cluster_pca').collect()[0][0]
    recommended_songs = projection_kmeans.filter(projection_kmeans.cluster_pca == cluster)\
                                         .select('artists_song', 'id', 'pca_features')
    song_components = recommended_songs.filter(recommended_songs.artists_song == song_name)\
                                       .select('pca_features').collect()[0][0]

    def calculate_distance(value):
        return euclidean(song_components, value)

    udf_calculate_distance = f.udf(calculate_distance, FloatType())

    recommended_songs_distance = recommended_songs.withColumn('Dist', udf_calculate_distance('pca_features'))

    recommended = spark.createDataFrame(recommended_songs_distance.sort('Dist').take(10)).select(['artists_song', 'id', 'Dist'])
    
    playlist_id = recommended.select('id').collect()
    
    playlist_track = []
    
    for id in playlist_id:
        playlist_track.append(sp.track(id[0]))

    return len(playlist_track)

song_recommender('Taylor Swift - Style')

import matplotlib.pyplot as plt
from skimage import io

song_name = 'Taylor Swift - Blank Space'

id = projection_kmeans\
          .filter(projection_kmeans.artists_song == song_name)\
          .select('id').collect()[0][0]

track = sp.track(id)

url = track["album"]["images"][1]["url"]
name = track["name"]

image = io.imread(url)
plt.imshow(image)
plt.xlabel(name, fontsize=10)
plt.show()

import matplotlib.pyplot as plt
from skimage import io

def visualize_songs(name, url):

    plt.figure(figsize=(15, 10))
    columns = 5
    for i, u in enumerate(url):
        ax = plt.subplot(len(url) // columns + 1, columns, i + 1)
        image = io.imread(u)
        plt.imshow(image)
        ax.get_yaxis().set_visible(False)
        plt.xticks(color='w', fontsize=0.1)
        plt.yticks(color='w', fontsize=0.1)
        plt.xlabel(name[i], fontsize=10)
        plt.tight_layout(h_pad=0.7, w_pad=0)
        plt.subplots_adjust(wspace=None, hspace=None)
        plt.grid(visible=None)
    plt.show()

playlist_id = df_recommended.select('id').collect()

name = []
url = []
for i in playlist_id:
    track = sp.track(i[0])
    url.append(track["album"]["images"][1]["url"])
    name.append(track["name"])

visualize_songs(name, url)

def song_recommender(song_name):
    cluster = projection_kmeans.filter(projection_kmeans.artists_song == song_name).select('cluster_pca').collect()[0][0]
    recommended_songs = projection_kmeans.filter(projection_kmeans.cluster_pca == cluster)\
                                         .select('artists_song', 'id', 'pca_features')
    song_components = recommended_songs.filter(recommended_songs.artists_song == song_name)\
                                       .select('pca_features').collect()[0][0]

    def calculate_distance(value):
        return euclidean(song_components, value)

    udf_calculate_distance = f.udf(calculate_distance, FloatType())

    recommended_songs_distance = recommended_songs.withColumn('Dist', udf_calculate_distance('pca_features'))

    recommended = spark.createDataFrame(recommended_songs_distance.sort('Dist').take(10)).select(['artists_song', 'id', 'Dist'])

    playlist_id = recommended.select('id').collect()
    name = []
    url = []
    for i in playlist_id:
        track = sp.track(i[0])
        url.append(track["album"]["images"][1]["url"])
        name.append(track["name"])

    plt.figure(figsize=(15, 10))
    columns = 5
    for i, u in enumerate(url):
        ax = plt.subplot(len(url) // columns + 1, columns, i + 1)
        image = io.imread(u)
        plt.imshow(image)
        ax.get_yaxis().set_visible(False)
        plt.xticks(color='w', fontsize=0.1)
        plt.yticks(color='w', fontsize=0.1)
        plt.xlabel(name[i], fontsize=10)
        plt.tight_layout(h_pad=0.7, w_pad=0)
        plt.subplots_adjust(wspace=None, hspace=None)
        plt.grid(visible=None)
    plt.show()

song_recommender('Taylor Swift - Style')
