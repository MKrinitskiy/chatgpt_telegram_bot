import sys
import traceback
import datetime


def ReportException(err_fname = None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if err_fname is None:
        print('================ ' + str(datetime.datetime.now()) + ' ================\n')
        traceback.print_tb(exc_traceback, limit=None, file=None)
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=None)
        print('\n\n\n')
    else:
        with open(err_fname, 'a') as errf:
            errf.write('================ ' + str(datetime.datetime.now()) + ' ================\n')
            traceback.print_tb(exc_traceback, limit=None, file=errf)
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=errf)
            errf.write('\n\n\n')


def LogMessage(log_fname = None, text = ''):
    if log_fname is None:
        print('================ ' + str(datetime.datetime.now()) + ' ================\n')
        print(text)
        print('\n\n\n')
    else:
        with open(log_fname, 'a') as logf:
            logf.write('================ ' + str(datetime.datetime.now()) + ' ================\n')
            logf.write(text)
            logf.write('\n\n\n')