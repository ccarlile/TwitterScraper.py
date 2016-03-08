Python Twitter Streamer
=======================
Streaming client for the Twitter [gardenhose](https://dev.twitter.com/streaming/reference/get/statuses/sample) service.
Connects to stream and collects data on tweets recieved, including statistics on emoji, hashtags, urls, and pictures in 
tweets.
Written in Python3. 

Installation
------------
```bash
    git clone http://github.com/ccarlile
    pip install emoji TwitterAPI
```
And edit `twitter.py` with your API information or pass it when running with 
`python twitter.py access_token_secret=YOURACCESSTOKEN...`.

Usage
-----
The client will start up automatically and start scraping and parsing. Answer 
the prompt with a 'y' to recieve info.
