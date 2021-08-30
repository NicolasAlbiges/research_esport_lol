import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import RandomForestClassifier
from yellowbrick.classifier import ConfusionMatrix
from sklearn.metrics import classification_report
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
import numpy as np


class Ml:
	def __init__(self):
		self.dataset = pd.read_csv("dataset_v2.csv")
		self.dataset_in_game = pd.read_csv("dataset_in_game.csv")
		self.dataset_player_playstyle = pd.read_csv("dataset_player_playstyle_v2.csv")
		self.dataset_hybrid = pd.read_csv("dataset_hybrid_v2.csv")
		self.get_data(self.dataset_in_game)

	def get_data(self, dataset):
		for index in dataset:
			ct = 0
			for value in dataset[index]:
				if np.isnan(value) == True:
					dataset.loc[ct, index] = dataset[index].mean()
				ct = ct + 1
		y_all = dataset['win']
		x_all = dataset.drop(['win'], 1)
		self.xtrain, self.xtest, self.ytrain, self.ytest = train_test_split(x_all, y_all, test_size=0.3, random_state=912)

	def logistic_regression_cross_va(self, max_iter=100, class_weight="balanced", solver="liblinear"):
		lr = LogisticRegressionCV(cv=10, max_iter=max_iter, class_weight=class_weight, solver=solver, random_state=42)
		lr.fit(self.xtrain, self.ytrain)
		y_predicted = lr.predict(self.xtest)
		score = lr.score(self.xtest, self.ytest)
		print('Score is: {}'.format(score))
		y_true, y_pred = self.ytest, lr.predict(self.xtest)
		print(classification_report(y_true, y_pred), "\n")
		return lr

	def random_forest(self, n_estimators=100, class_weight="balanced", random_state=42):
		rf = RandomForestClassifier(n_estimators=n_estimators, class_weight=class_weight, random_state=random_state)
		rf.fit(self.xtrain, self.ytrain)
		score = rf.score(self.xtest, self.ytest)
		print('Score is: {}'.format(score))
		y_true, y_pred = self.ytest, rf.predict(self.xtest)
		print(classification_report(y_true, y_pred), "\n")
		return rf

	def Gaussian_Naive_Bayes(self):
		gnb = GaussianNB()
		gnb.fit(self.xtrain, self.ytrain)
		y_predicted = gnb.predict(self.xtest)
		score = gnb.score(self.xtest, self.ytest)
		print('Score is: {}'.format(score))
		y_true, y_pred = self.ytest, gnb.predict(self.xtest)
		print(classification_report(y_true, y_pred), "\n")
		return gnb

	def k_Nearest_Neighbors(self, n_neighbors=5, algorithm='ball_tree',  weights="uniform"):
		nbrs = KNeighborsClassifier(n_neighbors=n_neighbors, weights=weights, algorithm=algorithm)
		nbrs.fit(self.xtrain, self.ytrain)
		y_predicted = nbrs.predict(self.xtest)
		score = nbrs.score(self.xtest, self.ytest)
		print('Score is: {}'.format(score))
		y_true, y_pred = self.ytest, nbrs.predict(self.xtest)
		print(classification_report(y_true, y_pred), "\n")
		return nbrs

	def metrics(self, model):
		# Confusion Matrix à utiliser (ex : dans quels cas l'algo est fort ou faible)
		cm = ConfusionMatrix(model, classes=[1, 0])
		cm.score(self.xtest, self.ytest)
		cm.show()

	def run_all_ml(self):
		print("\nLogistic regression\n")

		self.logistic_regression_cross_va()
		self.logistic_regression_cross_va(max_iter=10000, class_weight="balanced", solver="liblinear")
		self.logistic_regression_cross_va(max_iter=10000, class_weight="balanced", solver="sag")

		print("\nRandom forest\n")

		self.random_forest()
		self.random_forest(n_estimators=10000, class_weight="balanced", random_state=42)

		print("\nKnearest Neighbors\n")
		self.k_Nearest_Neighbors()
		self.k_Nearest_Neighbors(n_neighbors=2, algorithm='kd_tree', weights="uniform")
		self.k_Nearest_Neighbors(n_neighbors=2, algorithm='brute', weights="uniform")

		print("\nNaive Bayes\n")
		self.Gaussian_Naive_Bayes()

if __name__ == "__main__":
	ml = Ml()
	#ml.get_data(ml.dataset_in_game)
	#ml.get_data(ml.dataset_player_playstyle)
	ml.get_data(ml.dataset_hybrid)

	#ml.run_all_ml()


	logistic_model = ml.logistic_regression_cross_va(max_iter=100, class_weight="balanced", solver="liblinear")
	ml.metrics(logistic_model)

	logistic_model = ml.logistic_regression_cross_va(max_iter=10000, class_weight="balanced", solver="liblinear")
	ml.metrics(logistic_model)


	'''

	Gaussian_Naive_Bayes_model = ml.Gaussian_Naive_Bayes()
	ml.metrics(Gaussian_Naive_Bayes_model)



	logistic_model = ml.logistic_regression_cross_va()
	ml.metrics(logistic_model)

	ml.get_data(ml.dataset_player_playstyle)
	logistic_model = ml.logistic_regression_cross_va()
	ml.metrics(logistic_model)

	ml.get_data(ml.dataset_hybrid)
	logistic_model = ml.logistic_regression_cross_va()
	ml.metrics(logistic_model)
	'''


	'''

	logistic_model = ml.logistic_regression_cross_va(max_iter=10000, class_weight="balanced", solver="sag")
	ml.metrics(logistic_model)
	'''

	'''

	logistic_model = ml.logistic_regression_cross_va(max_iter=10000, class_weight="balanced", solver="sag")
	ml.metrics(logistic_model)

	random_forest_model = ml.random_forest()
	ml.metrics(random_forest_model)

	random_forest_model = ml.random_forest(n_estimators=10000, class_weight="balanced", random_state=42)
	ml.metrics(random_forest_model)

		'''

	'''

	temp_k_Nearest_Neighbors = ml.k_Nearest_Neighbors()
	ml.metrics(temp_k_Nearest_Neighbors)


	temp_k_Nearest_Neighbors = ml.k_Nearest_Neighbors(n_neighbors=2, algorithm='kd_tree', weights="uniform")
	ml.metrics(temp_k_Nearest_Neighbors)

	temp_k_Nearest_Neighbors = ml.k_Nearest_Neighbors(n_neighbors=2, algorithm='brute', weights="uniform")
	ml.metrics(temp_k_Nearest_Neighbors)


	Gaussian_Naive_Bayes_model = ml.Gaussian_Naive_Bayes()
	ml.metrics(Gaussian_Naive_Bayes_model)

	#search_param(xtest, ytest)
	'''
