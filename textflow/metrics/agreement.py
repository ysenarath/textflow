"""Implements a common interface for agreement metrics: AgreementScore

This module implements one class :class:`AgreementScore`
"""
from functools import reduce

import numpy as np
from sklearn import metrics as skm

import pandas as pd

__all__ = [
    'AgreementScore'
]


def _get_unique_intersect(x, y) -> np.ndarray:
    return np.intersect1d(x, y, assume_unique=True, return_indices=False)


class AgreementScore:
    def __init__(self, dataset, blacklist=None):
        if blacklist is None:
            blacklist = []
        if hasattr(dataset, 'build_item_tuples'):
            dataset = dataset.build_item_tuples()
        if not isinstance(dataset, pd.DataFrame):
            dataset = pd.DataFrame(dataset, columns=['coder', 'item', 'label'])
        self._dataset = dataset
        self._blacklist = blacklist
        self._support = self._dataset \
            .groupby('coder') \
            .agg({'item': lambda x: np.unique(x).tolist()}) \
            .to_dict()['item']
        self._coder_pairs = self._get_pairs()

    def _get_pairs(self):
        """Gets coder pairs in dataset

        :return: all coder pairs
        """
        cs = self._dataset['coder'].unique().tolist()
        results = []
        for cs_a in cs:
            cs.remove(cs_a)
            for cs_b in cs:
                results.append((cs_a, cs_b))
        return results

    def _filter_data(self, coders):
        """Filter and return only data for coders provided.

        :param coders: list of names of coders
        :return: data from only provided coders and support (optional) or None
        """
        # get common support item set
        common_items = reduce(_get_unique_intersect, [self._support[c] for c in coders if c in coders])
        if common_items.shape[0] == 0:
            return None
        df = self._dataset[self._dataset['item'].isin(common_items) & self._dataset['coder'].isin(coders)]
        label_counts = pd.pivot_table(df, values='label', index=['item', 'coder'], aggfunc=set)['label'].apply(len)
        if label_counts.max() > 1:  # multilabel
            pivot_table = pd.pivot_table(df, index=['item'], columns=['label', 'coder'], aggfunc=len) \
                .fillna(0)
        else:  # multi class / binary
            pivot_table = pd.pivot_table(df, index=['item'], columns=['coder'], values='label', aggfunc='first')
        return pivot_table

    def _pairwise_average(self, func):
        """Run provided function for every pair of annotators

        :param func: input function
        :return: average score and table of scores
        """
        scores, weights = [], []
        for ix, pair in enumerate(self._coder_pairs):
            pivot_table = self._filter_data(pair)
            if pivot_table is None:
                continue
            if hasattr(pivot_table.columns, 'levels'):
                if len(pivot_table.columns.levels) == 2:
                    _support, _agreement = 0, 0
                    labels = pivot_table.columns.levels[0]
                    for label in labels:
                        label_agreement = func(pivot_table[label])
                        _agreement += label_agreement
                        _support += pivot_table[label].shape[0]
                    _agreement = _agreement / len(labels)
                    _support = _support / len(labels)
                else:
                    continue
            else:
                _agreement = func(pivot_table)
                _support = pivot_table.shape[0]
            scores.append(_agreement)
            weights.append(_support)
        columns = ('Annotators', 'Agreement', 'Support')
        if len(scores) == 0:
            return pd.DataFrame([], columns=columns)
        avg_score = np.mean(scores)
        weighted_avg_score = np.average(scores, weights=weights)
        rows = list(zip(self._coder_pairs, scores, weights))
        rows.append(('Average', avg_score, sum(weights)))
        rows.append(('Average (weighted)', weighted_avg_score, sum(weights)))
        return pd.DataFrame(rows, columns=columns)

    @staticmethod
    def kappa_pairwise(table):
        """Gets kappa score for provided pair of coders.

        :return: kappa score and support (optional)
        """
        col_1, col_2 = table.columns
        return skm.cohen_kappa_score(table[col_1], table[col_2])

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
