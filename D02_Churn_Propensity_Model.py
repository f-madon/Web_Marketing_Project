# -*- coding: utf-8 -*-
"""Churn Propensity - Model

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O49MSG3ZbVZKMf1AvCQkmyzoeOOtq-2B

# Importazioni
"""

# Commented out IPython magic to ensure Python compatibility.
#Standard libraries for data analysis:  
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import norm, skew
from scipy import stats
import statsmodels.api as sm

# sklearn modules for data preprocessing:
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
#sklearn modules for Model Selection:
from sklearn import svm, tree, linear_model, neighbors
from sklearn import naive_bayes, ensemble, discriminant_analysis, gaussian_process
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
#sklearn modules for Model Evaluation & Improvement:    
from sklearn.metrics import confusion_matrix, accuracy_score 
from sklearn.metrics import f1_score, precision_score, recall_score, fbeta_score
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import KFold
from sklearn import feature_selection
from sklearn import model_selection
from sklearn import metrics
from sklearn.metrics import classification_report, precision_recall_curve
from sklearn.metrics import auc, roc_auc_score, roc_curve
from sklearn.metrics import make_scorer, recall_score, log_loss
from sklearn.metrics import average_precision_score

#Standard libraries for data visualization:
import seaborn as sn
from matplotlib import pyplot
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import matplotlib 
# %matplotlib inline
color = sn.color_palette()
import matplotlib.ticker as mtick
from IPython.display import display
pd.options.display.max_columns = None
from pandas.plotting import scatter_matrix
from sklearn.metrics import roc_curve
    
import random
import os
import re
import sys
import timeit
import string
import time
from datetime import datetime
from time import time
from dateutil.parser import parse
import joblib

from importlib_metadata import version
print("Versione libreria pandas: " + version('pandas'))
print("Versione libreria numpy: " + version('numpy'))
print("Versione libreria re: " + version('regex'))
print("Versione libreria scipy: " + version('scipy'))
print("Versione libreria matplotlib: " + version('matplotlib'))
print("Versione libreria seaborn: " + version('seaborn'))
print("Versione libreria scikit-learn: " + version('scikit-learn'))
print("Versione libreria joblib: " + version('joblib'))

from google.colab import drive
drive.mount('/content/drive')

BASE_PATH = '/content/drive/MyDrive/Progetto_Web/Dataset_Clean/'

#Importation of Datasets
# df1: contiene informazioni sugli abbonamenti fedelt?? di ciascun account cliente
df1 = pd.read_csv(BASE_PATH + 'df1.csv', sep = ',', na_values = '', encoding = 'latin-1')
# df2: contiene informazioni su ciascun account cliente e descrive le caratteristiche di esse, tra la prima tabella e la seconda ci sono dei duplicati, 
# per esempio, perch?? un cliente pu?? avere pi?? tessere fedelt?? o la stessa tessera fedelt?? pu?? appartenere a pi?? clienti
df2 = pd.read_csv(BASE_PATH + 'df2.csv', sep = ',', na_values = '', encoding = 'latin-1')
# df3: contiene informazioni sull'indirizzo corrispondente a un account cliente
df3 = pd.read_csv(BASE_PATH + 'df3.csv', sep = ',', na_values = '', encoding = 'latin-1')
# df4: contiene informazioni sulle politiche sulla privacy accettate da ciascun cliente
df4 = pd.read_csv(BASE_PATH + 'df4.csv', sep = ',', na_values = '', encoding = 'latin-1')

# df7: contiene le transazioni di acquisto e rimborso di ciascun cliente, ?? una delle parti pi?? cospicue di questa base di dati
# df7 = pd.read_csv(BASE_PATH + 'df7.csv', sep = ',', na_values = '', encoding = 'latin-1')

df7_churn_tot = pd.read_csv(BASE_PATH + 'df7_churn.csv', sep = ',', na_values = '', encoding = 'latin-1')
df7_churn = df7_churn_tot[['ID_CLI', 'CHURN']]

"""# Merge"""

df = pd.merge(left=df1, right=df2, how='inner', on='ID_CLI')
pd.merge(left=df, right=df3, how='inner', on='ID_ADDRESS')
pd.merge(left=df, right=df4, how='inner', on='ID_CLI')

df = pd.merge(left=df, right=df7_churn, how='inner', on='ID_CLI')

df.columns.to_series().groupby(df.dtypes).groups

df.isna().any()

#df.to_csv('df_tot.csv', index=False)

df.corr()

corr_df = df.corr(method='pearson')

plt.figure(figsize=(20, 14))
sn.heatmap(corr_df, annot=True)
plt.show()

df.drop(columns = ['ID_ADDRESS'], inplace = True)
df.reset_index(inplace = True, drop = True)

# df = df[:7000].drop('TYP_CLI_ACCOUNT', axis = 1).copy()
df = df.copy()

df

"""# Modello"""

df.info()

df["CHURN"].value_counts()

import matplotlib.ticker as mtick

churn_rate = df[["CHURN", "ID_CLI"]]
churn_rate["churn_label"] = pd.Series(np.where((churn_rate["CHURN"] == 0), "No", "Yes"))
sectors = churn_rate.groupby("churn_label")
churn_rate = pd.DataFrame(sectors["ID_CLI"].count())
churn_rate ["Churn Rate"] = (churn_rate ["ID_CLI"]/sum(churn_rate ["ID_CLI"]))*100

ax = churn_rate[["Churn Rate"]].plot.bar(title = 'Overall Churn Rate', legend = True, table = False, grid = False, subplots = False,
                                         figsize = (12, 7), color = '#ec838a', fontsize = 15, stacked = False, ylim = (0,100))

plt.ylabel('Proportion of Customers', horizontalalignment="center", fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.xlabel('Churn', horizontalalignment="center", fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.title('Overall Churn Rate \n', horizontalalignment="center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")

#plt.legend(loc ='top right', fontsize = "medium")
plt.xticks(rotation=0, horizontalalignment="center")
plt.yticks(rotation=0, horizontalalignment="right")

ax.yaxis.set_major_formatter(mtick.PercentFormatter())
x_labels = np.array(churn_rate[["ID_CLI"]])

def add_value_labels(ax, spacing=5):   
  for rect in ax.patches:
    y_value = rect.get_height()
    x_value = rect.get_x() + rect.get_width()/2
    space = spacing
    va = 'bottom'
    if y_value < 0:
      space *= -1
      va = 'top'
    label = "{:.1f}%".format(y_value)
  ax.annotate(label, (x_value, y_value), xytext=(0, space), textcoords="offset points", ha='center',va=va)

add_value_labels(ax)
ax.autoscale(enable=False, axis='both', tight=False)

import matplotlib.ticker as mtick
contract_churn = df.groupby(['LAST_COD_FID','CHURN']).size().unstack()
contract_churn.rename(columns={0:'No', 1:'Yes'}, inplace=True)
colors  = ['#ec838a','#9b9c9a']
ax = (contract_churn.T*100.0 / contract_churn.T.sum()).T.plot(kind='bar',width = 0.3,stacked = True,rot = 0,figsize = (12,7),color = colors)
plt.ylabel('Proportion of Customers\n', horizontalalignment="center",fontstyle = "normal", 
           fontsize = "large", fontfamily = "sans-serif")
plt.xlabel('Type Fidelity Program\n',horizontalalignment="center", fontstyle = "normal", fontsize = "large", 
           fontfamily = "sans-serif")
plt.title('Churn Rate by Contract type \n', horizontalalignment="center", fontstyle = "normal", 
          fontsize = "22", fontfamily = "sans-serif")
plt.legend(loc='top right', fontsize = "medium")
plt.xticks(rotation=0, horizontalalignment="center")
plt.yticks(rotation=0, horizontalalignment="right")
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
for p in ax.patches:
    width, height = p.get_width(), p.get_height()
    x, y = p.get_xy() 
    ax.text(x+width/2, y+height/2, '{:.1f}%'.format(height), horizontalalignment='center', verticalalignment='center')
ax.autoscale(enable=False, axis='both', tight=False)

"""Si nota che gli utenti con un programma di fedelt?? standard hanno pi?? probabilit?? di essere dei churn."""

df2 = df[[ 'LAST_TYP_CLI_FID', 'LAST_STATUS_FID', 'FIRST_ID_NEG', 'NUM_FIDs', 'W_PHONE', 'TYP_CLI_ACCOUNT' ]]
correlations = df2.corrwith(df.CHURN)
correlations = correlations[correlations!=1]
positive_correlations = correlations[correlations >0].sort_values(ascending = False)
negative_correlations = correlations[correlations<0].sort_values(ascending = False)
print('Most Positive Correlations: \n', positive_correlations)
print('\nMost Negative Correlations: \n', negative_correlations)

correlations = df2.corrwith(df.CHURN)
correlations = correlations[correlations!=1]
correlations.plot.bar(figsize = (18, 10), fontsize = 15, color = '#ec838a', rot = 45, grid = True)
plt.title('Correlation with Churn Rate \n', horizontalalignment = "center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")

"""La maggior correlazione positiva si ha con la variabile TYP_CLI_ACCOUNT ovvero che spiega che tipo di account ha l'utente, mentre la maggior correlazione negativa si ha con la variabile LAST_STATUS_FID che spiega se l'account ?? attivo oppure no."""

#Set and compute the Correlation Matrix:
sn.set(style="white")
corr = df2.corr()
#Generate a mask for the upper triangle:
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True
#Set up the matplotlib figure and a diverging colormap:
f, ax = plt.subplots(figsize=(18, 15))
cmap = sn.diverging_palette(220, 10, as_cmap=True)
#Draw the heatmap with the mask and correct aspect ratio:
sn.heatmap(corr, mask=mask, cmap=cmap, vmax=.3, center=0,
square=True, linewidths=.5, cbar_kws={"shrink": .5})

"""Si verifica della multicollinearit?? utilizzando VIF: proviamo a esaminare la multicollinearit?? utilizzando i fattori di inflazione variabili (VIF). A differenza della matrice di correlazione, VIF determina la forza della correlazione di una variabile con un gruppo di altre variabili indipendenti in un set di dati. VIF inizia di solito a 1 e ovunque superiore a 10 indica un'elevata multicollinearit?? tra le variabili indipendenti."""

def calc_vif(X):
  # Calculating VIF
  vif = pd.DataFrame()
  vif["variables"] = X.columns
  vif["VIF"] = [variance_inflation_factor(X.values, i)
  for i in range(X.shape[1])]
  return(vif)
df2 = df[[ 'LAST_TYP_CLI_FID', 'LAST_STATUS_FID', 'FIRST_ID_NEG', 'NUM_FIDs', 'W_PHONE', 'TYP_CLI_ACCOUNT' ]]
calc_vif(df2)

"""Si prova ad eliminare una delle caratteristiche correlate per vedere se aiuta a ridurre la multicollinearit?? tra le caratteristiche correlate:"""

df.drop(['LAST_STATUS_FID'], axis=1, inplace = True)
df.drop(['NUM_FIDs'], axis=1, inplace = True)
df.drop(['LAST_TYP_CLI_FID'], axis=1, inplace = True)
def calc_vif(X):
  # Calculating VIF
  vif = pd.DataFrame()
  vif["variables"] = X.columns
  vif["VIF"] = [variance_inflation_factor(X.values, i)
  for i in range(X.shape[1])]
  return(vif)
df2 = df[['FIRST_ID_NEG', 'W_PHONE', 'TYP_CLI_ACCOUNT' ]]
calc_vif(df2)

df.drop_duplicates('ID_CLI', inplace = True)
print(df.shape)

## Convert rest of categorical variable in dummy variable:
lcf = pd.get_dummies(df['LAST_COD_FID']).iloc[:,1:]
ldta = pd.get_dummies(df['LAST_DT_ACTIVE']).iloc[:,1:]
fdta = pd.get_dummies(df['FIRST_DT_ACTIVE']).iloc[:,1:]
ep = pd.get_dummies(df['EMAIL_PROVIDER']).iloc[:,1:]
tj = pd.get_dummies(df['TYP_JOB']).iloc[:,1:]

df.drop(['LAST_COD_FID', 'LAST_DT_ACTIVE', 'FIRST_DT_ACTIVE', 'EMAIL_PROVIDER', 'TYP_JOB'], axis=1, inplace = True)

df = pd.concat([df, lcf, ep, tj], axis=1)

"""Generazione di set di dati di addestramento e test: disaccoppiamo il set di dati master in set di addestramento e test con un rapporto dell'80%-20%."""

#Identify response variable:
    
response = df["CHURN"]
dataset = df.drop(columns="CHURN")

X_train, X_test, y_train, y_test = train_test_split(dataset, response, stratify=response, test_size = 0.9)
#to resolve any class imbalance - use stratify parameter.
print("Number transactions X_train dataset: ", X_train.shape)
print("Number transactions y_train dataset: ", y_train.shape)
print("Number transactions X_test dataset: ", X_test.shape)
print("Number transactions y_test dataset: ", y_test.shape)

"""Rimuovere gli identificatori: separare "ID_CLI" dai frame di dati di addestramento e test."""

train_identity = X_train['ID_CLI']
X_train = X_train.drop(columns = ['ID_CLI'])
test_identity = X_test['ID_CLI']
X_test = X_test.drop(columns = ['ID_CLI'])

"""**Ridimensionamento delle funzionalit??.**
?? importante normalizzare le variabili prima di eseguire qualsiasi algoritmo di apprendimento automatico (classificazione) in modo che tutte le variabili di addestramento e test vengano ridimensionate in un intervallo da 0 a 1.
"""

sc_X = StandardScaler()
X_train2 = pd.DataFrame(sc_X.fit_transform(X_train))
X_train2.columns = X_train.columns.values
X_train2.index = X_train.index.values
X_train = X_train2
X_test2 = pd.DataFrame(sc_X.transform(X_test))
X_test2.columns = X_test.columns.values
X_test2.index = X_test.index.values
X_test = X_test2

"""L'accuracy della classificazione ?? una delle metriche di valutazione della classificazione pi?? comuni per confrontare gli algoritmi di base in quanto rappresenta il numero di previsioni corrette effettuate come rapporto delle previsioni totali. Tuttavia, non ?? la metrica ideale quando vi sono problemi di sbilanciamento di classe. Quindi, si ordinano i risultati in base al valore **Mean AUC** che non ?? altro che la capacit?? del modello di discriminare tra classi positive e negative."""

models = []
models.append(('Logistic Regression', LogisticRegression(solver='liblinear', random_state = 0,
                                                         class_weight='balanced')))
models.append(('SVC', SVC(kernel = 'linear', random_state = 0)))
models.append(('Kernel SVM', SVC(kernel = 'rbf', random_state = 0)))
models.append(('KNN', KNeighborsClassifier(n_neighbors = 5, metric = 'minkowski', p = 2)))
models.append(('Gaussian NB', GaussianNB()))
models.append(('Decision Tree Classifier',
               DecisionTreeClassifier(criterion = 'entropy', random_state = 0)))
models.append(('Random Forest', RandomForestClassifier(
    n_estimators=100, criterion = 'entropy', random_state = 0)))
#Evaluating Model Results:
acc_results = []
auc_results = []
names = []
# set table to table to populate with performance results
col = ['Algorithm', 'ROC AUC Mean', 'ROC AUC STD', 
       'Accuracy Mean', 'Accuracy STD']
model_results = pd.DataFrame(columns=col)
i = 0
# Evaluate each model using k-fold cross-validation:
for name, model in models:
    kfold = model_selection.KFold(
        n_splits=10, random_state=None)
    start = datetime.now().timestamp()
    # accuracy scoring:
    cv_acc_results = model_selection.cross_val_score(  
    model, X_train, y_train, cv=kfold, scoring='accuracy')
    # roc_auc scoring:
    cv_auc_results = model_selection.cross_val_score(  
    model, X_train, y_train, cv=kfold, scoring='roc_auc')
    acc_results.append(cv_acc_results)
    auc_results.append(cv_auc_results)
    names.append(name)
    model_results.loc[i] = [name,
                        round(cv_auc_results.mean()*100, 2),
                        round(cv_auc_results.std()*100, 2),
                        round(cv_acc_results.mean()*100, 2),
                        round(cv_acc_results.std()*100, 2)
                        ]
    i += 1
    end = datetime.now().timestamp()
    print(i, name, (end-start))
        
model_results.sort_values(by=['ROC AUC Mean'], ascending=False)

#Visualizzare i confronti di precisione degli algoritmi di classificazione
fig = plt.figure(figsize=(15, 7)) 
ax = fig.add_subplot(111) 
plt.boxplot(acc_results) 
ax.set_xticklabels(names)
plt.ylabel('ROC AUC Score\n', horizontalalignment="center",fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.xlabel('\n Algoritmi di classificazione di base\n', horizontalalignment="center",fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.title('Accuracy Score Comparison \n', horizontalalignment="center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")
#plt.legend(loc='in alto a destra', fontsize = "medium") 
plt.xticks(rotation=0, horizontalalignment="center") 
plt.yticks(rotation=0, horizontalalignment="right")
plt.show()

"""Utilizzo dell'area sotto la curva ROC: dalla prima iterazione degli algoritmi di classificazione di base, possiamo vedere che la SVM hanno sovraperformato gli altri cinque modelli per il set di dati scelto con i punteggi AUC medi pi?? alti. Riconfermiamo i nostri risultati nella seconda iterazione come mostrato nei passaggi successivi."""

fig = plt.figure(figsize=(15, 7)) 
ax = fig.add_subplot(111) 
plt.boxplot(auc_results) 
ax.set_xticklabels(names)
plt.ylabel('ROC AUC Score\n', horizontalalignment="center",fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.xlabel('\n Algoritmi di classificazione di base\n', horizontalalignment="center",fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.title('ROC AUC Comparison \n',horizontalalignment="center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")
#plt.legend(loc='in alto a destra', fontsize = "medio") 
plt.xticks(rotation=0, horizontalalignment="center") 
plt.yticks(rotation=0, horizontalalignment="right")
plt.show()

"""Ottenere i parametri giusti per i modelli di base: prima di eseguire la seconda iterazione, si ottimizzano i parametri e si finalizzano le metriche di valutazione per la selezione del modello.

Identificare il numero ottimale di K vicini per il modello KNN: nella prima iterazione, abbiamo assunto che K = 3, ma in realt?? non sappiamo quale sia il valore K ottimale che fornisce la massima precisione per il set di dati di addestramento scelto. Pertanto, scriviamo un ciclo for che itera da 20 a 30 volte e dia l'accuratezza ad ogni iterazione in modo da calcolare il numero ottimale di K vicini per il modello KNN.
"""

score_array = []
for each in range(1,25):
    knn_loop = KNeighborsClassifier(n_neighbors = each) 
#set K neighbor as 3
    knn_loop.fit(X_train,y_train)
    score_array.append(knn_loop.score(X_test,y_test))
fig = plt.figure(figsize=(15, 7))
plt.plot(range(1,25),score_array, color = '#ec838a')
plt.ylabel('Range\n',horizontalalignment="center", fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.xlabel('Score\n',horizontalalignment="center", fontstyle = "normal", fontsize = "large", fontfamily = "sans-serif")
plt.title('Optimal Number of K Neighbors \n', horizontalalignment="center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")
#plt.legend(loc='top right', fontsize = "medium")
plt.xticks(rotation=0, horizontalalignment="center")
plt.yticks(rotation=0, horizontalalignment="right")
plt.show()

"""Come possiamo vedere dalle iterazioni precedenti, se utilizziamo K = 23, otterremo il punteggio massimo del 70%.

Identificare il numero ottimale di alberi per il modello Random Forest: abbastanza simile alle iterazioni nel modello KNN, qui stiamo cercando di trovare il numero ottimale di alberi decisionali per comporre la migliore foresta casuale.
"""

score_array = []
for each in range(1,100):
    rf_loop = RandomForestClassifier(
n_estimators = each, random_state = 1) 
    rf_loop.fit(X_train,y_train)
    score_array.append(rf_loop.score(X_test,y_test))
 
fig = plt.figure(figsize=(15, 7))
plt.plot(range(1,100),score_array, color = '#ec838a')
plt.ylabel('Range\n',horizontalalignment="center",
fontstyle = "normal", fontsize = "large", 
fontfamily = "sans-serif")
plt.xlabel('Score\n',horizontalalignment="center",
fontstyle = "normal", fontsize = "large", 
fontfamily = "sans-serif")
plt.title('Optimal Number of Trees for Random Forest Model \n',horizontalalignment="center", fontstyle = "normal", fontsize = "22", fontfamily = "sans-serif")
#plt.legend(loc='top right', fontsize = "medium")
plt.xticks(rotation=0, horizontalalignment="center")
plt.yticks(rotation=0, horizontalalignment="right")
plt.show()

"""Confronta algoritmi di classificazione di base (2a iterazione):

Nella seconda iterazione del confronto degli algoritmi di classificazione di base, utilizzeremo i parametri ottimizzati per i modelli KNN e Random Forest. Inoltre, sappiamo che i falsi negativi sono pi?? costosi dei falsi positivi in ??????una churn e quindi utilizziamo i punteggi di precisione, richiamo e F2 come metrica ideale per la selezione del modello.
"""

## Logistic Regression

# Fitting Logistic Regression to the Training set
classifier = LogisticRegression(random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results
y_pred = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
results = pd.DataFrame([['Logistic Regression', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## Support Vector Machine (linear classifier)

# Fitting SVM (SVC class) to the Training set
classifier = SVC(kernel = 'linear', random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results y_pred = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['SVM (Linear)', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## K-Nearest Neighbors

# Fitting KNN to the Training set:
classifier = KNeighborsClassifier(n_neighbors = 22, metric = 'minkowski', p = 2)
classifier.fit(X_train, y_train)
# Predicting the Test set results 
y_pred  = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['K-Nearest Neighbours', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## Kernel SVM

# Fitting Kernel SVM to the Training set:
classifier = SVC(kernel = 'rbf', random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results 
y_pred = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['Kernel SVM', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## Naive Byes

# Fitting Naive Byes to the Training set:
classifier = GaussianNB()
classifier.fit(X_train, y_train)
# Predicting the Test set results 
y_pred = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['Naive Byes', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## Decision Tree

# Fitting Decision Tree to the Training set:
classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results 
y_pred = classifier.predict(X_test)
#Evaluate results
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['Decision Tree', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

## Random Forest

# Fitting Random Forest to the Training set:
    
classifier = RandomForestClassifier(n_estimators = 72, 
criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)
# Predicting the Test set results 
y_pred = classifier.predict(X_test)
#Evaluate results
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
model_results = pd.DataFrame([['Random Forest', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
results = results.append(model_results, ignore_index = True)
results = results.sort_values(["Precision", "Recall", "F2 Score"], ascending = False)
print (results)

"""Dalla 2a iterazione, possiamo concludere definitivamente che la regressione logistica ?? un modello ottimale di scelta per il set di dati dato in quanto ha la combinazione relativamente pi?? alta di precision, recall e F1 score; fornendo il maggior numero di previsioni positive corrette riducendo al minimo i falsi negativi. Quindi, proviamo a utilizzare la regressione logistica e ne valutiamo le prestazioni nelle prossime sezioni.

## Valutazione del modello

Addestrare e valutare il modello scelto: adattiamo il modello selezionato (in questo caso la regressione logistica) al set di dati di addestramento e valutiamo i risultati.
"""

classifier = LogisticRegression(random_state = 0, penalty = 'l2')
classifier.fit(X_train, y_train)
# Predict the Test set results
y_pred = classifier.predict(X_test)
#Evaluate Model Results on Test Set:
acc = accuracy_score(y_test, y_pred )
prec = precision_score(y_test, y_pred )
rec = recall_score(y_test, y_pred )
f1 = f1_score(y_test, y_pred )
f2 = fbeta_score(y_test, y_pred, beta=2.0)
results = pd.DataFrame([['Logistic Regression', acc, prec, rec, f1, f2]], columns = ['Model', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'F2 Score'])
print(results)

"""K-Fold Cross-Validation: la valutazione del modello viene pi?? comunemente eseguita attraverso la tecnica "K-fold Cross-Convalidation" che aiuta principalmente a correggere la varianza. Il problema della varianza si verifica quando otteniamo una buona precisione durante l'esecuzione del modello su un set di addestramento e un set di test, ma l'accuratezza appare diversa quando il modello viene eseguito su un altro set di dati di test.

Quindi, per risolvere il problema della varianza, la convalida incrociata k-fold ha sostanzialmente diviso il set di addestramento in 10 "folds" e addestra il modello su 9 "folds" (9 sottoinsiemi del set di dati di addestramento) prima di testarlo nel ripiegamento di prova. Questo permette di dare la flessibilit?? di addestrare il nostro modello su tutte e dieci le combinazioni di 9 "folds", dando ampio spazio per finalizzare la varianza.
"""

accuracies = cross_val_score(estimator = classifier, X = X_train, y = y_train, cv = 10)
print("Logistic Regression Classifier Accuracy: %0.2f (+/- %0.2f)"  % (accuracies.mean(), accuracies.std() * 2))

"""Pertanto, i risultati di convalida incrociata k-fold ottenuti indicano che avremmo un'accuratezza compresa tra il 68% e l'72% durante l'esecuzione di questo modello su qualsiasi set di test.

Di seguito si visualizzano i risultati all'interno una matrice di confusione: tale matrice di confusione indica che abbiamo 98870 + 34037 previsioni corrette e 41175 + 16366 previsioni errate.

Tasso di precisione = numero di previsioni corrette/pronostici totali * 100 = 132907 / 190448 * 100 = 69,79%

Tasso di errore = numero di previsioni errate/pronostici totali * 100 = 57541 / 190448 * 100 = 30,21%

Pertanto si ha una precisione del quasi 70%.
"""

cm = confusion_matrix(y_test, y_pred) 
df_cm = pd.DataFrame(cm, index = (0, 1), columns = (0, 1))
plt.figure(figsize = (28,20))
fig, ax = plt.subplots()
sn.set(font_scale=1.4)
sn.heatmap(df_cm, annot=True, fmt='g')
class_names=[0,1]
tick_marks = np.arange(len(class_names))
plt.tight_layout()
plt.title('Confusion matrix\n', y=1.1)
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)
ax.xaxis.set_label_position("top")
plt.ylabel('Actual label\n')
plt.xlabel('Predicted label\n')

"""**Valutazione del modello usando il grafico ROC.**

Si rivaluta il modello usando il grafico ROC. Il grafico ROC mostra la capacit?? di un modello di distinguere tra le classi in base al punteggio medio AUC. 

La linea arancione rappresenta la curva ROC di un classificatore casuale mentre un buon classificatore cerca di rimanere il pi?? lontano possibile da quella linea. Come mostrato nel grafico seguente, il modello di regressione logistica perfezionato ha mostrato un punteggio AUC pi?? elevato.
"""

classifier.fit(X_train, y_train) 
probs = classifier.predict_proba(X_test) 
probs = probs[:, 1] 
classifier_roc_auc = accuracy_score(y_test, y_pred )
rf_fpr, rf_tpr, rf_thresholds = roc_curve(y_test, classifier.predict_proba(X_test)[:,1])
plt.figure(figsize=(14, 6))
# Plot Logistic Regression ROC
plt.plot(rf_fpr, rf_tpr, 
label='Logistic Regression (area = %0.2f)' % classifier_roc_auc)
# Plot Base Rate ROC
plt.plot([0,1], [0,1],label='Base Rate' 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.ylabel('True Positive Rate \n',horizontalalignment="center",
fontstyle = "normal", fontsize = "medium", 
fontfamily = "sans-serif")
plt.xlabel('\nFalse Positive Rate \n',horizontalalignment="center",
fontstyle = "normal", fontsize = "medium", 
fontfamily = "sans-serif")
plt.title('ROC Graph \n',horizontalalignment="center", 
fontstyle = "normal", fontsize = "22", 
fontfamily = "sans-serif")
plt.legend(loc="lower right", fontsize = "medium")
plt.xticks(rotation=0, horizontalalignment="center")
plt.yticks(rotation=0, horizontalalignment="right")
plt.show()

"""## Prevedere l'importanza delle caratteristiche
La regressione logistica ci consente di determinare le caratteristiche chiave che hanno significato nella previsione dell'attributo target ("Churn").

Il modello di regressione logistica prevede che il tasso di abbandono aumenterebbe positivamente con contratto standard, email account provider con gmail, libero, hotmail.

D'altra parte, il modello prevede una correlazione negativa con l'abbandono se un cliente ha un programma fedelt??, lo store in cui ha acquistato oppure se ?? disoccupato.
"""

# Analyzing Coefficients
feature_importances = pd.concat([pd.DataFrame(dataset.drop(columns = 'ID_CLI').columns, columns = ["features"]), 
                                 pd.DataFrame(np.transpose(classifier.coef_), columns = ["coef"])],axis = 1)
feature_importances.sort_values("coef", ascending = False)

"""## Miglioramento del modello
Il miglioramento del modello implica fondamentalmente la scelta dei migliori parametri per il modello di apprendimento automatico che abbiamo elaborato. Esistono due tipi di parametri in qualsiasi modello di apprendimento automatico: il primo tipo ?? il tipo di parametri che il modello apprende; i valori ottimali trovati automaticamente eseguendo il modello. Il secondo tipo di parametri sono quelli che l'utente pu?? scegliere durante l'esecuzione del modello. Tali parametri sono chiamati iperparametri; un insieme di valori configurabili esterni a un modello che non pu?? essere determinato dai dati e che stiamo cercando di ottimizzare attraverso tecniche di Parameter Tuning come Random Search o Grid Search.

L'ottimizzazione degli iperparametri potrebbe non migliorare il modello ogni volta. Ad esempio, cercando di ottimizzare ulteriormente il modello si ?? ottenuto un punteggio di precisione inferiore a quello predefinito. Tutto ci?? serve per dimostrare i passaggi coinvolti nell'ottimizzazione degli iperparametri.

Regolazione dei parametri ipertestuali tramite la Grid Search.
"""

# Round 2:
# Select Regularization Method
import time
penalty = ['l2']
# Create regularization hyperparameter space
C = [ 0.0001, 0.001, 0.01, 0.02, 0.05]
# Combine Parameters
parameters = dict(C=C, penalty=penalty)
lr_classifier = GridSearchCV(estimator = classifier,
                           param_grid = parameters,
                           scoring = "balanced_accuracy",
                           cv = 10,
                           n_jobs = -1)
t0 = time.time()
lr_classifier  = lr_classifier .fit(X_train, y_train)
t1 = time.time()
print("Took %0.2f seconds" % (t1 - t0))
lr_best_accuracy = lr_classifier.best_score_
lr_best_parameters = lr_classifier.best_params_
lr_best_accuracy, lr_best_parameters

lr_classifier = LogisticRegression(random_state = 0, penalty = 'l2')
lr_classifier.fit(X_train, y_train)
# Predict the Test set results
y_pred = lr_classifier.predict(X_test)
#probability score
y_pred_probs = lr_classifier.predict_proba(X_test)
y_pred_probs  = y_pred_probs [:, 1]

"""## Future Predictions
Comparazione delle predizioni con il test set a selezionato precedentemente.
"""

#Revalidate final results with Confusion Matrix:
cm = confusion_matrix(y_test, y_pred) 
print (cm)
#Confusion Matrix as a quick Crosstab:
    
pd.crosstab(y_test,pd.Series(y_pred),
rownames=['ACTUAL'],colnames=['PRED'])
#visualize Confusion Matrix:
cm = confusion_matrix(y_test, y_pred) 
df_cm = pd.DataFrame(cm, index = (0, 1), columns = (0, 1))
plt.figure(figsize = (28,20))
fig, ax = plt.subplots()
sn.set(font_scale=1.4)
sn.heatmap(df_cm, annot=True, fmt='g'#,cmap="YlGnBu" 
           )
class_names=[0,1]
tick_marks = np.arange(len(class_names))
plt.tight_layout()
plt.title('Confusion matrix\n', y=1.1)
plt.xticks(tick_marks, class_names)
plt.yticks(tick_marks, class_names)
ax.xaxis.set_label_position("top")
plt.ylabel('Actual label\n')
plt.xlabel('Predicted label\n')
print("Test Data Accuracy: %0.4f" % accuracy_score(y_test, y_pred))

"""**Formattazione dei risultati finali.**
?? sempre una buona pratica costruire un punteggio di propensione oltre a un risultato assoluto previsto. Invece di recuperare solo un risultato target stimato binario (0 o 1), ogni "ID cliente" potrebbe ottenere un punteggio di propensione che evidenzia la percentuale di probabilit?? di intraprendere l'azione target ("churn").
"""

final_results = pd.concat([test_identity, y_test], axis = 1).dropna()
final_results['predictions'] = y_pred
final_results["propensity_to_churn(%)"] = y_pred_probs
final_results["propensity_to_churn(%)"] = final_results["propensity_to_churn(%)"]*100
final_results["propensity_to_churn(%)"]=final_results["propensity_to_churn(%)"].round(2)
final_results = final_results[['ID_CLI', 'CHURN', 'predictions', 'propensity_to_churn(%)']]
final_results ['Ranking'] = pd.qcut(final_results['propensity_to_churn(%)'].rank(method = 'first'),10,labels=range(10,0,-1))
print (final_results)

"""## Conclusione

Pertanto in questo progetto abbiamo utilizzato il merge di 5 set di dati per raccogliere maggiori informazioni sui clienti al fine di creare un classificatore di apprendimento automatico che prevede la propensione di qualsiasi cliente ad abbandonare nei mesi a venire con un punteggio di accuratezza compreso tra il 68% e il 72%.
"""
