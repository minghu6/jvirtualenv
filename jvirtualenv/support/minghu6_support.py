# -*- coding:utf-8 -*-
"""Supported by minghu6 package"""

from threading import Thread
from subprocess import Popen, PIPE
import codecs
import locale
import platform
import ctypes
from functools import partial
import inspect
import os
import sys


# minghu6.algs.decorator.handle_exception
def handle_excpetion(exception_handler, exception_classes):
    """
    An exception handling idiom using decorators
    Specify exceptions in order, first one is handled first
    last one last.
    >>> def handler(ex):
    ...     print(ex, type(ex))
    ...     return ex.args
    >>> from collections import OrderedDict
    >>> @handle_excpetion(handler, Exception)
    ... def f():
    ...     d=OrderedDict()
    ...     d['a']=1
    ...     d['b']=2
    ...     raise Exception([1, 2, '3'], d)
    >>> f()
    ([1, 2, '3'], OrderedDict([('a', 1), ('b', 2)])) <class 'Exception'>
    ([1, 2, '3'], OrderedDict([('a', 1), ('b', 2)]))
    >>> @handle_excpetion(handler, (FileExistsError, FileNotFoundError))
    ... def f2():
    ...     raise FileNotFoundError('abc.txt')
    >>> f2()
    abc.txt <class 'FileNotFoundError'>
    ('abc.txt',)
    """

    def wrapper(func):
        nonlocal exception_classes

        if inspect.isclass(exception_classes):
            exception_classes = [exception_classes]

        exception_chain = list(exception_classes)
        exception_chain.reverse()  # for recursive invokation

        def newfunc(exception_chain, *args, **kwargs):  # recursion
            exception_class = exception_chain[0]

            try:
                if len(exception_chain) == 1:
                    result = func(*args, **kwargs)
                else:
                    result = newfunc(exception_chain[1:], *args, **kwargs)  # spread exception
            except exception_class as ex:
                return exception_handler(ex)
            else:
                return result

        return partial(newfunc, exception_chain)

    return wrapper


def get_locale_codec():
    return codecs.lookup(locale.getpreferredencoding()).name


# minghu6.etc.cmd.exec_cmd
def exec_cmd(cmd, shell=True):
    """
    only can be used in shell
    :param cmd:" " or []
    :param shell: default True
    :return: [str1,str2,...]
    """

    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell)

    stdout_data, stderr_data = p.communicate()

    codec = get_locale_codec()

    try:
        stdout_data = stdout_data.decode(codec, errors='ignore')
        stderr_data = stderr_data.decode(codec, errors='ignore')
    except UnicodeDecodeError:
        codec = 'utf-8'
        stdout_data = stdout_data.decode(codec, errors='ignore')
        stderr_data = stderr_data.decode(codec, errors='ignore')

    finally:
        info, err = stdout_data.split(os.linesep), stderr_data.split(os.linesep)

    return info, err


def chain_apply(funcs, var):
    """apply func from funcs[0] to funcs[-1]"""
    for func in funcs:
        var = func(var)

    return var


def path_level(path):
    """
    >>> path_level('/home/john')
    2
    >>> path_level('/home/john/')
    3
    """

    def _path_level(path, n=0):
        dir_path = os.path.dirname(path)
        if path == dir_path:
            return n
        else:
            n += 1
            return _path_level(dir_path, n)

    return _path_level(path)


def path_to(from_path: str, to_path: str):
    """
    >>> path_to('/home/john/coding', '/home/alice/Download')
    '../../alice/Download'
    """
    from_path = os.path.abspath(from_path)
    to_path = os.path.abspath(to_path)

    common_path = os.path.commonpath([from_path, to_path])

    from_extra_path = from_path.split(common_path)[1]
    to_extra_path = to_path.split(common_path)[1]

    parpath = os.sep.join([os.pardir] * path_level(from_extra_path))

    if parpath:
        target_path = parpath + to_extra_path
    else:
        target_path = os.curdir + to_extra_path

    return target_path


def get_home_dir():
    return os.path.expanduser('~')


def iswin():
    return platform.platform().upper().startswith('WIN')


def get_drivers():
    if not iswin():
        raise OSError('only support in Windows')
    
    lp_buffer = ctypes.create_string_buffer(78)
    ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lp_buffer), lp_buffer)
    drivers = lp_buffer.raw.split(b'\x00')
    
    return [each_driver.decode()[:2] for each_driver in drivers if each_driver and os.path.isdir(each_driver)]


try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


class CommandRunner(object):
    """Inspired by https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python"""
    ON_POSIX = 'posix' in sys.builtin_module_names
    
    @classmethod
    def _enqueue_output(cls, process, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        
        process.terminate()
    
    @classmethod
    def run(cls, cmd):
        
        p = Popen('{cmd} && exit'.format(cmd=cmd), stdout=PIPE, stderr=PIPE, bufsize=1,
                  close_fds=CommandRunner.ON_POSIX, shell=True)
        q = Queue()
        t_stdout = Thread(target=CommandRunner._enqueue_output, name='{cmd} fetch stdout'.format(cmd=cmd),
                          args=(p, p.stdout, q), daemon=True)
        t_stderr = Thread(target=CommandRunner._enqueue_output, name='{cmd} fetch stderr'.format(cmd=cmd),
                          args=(p, p.stderr, q), daemon=True)
        
        t_stdout.start()
        t_stderr.start()
        
        # read line without blocking
        codec = get_locale_codec()
        while p.returncode is None:
            try:
                line = q.get(timeout=.1)
                line = line.strip().decode(codec, errors='ignore')
            except Empty:
                pass
            else:  # got line
                yield line


def isiterable(obj, but_str_bytes=True):
    """
    :param obj:
    :param but_str_bytes: most of time, we don't need str and bytes
    :return:
    """
    from collections import Iterable
    if but_str_bytes and isinstance(obj, (str, bytes, bytearray)):
        return False
    else:
        return isinstance(obj, Iterable)


def find_wrapper(start_dir, pattern):
    if not isiterable(pattern):
        pattern = [pattern]
    
    command_runner = CommandRunner()
    if iswin():
        cmd = 'where /R "{start_dir}" {pattern}'.format(start_dir=start_dir, pattern=' '.join(pattern))
    else:
        cmd = 'find {start_dir} {pattern}'.format(
            start_dir=start_dir,
            pattern=' '.join(['-name "%s"' % each_pattern for each_pattern in pattern])
        )
    
    for line in command_runner.run(cmd):
        if os.path.exists(line):
            yield line


def get_drivers():
    if not iswin():
        raise OSError('only support in Windows')
    
    lp_buffer = ctypes.create_string_buffer(78)
    ctypes.windll.kernel32.GetLogicalDriveStringsA(ctypes.sizeof(lp_buffer), lp_buffer)
    drivers = lp_buffer.raw.split(b'\x00')
    
    return [each_driver.decode()[:2] for each_driver in drivers if each_driver and os.path.isdir(each_driver)]
