import os
from collections import Counter
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import praw
import seaborn as sns
# Lemmatizer helps to reduce words to the base form
from nltk.stem import WordNetLemmatizer
# This allows to create individual objects from a bog of words
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

CSV_PATH_FILE = os.path.join(os.path.dirname(__file__), "csv_files")
TXT_PATH_FILE = os.path.join(os.path.dirname(__file__), "text_files")
IMG_PATH_FILE = os.path.join(os.path.dirname(__file__), "img_files")
# attempt to remove 'u' from plots
stopwords_personalized = nltk.corpus.stopwords.words('english')
new_stopwords = ['u','/u']
stopwords_personalized.extend(new_stopwords)


def write_txt_files(all_posts, dict_key):
    print("-----------WRITING TEXT")

    if dict_key == "post_id":
        with open(os.path.join(TXT_PATH_FILE, f"{dict_key}_all.txt"), "a") as f:
            for post in all_posts:
                f.write(post["post_id"] + "\n")
    else:
        # Create a new list for each key, title or text in a post
        text_list = list()
        for post in all_posts:
            text_list.append(post[dict_key].replace("\n", " "))
        # joins all the sentences
        text_joined = " ".join(text_list)
        with open(os.path.join(TXT_PATH_FILE, f"{dict_key}_all.txt"), "a") as f:
            f.write(text_joined)


def read_txt_file(filename):
    print("-----------READING TEXT")
    with open(os.path.join(TXT_PATH_FILE, f"{filename}_all.txt"), "r") as f:
        text = f.read()
        return text


def extract_posts(subreddit_name):
    all_posts = list()

    reddit = praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
        username=os.environ["REDDIT_USERNAME"],
    )
    posts_id_text = read_txt_file("post_id")
    posts_revised = posts_id_text.split("\n")
    posts_revised = list(filter(None, posts_revised))

    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.hot(limit=10):
        if submission.id not in posts_revised:
            titles = submission.title
            text = submission.selftext
            scores = submission.score
            url = submission.url

            post_preview = {
                "post_id": str(submission.id),
                "post_title": str(titles),
                "post_text": str(text),
                "post_score": str(scores),
                "post_url": str(url),
            }
            all_posts.append(post_preview)

    write_txt_files(all_posts, "post_id")
    write_txt_files(all_posts, "post_title")
    write_txt_files(all_posts, "post_text")


def word_freq(filename):
    text = read_txt_file(filename)
    # creates tokens, creates lower class, removes numbers and lemmatizes the words
    new_tokens = word_tokenize(text)
    new_tokens = [t.lower() for t in new_tokens]
    # attempt to remove 'u' from plots
    new_tokens = [t for t in new_tokens if t not in stopwords_personalized]
    new_tokens = [t for t in new_tokens if t.isalpha() and len(t) >= 2]

    lemmatizer = WordNetLemmatizer()
    new_tokens = [lemmatizer.lemmatize(t) for t in new_tokens]
    counted = Counter(new_tokens)
    word_counter_df = pd.DataFrame(
        counted.items(), columns=[f"words_in_{filename}", "frequency"]
    ).sort_values(by="frequency", ascending=False)

    print(word_counter_df)
    word_counter_df.to_csv(
        os.path.join(CSV_PATH_FILE, f"{filename}.csv"),
        encoding="utf-8-sig",
        index=False,
    )
    return word_counter_df


def create_graph(df):
    fig, axes = plt.subplots()
    fig.suptitle("Data taken from r/Ghoststories")  # or plt.suptitle('Main title')
    if "words_in_post_title" in list(df.columns):
        sns.barplot(x="frequency", y="words_in_post_title", data=df.head(25))
    else:
        sns.barplot(x="frequency", y="words_in_post_text", data=df.head(25))
    plt.savefig(
        os.path.join(IMG_PATH_FILE, f"{axes.get_ylabel()}.png"),
        bbox_inches="tight",
        dpi=150,
    )
    plt.close()


def create_wordcloud(filename):
    text = read_txt_file(filename)
    wordcloud = WordCloud(colormap = 'ocean', background_color ='gold', min_font_size = 10).generate(text)
    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(
        os.path.join(IMG_PATH_FILE, f"wordcloud_{filename}.png"),
        bbox_inches="tight"
    )
    plt.close()


if __name__ == "__main__":
    extract_posts("Ghoststories")
    df_post_title = word_freq("post_title")
    df_post_text = word_freq("post_text")
    create_graph(df_post_title)
    create_graph(df_post_text)
    create_wordcloud("post_title")
    create_wordcloud("post_text")
