from TwitterAPI import TwitterAPI
from urllib.parse import urlparse
from threading import Thread
from emoji import demojize
from time import time
import re, pprint, sys

config = {
    'access_token_secret': '',
    'access_token_key' : '',
    'consumer_key' : '',
    'consumer_secret' : ''
}
class TwitterScraper():
    def __init__(self, **config):
        self.config = config
        self.is_alive = False
        self.stats = {
                'totalTweets' : 0,
                'emoji': {},
                'tweetsWithEmoji': 0,
                'hashtags': {},
                'tweetsWithURL': 0,
                'urls': {},
                'tweetsWithPictures': 0}
        self.startTime = time();
        #Which regex matches emoji depends on your version of python, and whether utf-8
        #works correctly - http://bit.ly/1Qze0uE
        try:
            self.emoji_regex = re.compile('[\U00010000-\U0010ffff]')
        except re.error:
            self.emoji_regex = re.compile('[\uD800-\uDBFF][\uDC00-\uDFFF]')

    def client(self):
        #Open streaming client
        try:
            api = TwitterAPI(self.config['consumer_key'], self.config['consumer_secret'], 
                    self.config['access_token_key'], self.config['access_token_secret'])
        except:
            print('Invalid auth credentials')
            sys.exit()

        self.is_alive = True
        r = self.api.request('statuses/sample')
        for tweet in r:
            try: 
                if 'text' in tweet:
                    self.parse(tweet)
            except TwitterRequestError:
                sys.is_alive = False
                print('Invalid Credentials')
                sys.exit()

    def parse(self, tweet):
        self.stats['totalTweets'] += 1

        #Look for images
        if 'media' in tweet['entities'] or self._is_instagram(tweet):
            self.stats['tweetsWithPictures'] += 1

        #Look for hashtags
        for hashtag in tweet['entities']['hashtags']:
            self._increase_count(hashtag['text'], self.stats['hashtags'])

        #Look for urls
        if tweet['entities']['urls']:
            self.stats['tweetsWithURL'] += 1
            for url in tweet['entities']['urls']:
                netloc = urlparse(url['expanded_url']).netloc
                self._increase_count(netloc, self.stats['urls'])

        #Look for emoji
        emojis = self.emoji_regex.findall(tweet['text'])
        if emojis:
            self.stats['tweetsWithEmoji'] += 1
            for emoji in emojis:
                self._increase_count(demojize(emoji), self.stats['emoji'])

    def serve(self):
        pp = pprint.PrettyPrinter(indent=4)
        while True:
            response = input('Want some data? (y/n) ')
            if self.is_alive is not True:
                print('Too bad')
                sys.exit()
            if response.lower() == 'y':
                pp.pprint(self.calculate())
            elif response.lower() == 'n':
                break
            else: 
                pass

    def calculate(self):
        stats = self.stats
        results = {}
        results['total'] = stats['totalTweets']
        results['elapsed'] = round(time() - self.startTime, 2)
        #averages - sec, min, hr
        results['averages'] = {}
        for unit in ['seconds', 'minutes', 'hours']:
            results['averages'][unit] = round(self._average(results['total'], 
                unit, results['elapsed']), 2)

        #most popular: domains, emoji, hashtags
        results['popular'] = {}
        for metric in ['urls', 'emoji', 'hashtags']:
            results['popular'][metric] = self._most_popular(stats[metric], 10)

        #Percent urls, emojis, pictures
        results['percent'] = {}
        for metric in ['tweetsWithURL', 'tweetsWithEmoji', 'tweetsWithPictures']:
            try:
                results['percent'][metric] = round(stats[metric] / results['total'] * 100, 2)
            except ZeroDivisionError:
                results['percent'][metric] = 0

        return results
    
    def _average(self, total, unit, elapsed):
        conversion= {
            'seconds' : 1,
            'minutes' : 60,
            'hours': 60 * 60
            }
        try:
            return round(total / (elapsed / conversion[unit]), 2)
        except ZeroDivisionError:
            return 0

    def _increase_count(self, item, collection):
        #Add item count to collection
        if item in collection:
            collection[item] += 1
        else:
            collection[item] = 1

    def _is_instagram(self, tweet):
        for url in tweet['entities']['urls']:
            if urlparse(url['expanded_url']).netloc == 'www.instagram.com':
                return True
        return False

    def _most_popular(self, collection, n):
        #Sorted retrns smallest-to-largest; we revese sort to get the descending list then
        #take the head n elements
        try:
            return sorted(collection, key=lambda val:collection[val], reverse=True)[:n]
        except IndexError:
            return []

if __name__ == '__main__':
    #get configuration
    config = dict(x.split('=', 1) for x in sys.argv[1:]) or config
    twitter = TwitterScraper(**config)
    t1 = Thread(target=twitter.client)
    t1.daemon = True
    t1.start()
    twitter.serve()

