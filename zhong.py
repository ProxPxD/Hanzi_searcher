#!/usr/bin/python3.8
import sys
import re


def get_vowels(word):
    return [l for l in word if l in 'aeouiü']


def add_tone(vowel, num):
    proper = {
        'a': ['ā','á','ǎ','à','a'],
        'e': ['ē','é','ě','è','e'],
        'o': ['ō','ó','ǒ','ò','o'],
        'u': ['ū','ú','ǔ','ù','u'],
        'i': ['ī','í','ǐ','ì','i'],
        'ü': ['ǖ','ǘ','ǚ','ǜ','ü']
    }
    num = int(num) - 1
    return proper[vowel][num]


def beautiful_pinyin(pinyin):
    tone = pinyin[-1]
    pinyin = pinyin.replace('u:', 'ü')[:-1]
    vowels = get_vowels(pinyin)
    if len(vowels) == 0:
        return ''

    if len(vowels) > 1 and vowels[0] in 'ui':
        vowel = vowels[-1]
    else:
        vowel = vowels[0]

    pinyin = pinyin.replace(vowel, add_tone(vowel, tone))
    return pinyin


def get_measure_words(definitions):
    result = []
    for definition in definitions:
        if 'CL:' in definition:
            measure_words = definition[3:].split(',')
            for measure_word in measure_words:
                if '|' in measure_word:
                    measure_word = measure_word[2:]
                word = measure_word[0]
                pronunciation = beautiful_pinyin(measure_word[2:-1])
                result.append([word, pronunciation])
            definitions.remove(definition)
            break
    return result


def process_line(line):#'() () [()] /()/.*'
    regex = re.compile('(.+) (.+) \[(.+)\] /(.+)/')
    result = [elem for elem in regex.match(line).groups()]
    result[2] = [beautiful_pinyin(pinyin) for pinyin in result[2].split(' ')]
    result[3] = result[3].split('/')
    result.append(get_measure_words(result[3]))

    return result


def search(path, key, condition=lambda line, key: True, variants=False):
    with open(path, 'r') as f:
        result = [process_line(line) for line in f if condition(line, key) and line[0] != '#' and (variants or 'variant' not in line)]

    return result


def search_for_words(path, key, variants=False):
    condition = lambda line, key: key in line.split('/', 1)[0]
    return search(path, key, condition, variants)


def search_for_word(path, key, variants=False):
    condition = lambda line, key: key == line.split('/', 1)[0].split(' ')[1]
    return search(path, key, condition, variants)


def is_any(line, sentence):
    cond = False
    for character in sentence:
        cond = cond or character in line.split('/', 1)[0]
    return cond


def generate_substrings(word):
    for l in range(len(word) + 1, 0, -1):
        for p in range(0, len(word) - l + 1):
            yield word[p:p+l]


def split_to_words(path, sentence, variants=False):
    results = []
    for substring in generate_substrings(sentence):
        if len(substring) > 50:
            continue
        res = search_for_word(path, substring)
        if len(res) > 0:
            parts = sentence.split(substring)
            part1 = parts[0]
            part2 = parts[1]
            
            results.append(res[0])
            results.extend(split_to_words(path, part1))
            results.extend(split_to_words(path, part2))
            break

    return results


def show_results(results):
    for record in results:
        show_record(record)


def show_record(record):
    string = record[1] #word
    if record[1] != record[0]:
        string += '[{}]'.format(record[0]) #traditional if exists
    #string += ' '

    for pinyin in record[2]: #pinyin pronunciaion
        string += pinyin
    if len(record[4]) > 0:
        string += ' ('
        for meassure in record[4]:
            string += meassure[0] + meassure[1] + ', '
        string = string[0:-2] + ')'

    string += ': '
    for trans in record[3]: #translations
        string += trans + ', '
    string = string[0:-2]
    print(string)


def select_results(results, i):
    return [res for res in results if len(res[1]) == i]


def main():
    path = '/home/proxpxd/Desktop/moje_programy/python/systemowe/Hanzi_searcher/cedict_ts.u8'
    key = sys.argv[1]
    if '-s' in sys.argv:
        results = split_to_words(path, key)
    elif '-a' in sys.argv:
        results = search_for_words(path, key)
    else:
        results = search_for_word(path, key)

    results.sort(key=lambda part: len(part[0]), reverse=True)
    show_results(results)


if __name__ == '__main__':
    main()
