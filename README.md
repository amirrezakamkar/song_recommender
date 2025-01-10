# MelodyMatch
## A song recommendation app based on user's favorite song input.

### 1. Project overview
The aim of this Project was to create a streamlit app for song recommendation based on user's input for his favorite song. The Machine Learning model has been trainedUsing based on a subset of Million Song Database and Spotify API. The user can enter any song that exist in Spotify, but the suggestions are limited to the database.
### 2. The app
The app can be seen in the following link:

### 3. Model used and evevaluation
In this project, the KMeans model from the sklearn library was utilized. The model was trained with cluster values ranging from k=2k=2 to k=51k=51 to generate the silhouette and elbow charts. Based on the analysis of these charts, k=9k=9 was identified as the optimal number of clusters and was subsequently used in the project.
![Alt text](https://github.com/amirrezakamkar/song_recommender/blob/main/images/elbow.png)
![Alt text](https://github.com/amirrezakamkar/song_recommender/blob/main/images/silhouette.png)
