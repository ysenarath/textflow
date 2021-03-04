"""Implements a common interface for agreement metrics: AgreementScore

This module implements one class :class:`AgreementScore`
"""

import statistics

from nltk import AnnotationTask

__all__ = [
    'AgreementScore'
]

from textflow.utils.types import Table


class AgreementScore:
    def __init__(self, dataset):
        self.data = dataset.build_item_tuples()

    def _get_coders(self):
        """Gets coders in dataset

        :return: all coders
        """
        result = set()
        for (c, _, _) in self.data:
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

    def _filter_data(self, coders, return_support=False):
        """Filter and return only data for coders provided.

        :param coders: list of names of coders
        :param return_support: whether to return support with selected data
        :return: data from only provided coders and support (optional) or None
        """
        result, support = [], {c: set() for c in coders}
        # add items coded by each coder to support
        for coder, item, _ in self.data:
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
        for coder, item, label in self.data:
            if (coder in support) and (item in common_items):
                result += [(coder, item, label)]
        # check if result is non empty
        if len(result) == 0:
            return None
        return (result, len(common_items)) if return_support else result

    def _pairwise_average(self, func):
        """Run provided function for every pair of annotators

        :param func: input function
        :return: average score and table of scores
        """
        pairs = self._get_pairs()
        scores = [0 for _ in range(len(pairs))]
        if len(scores) == 0:
            header = ('pair', 'score', 'support')
            rows = [('avg_score', 0.0, 0), ('weighted_avg_score', 0.0, 0), ]
            score_table = Table(header, rows)
            return score_table
        for ix, pair in enumerate(pairs):
            scores[ix] = func(*pair, return_support=True)
        sum_of_weights = sum([w for _, w in scores])
        if sum_of_weights == 0:
            weighted_avg_score = 0
        else:
            weighted_sum = sum([score * w for score, w in scores])
            weighted_avg_score = weighted_sum / sum_of_weights
        avg_score = statistics.mean([score for score, _ in scores])
        scores, support = list(zip(*scores))
        header = ('Pair', 'Score', 'Support')
        rows = list(zip(pairs, scores, support))
        rows.append(('Average Score', avg_score, sum(support)))
        rows.append(('Weighted Average Score', weighted_avg_score, sum(support)))
        score_table = Table(header, rows)
        return score_table

    def kappa_pairwise(self, c_a, c_b, return_support=True):
        """Gets kappa score for provided pair of coders.

        :param c_a: name of annotator 1
        :param c_b: name of annotator 2
        :param return_support: whether to return support with score
        :return: kappa score and support (optional)
        """
        data = self._filter_data((c_a, c_b), return_support=True)
        if data is None:
            score, sup = 0, 0
        else:
            t = AnnotationTask(data[0])
            sup = data[1]
            try:
                score = t.kappa()
            except ZeroDivisionError:
                score = 0
        return (score, sup) if return_support else score

    def kappa(self):
        """Cohen 1960 - Averages naively over kappas for each coder pair.

        :return: average kappa score and table of pairwise kappa scores (optional)
        """
        return self._pairwise_average(self.kappa_pairwise)
