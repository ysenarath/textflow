""" Base class and in-built dataset types. """
from types import SimpleNamespace

from textflow.utils import PluginManager
from textflow.utils.text import Tokenizer

__all__ = [
    'Dataset',
    'datasets',
    'MultiLabelDataset',
    'SequenceLabelingDataset',
]

datasets = PluginManager()

IB_TAGS = ['I', 'B']


class Dataset:
    def __init__(self, annotation_sets, tokenizer=None, validator='MAJORITY'):
        self.records = self.build_dataset(annotation_sets, tokenizer=tokenizer)
        self.validator = validator

    def build_dataset(self, annotation_sets, tokenizer):
        """Builds dataset from provided annotation sets

        :param annotation_sets: an iterable of annotation sets
        :param tokenizer: tokenizer function that returns (start, end, token string) of
        :return: records in dataset with labels by each annotator
        """
        raise NotImplementedError

    def build_item_tuples(self):
        """Make item tuples for annotation agreement

        :return: label item tuples
        """
        raise NotImplementedError

    @property
    def groups_(self):
        group_set = set()
        for d in self.records.values():
            for user, _ in d.labels.items():
                group_set.add(user)
        return group_set

    @property
    def classes_(self):
        """List all classes of dataset if defined else return None

        :return: list of unique classes
        """
        label_set = set()
        for d in self.records.values():
            for _, labels in d.labels.items():
                label_set.update(labels)
        return label_set

    @property
    def X(self):
        """Gets feature/independent variable of dataset

        :return: an iterable of feature/independent variable
        """
        raise NotImplementedError

    @property
    def y(self):
        """Gets target/dependent variable of dataset

        :return: an iterable of target/dependent variable
        """
        raise NotImplementedError


@datasets.register('sequence_labeling')
class SequenceLabelingDataset(Dataset):
    def build_dataset(self, annotation_sets, tokenizer=None):
        """Builds dataset from provided annotation sets

        :param annotation_sets: an iterable of annotation sets
        :param tokenizer: tokenizer function that returns (start, end, token string) of
        :return: records in dataset with labels by each annotator
        """
        if tokenizer is None:
            tokenizer = Tokenizer()
        records = dict()
        for annotation_set in annotation_sets:
            document = annotation_set.document
            if document.id in records:
                document = records[document.id]
            else:
                document = SimpleNamespace(
                    id=document.id,
                    id_str=document.id_str,
                    text=document.text,
                    tokens=tokenizer.tokenize(document.text),
                    labels=dict(),
                )
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            # set labels
            token_index = {}
            for tid, (s, e, _) in enumerate(document.tokens):
                for i in range(s, e):
                    token_index[i] = tid
            user = annotation_set.user
            if '__{}__'.format(user.username) in document.labels:
                labels = document.labels['__{}__'.format(user.username)]
            else:
                labels = [('O', None) for _ in document.tokens]
            for annotation in annotation_set.annotations:
                label_value = annotation.label.value
                annotation_span = annotation.span
                for aix in range(annotation_span.start, annotation_span.start + annotation_span.length):
                    bio_tag = IB_TAGS[aix == annotation_span.start]
                    # update only tags marked as other
                    if (aix in token_index) and (labels[token_index[aix]] == ('O', None)):
                        labels[token_index[aix]] = (bio_tag, label_value)
            document.labels['__{}__'.format(user.username)] = labels
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            records[document.id] = document
        for i in records:
            labels = records[i].labels.values()
            majority_vote = []
            prv_label = 'O'
            for ll in zip(*labels):
                # count lbl values
                lbl_counts, lbl_val = [], list(map(lambda x: x[1], ll))
                for lbl in set(lbl_val):
                    lbl_counts.append((lbl, lbl_val.count(lbl)))
                maj_lbl, maj_lbl_count = sorted(lbl_counts, key=lambda x: x[-1])[-1]
                # count BIO tags
                tag_counts, tag_val = [], list(map(lambda x: x[0], ll))
                for tag in set(tag_val):
                    tag_counts.append((tag, tag_val.count(tag)))
                maj_tag, _ = sorted(tag_counts, key=lambda x: x[-1])[-1]
                min_num = len(ll) // 2 + 1
                # Update word position tag (BIO)
                if maj_lbl_count >= min_num:
                    if maj_lbl is not None:
                        if prv_label[0] in ['O', '?']:
                            maj_tag = 'B'
                        else:
                            # keep the majority tag
                            pass
                    else:
                        maj_tag = 'O'
                else:
                    # disagreement
                    # -- unable to identify majority
                    maj_tag, maj_lbl = '?', None
                prv_label = (maj_tag, maj_lbl)
                majority_vote.append(prv_label)
            records[i].labels['MAJORITY'] = majority_vote
        return records

    def build_item_tuples(self):
        """Make item tuples for annotation agreement

        :return: label item tuples
        """
        result = []
        for d in self.records.values():
            for coder, labels in d.labels.items():
                for index, (label, (_, _, token)) in enumerate(zip(labels, d.tokens)):
                    result.append((coder, '{}_{}'.format(d.id, index), label[-1]))
        return result

    @property
    def classes_(self):
        """List all classes of dataset if defined else return None

        :return: list of unique classes
        """
        label_set = set()
        for d in self.records.values():
            for _, labels in d.labels.items():
                label_set.update([label[-1] for label in labels])
        return label_set

    @property
    def X(self):
        """Gets tokens for each sentence

        :return: list of tokens for each sentence
        """
        # select third position in tokens (i.e. index 2) to get string token
        # token tuple struct (start, end, token)
        X = [list(zip(*self.records[r].tokens))[2] for r in self.records]
        return X

    @staticmethod
    def _format_labels(tags):
        """Format labels by converting None to 'O'.

        :param tags: list of tags
        :return: formatted list of tags
        """
        return [t + ('' if l is None else '_{}'.format(l)) for t, l in tags]

    @property
    def y(self):
        """Gets (multi-class) labels for each token of each sentence

        :return: list of labels for each token of each sentence
        """
        # noinspection PyPep8Naming
        X = [self._format_labels(self.records[r].labels[self.validator]) for r in self.records if
             self.validator in self.records[r].labels]
        return X


@datasets.register('document_classification')
class MultiLabelDataset(Dataset):
    def build_dataset(self, annotation_sets, tokenizer=None):
        """Builds dataset from provided annotation sets

        :param annotation_sets: an iterable of annotation sets
        :param tokenizer: tokenizer function that returns (start, end, token string) of
        :return: records in dataset with labels by each annotator
        """
        if tokenizer is None:
            tokenizer = Tokenizer()
        records = dict()
        for annotation_set in annotation_sets:
            document = annotation_set.document
            if document.id in records:
                document = records[document.id]
            else:
                document = SimpleNamespace(
                    id=document.id,
                    id_str=document.id_str,
                    text=document.text,
                    tokens=tokenizer.tokenize(document.text),
                    labels=dict(),
                )
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            # set labels
            user = annotation_set.user
            if '__{}__'.format(user.username) in document.labels:
                labels = document.labels['__{}__'.format(user.username)]
            else:
                labels = []
            for annotation in annotation_set.annotations:
                label_value = annotation.label.value
                labels.append(label_value)
            document.labels['__{}__'.format(user.username)] = labels
            # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
            records[document.id] = document
        for i in records:
            # labels by different coders
            labels = records[i].labels.values()
            label_counts = {}
            for ls in labels:
                for ll in set(ls):
                    if ll not in label_counts:
                        label_counts[ll] = 0
                    label_counts[ll] += 1
            # minimum number of labels needed
            #   to consider for annotation (half of the number of available annotations)
            min_num = len(labels) // 2 + 1
            majority_vote = [k for k, v in label_counts.items() if v >= min_num]
            records[i].labels['MAJORITY'] = majority_vote
        return records

    def build_item_tuples(self):
        """Make item tuples for annotation agreement

        :return: label item tuples
        """
        result = []
        label_set = self.classes_
        for d in self.records.values():
            for coder, labels in d.labels.items():
                for label in label_set:
                    result.append((coder, '{}_{}'.format(d.id, label), str(label in labels)))
        return result

    @property
    def X(self):
        """Gets tokens for each sentence

        :return: list of tokens for each sentence
        """
        X = [self.records[r].text for r in self.records]
        return X

    @property
    def y(self):
        """Gets (multi-) label each sentence

        :return: list of labels of each document
        """
        y = [self.records[r].labels[self.validator] for r in self.records]
        return y
