import numpy as np
from sklearn import preprocessing, cross_validation, neighbors
import pandas as pd

df = pd.read_csv('breast-cancer-wisconsin.data.txt')
df.replace('?',-99999, inplace=True)
df.drop(['id'], 1, inplace=True)

X = np.array(df.drop(['class'], 1))
y = np.array(df['class'])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

clf = neighbors.KNeighborsClassifier()
clf.fit(X_train, y_train)

# with open('classifier.pickle','wb') as f:
#     pickle.dump(clf, f)

# pickle_in = open('linearregression.pickle','rb')
# clf = pickle.load(pickle_in)

accuracy = clf.score(X_test, y_test)
print(accuracy)

example_measures = np.array([10,10,10,8,6,1,8,9,1,]) # line 38
example_measures = example_measures.reshape(1, -1)
prediction = clf.predict(example_measures)
print(prediction)
