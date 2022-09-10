import logging
import os
import sqlite3
import string
from datetime import datetime
from os.path import exists
from random import choice

from flask import Flask, request, jsonify
from time import perf_counter_ns as timer

# Database schema to store url --> short_url relations
db_schema = """
CREATE TABLE urls (
    original_url TEXT NOT NULL,
    short_url TEXT NOT NULL
);
"""


# Initialize the Flask app and the logging system
app = Flask(__name__)
if not exists('logs'):
    os.makedirs("logs")
if not exists('db'):
    os.makedirs("db")
logging.basicConfig(filename="logs/" + datetime.today().strftime('%Y%m%d') + "_url_shortener.log",
                    level=logging.DEBUG,
                    format="%(asctime)s %(message)s",
                    force=True)


# Idea brought from https://python.plainenglish.io/create-a-url-shortener-with-flask-47d08c23a695
def generate_short_id(num_of_chars: int):
    """Function to generate short_id of a specified number of characters
    :num_of_chars: length of the generated short id
    """
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(num_of_chars))


def get_db_connection():
    """
    Create the database if it does not exist and return a connection to it
    :return: db connection
    """
    if not exists('db/database.db'):
        connection = sqlite3.connect('db/database.db')
        connection.executescript(db_schema)
        connection.execute("CREATE INDEX short_urls_idx ON urls (short_url);")
        connection.commit()
        connection.close()

    conn = sqlite3.connect('db/database.db')
    return conn


def bad_request(message):
    """
    Generates a HttpResponse with code 400 (bad request) with the given message
    :message: Message containing the error description
    :return: HttpResponse with the given message and code 400.
    """
    response = jsonify({'message': message})
    response.status_code = 400
    return response


@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    """
    POST endpoint. Expects a json object containing an "url" property.
    Validates the existence of the json and the property, and gets the
    property value as the original url to shorten. Checks if the URL has
    already been shortened (by looking for it in the DB, and if not,
    generates a shortened URL and stores both in the DB. Finally, returns
    the short URL version.
    :return: HttpResponse with an error if the URL to shorten could not
    be retrieved from the JSON, or a 201 code and the resulting shortened
    URL in a property called "shortened_url" in a JSON object
    """
    try:
        start = timer()
        if not request.is_json:
            logging.error("[shorten_url] Url must be provided in json format.")
            return bad_request('Url must be provided in json format.')

        if 'url' not in request.json:
            logging.error(f"[shorten_url] Url parameter not found. Json received: {request.json}")
            return bad_request('Url parameter not found.')

        url = request.json['url']
        logging.debug(f"[shorten_url] Received url: {url}")

        if url:
            conn = get_db_connection()
            shortened_url = conn.execute('SELECT short_url FROM urls WHERE original_url = (?)', (url,)).fetchone()

            if not shortened_url:
                logging.debug(f"[shorten_url] Short url for {url} not found in DB")
                hashid = generate_short_id(8)
                shortened_url = request.host_url + hashid

                conn.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (url, hashid))
            else:
                shortened_url = request.host_url + shortened_url[0]
                logging.debug(f"[shorten_url] Short url for {url} found in DB")

            conn.commit()
            conn.close()

            logging.info(f"[shorten_url] Short url for {url}: {shortened_url}")
            end = timer()
            logging.debug(f"Short url generated in {str(end - start)} nanoseconds")
            return jsonify({'shortened_url': shortened_url}), 201
        else:
            logging.error(f"[shorten_url] Url empty. Json received: {request.json}")
            return bad_request('Url empty.')
    except Exception as e:
        logging.error(f"Exception raised while generating the short URL: {e}")
        return "Unexpected error generating the short URL", 500


@app.route('/shorten_url', methods=['GET'])
def shorten_url_get():
    """GET endpoint. Present to warn the users that the POST option should be used.
    :return: HttpResponse with code 400
    """
    logging.error("[shorten_url] Received GET call")
    return bad_request('Must use POST.')


@app.route('/<short_url>', methods=['GET'])
def get_original_url(short_url):
    """GET endpoint. Takes a shortened_url code and returns the original URL in a
    JSON object if successful.
    :short_url: shortened_url code
    :return: JSON object with the original URL corresponding to the shortened code
    in a property called "original_url".
    """
    try:
        start = timer()
        logging.debug(f"[get_original_url] Received petition to get original URL from {short_url}")
        conn = get_db_connection()
        original_url = conn.execute('SELECT original_url FROM urls'
                                    ' WHERE short_url = (?)', (short_url,)
                                    ).fetchone()

        if not original_url:
            logging.error(f"[get_original_url] Short URL {short_url} not found in DB")
            return '', 204

        original_url = original_url[0]
        logging.info(f"[get_original_url] Original url for {short_url}: {original_url}")
        end = timer()
        logging.debug(f"Short url generated in {str(end - start)} nanoseconds")
        return jsonify({'original_url': original_url}), 200
    except Exception as e:
        logging.error(f"Exception raised while retrieving the original URL: {e}")
        return "Unexpected error retrieving the original URL", 500


if __name__ == '__main__':
    app.run(debug=True)