#!/usr/bin/python3

from api import Learn
from getpass import getpass
import os
import json
import time
import urllib.request
import argparse

TOKEN_ROTTEN_TIME = 3000
TOKEN_FILENAME = "./token.json"


def pathify(course, section, file, root="."):
    return os.path.join(root, course.strip(), section.strip(), file.strip())


def get_saved_token():
    try:
        if os.path.getmtime(TOKEN_FILENAME) + TOKEN_ROTTEN_TIME > time.time():
            with open(TOKEN_FILENAME, 'r') as token_file:
                return json.load(token_file)['token']
        else:
            return None

    except FileNotFoundError:
        return None


def save_token(token):
    # Modify JSON file. Taken from https://stackoverflow.com/a/21035861
    with open(TOKEN_FILENAME, 'w') as token_file:
        data = {
            "token": token
        }

        json.dump(data, token_file, indent=4)


def is_new(filepath, filesize):
    if not os.path.exists(filepath):
        return True

    if os.path.getsize(filepath) != filesize:
        print("{} failed size check. local:{} vs remote:{}".format(filepath, os.path.getsize(filepath), filesize))
        return True

    return False


def download(src, dst):
    directory = os.path.dirname(dst)
    os.makedirs(directory, exist_ok=True)

    urllib.request.urlretrieve(src, dst)


def main(args):
    username = args['user']
    learn = None

    if args['use_token']:
        token = get_saved_token()
        if token:
            learn = Learn(token=token)

    if not learn:
        if not username:
            username = input("Username: ")

        password = getpass("Password: ")

        learn = Learn(username, password)
        save_token(learn.token)

    download_count = 0
    update_count = 0

    for file in learn.all_files():
        course = file['course_name']
        section = file['section_name']
        filename = file['filename']
        filesize = file['filesize']

        file_ext = os.path.splitext(filename)[1][1:]  # cut off preceding '.'

        if "ignore" in args and file_ext in args['ignore']:
            continue  # Skip this file


        if "only" in args and file_ext not in args["only"]:
            continue  # Skip

        filepath = pathify(course, section, filename, root=args['directory'])

        if filesize > 0 and is_new(filepath, filesize):
            download(file['url'], filepath)
            download_count += 1
            print("Downloaded {0}".format(filename))
        else:
            update_count += 1

    if download_count > 0:
        print("{} files downloaded".format(download_count))
    elif update_count > 0:
        print("{} files verified".format(update_count))
    else:
        print("Nothing to do")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download files off Learn")
    parser.add_argument('directory',
                        default='learn',
                        nargs="?",
                        help='The target directory to place files')
    parser.add_argument('--user', '-u',
                        metavar="abc12",
                        required=False,
                        type=str,
                        help='Learn username')
    parser.add_argument('--refresh-token',
                        action='store_false',
                        dest="refresh_token",
                        help="Don't use cached token. Login with username and password and refresh it.")
    parser.add_argument('--ignore', '-i',
                        metavar="ext,ext",
                        help="Download all files except ones ending with these file extentions. Comma Sepearated.")
    parser.add_argument('--only',
                        metavar="ext,ext",
                        help="Only download files with this file extention. Comma seperated.")
    parsed_args = parser.parse_args()
    args = {
        "user": parsed_args.user,
        "directory": parsed_args.directory,
        "use_token": parsed_args.refresh_token,
    }

    if parsed_args.ignore:
        args['ignore'] = parsed_args.ignore.split(',')
    if parsed_args.only:
        args['only'] = parsed_args.only.split(',')
    main(args)
