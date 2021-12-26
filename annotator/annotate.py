import os

import spacy

from utils.annotation_keys import TESTIMONY, NOT_TESTIMONY
from utils.file_utils import read_corpus_generator, save_tweet_label
from utils.paths import TRANSLATED_DATA_PATH, ANNOTATED_DATA_PATH


def annotate(data_path: str, output_path: str):
    done_ids = [tweet.get('id') for tweet in read_corpus_generator(output_path)]
    nlp = spacy.load("ja_core_news_trf")
    for file_name, tweet in read_corpus_generator(data_path):
        if tweet.get('id') not in done_ids:
            doc = nlp(tweet.get('text'))
            english_text = tweet.get('english_text')
            label = doc.cats.get(TESTIMONY)
            output_file = os.path.join(output_path, file_name)
            if label:
                if get_user_validation(doc, label, english_text):
                    save_tweet_label(output_file, tweet, label)
                else:
                    new_label = reverse_label(label)
                    save_tweet_label(output_file, tweet, new_label)
            else:
                label = ask_user_label(doc, english_text)
                save_tweet_label(output_file, tweet, label)


def get_user_validation(doc, label, english_text=None):
    print("\n" + ("-" * 80) + "\n\n")
    print(doc.text + "\n\n")
    print("LABEL " + ("-" * 10) + ">" + f"{label}" + "\n\n")
    if english_text:
        print(f"ENGLISH VERSION : {english_text}\n\n")
    label = input("is this the right label ? Y/y = YES, any other key = NO : ")
    if label == "y" or label == "Y":
        return True
    else:
        return False


def ask_user_label(doc, english_text=None):
    print("\n" + ("-" * 80) + "\n\n")
    print(doc.text + "\n\n")
    if english_text:
        print(f"ENGLISH VERSION : {english_text}\n\n")
    label = input("define LABEL of text : T/t = TESTIMONY, any other key = NOT_TESTIMONY : ")
    if label == "T" or label == "t":
        return TESTIMONY
    else:
        return NOT_TESTIMONY


def reverse_label(label: str):
    if label == TESTIMONY:
        return NOT_TESTIMONY
    elif label == NOT_TESTIMONY:
        return TESTIMONY
    else:
        return label


if __name__ == "__main__":
    annotate(TRANSLATED_DATA_PATH, ANNOTATED_DATA_PATH)
