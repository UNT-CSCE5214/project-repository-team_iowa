#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import sklearn
import math
import re
from pathlib import Path
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score,roc_auc_score


# In[2]:


# Import data
df_train = pd.read_csv('train_canonical.csv')
df_train.shape


# In[3]:


df_train = pd.read_csv('train_data.csv')
df_train = df_train[['user_review','user_suggestion']]
df_train


# In[4]:


#change the label
df_train = df_train.rename(columns={'user_suggestion':'label'})


# In[5]:


df_train.head()


# In[6]:


df_train['label'].unique()


# In[7]:


df_train.info()


# In[8]:


# tokenize word from game review
import re

def process_text(content):
    sentence = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','', content['user_review'])
    sentence = re.sub('@[^\s]+','', sentence)
    sentence = sentence.lower().split()
    reformed_sentence = [word for word in sentence]
    reformed_sentence = " ".join(reformed_sentence) 
    sentence = re.sub('&[^\s]+;', '', reformed_sentence)
    sentence = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', sentence)
    sentence = re.sub(' +',' ', sentence)
    #text = re.sub(' [\w] ', ' ', text)
    return sentence.strip()

df_train['user_review'] = df_train.apply(process_text, axis=1)
pd.set_option('display.max_colwidth', None)
df_train.head()


# In[9]:


def process_text1(content):
    sentence = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','', content)
    sentence = re.sub('@[^\s]+','', sentence)
    sentence = sentence.lower().split()
    reformed_sentence = [word for word in sentence]
    reformed_sentence = " ".join(reformed_sentence) 
    sentence = re.sub('&[^\s]+;', '', reformed_sentence)
    sentence = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', sentence)
    sentence = re.sub(' +',' ', sentence)
    #text = re.sub(' [\w] ', ' ', text)
    return [sentence.strip()]


# In[10]:


process_text1('i liek @dasd,123,hello, world! hello')


# In[11]:


df_train['label'].value_counts()


# In[12]:


df_train_X = df_train['user_review']
df_train_y = df_train['label']


# In[13]:


# dataset is balanced, we don't need to deal 
df_train_y.sum()/len(df_train_y)


# In[14]:


#Import testing data
df_test = pd.read_csv('test_held_out.csv')
df_test=df_test.rename(columns={"user_suggestion":'label'})
df_test = df_test[['user_review','label']]


# In[15]:


df_test_X = df_test['user_review']
df_test_y = df_test['label']
df_test_X.shape


# In[16]:


df_test_y


# In[17]:


# Use different model and create pipeline
# 1.LogisticRegression
# 2.RandomForest
# 3.KNN
# 4.Decision Tree
# 5.SVM
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

tvec = TfidfVectorizer()
classifier_lr = LogisticRegression()
classifier_rf = RandomForestClassifier()
classifier_knn = KNeighborsClassifier()
classifier_dt = DecisionTreeClassifier()
classifier_svm = SVC()

pipeline_model_lr = Pipeline([('vectorizer1',tvec),('classifier_lr',classifier_lr)])
pipeline_model_rf = Pipeline([('vectorizer2',tvec),('classifier_rf',classifier_rf)])
pipeline_model_knn = Pipeline([('vectorizer3',tvec),('classifier_knn',classifier_knn)])
pipeline_model_dt = Pipeline([('vectorizer4',tvec),('classifier_dt',classifier_dt)])
pipeline_model_svm = Pipeline([('vectorizer5',tvec),('classifier_svm',classifier_svm)])


pipelines = [pipeline_model_lr,pipeline_model_rf,pipeline_model_knn,pipeline_model_dt,pipeline_model_svm]


# In[18]:


best_accuracy=0.0
best_classifier=0
best_pipeline=""


# In[19]:


pipe_dict = {0:'Logistic Regression',1:'RandomForest',2:'KNN',3:'Decision Tree',4:'SVM'}


# In[20]:


for pipe in pipelines:
    pipe.fit(df_train_X,df_train_y)


# In[21]:


# Accuracy
for i,model in enumerate(pipelines):
    print("{} Test Accuracy: {}".format(pipe_dict[i],accuracy_score(model.predict(df_test_X),df_test_y)))


# In[22]:


# Precision score
for i,model in enumerate(pipelines):
    print("{} Test Preception Score: {}".format(pipe_dict[i],precision_score(model.predict(df_test_X),df_test_y)))


# In[23]:


# Recall score
for i,model in enumerate(pipelines):
    print("{} Test Recall Score: {}".format(pipe_dict[i],recall_score(model.predict(df_test_X),df_test_y)))


# In[24]:


# f1 score
for i,model in enumerate(pipelines):
    print("{} Test f1 Score: {}".format(pipe_dict[i],f1_score(model.predict(df_test_X),df_test_y)))


# In[25]:


# roc_auc score
for i,model in enumerate(pipelines):
    print("{} Test f1 Score: {}".format(pipe_dict[i],roc_auc_score(model.predict(df_test_X),df_test_y)))


# In[26]:


for i,model in enumerate(pipelines):
    if accuracy_score(model.predict(df_test_X),df_test_y)>best_accuracy:
        best_accuracy = accuracy_score(model.predict(df_test_X),df_test_y)
        best_pipeline = model
        best_classifier = i
print("The best classifier is {},and accuracy is {}".format(pipe_dict[best_classifier],best_accuracy))        


# In[27]:


best_model = pipelines[[i for i in pipe_dict if pipe_dict[i]==pipe_dict[best_classifier]][0]]


# In[28]:


from sklearn.metrics import confusion_matrix
best_prediction =best_model.predict(df_test_X)
confusion_matrix(best_prediction, df_test_y)


# In[29]:


from sklearn.metrics import accuracy_score, precision_score, recall_score,f1_score

print("Best_model Accuracy : ", accuracy_score(best_prediction, df_test_y))
print("Best_model Precision : ", precision_score(best_prediction, df_test_y, average = 'weighted'))
print("Best_model Recall : ", recall_score(best_prediction, df_test_y, average = 'weighted'))
print("Best_model F1 score:",f1_score(best_prediction,df_test_y,average = 'weighted'))


# In[30]:


import pickle
file = open('sentiment_analysis_best_model.pkl','wb')
pickle.dump(best_model,file)


# In[31]:


model = pickle.load(open('sentiment_analysis_best_model.pkl','rb'))


# In[ ]:


example = 'Do NOT buy anything from them. I stupidly boug'

best_model.predict(process_text1(example))


# In[ ]:





# In[ ]:




