# -*- coding: utf-8 -*-
"""postMidterm.ipynb

Automatically generated by Colaboratory.


"""

import pandas as pd
import numpy as np
from imblearn.under_sampling import ClusterCentroids
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split,KFold,cross_val_score,StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, chi2, f_regression

df=pd.read_csv('survival.csv',header=0)
# Dropping irrelevant columns
df.drop(['encounter_id','patient_id','hospital_id','icu_id','Unnamed: 83'],inplace=True,axis=1)
# Dealing with negative probabilities
df.drop(df[(df['apache_4a_hospital_death_prob'] <0)].index, inplace=True)
df.drop(df[(df['apache_4a_icu_death_prob'] <0)].index, inplace=True)
df=df.fillna(df.median()) #Mean imputation for numeric features
df = df.fillna(df.mode().iloc[0]) # Mode imputation for categorical features
# Dropping more columns
df.drop(['aids','leukemia','lymphoma'],inplace=True,axis=1)

# Outlier treatment
for col in df.columns:
    if df[col].dtype=='int64' or df[col].dtype=='float64':
        uq=np.percentile(df[col],[99])[0] #Upper Quartile
        df[col][(df[col] > 3*uq)] = 3*uq
        lq=np.percentile(df[col],[1])[0] #Lower quartile
        df[col][(df[col] < 0.3*lq)] = 0.3*lq

#Generating dummy variables
df=pd.get_dummies(df, columns=['ethnicity','gender','icu_admit_source','icu_stay_type','icu_type','apache_3j_bodysystem','apache_2_bodysystem'],drop_first=True)

df.columns

#Basic model
X=df.loc[:,df.columns!='hospital_death']
Y=df['hospital_death']

X.shape

scaler=StandardScaler()
scaler.fit(X)
X=scaler.transform(X)
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.3,random_state=42)

#method to produce cross-validation scores depending upon the selected model
def cross_val(model,X,Y):
    cfv = StratifiedKFold(n_splits=10, random_state=5, shuffle=True)
    scores = cross_val_score(model, X, Y, scoring='f1', cv=cfv, n_jobs=-1)
    scores1 = cross_val_score(model, X, Y, scoring='precision', cv=cfv, n_jobs=-1)
    scores2 = cross_val_score(model, X, Y, scoring='recall', cv=cfv, n_jobs=-1)
    print("Precison Score: ",np.mean(scores1))
    print("Recall Score: ",np.mean(scores2))
    print("F1 Score: ",np.mean(scores),'\n')

### Basic Logistic Regression Model

#Logistic Regression
lrm=LogisticRegression(random_state=42)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm,X,Y)
lrm.fit(X_train,Y_train)
print(classification_report(Y_test,lrm.predict(X_test)))

"""### Resampling without Feature Engineering"""

#Undersampling

cc=ClusterCentroids(sampling_strategy='majority',random_state=52)

X_under,Y_under=cc.fit_resample(X,Y)

"""#### Logistic Regression using Cluster Centroids"""

lrm1=LogisticRegression(random_state=42)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm1,X_under,Y_under)
X_train,X_test,Y_train,Y_test=train_test_split(X_under,Y_under,test_size=0.3,random_state=42)
lrm1.fit(X_train,Y_train)
print(classification_report(Y_test,lrm1.predict(X_test)))

#Oversampling

X_new=X.astype(np.uint8) #Modifying the data type to get optimal runtime
Y_new=Y.astype(np.uint8)

smt=SMOTE(sampling_strategy='minority',k_neighbors=5,random_state=42)
X_over,Y_over=smt.fit_resample(X_new,Y_new)

Y_new=Y.astype(np.uint8)
smt=SMOTE(sampling_strategy='minority',k_neighbors=5,random_state=42)
X_over,Y_over=smt.fit_resample(X_new,Y_new)

"""#### Logistic Regression using SMOTE"""

lrm2=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm2,X_over,Y_over)
X_train,X_test,Y_train,Y_test=train_test_split(X_over,Y_over,test_size=0.3,random_state=42)
lrm2.fit(X_train,Y_train)
print(classification_report(Y_test,lrm2.predict(X_test)))

#Combined resampling

stmk=SMOTETomek(random_state=42)
X_comb,Y_comb=stmk.fit_resample(X_new,Y_new)

"""#### Logistic Regression using SMOTETomek"""

lrm3=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm3,X_comb,Y_comb)
X_train,X_test,Y_train,Y_test=train_test_split(X_comb,Y_comb,test_size=0.3,random_state=42)
lrm3.fit(X_train,Y_train)
print(classification_report(Y_test,lrm3.predict(X_test)))

"""### Feature Engineering 1"""

#Select From Model

sfm_selector = SelectFromModel(estimator=LogisticRegression()).fit(X,Y)
X=sfm_selector.transform(X)

"""#### Logistic Regression using SelectFromModel and no resampling"""

lrm4=LogisticRegression(random_state=42)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm4,X,Y)
X_train,X_test,Y_train,Y_test=train_test_split(X,Y,test_size=0.3,random_state=42)
lrm4.fit(X_train,Y_train)
print(classification_report(Y_test,lrm4.predict(X_test)))

"""#### Logistic Regression using Cluster Centroids and SelectFromModel"""

#UnderSampling
X_under,Y_under=cc.fit_resample(X,Y)
lrm5=LogisticRegression(random_state=42)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm5,X_under,Y_under)
X_train,X_test,Y_train,Y_test=train_test_split(X_under,Y_under,test_size=0.3,random_state=42)
lrm5.fit(X_train,Y_train)
print(classification_report(Y_test,lrm5.predict(X_test)))

"""#### Logistic Regression using SMOTE and SelectFromModel"""

#oversampling

X_new=X.astype(np.uint8)
Y_new=Y.astype(np.uint8)
smt=SMOTE(sampling_strategy='minority',k_neighbors=5,random_state=42)
X_over,Y_over=smt.fit_resample(X_new,Y_new)

lrm2=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm2,X_over,Y_over)
X_train,X_test,Y_train,Y_test=train_test_split(X_over,Y_over,test_size=0.3,random_state=42)
lrm2.fit(X_train,Y_train)
print(classification_report(Y_test,lrm2.predict(X_test)))

"""#### Logistic Regression using SMOTETomek and SelectFromModel"""

#Combined resampling

stmk=SMOTETomek(random_state=42)
X_comb,Y_comb=stmk.fit_resample(X_new,Y_new)

lrm3=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm3,X_comb,Y_comb)
X_train,X_test,Y_train,Y_test=train_test_split(X_comb,Y_comb,test_size=0.3,random_state=42)
lrm3.fit(X_train,Y_train)
print(classification_report(Y_test,lrm3.predict(X_test)))

"""### Feature Engineering 2"""

# selectK Best

print(X.shape)
len(X)
X_clf = SelectKBest(score_func=f_regression,k=50).fit_transform(X,Y)
X_train,X_test,Y_train,Y_test=train_test_split(X_clf,Y,test_size=0.3,random_state=42)

X_clf.shape

"""#### Logistic Regression using SelectKBest and no Resampling"""

lrm=LogisticRegression(random_state=42,max_iter=100)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm,X_clf,Y)
lrm.fit(X_train,Y_train)
print(classification_report(Y_test,lrm.predict(X_test)))

"""#### Logistic Regression using Cluster Centroids and SelectKBest"""

#UnderSampling
X_under,Y_under=cc.fit_resample(X_clf,Y)
lrm5=LogisticRegression(random_state=42)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm5,X_under,Y_under)
X_train,X_test,Y_train,Y_test=train_test_split(X_under,Y_under,test_size=0.3,random_state=42)
lrm5.fit(X_train,Y_train)
print(classification_report(Y_test,lrm5.predict(X_test)))

"""#### Logistic Regression using SMOTE and SelectKBest"""

#oversampling

X_new=X_clf.astype(np.uint8)
Y_new=Y.astype(np.uint8)
smt=SMOTE(sampling_strategy='minority',k_neighbors=5,random_state=42)
X_over,Y_over=smt.fit_resample(X_new,Y_new)

lrm2=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm2,X_over,Y_over)
X_train,X_test,Y_train,Y_test=train_test_split(X_over,Y_over,test_size=0.3,random_state=42)
lrm2.fit(X_train,Y_train)
print(classification_report(Y_test,lrm2.predict(X_test)))

"""#### Logistic Regression using SMOTETomek and SelectKBest"""

# combined resampling

stmk=SMOTETomek(random_state=42)
X_comb,Y_comb=stmk.fit_resample(X_clf,Y)

lrm3=LogisticRegression(random_state=42,max_iter=150)
print('Stratified 10 fold cross validation scores:')
cross_val(lrm3,X_comb,Y_comb)
X_train,X_test,Y_train,Y_test=train_test_split(X_comb,Y_comb,test_size=0.3,random_state=42)
lrm3.fit(X_train,Y_train)
print(classification_report(Y_test,lrm3.predict(X_test)))

"""### Interpretation (SMOTETomek without feature engineering)"""

from interpret.glassbox import ExplainableBoostingClassifier

ebm = ExplainableBoostingClassifier()
ebm.fit(X_comb, Y_comb) #Retreiving results results from SMOTETomek

from interpret import show

ebm_global = ebm.explain_global()
show(ebm_global)

X_train,X_test,Y_train,Y_test=train_test_split(X_comb,Y_comb,test_size=0.3,random_state=42)
ebm_local = ebm.explain_local(X_test, Y_test)
show(ebm_local)