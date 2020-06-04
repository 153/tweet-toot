import helpers
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def getTweets(twitter_nametopull, mastodon_secret, mastodon_host):
    """ Get list of tweets, with tweet ID and content, from configured Twitter account URL.

    This function relies on BeautifulSoup to extract the tweet IDs and content of all tweets on the specified page.

    The data is returned as a list of dictionaries that can be used by other functions.
    """

    all_tweets = []
    tweet_count_max = 1 	# set me yes

    # old way from config.json file url = helpers._config('tweets.source_account_url')
    url = twitter_nametopull    

    if not url:

        helpers._error('getTweets() => The source Twitter account URL (' + url + ') was incorrect. Could not retrieve tweets.')

        return False

    headers = {}
    headers['accept-language'] = 'en-US,en;q=0.9'
    headers['dnt'] = '1'
    headers['user-agent'] = helpers._config('gen.APP_NAME')


    # Getting users timeline pulling...
    data = requests.get(url)

    html = BeautifulSoup(data.text, 'html.parser')

    timeline = html.select('#timeline li.stream-item')

    if timeline is None:

        helpers._error('getTweets() => Could not retrieve tweets from the page. Please make sure the source Twitter account URL (' + url + ') is correct.')

        return False

    helpers._info('getTweets() => Fetched tweets for ' + url + '.')

    tweet_count_loop = 0
    tweet_error = 0

    for tweet in timeline:
        # print(tweet)    
        tweet_skip =0
        if (tweet_error == 0) and (tweet_count_loop <= (tweet_count_max)): #NOTE: tweet_count_max would be tweet_count_max MINUS 1 if you wanted to do it normally but we want the top 2 tweets in case the top one was PINNED as is a twitter feature and we would want to skip it
                tweet_count_loop = tweet_count_loop + 1
                # print(tweet)
                tweet_id = tweet['data-item-id']
                # suposed to let you dup post as Mastodon will reject if header same twice.... headers['Idempotency-Key'] = tweet_id

                tweet_text = []
                retweet_text = []
                tweet_url = []
                tweet_datetimestamp = []

                tweet_url=url + '/status/' + tweet_id
		
                try:
                   tweet_ispinned=retweet_text=tweet.select('span.js-pinned-text')[0].get_text()
                   helpers._info('getTweets() => This tweet is a pinned tweet. Skipping')
                except:
                   tweet_ispinned=[]

                if (tweet_ispinned):
                   tweet_skip =1

                try:

       	            tweet_text = tweet.select('p.tweet-text')[0].get_text()
                    # tweet_datetimestamp = tweet.select('a.tweet-timestamp')[0].get_text()
                    tweet_datetimestamp = tweet.select('a.tweet-timestamp')[0]
                    tweet_datetimestamp=tweet_datetimestamp['title']
                    # print(tweet)
                    
                    try:
                       # Only using to identify in the below ifthen since the tweet text seems to be the same. Not best way but too many scraping variables to keep track of.
                       retweet_text=tweet.select('span.js-retweet-text')[0].get_text()
                       retweet_text_itself=tweet.select('span.js-retweet-text')[0].get_text()                  
                       # we are here. not pullnig I think .... retweet_originaltweeter=tweet.select('div.data-screen-name')[0].get_text()                  
                    except:
                       retweet_text=[]
                       retweet_text_itself=[]

                    if retweet_text:

                            tweet_text = retweet_text_itself.strip()+':\n '+tweet_text.strip()

                            helpers._info('getTweets() => Is Retweet!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

                            #helpers._info('getTweets() =>' + retweet_text)                            
       	        except:
           	
       	            helpers._info('getTweets() => No tweet text found. Moving on...')

       	            continue

                # cleanup if good tweet
                if tweet_text:
                        tweet_text=tweet_text.replace('<a href', ' \n<a href') # should be regex this is sloppy in case they already had a space. Doesnt seem to be using this one either. Already stripped it appears
                        tweet_text=tweet_text.replace('pic.twitter.com', ' \nhttps://pic.twitter.com') # should be regex this is sloppy
                        tweet_text=tweet_text.replace('http', ' \nhttp') # should be regex this is sloppy in case they already had a space.
                        # change up a specific tweet if you want tweet_text=tweet_text.replace('reassuring.','reassuring. (BOT REPOST)')
                        helpers._info('getTweets() => =============================' + tweet['data-item-id'] + '\n\n')
#                        tweet_text = tweet_text + ' \n\nSource: ' + tweet_url + ' ' + tweet_datetimestamp
#                        tweet_text = tweet_text + '\n\nEND==================\n\nMy other bots: https://pastebin.com/yuwXfDjZ'
                        helpers._info('getTweets() => TWEET TEXT--> ' + tweet_text)
                if (tweet_error == 0) and (tweet_skip == 0):    
       	                all_tweets.append({"id": tweet_id, "text": tweet_text})
                else:
	                helpers._info('getTweets() => Not adding tweet: Either exists and error or exists and Skipping on purpose')

    return all_tweets if len(all_tweets) > 0 else None


def tootTheTweet(tweet, mastodon_secret, mastodon_host):
    """ Receieve a dictionary containing Tweet ID and text... and TOOT!

    This function relies on the requests library to post the content to your Mastodon account (human or bot).

    A boolean success status is returned.

    Arguments:
        tweet {dictionary} -- Dictionary containing the "id" and "text" of a single tweet.
    """

    # old way using config.json host_instance = helpers._config('toots.host_instance')
    # old way using config.json token = helpers._config('toots.app_secure_token')

    host_instance = mastodon_host
    token = mastodon_secret

    tweet_id = tweet['id']

    if not host_instance:

        helpers._error('tootTheTweet() => Your host Mastodon instance URL (' + host_instance + ') was incorrect.')

        return False

    if not token:

        helpers._error('tootTheTweet() => Your Mastodon access token was incorrect.')

        return False  

    headers = {}
    headers['Authorization'] = 'Bearer ' + token
    headers['Idempotency-Key'] = tweet_id

    data = {}
    data['status'] = tweet['text']
    data['visibility'] = 'public'

    tweet_check_file_path = helpers._config('toots.cache_path') + tweet['id']
    tweet_check_file = Path(tweet_check_file_path)

    if tweet_check_file.is_file():

        helpers._info('tootTheTweet() => TWEET STATUS--> Tweet ' + tweet_id + ' was already posted. Taking no action.')

        return False

    else:

        tweet['text'].encode('utf-8')
        
        tweet_check = open(tweet_check_file_path, mode='w')
        tweet_check.write(tweet['text'])
        tweet_check.close()

        helpers._info('tootTheTweet() => New tweet ' + tweet_id + ' => "' + tweet['text'] + '".')

        response = requests.post(
        url=host_instance + '/api/v1/statuses', data=data, headers=headers)

    # Cleanup before return --- just not firing for some reason strange
    helpers._info('tootTheTweet() => /============================' + tweet['id'] + '\n\n')

    if response.status_code == 200:

        helpers._info('tootTheTweet() => OK. Posted tweet ' + tweet_id + 'to Mastodon.')
        helpers._info('tootTheTweet() => Response: ' + response.text)

        return True

    else:

        helpers._info('tootTheTweet() => FAIL. Could not post tweet ' + tweet_id + 'to Mastodon.')
        helpers._info('tootTheTweet() => Response: ' + response.text)

        return False


