# -*- coding:utf-8 -*-
"""Supported by minghu6 package"""

from subprocess import Popen, PIPE
import codecs
import locale
from functools import partial
import inspect
import os


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
    p.wait()

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


def path_to(from_path:str, to_path:str):
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
