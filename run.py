import encodings.idna
import helpers
import social
import sys


def runME(twitter_nametopull, mastodon_secret, mastodon_host):

    """  

    This function will get a new Tweet from the configured Twitter account and publish to the configured Mastodon instance.
    It will only toot once per invokation to avoid flooding the instance.
    """
    
    try:
        twitter_nametopull = "https://www.twitter.com/" + twitter_nametopull
    except:
        print("Syntax: twitter_nametopull mastodon_secret mastodon_host No action taken. Exiting.")	
        sys.exit()

    print(twitter_nametopull)
    print(mastodon_secret)
    print(mastodon_host)

    if (twitter_nametopull) and (mastodon_secret) and (mastodon_host):

        tweets = social.getTweets(twitter_nametopull, mastodon_secret, mastodon_host)
    
        if not tweets:
    
            helpers._error(
                '__main__ => No tweets fetched.')
    
            sys.exit()
    
        helpers._info('__main__ => ' + str(len(tweets)) + ' tweets fetched.')
    
        for tweet in tweets:
            toot_status = "No Attempt Yet"
            if social.tootTheTweet(tweet, mastodon_secret, mastodon_host):
    
                helpers._info('__main__ => Tooted "' + tweet['text'] + '"')
                helpers._info(
                    '__main__ => Tooting less is tooting more. Sleeping...')
    
                toot_status = "Success"
                #   070519 sys.exit()
            else:
                toot_status = ""
            # helpers._info('__main__ => /============================' + tweet['id'] + '\n\n')
    else:
        print("Syntax: twitter_nametopull mastodon_secret mastodon_host No action taken. Exiting.")
        toot_status = "No Attempt Made. Likely an error in you not sending in all three variables. Exiting."
    return(toot_status)
