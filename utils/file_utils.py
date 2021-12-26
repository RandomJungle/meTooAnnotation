import json
import os
from typing import Dict, List


def read_corpus_generator(data_path: str):
    for file_name in os.listdir(data_path):
        with open(os.path.join(data_path, file_name), 'r') as data_file:
            for entry in data_file.readlines():
                yield file_name, json.loads(entry)


def read_file_generator(file_path: str):
    with open(file_path, 'r') as data_file:
        for entry in data_file.readlines():
            yield json.loads(entry)


def save_tweet_label(file_path: str, tweet: Dict, label: str):
    tweet.update({'category': label})
    with open(file_path, 'a') as data_file:
        data_file.write(json.dumps(tweet))


def read_tweet_from_path_and_index(file_path: str, index: int):
    with open(file_path, 'r') as data_file:
        lines = data_file.readlines()
        if index > len(lines)-1:
            return 0
        return json.loads(lines[index])
