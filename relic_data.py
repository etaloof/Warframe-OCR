import json
import os
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup


def collect_custom(transform):
    """
    Decorator to turn a function returning an iterator with the given transform callable
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return transform(result)

        return wrapper
    return decorator


def collect(func):
    """
    Decorator to turn a function returning an iterator into a function returning a list
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return list(result)

    return wrapper


def collect_unique(func):
    """
    Decorator to turn a function returning an iterator into a function returning a set,
    effectively removing duplicates.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return set(result)

    return wrapper


def collect_unique_ordered(func):
    """
    Decorator to turn a function returning an iterator into a function returning a set,
    effectively removing duplicates. Keeps the order of elements which means
    only the first occurrence of an element is kept and all following duplicates are removed.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return OrderedDict.fromkeys(result).keys()

    return wrapper


WFDATA_VERSION_PATH = '.cache/wfdata.version'
WFDATA_FILES = """All.json
Arcanes.json
Arch-Gun.json
Arch-Melee.json
Archwing.json
Enemy.json
Fish.json
Gear.json
Glyphs.json
Melee.json
Misc.json
Mods.json
Node.json
Pets.json
Primary.json
Quests.json
Relics.json
Resources.json
Secondary.json
SentinelWeapons.json
Sentinels.json
Sigils.json
Skins.json
Warframes.json"""


@collect_custom(dict)
def get_relic_data():
    os.makedirs('.cache', exist_ok=True)

    def local_version(new=None):
        if new and int(new, base=16):
            with open(WFDATA_VERSION_PATH, 'w', encoding='utf-8') as f:
                f.write(new)
                return
        try:
            with open(WFDATA_VERSION_PATH, encoding='utf-8') as f:
                new = f.read()
                if new and int(new, base=16):
                    return new
        except OSError:
            pass

    def remote_version():
        soup = requests.get('https://github.com/WFCD/warframe-items/commits').content
        soup = BeautifulSoup(soup, 'lxml')
        soup = soup.select_one('clipboard-copy')
        return soup['value']

    version = remote_version()
    is_cache_fresh = version == local_version()
    print('cache is fresh' if is_cache_fresh else 'cache is not fresh')

    for file_name in WFDATA_FILES.splitlines():
        name, *_ = file_name.split('.')
        yield name, fetch(file_name, is_cache_fresh)

    local_version(version)


def fetch(name, from_cache=False):
    path = '.cache/' + name
    if from_cache:
        with open(path, encoding='utf-8') as f:
            return json.loads(f.read())

    url = 'https://raw.githubusercontent.com/WFCD/warframe-items/development/data/json/' + name
    print('Downloading ' + url)

    d = requests.get(url).text
    with open(path, 'w', encoding='utf-8') as f:
        f.write(d)

    return json.loads(d)


def find_relic_rewards_from_relic_name(data, relic_name):
    """
    Find all rewards which can be obtained from the given relic.
    """

    @collect_unique
    def _find_relic_rewards_from_relic_name(name):
        era, name, *_ = name.split()
        name = f'{era.capitalize()} {name.capitalize()} Relic'

        for category in data.values():
            for item in category:
                if 'components' in item and 'Prime' in item['name']:
                    for component in item['components']:
                        if 'drops' in component:
                            for drop in component['drops']:
                                if drop['location'] == name:
                                    yield drop['chance'], drop['type']

    def key(chance_and_name):
        chance, name = chance_and_name
        return float(chance)

    drops = _find_relic_rewards_from_relic_name(relic_name)
    drops = sorted(drops, key=key, reverse=True)
    for _, reward_name in drops:
        yield reward_name


@collect_unique_ordered
def relic_names(data):
    for relic in data['Relics']:
        full_relic_name = relic['name']
        index = full_relic_name.rfind(' ')
        yield full_relic_name[:index]


def is_vaulted_relic(data, name):
    return not any(['drops' in relic for relic in data['Relics'] if name in relic['name']])


if __name__ == '__main__':
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    VAULTED = RED + 'V'
    UNVAULTED = GREEN + ' '

    item_data = get_relic_data()
    for relic_name in relic_names(item_data):
        v = is_vaulted_relic(item_data, relic_name)
        v = VAULTED if v else UNVAULTED
        rewards = find_relic_rewards_from_relic_name(item_data, relic_name)
        rewards = ' | '.join(rewards)
        ljust = relic_name.ljust(
            4  # max(len(x) for x in ('lith', 'meso', 'neo', 'axi'))
            + 1  # space
            + 1  # relic letter
            + 2  # relic number (at most two digits)<
        )
        print(v, ljust, '-', rewards, RESET)
