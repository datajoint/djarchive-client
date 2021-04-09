#! /usr/bin/env python

import os
import sys
import logging

from textwrap import dedent
from code import interact
from collections import ChainMap

import datajoint as dj

from djarchive_client import client


log = logging.getLogger(__name__)


def usage_exit():
    print(dedent(
        '''
        usage: {} cmd args

        where 'cmd' is one of:

        {}
        ''').lstrip().rstrip().format(
            os.path.basename(sys.argv[0]),
            str().join("  - {}:{}{}{}".format(
                k, os.linesep,
                dedent(v[1]).replace(os.linesep, '{}    '.format(os.linesep)),
                os.linesep)
                       for k, v in actions.items())), end=(os.linesep * 2))

    sys.exit(0)


def logsetup(*args):
    level_map = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }
    level = level_map[args[0]] if args else logging.INFO

    logfile = dj.config.get('custom', {'logfile': None}).get('logfile', None)

    if logfile:
        handlers = [logging.StreamHandler(), logging.FileHandler(logfile)]
    else:
        handlers = [logging.StreamHandler()]

    datefmt = '%Y-%m-%d %H:%M:%S'
    msgfmt = '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(message)s'

    logging.basicConfig(format=msgfmt, datefmt=datefmt, level=logging.ERROR,
                        handlers=handlers)

    log.setLevel(level)

    logging.getLogger('djarchive_client').setLevel(level)


def datasets(*args):
    for d in client().datasets():
        print('{}'.format(d))


def revisions(*args):
    for d in client().revisions(*args):
        print('{},{}'.format(*d))


def download(*args):
    if len(args) != 3:
        raise TypeError('download dataset revision target_directory')

    client().download(*args, create_target=True)


def shell(*args):
    interact('djarchive shell', local=dict(ChainMap(locals(), globals())))


actions = {
    'datasets': (datasets,
                 '''
                 datasets:

                 list available datasets
                 '''),
    'revisions': (revisions,
                  '''
                  revisions [dataset]:

                  list revisions for dataset if given.
                  if dataset is not given, list all datasets+revisions.
                  '''),
    'download': (download,
                 '''
                 download dataset revision target_directory:

                 Retreive dataset into top-level of target_directory.

                 If target_directory does not exist, djarchive will attempt
                 to create it prior to downloading the dataset.
                 '''),
    'shell': (shell,
              '''
              shell:

              start an interactive shell
              ''')
}

if __name__ == '__main__':

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        usage_exit()

    logsetup(
        os.environ.get('DJARCHIVE_LOGLEVEL',
                       dj.config.get('loglevel', 'INFO')))

    action = sys.argv[1]
    actions[action][0](*sys.argv[2:])
