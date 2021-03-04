""" Implements model types: `classifiers` and `sequence classifier` """

import sklearn_crfsuite
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from textflow.utils import PluginManager

__all__ = [
    'SequenceClassifier',
    'models',
]

models = PluginManager()


class SequenceClassifierMixin:
    """Mixin class for all sequence classifiers (for text) in scikit-learn."""

    _estimator_type = "sequence_classifier"

    def score(self, X, y, sample_weight=None):
        """Return the flat f1 score on the given test data and labels.

        :param X: features
        :param y: target
        :param sample_weight: ignored
        :return:
        """
        from sklearn_crfsuite.metrics import flat_f1_score
        labels = list(self.classes_).copy()
        labels.remove('O')
        return flat_f1_score(y, self.predict(X), average='weighted', labels=labels)


@models.register('sequence_labeling')
class SequenceClassifier(BaseEstimator, SequenceClassifierMixin):
    """ A CRF model with basic features for sequence classification in NLP.
    This is a wrapper around the python-crfsuite wrapper with interface similar to scikit-learn.

    reference: https://sklearn-crfsuite.readthedocs.io/en/latest/tutorial.html
    """

    def __init__(self, algorithm='lbfgs', c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True):
        """Initialize parameters for model building.

        To see all possible CRF parameters check its docstring.
        Here we are useing L-BFGS training algorithm (it is default) with Elastic Net (L1 + L2) regularization.
        :param algorithm: algorithm (str, optional (default='lbfgs'))
        :param c1: c1 (float, optional (default=0.1))
        :param c2: c2 (float, optional (default=0.1))
        :param max_iterations: max_iterations (int, optional (default=100))
        :param all_possible_transitions: all_possible_transitions (bool, optional (default=True))
        """
        self.algorithm = algorithm
        self.c1 = c1
        self.c2 = c2
        self.max_iterations = max_iterations
        self.all_possible_transitions = all_possible_transitions

    # noinspection PyAttributeOutsideInit
    def fit(self, X, y, **kwargs):
        """Trains the model and returns trained model.

        :param X: iterable of tokenized text documents. shape: (n_samples, ?:len(sent))
        :param y: iterable of labels for each token of document. shape: (n_samples, ?:len(sent))
        :param kwargs: optional data-dependent parameters
        :return:
        """
        X_train = [self._sent2features(sent) for sent in X]
        y_train = y
        self.model_ = sklearn_crfsuite.CRF(
            algorithm=self.algorithm,
            c1=self.c1,
            c2=self.c2,
            max_iterations=self.max_iterations,
            all_possible_transitions=self.all_possible_transitions,
        )
        self.model_.fit(X_train, y_train)
        self.classes_ = list(self.model_.classes_)
        return self

    def predict(self, X):
        """

        :param X: iterable of tokenized text documents. shape: (n_samples, ?:len(sent))
        :return: predictions of shape (n_samples, ?:len(sent))
        """
        X_test = [self._sent2features(sent) for sent in X]
        y_pred = self.model_.predict(X_test)
        return y_pred

    def _sent2features(self, sent):
        return [self._word2features(sent, i) for i in range(len(sent))]

    @staticmethod
    def _word2features(sent, i):
        word = sent[i]
        features = {
            'bias': 1.0,
            'word.lower()': word.lower(),
            'word[-3:]': word[-3:],
            'word[-2:]': word[-2:],
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
        }
        if i > 0:
            word1 = sent[i - 1]
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
                '-1:word.isupper()': word1.isupper(),
            })
        else:
            features['BOS'] = True
        if i < len(sent) - 1:
            word1 = sent[i + 1]
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
                '+1:word.isupper()': word1.isupper(),
            })
        else:
            features['EOS'] = True
        return features


@models.register('classification')
class MultiLabelClassifier(BaseEstimator, ClassifierMixin):
    def __init__(self):
        pass

    # noinspection PyAttributeOutsideInit
    def fit(self, X, y, **kwargs):
        """

        :param X: iterable of documents
        :param y: labels
        :param kwargs:
        :return:
        """
        clf = LogisticRegression()
        self.model_ = MultiOutputClassifier(clf)
        self.mlb_ = MultiLabelBinarizer()
        self.ext_ = TfidfVectorizer()
        X = self.ext_.fit_transform(X)
        y = self.mlb_.fit_transform(y)
        self.model_.fit(X, y)

    def predict(self, X):
        """Predict labels for provided iterable of documents

        :param X: iterable of documents
        :return: labels
        """
        X = self.ext_.transform(X)
        yt = self.model_.predict(X)
        return self.mlb_.inverse_transform(yt)
