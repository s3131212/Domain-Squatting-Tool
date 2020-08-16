# Domain-Squatting-Tool
A tool to detect Domain Squatting (a.k.a. Cybersquatting) from a given list of domains.  

If you're looking for a tool to discover new cybersquatting domains, [dnstwist](https://github.com/elceef/dnstwist) is a great tool.

## Installation
First, install all dependencies by:  

```
pip install -r requirements.txt
```

Since we use `pyenchant`, you might want to check out how to install enchant [here](https://pyenchant.github.io/pyenchant/install.html#installing-the-enchant-c-library).  


## Usage

```
python3 main.py [OPTION] list.txt
```

All domains to be scanned should be separated by `\n`, for example:  

```
google.com
gooogle.com
ggogle.com
golgle.com
paypal-member.com
wwwpaypal.com
y0utube.com
```

The results are:
```
{'bitsqautting': [('ggogle.com', 'google.com')],
 'combosquatting': [],
 'homographsquatting': [('y0utube.com', 'youtube.com')],
 'typosquatting': {'character-duplication': [('gooogle.com', 'google.com')],
                   'character-omission': [],
                   'character-permutation': [],
                   'character-substitution': [('ggogle.com', 'google.com'),
                                              ('golgle.com', 'google.com'),
                                              ('y0utube.com', 'youtube.com')],
                   'missing-dot': []}}
```

Options:
```
positional arguments:
  filename              Filename of the list of domains to be scanned (separated by \n)

optional arguments:
  -h, --help            show this help message and exit
  --source SOURCE       List of domains that might be the victims of domain squatting, separated by comma.
  --top-tranco TOP_TRANCO
                        If the --source is not provided, consider Tranco top N as the source. By default, N=500
  --qwerty-adj QWERTY_ADJ
                        Only consider a domain typosquatting when the characters are replaced by their adjacent one on the QWERTY layout.
                        True by default.
  --export EXPORT       Export results to FILE
```

For example:  

```
# Don't take keyboard layout into consideration, look for domain squatting of google.com and paypal.com, export results to output.csv
python3 main.py --qwerty-adj=false --export=output --top-tranco=100 list.txt


# Take keyboard layout into consideration, look for domain squatting of Tranco top 10
python3 main.py --top-tranco=10 list.tx a blocklist, the lists are located in the function parse_source.

Tranco is a research-oriented top sites ranking, which is considered more robust than Alexa and some other rt

# Take keyboard layout into consideration, look for domain squatting of Tranco top 500
python3 main.py list.txt
```

Since some trademarks may be too common to take into consideration, we build an allowlist and a blocklist, the lists are located in the function `parse_source`.  

[Tranco](https://tranco-list.eu/) is a research-oriented top sites ranking, which is considered more robust than Alexa and some other ranking lists. When no source is provided, the script would fetch the newest Tranco ranking as the source.  

## License
MIT License.  
Also, feel free to open issues and pull requests.  

The homoglyph list and qwerty layout are from [dnstwsit](https://github.com/elceef/dnstwist), you might want to check out their amazing work.  

## Reference
The methods used in this project are mentioned in or inspired by the following works:  

Agten, P., Joosen, W., Piessens, F., & Nikiforakis, N. (2015). Seven Months Worth of Mistakes: A Longitudinal Study of Typosquatting Abuse. Proceedings 2015 Network and Distributed System Security Symposium. doi: 10.14722/ndss.2015.23058  
Dinaburg, A. (2011). Bitsquatting: DNS Hijacking without Exploitation. Proceedings of BlackHat Security.  
Kintis, P., Miramirkhani, N., Lever, C., Chen, Y., Romero-Gómez, R., Pitropakis, N., … Antonakakis, M. (2017). Hiding in Plain Sight: A Longitudinal Study of Combosquatting Abuse. Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security. doi: 10.1145/3133956.3134002  
Nikiforakis, N., Acker, S. V., Meert, W., Desmet, L., Piessens, F., & Joosen, W. (2013). Bitsquatting: Exploiting Bit-flips for Fun, or Profit? Proceedings of the 22nd International Conference on World Wide Web - WWW 13. doi: 10.1145/2488388.2488474

