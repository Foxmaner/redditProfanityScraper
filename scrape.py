import praw
import threading
import time
import matplotlib.pyplot as plt
from progress.bar import Bar
from progress.spinner import MoonSpinner
import numpy as np

result = {}
subreddit_profanity_dict = {}
#Change this depending on what subreddit categori you wanna run
subredditFile = "Alternative Reddits To League"

def create_bad_words_set():
    with open("./badWords.txt", "r") as f:
        bad_words_set = set(f.read().split('\n'))
    return bad_words_set

def create_subreddits_list():
    path = "./subreddits/" + subredditFile  + ".txt"
    with open(path, "r") as f:
        subreddits_list = f.read().split('\n')
    return subreddits_list
    
    
    
def search(subredditName, bad_words, reddit_read_only) -> int:
    global result
    global subreddit_profanity_dict
    
    profanity_dict = {}
    commentCounter = 0
    profanityCounter = 0
    subreddit = reddit_read_only.subreddit(subredditName)    
    for post in subreddit.hot(limit=10):
            
        post.comments.replace_more(limit=None)
        comment_queue = post.comments[:]  # Seed with top-level
        while comment_queue:
            comment = comment_queue.pop(0)
            commentCounter+=1
            commentWordArray = comment.body.split()
            for word in commentWordArray:
                if word in bad_words:
                    profanityCounter+=1
                    if word not in profanity_dict:
                        profanity_dict[word] = 1
                    else:
                        profanity_dict[word] += 1
                    break  
            comment_queue.extend(comment.replies)
   
    subreddit_profanity_dict[subredditName] = profanity_dict
    result[subredditName]=(commentCounter, profanityCounter, str(int((profanityCounter/commentCounter)*100)) + "%")
    #print(result)      
    
    

def checkThread(thread, spinner):
    
    while(thread.is_alive()):
        #print("T is alive:", t1.is_alive())
        #print("T is alive:", t2.is_alive())
        spinner.next()
        time.sleep(1)
    spinner.finish()

"""
def graph(subredditName, commentCounter, profanityCounter, percentage):
   
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
    #plt.clf()"""
    
def generate_bar_graph():
    global result
    # Sort the lists based on percentages in reverse order
    result = dict(sorted(result.items(), key=lambda x: float(x[1][2].strip('%'))))

    commentCounter = []
    profanityCounter = []
    percentages = []
    labels = []
    for key, value in result.items():
        labels.append(key)
        commentCounter.append(value[0])
        profanityCounter.append(value[1])
        percentages.append(value[2])

    #print(percentages)

    # Bar graph
    x = np.arange(len(labels))
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, commentCounter, width, label='Comments')
    rects2 = ax.bar(x + width/2, profanityCounter, width, label='Profanity')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Amount')
    #ax.set_xlabel('Subreddit')
    ax.set_title(subredditFile)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend()

    # Add the percentage values to the plot
    for i, percentage in enumerate(percentages):
        plt.text(i, 1, f"{percentage}", ha='center', va='bottom', fontsize=15)


    fig.tight_layout()
    print("saves!")
    plt.savefig('graphs/{}.pdf'.format(subredditFile))
    #plt.show()


def save_result():
    # Open the file in write mode
    with open(f'./result/{subredditFile}.txt', 'w') as file:
        # Loop through the first dictionary
        for key, value in result.items():
            # Write the key-value pair to the file in a formatted string
            file.write(f"{key}: {value}\n")

        # Write a newline character to the file
        file.write("\n")

        # Loop through the second dictionary
        for key, value in subreddit_profanity_dict.items():
            # Write the key to the file
            file.write(f"{key}:\n")

            # Loop through the nested dictionary
            for nested_key, nested_value in value.items():
                # Write the nested key-value pair to the file in a formatted string
                file.write(f"\t{nested_key}: {nested_value}\n")

            # Write a newline character to the file
            file.write("\n")

def main():
    reddit_read_only = praw.Reddit(
        client_id="",              # your client id
        client_secret="",     # your client secret
        user_agent="True")                                  # your user agent

    badWordsSet = create_bad_words_set()
    sub_folder = ["Alternative Reddits To League", "Childrens Games", "FPS Games", "MMORPG Games", "Moba Games", "Mobile Games", "Most Popular Games", \
                  "No Gaming Related", "Single Player Games", "Strategy Games", "Survival Games"]
    global subredditFile

    for sub in sub_folder:
        global result
        result = {}
        global subreddit_profanity_dict
        subreddit_profanity_dict = {}
        subredditFile = sub
        subredditsList = create_subreddits_list()

        #init values
        i = 1
        threads = []
        statusThreads = []
        for subreddit in subredditsList:
            
            t = threading.Thread(target=search, args=(subreddit, badWordsSet, reddit_read_only))
            status_thread = threading.Thread(target=checkThread, args=([t, MoonSpinner("Thread nr " + str(i) + ": ")]))

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


    
        print(result)
        print(subreddit_profanity_dict)
        save_result()
        generate_bar_graph()
        
        print("Program complete!")


if __name__ == "__main__":
    main()