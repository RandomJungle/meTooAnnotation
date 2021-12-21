import json
import os


def read_corpus_generator(data_path: str):
    for file_name in os.listdir(data_path):
        with open(os.path.join(data_path, file_name), 'r') as data_file:
            for entry in data_file.readlines():
                yield json.loads(entry)


def read_file_generator(file_path: str):
    with open(file_path, 'r') as data_file:
        for entry in data_file.readlines():
            yield json.loads(entry)