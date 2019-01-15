#!/usr/bin/env python2
__author__ = 'mdshepard'
"""
Dirwatcher. Long running program that watches for txt files within a directory,
and scans the text files for occurances of a "magic" word, defined in the
command line, and upon new lines being added to the file(s), checks them as
they're created.
"""
import signal
import logging
import argparse
import time
import os
import sys

logger = logging.getLogger(__file__)
exit_flag = False
file_dict = {}


def setup_logger():
    """
    sets up our logger, which will provide input in the terminal as the program
    runs
    """
    fmt = '%(asctime)s:%(levelname)s:%(message)s'
    logging.basicConfig(format=fmt, level=logging.DEBUG)


def signal_handler(sig, stack):
    """
    Signal handler receives runtime errors and terminates the program.
    """
    logger.warning("Got signal: {}".format(sig))
    global exit_flag
    exit_flag = True


def find_magic(file, directory, magic_word):
    """checks for magic word within the current file, line by line"""
    full_path = os.path.join(directory, file)
    start_line = file_dict[file]
    with open(full_path) as f:
        i = -1
        for i, line in enumerate(f):
            if i >= start_line and magic_word in line:
                logger.info('{} found at line {} in {}'
                            .format(magic_word, i + 1, full_path))
        file_dict[file] = i + 1


def watch_directory(dir, ext, magic_word):
    """
    specifies the directory being searched, the file extension of the files
    within the directory with .txt as default, and the magic word to find
    within the text in the files.
    """
    directory = os.path.abspath(dir)

    watched_files = [f for f in os.listdir(directory) if f.endswith(ext)]

    if len(watched_files) > len(file_dict):
        for file in watched_files:
            if file not in file_dict:
                logger.info('new file {} found in {}'.format(file, dir))
                file_dict[file] = 0
    elif len(watched_files) < len(file_dict):
        for file in list(file_dict):
            # we're iterating over a copy of the keys of the file_dict, so we
            # can pop the keys in the dictionary without triggering
            # a runtime error. That way we can delete files in dir and the
            # program still runs. List creates the copy.
            if file not in watched_files:
                logger.info(" removed {} from {}".format(file, dir))
                file_dict.pop(file, None)
    for file in watched_files:
        find_magic(file, directory, magic_word)
        pass


def create_parser():
    """
    creates our command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string"
        )

    parser.add_argument(
        '-e', '--ext', type=str, default='.txt',
        help="Text file extension to watch e.g. .txt .log"
        )

    parser.add_argument(
        '-i', '--interval', type=int, default=2,
        help="How often the directory is to be watched in seconds."
    )

    parser.add_argument(
        'dir', help="Directory to watch", type=str,
    )

    parser.add_argument(
        'magic', help="magic word we're searching for", type=str,
    )

    return parser


def main(args):
    """
    le main function. Where the while loop that maintains the long running
    nature of the program resides.
    """

    setup_logger()

    parser = create_parser()

    start_time = time.time()

    arg_namespace = parser.parse_args(args)

    logger.info('Searching the following directory: {}'.format(
        arg_namespace.dir)
    )
    logger.info("starting {}...".format(__name__))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(
        "Polling of directory every {} seconds".format(
            arg_namespace.interval)
        )
    while not exit_flag:
        time.sleep(arg_namespace.interval)

        try:
            watch_directory(
                arg_namespace.dir, arg_namespace.ext, arg_namespace.magic
                )
        except OSError:
            logger.error("Error, not found: {}".format(
                arg_namespace.dir)
            )
        except Exception as e:
            logger.error("Unhandled exception:{}".format(e))

    logger.info('polling completed, uptime: {0:.1f} seconds'.format(
        time.time() - start_time)
    )


if __name__ == '__main__':
    main(sys.argv[1:])
