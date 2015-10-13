'''
Created on Oct 12, 2015

@author: phil
'''
import os
import spammodel
import spamclassifier
import click
import spam_config as config

@click.group()
def cli():
    """CLI for the Spam Filter"""
    pass

@cli.command()
@click.argument("folder")
@click.option("--type", help="The type of emails to train on. Values: 'ham' or 'spam'", type=click.Choice(['ham', 'spam']))
def train(folder, type):
    model = spammodel.SpamModel(config.db_path)
    classifier = spamclassifier.SpamClassifier(model)

    model.load_db()
    print("training...")

    for root, dirs, files in os.walk(folder):
        for email in files:
            classifier.learn(open(os.path.join(root, email), 'rb').read(), is_spam=True if type=='spam' else False)

    model.save_db()
    print("done!")

@cli.command()
@click.argument("email")
def classify(email):
    model = spammodel.SpamModel(config.db_path)
    classifier = spamclassifier.SpamClassifier(model)

    model.load_db()
    mail_bytes = open(email, 'rb').read()
    print(mail_bytes.decode())

    value = classifier.classify(mail_bytes)
    if value is None:
        #notclassified += 1
        print("could not classify email")
        print(mail_bytes.decode())
        is_spam = click.prompt('Is this E-Mail spam?', type=bool)
        if is_spam:
            classifier.learn(mail_bytes, is_spam=True)
        else:
            classifier.learn(mail_bytes, is_spam=False)
        return
    if config.threshold > value:
        print("spam")
        return
    else:
        print("ham")
        return



@cli.command()
@click.argument("threshold")
def auto_test(threshold):
    threshold = float(threshold)
    model = spammodel.SpamModel("testdb.json")
    classifier = spamclassifier.SpamClassifier(model)
    for root, dirs, files in os.walk('ham-anlern'):
        for email in files:
            classifier.learn(open(os.path.join(root, email), 'rb').read(), is_spam=False)
    for root, dirs, files in os.walk('spam-anlern'):
        for email in files:
            classifier.learn(open(os.path.join(root, email), 'rb').read(), is_spam=True)


    #threshold = 0.4

    print("threshold: {0:.2f}".format(threshold))
    print('-------------CLASSIFY HAM---------------')
    ham = 0
    total = 0
    notclassified = 0
    for root, dirs, files in os.walk('ham-test'):
        for email in files:
            total += 1
            value = classifier.classify(open(os.path.join(root, email), 'rb').read())
            #print(value)
            if value is None:
                notclassified += 1
                continue
            if threshold > value:
                ham += 1
    print("[correct: {0:.1f}, unclassified: {1}]".format(100*(ham/total), notclassified))
    spam = 0
    total = 0
    notclassified = 0

    print('-------------CLASSIFY SPAM---------------')
    for root, dirs, files in os.walk('spam-test'):
        for email in files:
            total += 1
            value = classifier.classify(open(os.path.join(root, email), 'rb').read())
            #print(value)

            if value is None:
                notclassified += 1
                continue
            if threshold <= value:
                spam += 1
            #print(classifier.classify(open(os.path.join(root, email), 'rb').read()))
    print("[correct: {0:.1f}, unclassified: {1}]".format(100*(spam/total), notclassified))


    model.save_db()

if __name__ == '__main__':
    cli()
