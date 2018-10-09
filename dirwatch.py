import signal
import logging
import argparse
import time
import os
import sys

# my ol' sloppy logger
logger = logging.getLogger(__name__)


def setup_logger():
    fmt = '%(asctime)s:%(levelname)s:%(message)s'
    # formatter = logging.Formatter(fmt)
    logging.basicConfig(format=fmt, level=logging.DEBUG)
    file_handler = logging.FileHandler('dirwatch.log')
    logger.addHandler(file_handler)


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
    with open(os.path.join(directory, file)) as f:
        for i, line in enumerate(f):
            if i <= file_dict[file]:
                continue
            if magic_word in line:
                logger.info('{} found at line {} in {}'
                            .format(magic_word, i + 1, file))
        file_dict[file] = i


def watch_directory(dir, ext):
    # path = ""
    directory = os.path.abspath(dir)
    # logger.info("setting the path to {0} where we'll search for files".format(
    #     directory)
    # )

    watched_files = [f for f in os.listdir(directory) if f.endswith(ext)]

    if len(watched_files) > len(file_dict):
        for file in watched_files:
            if file not in file_dict:
                logger.info(' {} found in {}'.format(file, dir))
                file_dict[file] = 0
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
        '-i', '--interval', type=int, default=2,
        help="How often the directory is to be watched in seconds."
    )

    parser.add_argument(
        'dir', help="Directory to watch", type=str,
    )

    return parser


def main(args):

    setup_logger()

    parser = create_parser()

    start_time = time.time()

    arg_namespace = parser.parse_args(args)

    logger.info('Searching the following directory: {}'.format(
        arg_namespace.dir)
    )
    logger.info("starting {}...".format(__name__))

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info(
        "Polling of directory every {} seconds".format(
            arg_namespace.interval)
        )
    while not exit_flag:
        time.sleep(arg_namespace.interval)

        try:
            watch_directory(arg_namespace.dir, arg_namespace.ext)
        except IOError:
            logger.exception('no directory? aint nobody got time for that!')
            logger.error("Error, not found: {}".format(
                arg_namespace.dir)
            )
        except Exception:
            logger.exception('unknown exception')
    logger.info('polling completed, uptime: {0:.1f} seconds'.format(
        time.time() - start_time)
    )


if __name__ == '__main__':
    main(sys.argv[1:])
