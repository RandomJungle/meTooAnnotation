import json

from flask import Flask, render_template, request
from multiprocessing import Value

from annotator.annotate import reverse_label
from utils.annotation_keys import TESTIMONY
from utils.file_utils import read_tweet_from_path_and_index
from utils.paths import INPUT_DATA_FILE, OUTPUT_DATA_FILE

counter = Value('i', 0)
app = Flask(__name__)
stored_data = []


@app.route('/', methods=['GET', 'POST'])
def index():

    done_ids = extract_done_ids_from_output_file(OUTPUT_DATA_FILE)
    tweet = read_tweet_from_path_and_index(INPUT_DATA_FILE, counter.value)

    # Listen for user input on saving data
    if request.method == "POST":
        if request.form['submit_button'] == 'save':
            write_entries_to_file(OUTPUT_DATA_FILE, stored_data)
            stored_data.clear()

    # read through file to find tweet not already done
    while tweet and tweet.get('id') in done_ids:
        counter.value += 1
        tweet = read_tweet_from_path_and_index(INPUT_DATA_FILE, counter.value)

    # variable for the progress bar
    len_progress_bar = calculate_progress_bar(INPUT_DATA_FILE)

    # end of file reached
    if not tweet:
        return render_template(
            'end.html',
            end_of_file_message="Good job !"
        )

    # all info about the tweet
    label = TESTIMONY
    tweet_id = tweet.get('id')
    tweet_text = tweet.get('text')
    tweet_english_text = tweet.get('english_text')

    # user input in one of the three action buttons
    if request.method == "POST":
        if request.form['submit_button'] in ['accept', 'reject', 'pass']:
            if request.form['submit_button'] == 'accept':
                tweet.update({'label': label})
            elif request.form['submit_button'] == 'reject':
                tweet.update({'label': reverse_label(label)})
            elif request.form['submit_button'] == 'pass':
                tweet.update({'flag': 'problematic'})
            stored_data.append(tweet)
            with counter.get_lock():
                counter.value += 1
                out = counter.value
            tweet = read_tweet_from_path_and_index(INPUT_DATA_FILE, out)
            if not tweet:
                return render_template(
                    'end.html',
                    end_of_file_message="Good job !"
                )
            return render_template(
                'base.html',
                tweet_id=tweet.get('id'),
                tweet_text=tweet.get('text'),
                tweet_english_text=tweet.get('english_text'),
                label=label,
                index_progress=out,
                progress_bar=len_progress_bar
            )

        elif request.form['submit_button'] == "revert":
            if counter.value != 0:
                if stored_data:
                    stored_data.pop(-1)
                    with counter.get_lock():
                        counter.value -= 1
                        out = counter.value
                    tweet = read_tweet_from_path_and_index(INPUT_DATA_FILE, out)
                    return render_template(
                        'base.html',
                        tweet_id=tweet.get('id'),
                        tweet_text=tweet.get('text'),
                        tweet_english_text=tweet.get('english_text'),
                        label=label,
                        index_progress=out,
                        progress_bar=len_progress_bar
                    )

    return render_template(
        'base.html',
        tweet_id=tweet_id,
        tweet_text=tweet_text,
        tweet_english_text=tweet_english_text,
        label=label,
        index_progress=counter.value,
        progress_bar=len_progress_bar
    )


def calculate_progress_bar(file_path):
    with open(file_path, 'r') as input_file:
        return len(input_file.readlines())


def write_entries_to_file(file_path, buffer):
    with open(file_path, 'a') as output_file:
        for tweet in buffer:
            output_file.write(json.dumps(tweet) + "\n")


def extract_done_ids_from_output_file(file_path):
    done_ids = []
    with open(file_path, 'r') as output_file:
        for line in output_file.readlines():
            done_ids.append(json.loads(line).get('id'))
    return done_ids
