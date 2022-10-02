"""Implements a common interface for agreement metrics: AgreementScore

This module implements one class :class:`AgreementScore`
"""
from functools import reduce
from itertools import combinations

import numpy as np
from sklearn import metrics as skm

import pandas as pd

__all__ = [
    'AgreementScore'
]


def _get_unique(x):
    return np.unique(x).tolist()


def _get_unique_intersect(x, y) -> np.ndarray:
    return np.intersect1d(x, y, return_indices=False)


class AgreementScore:
    def __init__(self, dataset, blacklist=None):
        if blacklist is None:
            blacklist = []
        if hasattr(dataset, 'build_item_tuples'):
            dataset = dataset.build_item_tuples()
        if not isinstance(dataset, pd.DataFrame):
            dataset = pd.DataFrame(dataset, columns=['coder', 'item', 'label'])
        dataset['label'].fillna('OTHER', inplace=True)
        self._dataset = dataset
        self._blacklist = blacklist
        self._support = self._dataset \
            .groupby('coder') \
            .agg({'item': _get_unique}) \
            .to_dict()['item']
        self._labels = _get_unique(self._dataset['label'])
        self._coder_pairs = self._get_coder_pairs()

    def _get_coder_pairs(self):
        """Gets coder pairs in dataset

        :return: all coder pairs
        """
        results = [c for c in self._dataset['coder'].unique() if c not in self._blacklist]
        return list(combinations(results, 2))

    def _pivot_table(self, coders):
        """Filter and return only data for coders provided.

        :param coders: list of names of coders
        :return: data from only provided coders and support (optional) or None
        """
        # get common support item set
        common_items = reduce(_get_unique_intersect, [self._support[c] for c in coders])
        if len(common_items) == 0:
            return None
        df = self._dataset[self._dataset['item'].isin(common_items) & self._dataset['coder'].isin(coders)]
        label_counts = pd.pivot_table(df, values='label', index=['item', 'coder'], aggfunc=_get_unique)
        if label_counts['label'].apply(len).max() > 1:  # multilabel
            _pivot_table = pd.pivot_table(df, index=['item'], columns=['coder'], values='label', aggfunc=list)
            pivot_table = {label: _pivot_table.applymap(lambda x: label in x) for label in self._labels}
        else:  # multi class / binary
            pivot_table = pd.pivot_table(df, index=['item'], columns=['coder'], values='label', aggfunc='first')
        pivot_table = pivot_table.fillna('OTHER')
        return pivot_table

    def _pairwise_average(self, func, multilabel=False, drop_unannotated_tokens=True):
        """Run provided function for every pair of annotators

        :param func: input function
        :param multilabel: whether func supports multilabel
        :return: average score and table of scores
        """
        scores, weights = [], []
        for ix, pair in enumerate(self._coder_pairs):
            pivot_table = self._pivot_table(pair)
            if pivot_table is None:
                _support, _agreement = 0, 0
            elif isinstance(pivot_table, dict):
                _support, _agreement = 0, 0
                for label in self._labels:
                    pivot_table_label = pivot_table[label]
                    if drop_unannotated_tokens:
                        pivot_table_label = pivot_table_label[(pivot_table_label != 'OTHER').any(axis=1)]
                    _agreement += func(pivot_table_label)
                    _support += pivot_table[label].shape[0]
                _agreement = _agreement / len(self._labels)
                _support = _support / len(self._labels)
            else:
                if drop_unannotated_tokens:
                    pivot_table = pivot_table[(pivot_table != 'OTHER').any(axis=1)]
                _agreement = func(pivot_table)
                _support = pivot_table.shape[0]
            scores.append(_agreement)
            weights.append(_support)
        columns = ('Annotators', 'Agreement', 'Support')
        if len(scores) == 0:
            return pd.DataFrame([], columns=columns)
        avg_weights = np.mean(weights)
        avg_score = np.mean(scores)
        weighted_avg_score = np.average(scores, weights=weights)
        coder_pairs_str = [', '.join(p) for p in self._coder_pairs]
        rows = list(zip(coder_pairs_str, scores, weights))
        rows.append(('Average', avg_score, avg_weights))
        rows.append(('Average (weighted)', weighted_avg_score, avg_weights))
        len_items = self._dataset[['coder', 'item']].drop_duplicates().groupby('item').count().value_counts()
        rows.append(('Dataset Size', len_items, len_items))
        return pd.DataFrame(rows, columns=columns)

    @staticmethod
    def kappa_pairwise(table):
        """Gets kappa score for provided pair of coders.

        :return: kappa score and support (optional)
        """
        col_1, col_2 = table.columns
        result = skm.cohen_kappa_score(table[col_1], table[col_2])
        return 0 if np.isnan(result) else result

    def kappa(self):
        """Cohen 1960 - Averages naively over kappas for each coder pair.

        :return: average kappa score and table of pairwise kappa scores (optional)
        """
        return self._pairwise_average(self.kappa_pairwise)

    @staticmethod
    def percentage_pairwise(table):
        col_1, col_2 = table.columns
        # calculate per task (/instance) agreement
        class_percent_agr = table[col_1].eq(table[col_2], fill_value=0)
        # calculate average agreement
        return class_percent_agr.sum() / len(class_percent_agr)

    def percentage(self):
        return self._pairwise_average(self.percentage_pairwise)

    @staticmethod
    def f1_pairwise(table):
        col_1, col_2 = table.columns
        # calculate average agreement
        result = skm.f1_score(table[col_1], table[col_2], average='micro')
        return 0 if np.isnan(result) else result

    def f1_score(self):
        return self._pairwise_average(self.f1_pairwise)
