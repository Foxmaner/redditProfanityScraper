import praw
import pandas as pd
from progress.bar import Bar
from progress.spinner import MoonSpinner
import threading
import time



def create_bad_words_set():
    with open("./badWords.txt", "r") as f:
        bad_words_set = set(f.read().split('\n'))
    return bad_words_set

def create_subreddits_list():
    with open("./subreddits.txt", "r") as f:
        subreddits_list = f.read().split('\n')
    return subreddits_list
    
    
    
def search(subredditName, bad_words, reddit_read_only) -> int:
    result = {}
    
    
    commentCounter = 0
    profanityCounter = 0
    subreddit = reddit_read_only.subreddit(subredditName)    
    for post in subreddit.top(time_filter="year", limit=5):
            
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
    result[subredditName]=(commentCounter,profanityCounter,str(int((profanityCounter/commentCounter)*100)) + "%")  
    print(result)      
    #return result

def checkThread(thread, threadNr, spinner):
    
    while(thread.is_alive()):
        #print("T is alive:", t1.is_alive())
        #print("T is alive:", t2.is_alive())
        spinner.next()
        time.sleep(1)
    spinner.finish()
    return

"""
def get_data(subreddit_name, sort_type, limit, reddit):
    subreddit = reddit.subreddit(subreddit_name)
    if sort_type == "new":
        posts = subreddit.new(limit=limit)
        comments = subreddit.comments(sort=sort_type, limit=limit)
    elif sort_type == "hot":
        posts = subreddit.hot(limit=limit)
        comments = subreddit.comments(sort=sort_type, limit=limit)
    elif sort_type == "top":
        posts = subreddit.top(limit=limit)
        comments = subreddit.comments(sort=sort_type, limit=limit)
    elif sort_type == "controversial":
        posts = subreddit.controversial(limit=limit)
        comments = subreddit.comments(sort=sort_type, limit=limit)
    elif sort_type == "random":
        posts = subreddit.random_rising(limit=limit)
        comments = subreddit.comments(limit=limit)
    else:
        print("Invalid sort type")
        return

    for post in posts:
        print(post.title)
    for comment in comments:
        print(comment.body)
"""



def main():
    reddit_read_only = praw.Reddit(
        client_id="jHaMZuAi8kiEX9erg6yH_w",              # your client id
        client_secret="QS6aK093s1gRBjt6XvW6RQ4dSXaySA",     # your client secret
        user_agent="True")                                  # your user agent

    subredditsList = create_subreddits_list()
    badWordsSet = create_bad_words_set()
    #print(search(subredditsList, badWordsSet, reddit_read_only))
    
    #init values
    i = 0
    threads = []
    statusThreads = []
    for subreddit in subredditsList:
        

        t = threading.Thread(target=search, args=(subreddit, badWordsSet, reddit_read_only))
        status_thread = threading.Thread(target=checkThread,args=([t,i, MoonSpinner("Thread nr " + str(i) + ": ")]))

        threads.append(t)
        statusThreads.append(status_thread)
        
        t.start()
        status_thread.start()

        i +=1

    #close all threads 
    for t in threads:
        t.join()
    for t in statusThreads:
        t.join()    

    
    """
    get_data("AskReddit", "new", 10, reddit_read_only)
    get_data("AskReddit", "hot", 10, reddit_read_only)
    get_data("AskReddit", "top", 10, reddit_read_only)
    get_data("AskReddit", "controversial", 10, reddit_read_only)
    get_data("AskReddit", "random", 10, reddit_read_only)
    """
 
    
    print("Program complete!")


if __name__ == "__main__":
    main()