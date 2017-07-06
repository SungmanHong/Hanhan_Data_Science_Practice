import numpy as np 
import pandas as pd 
from pandas import Series, DataFrame 
import lightgbm as lgb 
import xgboost as xgb 
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.model_selection import train_test_split 


data=pd.read_csv('adult.csv',header=None) 
# assign column names to the data
data.columns=['age','workclass','fnlwgt','education','education-num','marital_Status','occupation','relationship','race','sex','capital_gain','capital_loss','hours_per_week','native_country','Income'] 
data.head()

# encode label
l=LabelEncoder() 
l.fit(data.Income) 
l.classes_ 
data.Income=Series(l.transform(data.Income))
data.Income.value_counts() # label has been encoded as 0, 1

# convert categorical data into one-hot, and drop original categorical data
one_hot_workclass=pd.get_dummies(data.workclass) 
one_hot_education=pd.get_dummies(data.education) 
one_hot_marital_Status=pd.get_dummies(data.marital_Status) 
one_hot_occupation=pd.get_dummies(data.occupation)
one_hot_relationship=pd.get_dummies(data.relationship) 
one_hot_race=pd.get_dummies(data.race) 
one_hot_sex=pd.get_dummies(data.sex) 
one_hot_native_country=pd.get_dummies(data.native_country) 

data.drop(['workclass','education','marital_Status','occupation','relationship','race','sex','native_country'],axis=1,inplace=True) 
data=pd.concat([data,one_hot_workclass,one_hot_education,one_hot_marital_Status,one_hot_occupation,one_hot_relationship,one_hot_race,one_hot_sex,one_hot_native_country],axis=1) 

#removing dulpicate columns 
i = np.unique(data.columns, return_index=True) 
i[1]  # index of unique columns
data=data.iloc[:, i[1]]  # use the index of unique columns
data.head()

# seperate features and the label
features = data.drop('Income',axis=1) 
label = data.Income 
label.mode()[0]
label.fillna(label.mode()[0],inplace=True)  # impute missing data with mode
label.value_counts()

# split into training and testing data
features_train,features_test,label_train,label_test=train_test_split(features,label,test_size=.3)


# Method 1 - XGBOOST, single thread
dtrain=xgb.DMatrix(features_train,label=label_train)
dtest=xgb.DMatrix(features_test)
## xgboost params
parameters={'max_depth':7, 'eta':1, 'silent':1,'objective':'binary:logistic','eval_metric':'auc','learning_rate':.05}

from datetime import datetime 
num_round=50
start = datetime.now() 
xg=xgb.train(parameters,dtrain,num_round)  # train the model
stop = datetime.now()
execution_time_xgb = stop-start 
print(execution_time_xgb)   # 0:00:06.377225

ypred=xg.predict(dtest) 
print(ypred)

#Converting probabilities into 1 or 0  
for i in range(0,9769): 
    if ypred[i]>=.5:       # setting threshold to .5 
       ypred[i]=1 
    else: 
       ypred[i]=0  
        
from sklearn.metrics import accuracy_score 
accuracy_xgb = accuracy_score(label_test,ypred) 
accuracy_xgb  # 0.86713071962329824

from sklearn.metrics import confusion_matrix, roc_auc_score
cm = confusion_matrix(label_test, ypred)
TP = cm[0][0]
FP = cm[0][1]
FN = cm[1][0]
TN = cm[1][1]

accuracy = (TP + TN)/(TP+FP+FN+TN)   # accuracy: 0.867130719623
auc_score = roc_auc_score(label_test, ypred)   # AUC: 0.775170828432
precision = TP/(TP+FP)   # 0.952047413793, how noisy the predict result is
specificity = TN/(TN+FP)  # 0.797612279704
recall = TP/(TP+FN)   # 0.882397003745, how complete the predicted result is
