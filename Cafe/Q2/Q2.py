import numpy
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import persian_normal as pn

#reading training and test data from files
train = pd.read_csv('train_set.csv')
test = pd.read_csv('test_set.csv')

# reading stop words from text file
stop_words_path = 'persian_stop_words_clean.txt'
stop_words = set([pn.persian_pre_process(w) for w in
                      open(stop_words_path, encoding='utf-8').read().split()])

# preprocessing training and test data (just keeping persian characters, replacing half-space and enter with full-space and removing stop words)
train['desc_proc'] = train['description_fa'].apply(lambda x: pn.persian_pre_process(x,
                        for_view=False,
                        print_log=False,
                        ok_characters=['fa'],
                        special_characters=[],
                        nim_fasele_action='Space',
                        enter_action='Space',
                        stop_words=stop_words))

test['desc_proc'] = test['description_fa'].apply(lambda x: pn.persian_pre_process(x,
                        for_view=False,
                        print_log=False,
                        ok_characters=['fa'],
                        special_characters=[],
                        nim_fasele_action='Space',
                        enter_action='Space',
                        stop_words=stop_words))

train_df, test_df = train, test

#storing training data labels in seperate variable
train_labels = train['label']

# creating a pipeline for converting preprocessed text to count tokens, then tranforming to tf-idf representation and lastly applying svm classification model on them
model = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), ('clf', SVC(probability=True,kernel='linear'))])

# fitting the created pipeline on training data
model = model.fit(train_df['desc_proc'], train_labels)

# predicting test data labels and their respective probabilitis using trained model
test_df.loc[:, 'label'] = model.predict(test_df['desc_proc'])
test_df.loc[:, 'predicted_prob'] = numpy.amax(model.predict_proba(test_df['desc_proc']), axis=1)

# storing the test data labels and ids in a dataframe and then saving the result in a csv file
res = test_df[['app_id','label']]
res.to_csv('prediction.csv', index=False)