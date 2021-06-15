"""Implements a common interface for agreement metrics: AgreementScore

This module implements one class :class:`AgreementScore`
"""

import statistics

from sklearn import metrics as skm

import pandas as pd

__all__ = [
    'AgreementScore'
]


class AgreementScore:
    def __init__(self, dataset, blacklist=None):
        if blacklist is None:
            blacklist = []
        self._blacklist = blacklist
        if hasattr(dataset, 'build_item_tuples'):
            self._dataset = dataset.build_item_tuples()
        else:
            self._dataset = dataset
        self.coder_pairs = self._get_pairs()

    def _get_coders(self):
        """Gets coders in dataset

        :return: all coders
        """
        result = set()
        for (c, _, _) in self._dataset:
            if c not in self._blacklist:
                result.add(c)
        return list(result)

    def _get_pairs(self):
        """Gets coder pairs in dataset

        :return: all coder pairs
        """
        cs = self._get_coders()
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
        result, support = [], {c: set() for c in coders}
        # add items coded by each coder to support
        for coder, item, _ in self._dataset:
            if coder in support:
                support[coder].add(item)
        # get common support item set
        common_items = None
        for coder, items in support.items():
            if common_items is None:
                common_items = set(items)
            else:
                common_items = common_items.intersection(items)
        # check if there is common item set between coders
        #   if not there is none
        if common_items is None:
            return None
        # get all annotations from coders with common items
        for coder, item, label in self._dataset:
            if (coder in support) and (item in common_items):
                result += [(coder, item, label)]
        # check if result is non empty
        if len(result) == 0:
            return None
        df = pd.DataFrame(result, columns=['coder', 'item', 'label'])
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
        scores = [0 for _ in range(len(self.coder_pairs))]
        if len(scores) == 0:
            columns = ('pair', 'score', 'support')
            rows = [('avg_score', 0.0, 0), ('weighted_avg_score', 0.0, 0), ]
            score_table = pd.DataFrame(rows, columns=columns)
            return score_table
        for ix, pair in enumerate(self.coder_pairs):
            pivot_table = self._filter_data(pair)
            if hasattr(pivot_table.columns, 'levels'):
                _support, _agreement = 0, 0
                if len(pivot_table.columns.levels) == 2:
                    labels = pivot_table.columns.levels[0]
                    for label in labels:
                        label_agreement = func(pivot_table[label])
                        _agreement += label_agreement
                        _support += pivot_table[label].shape[0]
                    _agreement = _agreement / len(labels)
                    _support = _support / len(labels)
            else:
                _agreement = func(pivot_table)
                _support = pivot_table.shape[0]
            scores[ix] = _agreement, _support
        sum_of_weights = sum([w for _, w in scores])
        if sum_of_weights == 0:
            weighted_avg_score = 0
        else:
            weighted_sum = sum([score * w for score, w in scores])
            weighted_avg_score = weighted_sum / sum_of_weights
        avg_score = statistics.mean([score for score, _ in scores])
        scores, support = list(zip(*scores))
        columns = ('Pair', 'Score', 'Support')
        rows = list(zip(self.coder_pairs, scores, support))
        rows.append(('Average Score', avg_score, sum(support)))
        rows.append(('Weighted Average Score', weighted_avg_score, sum(support)))
        score_table = pd.DataFrame(rows, columns=columns)
        return score_table

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
