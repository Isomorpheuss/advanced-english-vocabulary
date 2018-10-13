import csv
import bisect
import os
import collections
import math
from wordfreq import word_frequency
from recordclass import recordclass
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer('english')

prefixes = ['a', 'ab', 'ac', 'ad', 'an', 'ante', 'anti', 'as', 'auto', 'ben', 'bi', 'circum', 'co', 'com', 'con', 'contra', 'counter', 'de', 'dis', 'e', 'ecto', 'em', 'en', 'epi', 'eu', 'ex', 'exo', 'extra', 'extro', 'fore', 'hemi', 'homo', 'hyper', 'hypo', 'il', 'im', 'in', 'infra', 'inter',
            'intra', 'ir', 'macro', 'mal', 'micro', 'mid', 'mis', 'mono', 'multi', 'non', 'o', 'ob', 'oc', 'omni', 'op', 'over', 'para', 'peri', 'poly', 'post', 'pre', 'pro', 'quad', 're', 'semi', 'sub', 'sup', 'super', 'supra', 'sus', 'sym', 'syn', 'therm', 'trans', 'tri', 'ultra', 'un', 'uni']

# 'extemp':({'extempore','extemporariness','extempore','extempory','extemporisation','extemporise'}, {'gre', 'magoosh'}, 'extemporaneous', 7e-8, 1e-7)
StemStuff = recordclass(
    'StemStuff', 'inflections wordlists freq_inflection max_freq freq_sum')


def bisect_contains(a, x):
    i = bisect.bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return True
    return False


def load_dictionary(dictionaryname):
    full_dictionary = []
    with open(dictionaryname, 'r', encoding='utf-8') as dictionary:
        for word in dictionary:
            full_dictionary.append(word.strip().lower())
    print('Full dictionary length', len(full_dictionary))
    return sorted(full_dictionary)


def get_surrounding_words(target, full_dictionary, listfile):
    surrounding = []
    try:
        i = full_dictionary.index(target)
        surrounding = full_dictionary[max(
            0, i-10):min(len(full_dictionary), i+10)]
        if len(surrounding) < 20:
            print(target, surrounding)
    except ValueError:
        print(f'Dictionary doesn\'t contain {target} from {str(listfile)}')
    finally:
        return surrounding


def check_prefixes(target, full_dictionary):
    prefixed_words = []
    for prefix in prefixes:
        full_word = prefix+target
        if bisect_contains(full_dictionary, full_word):
            prefixed_words.append(full_word)
    if prefixed_words:
        pass
        # print(f'{len(prefixed_words)} successful prefixes for {target}')
    return prefixed_words


def match_stems_etc(stem_dict, surrounding_words, target, containing_list, full_dictionary):
    target_stem = stemmer.stem(target)
    if target_stem in stem_dict:
        if target in stem_dict[target_stem].inflections:
            stem_dict[target_stem].wordlists.add(containing_list)
        else:
            stem_dict[target_stem].inflections.add(target)
            stem_dict[target_stem].wordlists.add(containing_list)
            wf = word_frequency(target, lang='en', wordlist='large')
            stem_dict[target_stem].freq_sum += wf
            if wf > stem_dict[target_stem].max_freq:
                stem_dict[target_stem].max_freq = wf
                stem_dict[target_stem].freq_inflection = target
    else:
        max_freq = 0
        inflections = set()
        max_freq_inflection = ''
        freq_sum = 0

        def add_word_and_update(word, prefix):
            nonlocal max_freq, inflections, max_freq_inflection, freq_sum
            inflections.add(word)
            wf = word_frequency(word, lang='en', wordlist='large')
            freq_sum += wf
            if not prefix:  # if prefix, don't update the representative because of potential conflicts. but, do update frequency
                if wf >= max_freq:
                    max_freq = wf
                    max_freq_inflection = word

        for word in surrounding_words:
            stem = stemmer.stem(word)
            if stem == '':
                print(stem, surrounding_words, max_freq,
                      inflections, max_freq_inflection, freq_sum)
            if stem == target_stem:
                prefixed_words = check_prefixes(word, full_dictionary)
                if prefixed_words:
                    for prefixed_word in prefixed_words:
                        if prefixed_word not in inflections:
                            add_word_and_update(prefixed_word, True)
                add_word_and_update(word, False)
        init_wordlist = set()
        init_wordlist.add(containing_list)

        # if all 0 freq just make the representative word the target
        if freq_sum == 0:
            max_freq_inflection = target
        stem_dict[target_stem] = StemStuff(
            inflections, init_wordlist, max_freq_inflection, max_freq, freq_sum)


def freq_to_zipf(freq):
    if freq == 0:
        return 0
    return round(math.log(freq, 10) + 9, 2)


def write_out_dict(stuff, filename):
    with open(filename, 'w', encoding='utf-8') as fo:
        for k, v in stuff:
            fo.write(str(k) + ' >>> ' + str(v) + '\n\n')


def write_out_list(stuff, filename):
    with open(filename, 'w', encoding='utf-8') as fo:
        for item in stuff:
            fo.write(str(item) + '\n')


def write_out_csv(stuff, filename):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        mywriter = csv.writer(csvfile, delimiter='\t')
        mywriter.writerows(stuff)


def simplify_dict(some_dict):
    simple_list = []
    for key, stuff in some_dict.items():
        simple_list.append((stuff.freq_inflection,
                            freq_to_zipf(stuff.freq_sum), sorted(list(stuff.wordlists))))
    return simple_list


def xormore(num_lists, stuff):
    for i in range(2, num_lists+1):
        just_words = [x[0] for x in stuff if x[2] >= i]
        everything = [x for x in stuff if x[2] >= i]
        list_length = len(just_words)
        if list_length != 0:
            write_out_list(just_words,
                           f'output/{i}ormore-justwords-{list_length}.txt')
            write_out_csv(everything,
                          f'output/{i}ormore-withfreqandlistcount-{list_length}.csv')


def main():
    folder = 'vocab'
    dictionaryname = 'words.txt'
    listnames = os.listdir(folder)
    num_lists = len(listnames)
    full_dictionary = load_dictionary(dictionaryname)
    stem_dict = {}

    # loop through every vocabulary list
    for listname in listnames:
        with open(f'{folder}/{listname}', 'r', encoding='utf-8') as listfile:
            for line in listfile:
                # first element is word. ignore everything after space.
                words = line.split('\t')[0].split(' ')
                if len(words) != 1:
                    print('Warning, weird word', ' '.join(
                        words), f'from {listname}')
                word = words[0].strip().lower()
                # get surrounding words (dictionary order) from large dictionary
                surrounding_words = get_surrounding_words(
                    word, full_dictionary, listname)
                if surrounding_words:
                    match_stems_etc(
                        stem_dict, surrounding_words, word, listname, full_dictionary)
    simple_list = simplify_dict(stem_dict)

    # minimum of 2 intersecions
    recommended_list = sorted(
        [(x[0], x[1], len(x[2])) for x in simple_list if len(x[2]) >= 2], key=lambda x: x[1], reverse=True)
    # trim off top fifth most frequent words. these are usually junk
    trimmed_recommended_list = recommended_list[math.floor(
        len(recommended_list)/5):]
    xormore(num_lists, trimmed_recommended_list)
    write_out_dict(
        sorted(stem_dict.items(), key=lambda x: x[0]), 'stemdict.txt')


main()
