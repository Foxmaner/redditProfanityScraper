import praw
import pandas as pd
from progress.bar import Bar
from progress.spinner import Spinner



def create_bad_words_set():
    with open("./badWords.txt", "r") as f:
        bad_words_set = set(f.read().split('\n'))
    return bad_words_set

def create_subreddits_list():
    with open("./subreddits.txt", "r") as f:
        subreddits_list = f.read().split('\n')
    return subreddits_list
    
    
    
def search(subredditArray, bad_words, reddit_read_only) -> int:
    result = {}
    
    for subredditName in subredditArray:
        commentCounter = 0
        profanityCounter = 0
        subreddit = reddit_read_only.subreddit(subredditName)    
        for post in subreddit.top(time_filter="year", limit=1):
            
            post.comments.replace_more(limit=20)
            comment_queue = post.comments[:]  # Seed with top-level
            while comment_queue:
                comment = comment_queue.pop(0)
                commentCounter+=1
                commentWordArray = comment.body.split()
                for word in commentWordArray:
                    if word in bad_words:
                        profanityCounter+=1
                        break  

                comment_queue.extend(comment.replies)
        result[subredditName]=(commentCounter,profanityCounter)        
    return result
    

def main():
    reddit_read_only = praw.Reddit(
        client_id="jHaMZuAi8kiEX9erg6yH_w",              # your client id
        client_secret="QS6aK093s1gRBjt6XvW6RQ4dSXaySA",     # your client secret
        user_agent="True")                                  # your user agent

    subredditsList = create_subreddits_list()
    badWordsSet = create_bad_words_set()
    print(search(subredditsList, badWordsSet, reddit_read_only))


if __name__ == "__main__":
    main()