# -*- coding:utf-8 -*-
"""Java Virtual Env
virtualenv for java JDK
jdk pattern: .*/java/jdk[^/]

Usage:
  jvirtualenv list-tag [-g]
  jvirtualenv --java=<tag> <project> [-g] [-f]
  jvirtualenv reinit-tag [-g]

Options:
  list-tag         list all the optional tag
  -j --java=<tag>  point a jdk to use
  reinit-tag       reinit the java version config
  -g --global      global mode, need sudo
  -f --force       force to create java virtual env in a existed folder

"""


import os
import re
from distutils.version import LooseVersion
import json
from collections import OrderedDict
from functools import partial

from sh import locate
from color import color
from docopt import docopt

from jvirtualenv.support.minghu6_support import exec_cmd, handle_excpetion, chain_apply, path_to
from jvirtualenv.template.activate_template import template as activate_template

__version__ = '0.0.1'
JAVA_PATTERN = '^.*/java/jdk[^/]*/bin/java$'


class GetVersionFailedError(Exception):
    pass


class GetJavaVersionFailedError(GetVersionFailedError):
    pass


class DirectoryConflicsError(Exception):
    """The first arg of the exception should be conflicted directory path"""
    pass


def _step_parent_dir(path, n=1):
    if n > 0:
        n -= 1
        path = os.path.dirname(path)
        return _step_parent_dir(path, n)

    return path


def get_java_version(java_path='java'):
    cmd = '{0} -version'.format(java_path)
    _, err = exec_cmd(cmd)  # It's confused that java -version outputstreram is stderr otherthan stdout

    try:
        version_s = re.split(r'\s+', err[0])[-1][1:-1]
        version = LooseVersion(version_s)

        match = re.match(r'\d+', re.split(r'\s+', err[2])[2])
        bit = match.group(0)
    except Exception as ex:
        raise GetJavaVersionFailedError from ex

    return version, bit


def build_version_infos():
    version_infos = []

    for item in locate('-A', '-r', JAVA_PATTERN):
        java_path = item.__str__().strip()
        version, bit = get_java_version(java_path)

        version_info = OrderedDict()
        if version.version[0] == 9:
            version_info['tag'] = version.vstring
        else:
            version_info['tag'] = '{0}.{1}:{2}:{3}'.format(*version.version[:3], bit)

        version_info['version'] = version
        version_info['bit'] = bit
        version_info['home'] = _step_parent_dir(java_path, 2)

        version_infos.append(version_info)

    return version_infos


def json_dump(version_infos):
    json.dump(version_infos,
              open(VERSION_JSON_PATH, 'w'),
              default=lambda o: o.__str__(),
              indent=4)


def json_load():
    return json.load(open(VERSION_JSON_PATH, 'r'), object_pairs_hook=OrderedDict)


def ensure_dir_exists(path):
    if not os.path.isdir(path):
        if os.path.exists(path):
            raise DirectoryConflicsError(path)
        else:
            os.makedirs(path)


def has_config_file():
    return os.path.exists(VERSION_JSON_PATH)


def handle_directory_conflics(ex):
    color.print_err('directory %s conflics' % ex.args[0])


def init_config():
    ensure_dir_exists(CONFIG_PATH)
    version_infos = build_version_infos()
    json_dump(version_infos)


def get_config():
    if not has_config_file():
        init_config()
        color.print_ok('init config in %s' % VERSION_JSON_PATH)

    return json_load()


def pretty_print_config(version_infos):
    color.print_info('-'*80)
    for version_info in version_infos:
        color.print_info()
        color.print_info('tag: {}'.format(version_info['tag']))
        color.print_info('version: {}'.format(version_info['version']))
        color.print_info('bit: {}'.format(version_info['bit']))
        color.print_info('home: {}'.format(version_info['home']))
        color.print_info()
        color.print_info('-'*80)


def find_version(tag: str):
    for version_info in get_config():
        if version_info['tag'].startswith(tag):
            return version_info


def create_activate_s(virtual_env, java_home, java_tag, doc=activate_template):
    funcs = [partial(re.sub, '"__VIRTUAL_ENV__"', '"%s"' % virtual_env),
             partial(re.sub, '"__JAVA_HOME__"', '"%s"' % java_home),
             partial(re.sub, '"__JAVA_TAG__"', '"%s"' % java_tag)]

    return chain_apply(funcs, doc)


def write_activate_file(virtual_env, java_home, java_tag, force=False):
    virtual_env = os.path.abspath(virtual_env)

    if os.path.lexists(virtual_env) and not force:
        color.print_warn('project diretory %s exists already\n'
                         'you can use -f argument to continue.'%virtual_env)
        return


    ensure_dir_exists(virtual_env)

    activate_dir = os.path.join(virtual_env, 'bin')
    ensure_dir_exists(os.path.join(activate_dir))

    activate_path = os.path.join(activate_dir, 'activate')

    with open(activate_path, 'w') as fw:
        fw.write(create_activate_s(virtual_env, java_home, java_tag))

    color.print_info('create active file {0}'.format(activate_path))

    color.print_info('run `source {0}` to activate it'.format(path_to(os.curdir, activate_path)))


@handle_excpetion(handle_directory_conflics, DirectoryConflicsError)
def cli():
    global GLOBAL_MODE
    global CONFIG_PATH
    global VERSION_JSON
    global VERSION_JSON_PATH

    arguments = docopt(__doc__, version=__version__)

    GLOBAL_MODE = bool(arguments['--global'])

    if GLOBAL_MODE:
        CONFIG_PATH = '/etc/jvirtualenv'
    else:
        CONFIG_PATH = os.path.expanduser('~/.jvirtualenv')

    VERSION_JSON = 'version.json'
    VERSION_JSON_PATH = os.path.join(CONFIG_PATH, VERSION_JSON)

    if arguments['list-tag']:
        pretty_print_config(get_config())

    elif arguments['reinit-tag']:
        init_config()
        color.print_ok('reinit config in %s'%VERSION_JSON_PATH)

    elif arguments['--java']:
        version_info = find_version(arguments['--java'])

        project_path = arguments['<project>']
        write_activate_file(project_path, version_info['home'], version_info['tag'], bool(arguments['--force']))


if __name__ == '__main__':
    cli()
