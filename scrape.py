import praw
import pandas as pd


global badWordsSet
global subredditsList

def createArrays():
    global badWordsSet
    global subredditsList
    badWordsText = open("./badWords.txt", "r")
    badWordsSet = set(badWordsText.read().split('\n'))

    subredditsText = open("./subreddits.txt", "r")
    subredditsList = subredditsText.read().split('\n')
    
    
    
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
                print(comment.body)
                commentCounter+=1

                commentWordArray = comment.body.split()
                for word in commentWordArray:
                    if word in bad_words:
                        profanityCounter+=1
                        
                        break  

                comment_queue.extend(comment.replies)

        result[subredditName]=(commentCounter,profanityCounter)        
    return result
    

reddit_read_only = praw.Reddit(client_id="jHaMZuAi8kiEX9erg6yH_w",         # your client id
                               client_secret="QS6aK093s1gRBjt6XvW6RQ4dSXaySA",      # your client secret
                               user_agent="True")        # your user agent
 
 





createArrays()

print(search(subredditsList, badWordsSet, reddit_read_only))

print(badWordsSet)


""""
subreddit = reddit_read_only.subreddit("redditdev")
 
# Display the name of the Subreddit
print("Display Name:", subreddit.display_name)
 
# Display the title of the Subreddit
print("Title:", subreddit.title)
 
# Display the description of the Subreddit
print("Description:", subreddit.description)
"""""