"""
Evaluates a pre-trained multi-class model.

Usage: evaluate.py [--config=CONFIG-MODULE-PATH] (--dev | --test | --file)

Options:
  --config=CONFIG-MODULE-PATH    configuration module
  --dev                          evaluate on development set
  --test                         evaluate on test set
  --file                         evaluate on a custom file (in tta format)

"""
from collections import OrderedDict

from docopt import docopt
import pandas as pd
from sklearn.metrics import accuracy_score

from estnltk.neural_morph.general_utils import load_config_from_file
from estnltk.neural_morph.data_utils import ConfigHolder
from estnltk.neural_morph.model import Model


def get_uniq_words(train_file, test_file):
    get_words = lambda _file: set([ln.split('\t')[0] for ln in open(_file, encoding='utf-8') if len(ln.rstrip()) > 0])
    train_words = get_words(train_file)
    test_words = get_words(test_file)
    unseen_words = test_words - train_words
    return unseen_words


def is_equal(tag1, tag2):
    return set(tag1.split("|")) == set(tag2.split("|"))


def iter_sentences(tta_file):
    words, tags, analyses = [], [], []
    for line in open(tta_file, encoding="utf-8"):
        line = line.rstrip()
        if line == "":
            if len(words) > 0:
                yield words, tags, analyses
            words, tags, analyses = [], [], []
        else:
            items = line.split("\t")
            word = items[0]
            tag = items[1]
            analysis_list = items[2:]

            words.append(word)
            tags.append(tag)
            analyses.append(analysis_list)

    if len(words) > 0:
        yield words, tags, analyses


def predict(model, config, test_file):
    uniq_words = get_uniq_words(config.filename_train, test_file)
    data = []
    for words, tags, analyses in iter_sentences(test_file):
        tags_pred = model.predict(words, analyses)
        for w, tt, pt in zip(words, tags, tags_pred):
            iserr = is_equal(tt, pt) == False
            if w in uniq_words:
                data.append((w, tt, pt, True, iserr))
            else:
                data.append((w, tt, pt, False, iserr))

    columns = ['word', 'tt_full', 'pt_full', 'uniq', 'err']
    df = pd.DataFrame(data=data, columns=columns)

    # set pos predictions
    df['tt_pos'] = df.tt_full.str.extract(r'POS=([A-Z]+)', expand=False).fillna('')
    df['pt_pos'] = df.pt_full.str.extract(r'POS=([A-Z]+)', expand=False).fillna('')

    # set morph predictions
    df['tt_morph'] = df.tt_full.str.replace(r'(\|POS=[A-Z]+\|)', '|').str.replace(r'(\|?POS=[A-Z]+\|?)', '')
    df['pt_morph'] = df.pt_full.str.replace(r'(\|POS=[A-Z]+\|)', '|').str.replace(r'(\|?POS=[A-Z]+\|?)', '')

    return df


def calculate_accuracy(df):
    return OrderedDict(
        # full tag  accuracy
        acc_full_all=accuracy_score(df.tt_full, df.pt_full),
        acc_full_oov=accuracy_score(df[df.uniq == True].tt_full, df[df.uniq == True].pt_full),
        acc_full_voc=accuracy_score(df[df.uniq == False].tt_full, df[df.uniq == False].pt_full),

        # pos accuracy
        acc_pos_all=accuracy_score(df.tt_pos, df.pt_pos),
        acc_pos_oov=accuracy_score(df[df.uniq == True].tt_pos, df[df.uniq == True].pt_pos),
        acc_pos_voc=accuracy_score(df[df.uniq == False].tt_pos, df[df.uniq == False].pt_pos),

        # morphology tag accuracy
        acc_morph_all=accuracy_score(df.tt_morph, df.pt_morph),
        acc_morph_oov=accuracy_score(df[df.uniq == True].tt_morph, df[df.uniq == True].pt_morph),
        acc_morph_voc=accuracy_score(df[df.uniq == False].tt_morph, df[df.uniq == False].pt_morph)
    )


def accuracy_to_string_verbose(acc_dict):
    return """
    FULL TAG ACCURACY:
    All words       : {acc_full_all}
    OOV words       : {acc_full_oov}
    Vocabulary words: {acc_full_voc}

    POS ACCURACY:
    All words       : {acc_pos_all}
    OOV words       : {acc_pos_oov}
    Vocabulary words: {acc_pos_voc}

    MORPH ACCURACY:
    All words       : {acc_morph_all}
    OOV words       : {acc_morph_oov}
    Vocabulary words: {acc_morph_voc}

    """.format(**acc_dict)


if __name__ == "__main__":
    args = docopt(__doc__)

    config = load_config_from_file(args['--config'])
    print("Using configuration", config.__file__)

    if args['--file'] is True:
        test_file = args['--file']
        eval_type = 'file'
    elif args['--test'] is True:
        test_file = config.filename_test
        eval_type = 'test'
    elif args['--dev'] is True:
        test_file = config.filename_dev
        eval_type = 'dev'
    else:
        raise ValueError('Specify test mode: --dev, --test, or --file')

    config_holder = ConfigHolder(config)

    model = Model(config_holder)
    model.build()
    model.restore_session(config.dir_model)

    df = predict(model, config_holder, test_file)
    acc_dict = calculate_accuracy(df)
    acc_verbose = accuracy_to_string_verbose(acc_dict)
    print(acc_verbose)
