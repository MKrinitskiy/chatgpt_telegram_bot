import sys
import os
import traceback
from datetime import datetime
import collections
import fnmatch
import pathlib


def ReportException(err_fname = None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if err_fname is None:
        print('================ ' + str(datetime.now()) + ' ================\n')
        traceback.print_tb(exc_traceback, limit=None, file=None)
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=None)
        print('\n\n\n')
    else:
        with open(err_fname, 'a') as errf:
            errf.write('================ ' + str(datetime.now()) + ' ================\n')
            traceback.print_tb(exc_traceback, limit=None, file=errf)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=errf)
            errf.write('\n\n\n')


def LogMessage(log_fname = None, text = ''):
    if log_fname is None:
        print('================ ' + str(datetime.now()) + ' ================\n')
        print(text)
        print('\n\n\n')
    else:
        with open(log_fname, 'a') as logf:
            logf.write('================ ' + str(datetime.now()) + ' ================\n')
            logf.write(text)
            logf.write('\n\n\n')


def find_files(directory, pattern):
    import os, fnmatch
    flist = []
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                filename = filename.replace('\\', '/')
                flist.append(filename)
    return flist

def find_directories(directory, pattern=None, maxdepth=None):
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            if pattern is None:
                retname = os.path.join(root, d, '')
                yield retname
            elif fnmatch.fnmatch(d, pattern):
                retname = os.path.join(root, d, '')
                retname = retname.replace('\\\\', os.sep)
                if maxdepth is None:
                    yield retname
                else:
                    if retname.count(os.sep)-directory.count(os.sep) <= maxdepth:
                        yield retname

def DoesPathExistAndIsDirectory(pathStr):
    if os.path.exists(pathStr) and os.path.isdir(pathStr):
        return True
    else:
        return False


def DoesPathExistAndIsFile(pathStr):
    if os.path.exists(pathStr) and os.path.isfile(pathStr):
        return True
    else:
        return False


def EnsureDirectoryExists(pathStr):
    if not DoesPathExistAndIsDirectory(pathStr):
        try:
            # os.mkdir(pathStr)
            pathlib.Path(pathStr).mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            err_fname = './errors.log'
            exc_type, exc_value, exc_traceback = sys.exc_info()
            with open(err_fname, 'a') as errf:
                traceback.print_tb(exc_traceback, limit=None, file=errf)
                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=errf)
            print(str(ex))
            print('the directory you are trying to place a file to doesn\'t exist and cannot be created:\n%s' % pathStr)
            raise FileNotFoundError('the directory you are trying to place a file to doesn\'t exist and cannot be created:')


def isSequence(obj):
    if isinstance(obj, str):
        return False
    return isinstance(obj, collections.Sequence)