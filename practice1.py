import matplotlib as mpl

mpl.use('TkAgg')  # change the image rendering backend
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn import svm

digits = datasets.load_digits()
print('digits.data ', digits.data)
print('digits.target ', digits.target)
# apparently setting gamma and data values yield, better results than being left blank
clf = svm.SVC(gamma=0.001, C=100)
X, y = digits.data[:-10], digits.target[:-10]
clf.fit(X,y)
print('clf.predict(digits.data[-5]): ', clf.predict(digits.data[-5]))

plt.imshow(digits.images[-5], cmap=plt.cm.gray_r, interpolation='nearest')
plt.show()
