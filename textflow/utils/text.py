import re


class Tokenizer:
    @staticmethod
    def tokenize(text):
        return [(m.start(0), m.end(0), m.group()) for m in re.finditer(r'\w+|\$[\d\.]+|\S+', text)]
