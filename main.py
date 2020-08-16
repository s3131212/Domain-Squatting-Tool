import argparse
import dateutil
import sys
import os
from tranco import Tranco
import Levenshtein
import enchant
import tldextract
import csv
from pprint import pprint

# English Dictionary
word_check = enchant.Dict("en_US")

def parse_source(source_domain):
    # some common trademarks are in the dictionary, we should put them back
    allowlist = ['google', 'yahoo', 'adobe', 'yelp', 'blogger', 'outlook']
    # some common trademarks are too common to appear in some other words
    blocklist = ['intel']

    source = [ (d, tldextract.extract(d).domain) for d in source_domain if len(tldextract.extract(d).domain) > 3 and not tldextract.extract(d).domain in blocklist and (not word_check.check(tldextract.extract(d).domain) or tldextract.extract(d).domain in allowlist) ]

    return source


def typosquatting(domain, source, qwerty_adj):
    qwerty_adjacency = {
        '1': ['2', 'q'], '2': ['3', 'w', 'q', '1'], '3': ['4', 'e', 'w', '2'], '4': ['5', 'r', 'e', '3'], '5': ['6', 't', 'r', '4'], '6': ['7', 'y', 't', '5'], '7': ['8', 'u', 'y', '6'], '8': ['9', 'i', 'u', '7'], '9': ['0', 'o', 'i', '8'], '0': ['p', 'o', '9'], 'q': ['1', '2', 'w', 'a'], 'w': ['3', 'e', 's', 'a', 'q', '2'], 'e': ['4', 'r', 'd', 's', 'w', '3'], 'r': ['5', 't', 'f', 'd', 'e', '4'], 't': ['6', 'y', 'g', 'f', 'r', '5'], 'y': ['7', 'u', 'h', 'g', 't', '6'], 'u': ['8', 'i', 'j', 'h', 'y', '7'], 'i': ['9', 'o', 'k', 'j', 'u', '8'], 'o': ['0', 'p', 'l', 'k', 'i', '9'], 'p': ['l', 'o', '0'], 'a': ['q', 'w', 's', 'z'], 's': ['e', 'd', 'x', 'z', 'a', 'w'], 'd': ['r', 'f', 'c', 'x', 's', 'e'], 'f': ['t', 'g', 'v', 'c', 'd', 'r'], 'g': ['y', 'h', 'b', 'v', 'f', 't'], 'h': ['u', 'j', 'n', 'b', 'g', 'y'], 'j': ['i', 'k', 'm', 'n', 'h', 'u'], 'k': ['o', 'l', 'm', 'j', 'i'], 'l': ['k', 'o', 'p'], 'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'], 'c': ['x', 'd', 'f', 'v'], 'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'], 'n': ['b', 'h', 'j', 'm'], 'm': ['n', 'j', 'k']
    }

    typosquatting = dict()

    # missing dot
    typosquatting["missing-dot"] = list()
    for d in domain:
        for t in source:
            if ("www" + t[1]) in d:
                typosquatting["missing-dot"].append((d, t[0]))

    # Character-omission
    typosquatting["character-omission"] = list()
    for d in domain:
        for t in source:
            if len(t[0]) - len(d) == 1 and Levenshtein.distance(d, t[0]) == 1:
                typosquatting["character-omission"].append((d, t[0]))
    
    # Character-permutation
    typosquatting["character-permutation"] = list()
    for d in domain:
        for t in source:
            if len(t[0]) == len(d):
                for i in range(len(t[0]) - 1):
                    if t[0][i+1] == t[0][i]:
                        continue
                    if d == (t[0][:i] + t[0][i+1] + t[0][i] + t[0][i+2:]):
                        typosquatting["character-permutation"].append((d, t[0]))
                        break

    # Character-substitution
    typosquatting["character-substitution"] = list()
    for d in domain:
        for t in source:
            if len(t[0]) == len(d):
                if qwerty_adj:
                    is_typosquatting = False
                    distance = 0
                    for i in range(len(d)):
                        if d[i] != t[0][i]:
                            if t[0][i] in qwerty_adjacency and d[i] in qwerty_adjacency[t[0][i]]:
                                distance += 1
                                is_typosquatting = True
                            else:
                                is_typosquatting = False
                                break
                    if is_typosquatting and distance <= 1:
                        typosquatting["character-substitution"].append((d, t[0]))
                else:
                    if len(t[0]) == len(d) and Levenshtein.distance(d, t[0]) == 1:
                        typosquatting["character-substitution"].append((d, t[0]))
    # Character-duplication
    typosquatting["character-duplication"] = list()
    for d in domain:
        for t in source:
            if len(t[0]) == len(d) - 1:
                for i in range(len(t[0]) - 1):
                    if t[0][i+1] == t[0][i]:
                        continue
                    if d == (t[0][:i] + t[0][i] * 2 + t[0][i+1:]):
                        typosquatting["character-duplication"].append((d, t[0]))
                        break
    
    return typosquatting

def combosquatting(domain, source):
    combosquatting = list()
    for d in domain:
        for t in source:
            if t[1] in d and tldextract.extract(t[0]).domain != tldextract.extract(d).domain:
                combosquatting.append((d, t[0]))
                break
    return combosquatting

def bitsqautting(domain, source):
    def hamming_binary(str1, str2):
        bstr1 = ' '.join(format(ord(x), 'b') for x in str1)
        bstr2 = ' '.join(format(ord(x), 'b') for x in str2)
        return sum(c1 != c2 for c1, c2 in zip(bstr1, bstr2))
    
    bitsqautting = list()
    for d in domain:
        for t in source:
            if len(t[0]) == len(d):
                if hamming_binary(t[0], d) == 1:
                    bitsqautting.append((d, t[0]))
    return bitsqautting

def homographsquatting(domain, source):
    # from https://github.com/elceef/dnstwist/blob/master/dnstwist.py#L244-L268
    homoglyph = {
        'a': [u'à', u'á', u'â', u'ã', u'ä', u'å', u'ɑ', u'ạ', u'ǎ', u'ă', u'ȧ', u'ą'],
        'b': ['d', 'lb', u'ʙ', u'ɓ', u'ḃ', u'ḅ', u'ḇ', u'ƅ'],
        'c': ['e', u'ƈ', u'ċ', u'ć', u'ç', u'č', u'ĉ'],
        'd': ['b', 'cl', 'dl', u'ɗ', u'đ', u'ď', u'ɖ', u'ḑ', u'ḋ', u'ḍ', u'ḏ', u'ḓ'],
        'e': ['c', u'é', u'è', u'ê', u'ë', u'ē', u'ĕ', u'ě', u'ė', u'ẹ', u'ę', u'ȩ', u'ɇ', u'ḛ'],
        'f': [u'ƒ', u'ḟ'],
        'g': ['q', u'ɢ', u'ɡ', u'ġ', u'ğ', u'ǵ', u'ģ', u'ĝ', u'ǧ', u'ǥ'],
        'h': ['lh', u'ĥ', u'ȟ', u'ħ', u'ɦ', u'ḧ', u'ḩ', u'ⱨ', u'ḣ', u'ḥ', u'ḫ', u'ẖ'],
        'i': ['1', 'l', u'í', u'ì', u'ï', u'ı', u'ɩ', u'ǐ', u'ĭ', u'ỉ', u'ị', u'ɨ', u'ȋ', u'ī'],
        'j': [u'ʝ', u'ɉ'],
        'k': ['lk', 'ik', 'lc', u'ḳ', u'ḵ', u'ⱪ', u'ķ'],
        'l': ['1', 'i', u'ɫ', u'ł'],
        'm': ['n', 'nn', 'rn', 'rr', u'ṁ', u'ṃ', u'ᴍ', u'ɱ', u'ḿ'],
        'n': ['m', 'r', u'ń', u'ṅ', u'ṇ', u'ṉ', u'ñ', u'ņ', u'ǹ', u'ň', u'ꞑ'],
        'o': ['0', u'ȯ', u'ọ', u'ỏ', u'ơ', u'ó', u'ö'],
        'p': [u'ƿ', u'ƥ', u'ṕ', u'ṗ'],
        'q': ['g', u'ʠ'],
        'r': [u'ʀ', u'ɼ', u'ɽ', u'ŕ', u'ŗ', u'ř', u'ɍ', u'ɾ', u'ȓ', u'ȑ', u'ṙ', u'ṛ', u'ṟ'],
        's': [u'ʂ', u'ś', u'ṣ', u'ṡ', u'ș', u'ŝ', u'š'],
        't': [u'ţ', u'ŧ', u'ṫ', u'ṭ', u'ț', u'ƫ'],
        'u': [u'ᴜ', u'ǔ', u'ŭ', u'ü', u'ʉ', u'ù', u'ú', u'û', u'ũ', u'ū', u'ų', u'ư', u'ů', u'ű', u'ȕ', u'ȗ', u'ụ'],
        'v': [u'ṿ', u'ⱱ', u'ᶌ', u'ṽ', u'ⱴ'],
        'w': ['vv', u'ŵ', u'ẁ', u'ẃ', u'ẅ', u'ⱳ', u'ẇ', u'ẉ', u'ẘ'],
        'y': [u'ʏ', u'ý', u'ÿ', u'ŷ', u'ƴ', u'ȳ', u'ɏ', u'ỿ', u'ẏ', u'ỵ'],
        'z': [u'ʐ', u'ż', u'ź', u'ᴢ', u'ƶ', u'ẓ', u'ẕ', u'ⱬ']
    }
    homographsquatting = list()
    for d in domain:
        for t in source:
            if len(d) == len(t[0]):
                is_homographsquatting = True
                for i in range(len(d)):
                    if d[i] != t[0][i] and d[i] not in (homoglyph[t[0][i]] if t[0][i] in homoglyph else []):
                        is_homographsquatting = False
                        break
                if is_homographsquatting:
                    homographsquatting.append((d, t[0]))
    return homographsquatting

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        usage='%s [OPTION]... [FILENAME]' % sys.argv[0],
        description=
        '''Domain Squatting Tool'''
    )
    parser.add_argument('filename', help='Filename of the list of domains to be scanned (separated by \\n)')
    parser.add_argument('--source', type=str, help='List of domains that might be the victims of domain squatting, separated by comma.')
    parser.add_argument('--top-tranco', type=int, default=500, help='If the --source is not provided, consider Tranco top N as the source. By default, N=500')
    parser.add_argument('--qwerty-adj', type=str, default="true", help='Only consider a domain typosquatting when the characters are replaced by their adjacent one on the QWERTY layout. True by default.')
    parser.add_argument('--export', type=str, help='Export results to FILE')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    print(args)

    domain_to_be_scanned = list()
    domain_source = list()

    if os.path.isfile(args.filename):
        with open(args.filename) as f:
            domain_to_be_scanned = f.readlines()
            domain_to_be_scanned = [x.strip() for x in domain_to_be_scanned] 
    else:
        print('%s not found.' % args.filename)
        sys.exit(1)

    if args.source is not None:
        domain_source = list(args.source.split(','))
    else:
        t = Tranco(cache=True, cache_dir='.tranco')
        domain_source = t.list().top(args.top_tranco)

    domain_source = parse_source(domain_source)

    print("Number of Domain:", len(domain_to_be_scanned))
    print("Number of Source:", len(domain_source))
    
    result = dict()
    result["typosquatting"] = typosquatting(domain_to_be_scanned, domain_source, args.qwerty_adj.lower() == "true")
    result["combosquatting"] = combosquatting(domain_to_be_scanned, domain_source)
    result["bitsqautting"] = bitsqautting(domain_to_be_scanned, domain_source)
    result["homographsquatting"] = homographsquatting(domain_to_be_scanned, domain_source)
    pprint(result)

    if args.export is not None:
        filename = args.export if args.export.endswith('.csv') else args.export + '.csv'
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['id', 'domain', 'source', 'type'])

            idc = 1

            for t in result.keys():
                if isinstance(result[t], list):
                    for d in result[t]:
                        writer.writerow([idc, d[0], d[1], t])
                        idc += 1
                else:
                    for tt in result[t].keys():
                        for d in result[t][tt]:
                            writer.writerow([idc, d[0], d[1], "{} ({})".format(t, tt)])
                            idc += 1

