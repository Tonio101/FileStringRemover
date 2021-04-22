#!/usr/bin/env python3

import argparse
import os
import sys
import time
import yaml

DATA_FILE=os.path.dirname(os.path.abspath(__file__)) + '/data/RemoveStrings.yaml'

def get_path_and_strip_string(args):
    if (not args):
        print("Invalid argument")
        sys.exit(2)
    
    if (not args.path):
        print("Must provide a path")
        sys.exit(2)

    if (args.strip):
        return (os.path.abspath(args.path), [args.strip])

    return (os.path.abspath(args.path), get_strings_from_file())

def get_strings_from_file():
    list_of_strings = []

    with open(DATA_FILE) as file:
        documents = yaml.full_load(file)

        for item, doc in documents.items():
            list_of_strings.append(doc)

        file.close()

        return list_of_strings

    return list_of_strings

def find_str(strip_strs, fname):
    if (len(strip_strs) == 2):
        movie_strip_strs = strip_strs[0]
        tv_shows_strip_strs = strip_strs[1]

        for movie_strip_str in movie_strip_strs:
            if (movie_strip_str in fname):
                return movie_strip_str

        for tv_shows_strip_str in tv_shows_strip_strs:
            if (tv_shows_strip_str in fname):
                return tv_shows_strip_str

    elif (strip_strs[0] in fname):
        return strip_strs[0]

    return None

def rename_file_name(fpath, strip_str, fname, force=False, replace_str=""):
    new_fname = fname.replace(strip_str, replace_str)
    old_file = fpath + '/' + fname
    new_file = fpath + '/' + new_fname

    print("Old Name: {0}\nNew Name: {1}\n".format(old_file, new_file))

    response = ''
    if (not force):
        response = input("Would you like to proceed with renaming the files displayed above? [y/n] ")
    else:
        response = 'y'

    if (response == 'y'):
        os.rename(old_file, new_file)
    elif (response == 'n'):
        exit(0)
    else:
        print("Not a valid response")
        exit(2)

def remove_string_from_files(fpath, strip_strs, force=False, replace_str=""):
    if (not os.path.exists(fpath)):
        print("{0} path does not exist".format(fpath))
        exit(2)

    list_of_fnames = os.listdir(fpath)

    for fname in list_of_fnames:
        strip_str = find_str(strip_strs, fname)
        if (strip_str):
            rename_file_name(fpath, strip_str, fname, force, replace_str)

def main(argv):
    usage = '{FILE} --strip="some_text" --path=torrents/GoT/Season1/'
    usage = usage.format(FILE=argv[0])
    description = 'Remove some string from file(s) located under the specified directory'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-p", "--path", help="path to the location of the files.", required=True)
    parser.add_argument("-s", "--strip", help="string to remove from files.", required=False)
    parser.add_argument("-r", "--replace", help="string replacement.", required=False)
    parser.add_argument("-f", "--force", action='store_true', help="strip string without approval.", required=False)
    args = parser.parse_args()

    (files_path, strip_strings) = get_path_and_strip_string(args)

    remove_string_from_files(fpath=files_path, strip_strs=strip_strings,
            force=True if args.force else False,
            replace_str= args.replace if args.replace else "")

if __name__ == '__main__':
    main(sys.argv)
