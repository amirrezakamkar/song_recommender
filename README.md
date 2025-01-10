# MelodyMatch
## A song recommendation app based on user's favorite song input.

### 1. Project overview
The aim of this Project was to create a streamlit app for song recommendation based on user's input for his favorite song. The Machine Learning model has been trainedUsing based on a subset of Million Song Database and Spotify API. The user can enter any song that exist in Spotify, but the suggestions are limited to the database.
### 2. The app
The app can be seen in the following link:

https://melodymatch.streamlit.app/
### 3. Resources
For this project, a subset of Million Song Database (http://millionsongdataset.com/) has been used. Several other columns have been added using Spotify API (http://millionsongdataset.com/)

### 4. Model used and evevaluation
In this project, the KMeans model from the sklearn library was utilized. The model was trained with cluster values ranging from k=2k=2 to k=51k=51 to generate the silhouette and elbow charts. Based on the analysis of these charts, k=9k=9 was identified as the optimal number of clusters and was subsequently used in the project.
![Alt text](https://github.com/amirrezakamkar/song_recommender/blob/main/images/elbow.png)
![Alt text](https://github.com/amirrezakamkar/song_recommender/blob/main/images/silhouette.png)
![Alt text](Demo.gif)
### 5. Steps to run the app locally:
- Clone the repository
- Run this code in your enviroment to install required libraries:
    
    pip install requirements.txt
- update secrets.toml file with Spotify API credential.
- run the app locally using streamlit.
### 6. Future works
At this point, the model is functioning well, but with a larger database, the song recommendations would significantly improve. Therefore, the key improvement to focus on is creating a more extensive database and utilizing the Spotify API to expand the training features for the clustering model.