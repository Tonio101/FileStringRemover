#!/usr/bin/env python3
import argparse
import functools
import os
import re
import sys

PATTERNS_FILE = os.path.dirname(os.path.abspath(__file__)) \
    + '/data/patterns.conf'

SUBTITLE_MAP = dict(
    English=".en.srt",
    Spanish=".es.srt",
)

SUPPORTED_SUBTITLES = dict(
    English=False,
    Spanish=False
)

SUPPORTED_FILE_TYPES = ['.mp4', '.mkv']


def get_path_and_file_patterns(args):
    if (not args):
        print("Invalid argument")
        sys.exit(2)

    if (not args.path):
        print("Must provide a path")
        sys.exit(2)

    if (args.strip):
        return (os.path.abspath(args.path), [args.strip])

    return (os.path.abspath(args.path), get_patterns())


def get_patterns():
    patterns = {
        'regex': [],
        'direct': [],
        'subtitle': []
    }

    with open(PATTERNS_FILE) as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("/") and line.endswith("/"):
                p = line.lstrip("/").rstrip("/")
                patterns['regex'].append(re.compile(p))
            elif line.startswith("SUBTITLE:"):
                p = line.split(":")[1].lstrip("/").rstrip("/")
                patterns['subtitle'].append(re.compile(p))
            else:
                patterns['direct'].append(line)

        return patterns


def find_str(patterns, fname):

    # Check regex patterns first
    for regex in patterns['regex']:
        r = regex.findall(fname)
        if (r):
            return r[0]

    for direct in patterns['direct']:
        if direct in fname:
            return direct

    return None


def rename_file_name(fpath, strip_str, fname, force=False, replace_str=""):
    new_fname = fname.replace(strip_str, replace_str)
    old_file = fpath + '/' + fname
    new_file = fpath + '/' + new_fname

    print("Old Name: {0}\nNew Name: {1}\n".format(old_file, new_file))

    response = ''
    if (not force):
        response = input(("Would you like to proceed with renaming"
                          " the files displayed above? [y/n] "))
    else:
        response = 'y'

    if (response == 'y'):
        os.rename(old_file, new_file)
    elif (response == 'n'):
        exit(0)
    else:
        print("Not a valid response")
        exit(2)

    return new_file


def compare(e0, e1):
    if e0[:2] < e1[:2]:
        return -1
    elif e0[:2] > e1[:2]:
        return 1
    else:
        return 0


def rename_subtile_files(fpath, new_fname, list_of_fnames, patterns):
    # TODO - Make this a bit more generic. Right now I only
    #        care about English and Spanish subtitles
    # found_en_sub = False
    # found_es_sub = False

    # Pick the smallest number subtitle.
    # Sometimes there are 2 files for the same language.
    sorted_list = sorted(list_of_fnames, key=functools.cmp_to_key(compare))
    for fname in sorted_list:
        for pattern in patterns['subtitle']:
            r = pattern.findall(fname)
            if (r):

                for type, found in SUPPORTED_SUBTITLES.items():
                    if not found and type in fname:
                        file_type = SUBTITLE_MAP[type]
                        curr_subtitle_fname = fpath + "/" + r[0]
                        new_subtile_fname = None

                        for ext in SUPPORTED_FILE_TYPES:
                            if ext in new_fname:
                                new_subtile_fname = \
                                    new_fname.replace(ext, file_type, 1)

                        print(curr_subtitle_fname)
                        print(new_subtile_fname)
                        if new_subtile_fname:
                            os.rename(curr_subtitle_fname, new_subtile_fname)
                            SUPPORTED_SUBTITLES[type] = True

                # if not found_en_sub and "English" in fname:
                #    file_type = SUBTITLE_MAP["English"]
                #    curr_subtitle_fname = fpath + "/" + r[0]
                #    new_subtile_fname = None

                #    for ext in SUPPORTED_FILE_TYPES:
                #        if ext in new_fname:
                #            new_subtile_fname = \
                #                new_fname.replace(ext, file_type, 1)

                #    print(curr_subtitle_fname)
                #    print(new_subtile_fname)
                #    if new_subtile_fname:
                #        os.rename(curr_subtitle_fname, new_subtile_fname)
                #        found_en_sub = True
                # elif not found_es_sub and "Spanish" in fname:
                #    file_type = SUBTITLE_MAP["Spanish"]
                #    curr_subtitle_fname = fpath + "/" + r[0]
                #    new_subtile_fname = None

                #    for ext in SUPPORTED_FILE_TYPES:
                #        if ext in new_fname:
                #            new_subtile_fname = \
                #                new_fname.replace(ext, file_type, 1)

                #    print(curr_subtitle_fname)
                #    print(new_subtile_fname)
                #    if new_subtile_fname:
                #        os.rename(curr_subtitle_fname, new_subtile_fname)
                #        found_es_sub = True


def remove_string_from_files(fpath, patterns, force=False, replace_str=""):
    if (not os.path.exists(fpath)):
        print("{0} path does not exist".format(fpath))
        exit(2)

    list_of_fnames = os.listdir(fpath)
    for fname in list_of_fnames:
        strip_str = find_str(patterns, fname)
        if (strip_str):
            print(strip_str)
            new_fname = \
                rename_file_name(fpath, strip_str, fname, force, replace_str)
            rename_subtile_files(fpath, new_fname, list_of_fnames, patterns)


def delete_left_over_subtitle_files(fpath, patterns, force=False):
    if (not os.path.exists(fpath)):
        print("{0} path does not exist".format(fpath))
        exit(2)

    list_of_fnames = os.listdir(fpath)
    for fname in list_of_fnames:
        for pattern in patterns['subtitle']:
            r = pattern.findall(fname)
            if r:
                print("Delete: {} ".format(
                    (fpath + "/" + fname)
                ))
                if force:
                    os.remove(fpath + "/" + fname)


def delete_unused_files(fpath, patterns, force=False):
    delete_left_over_subtitle_files(fpath, patterns, force)


def main(argv):
    usage = '{FILE} --path=torrents/GoT/Season1/'
    usage = usage.format(FILE=argv[0])
    description = 'Remove patterns from file(s)'
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-p", "--path",
                        help="path to the location of the files.",
                        required=True)
    parser.add_argument("-s", "--strip",
                        help="string to remove from files.",
                        required=False)
    parser.add_argument("-r", "--replace",
                        help="string replacement.",
                        required=False)
    parser.add_argument("-f", "--force", action='store_true',
                        help="strip string without approval.", required=False)
    args = parser.parse_args()

    (files_path, file_patterns) = get_path_and_file_patterns(args)

    remove_string_from_files(fpath=files_path, patterns=file_patterns,
                             force=True if args.force else False,
                             replace_str=args.replace if args.replace else "")

    delete_unused_files(fpath=files_path, patterns=file_patterns,
                        force=True if args.force else False)


if __name__ == '__main__':
    main(sys.argv)
