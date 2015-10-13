'''
Created on Oct 12, 2015

@author: phil
'''
import email
from functools import reduce


class NotClassifiableException(BaseException):
    pass


class SpamClassifier(object):
    '''
    Business logic of the spam filter.
    '''
    def __init__(self, model):
        '''
        Constructor for the SpamModel
        '''
        self.model = model

        #We're only interested in natural language
        self.nixed_characters = ".,*/><\\!@#$%^&*()=-_+][}{|`~\"'?:;"

        #part of the nixed_words come from everyday language and part from html emails.
        self.nixed_words = [ 'a', 'all', 'an',
                            'and', 'any', 'are', 'as', 'at', 'be', 'br', 'but', 'by', 'can', 'do',
                            'face', 'font', 'for', 'found', 'free', 'from', 'get', 'give', 'h', 'has', 'have', 'he',
                            'here', 'href', 'html', 'http', 'i', 'if', 'in', 'into', 'is', 'it', 'like',
                            'lists', 'm', 'made', 'mail', 'me', 'more', 'much', 'my', 'net', 'new', 'no', 'not', 'now',
                            'of', 'ok', 'on', 'or', 'org', 'our', 'out', 'p', 's', 'so',
                            'src', 't', 'table', 'td', 'that', 'the', 'their', 'there', 'they', 'this', 'to', 'tr', 'up',
                            'url', 'us', 'w', 'was', 'we', 'west', 'what', 'when', 'who', 'will', 'with',
                            'work', 'www', 'you', 'your']

    @staticmethod
    def product(numbers):
        '''helper function for calculating the product of a list of numbers'''
        return reduce(lambda l, x: l*x, numbers)

    def classify(self, raw_mail_bytes):
        '''Classify the given email according to the database.'''
        words = self._get_words_from_email(raw_mail_bytes)
        stats = {}
        for word in words:
            stats[word] = self.model.get_weight(word)

        stats = sorted(stats.items(), key=lambda x: x[1])
        #print(stats[-20:])
        # get the most significant words.
        stats = [x[0] for x in stats[-5:] if x[1] != 0]
        if not stats:
            return None
            #raise NotClassifiableException()
        #print(stats)
        product_ham = self.product([self.model.get_ham_probability(x) for x in stats])
        product_spam = self.product([self.model.get_spam_probability(x) for x in stats])

        p_spam = product_spam / (product_spam + product_ham)

        return p_spam

    def _get_words_from_email(self, raw_mail_bytes):
        message = email.message_from_bytes(raw_mail_bytes)
        to_be_parsed = [message]
        complete_text = ""

        while to_be_parsed:
            current_message = to_be_parsed.pop()
            if not current_message.is_multipart():
                # message only has one payload
                complete_text += (current_message.get_payload())
            else:
                # payload contains further emails which can contain
                # further multipart messages
                to_be_parsed.extend(current_message.get_payload())
        for character in self.nixed_characters:
            complete_text = complete_text.replace(character, ' ').lower()
        list_of_words = [x for x in complete_text.split() if x not in self.nixed_words]
        return set(list_of_words)

    def learn(self, raw_mail_bytes, is_spam):
        list_of_words = self._get_words_from_email(raw_mail_bytes)
        for word in list_of_words:
            self.model.learn_word(word, is_spam)
        self.model.increase_email_count(is_spam)
