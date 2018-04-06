import unicodedata

class Preprocess:
    def __init__(self):
        pass

    @staticmethod
    def preprocess(str):
        try:
            return unicodedata \
                .normalize('NFKD', str) \
                .encode('ascii', 'ignore') \
                .replace('\t', '').replace('\n', '')
        except TypeError:
            return str.replace('\t', '').replace('\n', '')