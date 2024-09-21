from sklearn.neighbors import NearestNeighbors
import pandas as pd
import sklearn.model_selection
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# reading training and test data from file
train = pd.read_csv('./train.csv')
test = pd.read_csv('./test.csv')

# concatenating historical games and next game of training data together
train['historical_games_plus_next_game'] = train['historical_games']
train.iloc[:,3] = train.iloc[:,3] + " " + train.iloc[:,2].astype(str)

# storing training data labels in a seperate variable
y = train['next_game']

# converting a training and test data features to a matrix of token counts
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(train['historical_games_plus_next_game'])
X_test = vectorizer.transform(test['historical_games'])

# finding the nearest neighbours of test data in training data
neigh = NearestNeighbors(n_neighbors=370, metric='russellrao')
neigh.fit(X_train.toarray())
x_test_neighbors = neigh.kneighbors(X_test.toarray(), return_distance=False)

# creating the result dataframe
res = pd.DataFrame({'id':test['id']})
res['next_games'] = ['' for _ in range(res.shape[0])]

# procedure of predicting test data labels by:
# 1) taking the nearest neighbours of each test data and their respective labels 
# 2) checking the existence of collected labels (in last phase) in test data history
# 3) finding the most repeated labels and picking first five in the list
# 4) storing five labels for each test data in the result dataframe and saving them in csv file
for i in range(X_test.shape[0]): 
    neighb_idx = x_test_neighbors[i]
    neighb_y = y[neighb_idx]
    nexts = []
    test_hist = test.iloc[i]['historical_games'].split(" ")
    for ny in neighb_y:
        for all_neighb in ny.split(" "):
            if all_neighb not in test_hist:
                nexts.append(all_neighb)
    nexts_series = pd.Series(nexts)
    unique_neighb_label_counts = nexts_series.value_counts()
    if len(unique_neighb_label_counts) > 5:
        unique_neighb_label_counts = unique_neighb_label_counts.iloc[:5]
    if len(unique_neighb_label_counts) < 5:
        count += 1
    res.at[i, 'next_games'] = " ".join(map(str, unique_neighb_label_counts.index.values))

res.to_csv('prediction.csv', index=False)