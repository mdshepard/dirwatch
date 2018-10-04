import signal
import logging
import argparse
import time
import os
import sys

# my ol' sloppy logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handle_file = logging.FileHandler('test.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logger.addHandler(handle_file)
exit_flag = False

file_dict = {}
global file_path


def handle_signal(sig, stack):
    logger.warning("Got signal: {}".format(sig))
    global exit_flag
    if sig == signal.SIGINT:
        exit_flag = True
    if sig == signal.SIGTERM:
        exit_flag = True


def find_magic(file, directory):
    """checks for magic word"""
    magic_word = 'wizard'
    with open(directory) as f:
        for i, line in enumerate(f.readlines()):
            if magic_word in line and i not in file_dict[file]:
                logger.info('{} found at line {} in {}'
                            .format(magic_word, i + 1, file))
                file_dict[file].append(i)


def watch_directory(dir):
    path = ""
    directory = path.join([os.path.relpath(os.getcwd), "/", dir])
    print "setting the path to {1} where we'll search for files".format(
        directory)

    watched_files = [f for f in os.listdir(directory) if ".txt" in f]

    if len(watched_files) > len(file_dict):
        for file in watched_files:
            if file not in file_dict:
                logger.info(' {} found in {}'.format(file, dir))
                file_dict[file] = []
    elif len(watched_files) < len(file_dict):
        for file in file_dict:
            if file not in watched_files:
                logger.info(" removed {} from {}".format(file, dir))
                file_dict.pop(file, None)
    for file in watched_files:
        find_magic(file, directory)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Watches a directory of text files for a magic string"
        )

    parser.add_argument(
        '-e', '--ext', type=str, default='.txt',
        help="Text file extension to watch e.g. .txt .log"
        )

    parser.add_argument(
        '-i', '--interval', type=int, default=4,
        help="How often the directory is to be watched in seconds."
    )

    parser.add_argument(
        'dir', help="Directory to watch", type=str,
    )

    return parser


def main(args):

    parser = create_parser()

    start_time = time.time()

    args = parser.parse_args(args)

    logger.info('Searching the following directory: {}'.format(args.dir))
    print "starting program..."

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while not exit_flag:
        time.sleep(args.interval)
        logger.info(
            "Starting main while loop in {} seconds".format(args.interval)
        )
        try:
            watch_directory(dir)
        except IOError:
            logger.exception('no directory? aint nobody got time for that!')
            print "Error,\ can't find directory"
            time.sleep(args.interval)

        except Exception:
            logger.exception('unknown exception')
            time.sleep(args.interval)
    logger.info('time running: {} seconds'.format(time.time() - start_time))


if __name__ == '__main__':
    main(sys.argv[1:])
