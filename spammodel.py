'''
Created on Oct 12, 2015

@author: phil
'''
from collections import defaultdict
import json

class PathNotFoundException(BaseException):
    pass

class SpamModel(object):
    '''
    This stores the spam filter db.
    The default model here is a dictionary of words with
    each a dictionary containing the number of times the
    word has been counted in the HAM category and in the
    SPAM category.

    SPAM is in the True column and HAM is in the False column.
    '''

    def __init__(self, db_path=False):

        self.epsilon = 0.0001

        # make sure we can automatically use the dictionary without checking.
        self.model = {
            "total": {
                'spam': 0,
                'ham': 0
            },
            "stats": {
                'spam': defaultdict(int),
                'ham': defaultdict(int)
            }
        }
        self.db_path = db_path

    def is_word_in_db(self, word):
        return word in self.model['stats']['spam']

    def get_ham_probability(self, word):
        return float(self.model['stats']['ham'][word]) / int(self.model['total']['ham'])

    def get_spam_probability(self, word):
        return float(self.model['stats']['spam'][word]) / int(self.model['total']['spam'])

    def get_weight(self, word):
        p_spam = self.get_spam_probability(word)
        p_ham = self.get_ham_probability(word)

        if p_spam == 0 or p_ham == 0:
            return 0

        return abs(0.5 - p_spam/(p_spam+p_ham))

        #return abs(self.model['stats']['ham'][word] - self.model['stats']['spam'][word])


    def increase_email_count(self, is_spam):
        self.model['total']['spam' if is_spam else 'ham'] += 1

    def learn_word(self, word, is_spam):
        # is_spam must be a boolean, not just truthy/falsy
        is_spam = bool(is_spam)

        spam_or_ham = 'spam' if is_spam else 'ham'
        the_other = 'ham' if is_spam else 'spam'

        self.model['stats'][spam_or_ham][word] += 1
        if self.model['stats'][the_other][word] == 0:
            self.model['stats'][the_other][word] = self.epsilon

    def save_db(self, db_path=False):
        '''
        This method writes or overwrites existing DBs. It exports
        the data as a JSON object.
        '''
        self._sanitize_db()
        if not db_path and not self.db_path:
            raise PathNotFoundException()

        if not db_path:
            db_path = self.db_path

        json.dump(self.model, open(db_path, 'w'))

    def _sanitize_db(self):
        pass

    def load_db(self, db_path=False):
        if not db_path and not self.db_path:
            raise PathNotFoundException()

        if not db_path:
            db_path = self.db_path

        loaded_db = None
        try:

            self.model = {
            'total': {
                'spam': 0,
                'ham': 0
            },
            'stats': {
                'spam': defaultdict(int),
                'ham': defaultdict(int)
            }
        }
            loaded_db = json.load(open(db_path, 'r'))

            self.model['total']['spam'] = loaded_db['total']['spam']
            self.model['total']['ham'] = loaded_db['total']['ham']
            self.model['stats']['spam'].update(loaded_db['stats']['spam'])
            self.model['stats']['ham'].update(loaded_db['stats']['ham'])
        except:
            print("created new db!")
            self.save_db(db_path)
