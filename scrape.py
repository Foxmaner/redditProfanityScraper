import praw
import threading
import time
import matplotlib.pyplot as plt
from progress.bar import Bar
from progress.spinner import MoonSpinner
import numpy as np

result = {}

def create_bad_words_set():
    with open("./badWords.txt", "r") as f:
        bad_words_set = set(f.read().split('\n'))
    return bad_words_set

def create_subreddits_list():
    with open("./subreddits.txt", "r") as f:
        subreddits_list = f.read().split('\n')
    return subreddits_list
    
    
    
def search(subredditName, bad_words, reddit_read_only) -> int:
    global result
    
    
    commentCounter = 0
    profanityCounter = 0
    subreddit = reddit_read_only.subreddit(subredditName)    
    for post in subreddit.top(time_filter="year", limit=5):
            
        post.comments.replace_more(limit=5)
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
    result[subredditName]=(commentCounter, profanityCounter, str(int((profanityCounter/commentCounter)*100)) + "%")
    #graph(subredditName, commentCounter, profanityCounter)
    #print(result)      
    

def checkThread(thread, threadNr, spinner):
    
    while(thread.is_alive()):
        #print("T is alive:", t1.is_alive())
        #print("T is alive:", t2.is_alive())
        spinner.next()
        time.sleep(1)
    spinner.finish()


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

def graph(subredditName, commentCounter, profanityCounter, percentage):

    # line graph
    """
    plt.plot(commentCounter, profanityCounter, color='red', label='Profanity', linewidth=2, linestyle='-')
    plt.plot(commentCounter, commentCounter, color='blue', label='Comments', linewidth=2, linestyle='-')
    plt.xlabel('Amount of comments', fontsize=14)
    plt.ylabel('Amount of profanity', fontsize=14)
    plt.title(subredditName, fontsize=16)
    plt.grid(True)
    plt.legend(fontsize=12)
    # Add the percentage value to the plot
    plt.text(0.95, 0.95, f"Profanity percentage: {percentage}", ha='right', va='top', transform=plt.gca().transAxes)
    plt.savefig(f'graphs/line/{subredditName}.pdf')
    #clear
    #plt.clf()"""

   
    # Pie chart
    labels = ['Comments without profanity', 'Amount of profanity']
    sizes = [commentCounter, profanityCounter]
    colors = ['yellowgreen', 'gold']
    total = sum(sizes)
    plt.pie(sizes, labels=labels, colors=colors,
            autopct=lambda x: f"{int(round(x * total / 100.0))}", startangle=140)
    plt.axis('equal')
    plt.title(subredditName, fontsize=16)
    plt.tight_layout()
    # Add the percentage value to the plot
    plt.text(0.28, 1, f"Profanity percentage: {percentage}", ha='right', va='top', transform=plt.gca().transAxes)
    plt.savefig(f'graphs/pie/{subredditName}.pdf')
    plt.show()
    #clear
    plt.clf()
    
def generate_bar_graph():
    commentCounter = []
    profanityCounter = []
    percentages = []
    labels = []
    for key, value in result.items():
        labels.append(key)
        commentCounter.append(value[0])
        profanityCounter.append(value[1])
        percentages.append(value[2])

    # Bar graph
    x = np.arange(len(labels))
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, commentCounter, width, label='Comments')
    rects2 = ax.bar(x + width/2, profanityCounter, width, label='Profanity')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Amount')
    ax.set_xlabel('Subreddit')
    ax.set_title('Profanity and Comments per Subreddit')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # Add the percentage values to the plot
    for i, percentage in enumerate(percentages):
        plt.text(i, 0.5, f"Profanity percentage: {percentage}", ha='center', va='top')

    fig.tight_layout()
    plt.show()


def main():
    reddit_read_only = praw.Reddit(
        client_id="jHaMZuAi8kiEX9erg6yH_w",              # your client id
        client_secret="QS6aK093s1gRBjt6XvW6RQ4dSXaySA",     # your client secret
        user_agent="True")                                  # your user agent

    subredditsList = create_subreddits_list()
    badWordsSet = create_bad_words_set()
    #print(search(subredditsList, badWordsSet, reddit_read_only))

    #graph("test", 20, 10, "50%")

    #init values
    i = 0
    threads = []
    statusThreads = []
    for subreddit in subredditsList:
        

        t = threading.Thread(target=search, args=(subreddit, badWordsSet, reddit_read_only))
        status_thread = threading.Thread(target=checkThread, args=([t, i, MoonSpinner("Thread nr " + str(i) + ": ")]))

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

    
    
    #get_data("AskReddit", "new", 10, reddit_read_only)
    #get_data("AskReddit", "hot", 10, reddit_read_only)
    #get_data("AskReddit", "top", 10, reddit_read_only)
    #get_data("AskReddit", "controversial", 10, reddit_read_only)
    #get_data("AskReddit", "random", 10, reddit_read_only)
   
    print(result)

    #for key, value in result.items():
    #    graph(key, value[0], value[1], value[2])
    generate_bar_graph()
    
    print("Program complete!")


if __name__ == "__main__":
    main()