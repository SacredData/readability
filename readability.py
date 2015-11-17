#!/usr/bin/env python

import math
import argparse

from utils import get_char_count
from utils import get_words
from utils import get_sentences
from utils import count_syllables
from utils import count_complex_words
from newspaper import Article


class Readability:
    """
    Pass a URL, get a bunch of analysis of the text held within it.
    The analysis will focus primarily upon the text's complexity and
    its other features relevant to the production of a spoken audio version.
    Essentially, this class will be used to populate a few records
    on the production db of clients who work with text content.

    This code is the result of a fork of the awesome Readability
    repo by Max Mautner. Thanks, my man!
    https://github.com/mmautner/readability
    """
    analyzedVars = {}

    def __init__(self, text):
        self.analyze_text(text)

    def analyze_text(self, text):
        words = get_words(text)
        char_count = get_char_count(words)
        word_count = len(words)
        sentence_count = len(get_sentences(text))
        syllable_count = count_syllables(words)
        complexwords_count = count_complex_words(text)
        avg_words_p_sentence = word_count/sentence_count

        self.analyzedVars = {
            'words': words,
            'char_cnt': float(char_count),
            'word_cnt': float(word_count),
            'sentence_cnt': float(sentence_count),
            'syllable_cnt': float(syllable_count),
            'complex_word_cnt': float(complexwords_count),
            'avg_words_p_sentence': float(avg_words_p_sentence)
        }

    def ARI(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = 4.71 * (self.analyzedVars['char_cnt'] / self.analyzedVars['word_cnt']) + 0.5 * (self.analyzedVars['word_cnt'] / self.analyzedVars['sentence_cnt']) - 21.43
        return score

    def FleschReadingEase(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = 206.835 - (1.015 * (self.analyzedVars['avg_words_p_sentence'])) - (84.6 * (self.analyzedVars['syllable_cnt']/ self.analyzedVars['word_cnt']))
        return round(score, 4)

    def FleschKincaidGradeLevel(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = 0.39 * (self.analyzedVars['avg_words_p_sentence']) + 11.8 * (self.analyzedVars['syllable_cnt']/ self.analyzedVars['word_cnt']) - 15.59
        return round(score, 4)

    def GunningFogIndex(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = 0.4 * ((self.analyzedVars['avg_words_p_sentence']) + (100 * (self.analyzedVars['complex_word_cnt']/self.analyzedVars['word_cnt'])))
        return round(score, 4)

    def SMOGIndex(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = (math.sqrt(self.analyzedVars['complex_word_cnt']*(30/self.analyzedVars['sentence_cnt'])) + 3)
        return score

    def ColemanLiauIndex(self):
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            score = (5.89*(self.analyzedVars['char_cnt']/self.analyzedVars['word_cnt']))-(30*(self.analyzedVars['sentence_cnt']/self.analyzedVars['word_cnt']))-15.8
        return round(score, 4)

    def LIX(self):
        longwords = 0.0
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            for word in self.analyzedVars['words']:
                if len(word) >= 7:
                    longwords += 1.0
            score = self.analyzedVars['word_cnt'] / self.analyzedVars['sentence_cnt'] + float(100 * longwords) / self.analyzedVars['word_cnt']
        return score

    def RIX(self):
        longwords = 0.0
        score = 0.0
        if self.analyzedVars['word_cnt'] > 0.0:
            for word in self.analyzedVars['words']:
                if len(word) >= 7:
                    longwords += 1.0
            score = longwords / self.analyzedVars['sentence_cnt']
        return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Text analysis via URL.')
    parser.add_argument('-url', type=str, help='URL of Article')
    args = parser.parse_args()
    url = args.url
    a = Article(url)
    print 'Retrieving article at URL: ', url
    a.download()
    print 'Article downloaded.'
    a.parse()
    print 'Article parsed.'
    text = a.text
    a.nlp()
    title = a.title
    summary = a.summary
    keywords = a.keywords
    seo_terms = []
    for word in keywords:
        seo_terms.append(str(word))
    print 'Article title:    ', title
    # print 'Article summary:  ', summary
    print 'Article text:     ', text
    rd = Readability(str(text))
    spoken_dur = rd.analyzedVars['word_cnt'] / 2.5 / 60  # approx minutes
    spoken_dur = round(spoken_dur, 2)
    if rd.SMOGIndex() > 12.0:
        read_level = 'College'
    elif rd.SMOGIndex() > 8.0:
        read_level = 'High school'
    elif rd.SMOGIndex() > 5.0:
        read_level = 'Middle school'
    else:
        read_level = 'Elementary school'
    print ''
    print 'SMOG Readability score:  ', rd.SMOGIndex()
    print 'Reading grade level:     ', read_level
    print 'Approx. spoken duration: ', str(spoken_dur), ' minutes'
    print 'Article keywords:        ', seo_terms
