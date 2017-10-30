# -*- coding:utf-8 -*-
"""Java Virtual Env
virtualenv for java JDK

jdk pattern:
  POSIX:  .*/java/jdk[^/]
  Windows: Program Files, Program Files (x86), ProgramData and current directory

Usage:
  jvirtualenv list-tag [-g]
  jvirtualenv --java=<tag> <project> [-g] [-f]
  jvirtualenv reinit-tag [-g]

Options:
  list-tag         list all the optional tag
  -j --java=<tag>  point a jdk to use
  reinit-tag       reinit the java version config
  -g --global      global mode, maybe need sudo
  -f --force       force to create java virtual env in a existed folder

"""

import re
from distutils.version import LooseVersion
import json
from collections import OrderedDict

from color import color
from docopt import docopt

from jvirtualenv.support.minghu6_support import *
from jvirtualenv.support.minghu6_support import iswin


if not iswin():
    import sh


__version__ = '0.1.0'


class GetVersionFailedError(Exception):
    pass


class NotBelongToJDKError(Exception):
    pass


class GetJavaVersionFailedError(GetVersionFailedError):
    pass


class DirectoryConflictError(Exception):
    """The first arg of the exception should be conflicted directory path"""
    pass


def _step_parent_dir(path, n=1):
    if n > 0:
        n -= 1
        path = os.path.dirname(path)
        return _step_parent_dir(path, n)

    return path


def get_java_version(java_path='java'):
    if iswin():
        cmd = '"{0}" -version'.format(java_path)
    else:
        cmd = '{0} -version'.format(java_path)

    _, err = exec_cmd(cmd)  # It's confused that java -version output-stream is stderr other than stdout

    try:
        version_s = re.split(r'\s+', err[0])[-1][1:-1]
        version = LooseVersion(version_s)

        match = re.match(r'\d+', re.split(r'\s+', err[2])[2])
        if match is None:
            bit = '32'
        else:
            bit = match.group(0)

    except Exception as ex:
        raise GetJavaVersionFailedError from ex

    return version, bit


def isjdk(java_path):
    if iswin():
        javac_path = os.path.join(os.path.dirname(java_path), 'javac.exe')
    else:
        javac_path = os.path.join(os.path.dirname(java_path), 'javac')

    return os.path.isfile(javac_path)


def _build_version_info(java_path):
    if not isjdk(java_path):
        raise NotBelongToJDKError
    
    try:
        version, bit = get_java_version(java_path)
    except GetJavaVersionFailedError as ex:
        raise NotBelongToJDKError from ex

    version_info = OrderedDict()
    if version.version[0] == 9:
        version_info['tag'] = version.vstring
    else:
        version_info['tag'] = '{0}.{1}:{2}:{3}'.format(*version.version[:3], bit)
    
    version_info['version'] = version
    version_info['bit'] = bit
    version_info['home'] = _step_parent_dir(java_path, 2)
    
    return version_info


def build_version_infos():
    version_infos = []

    if iswin():
        possible_dir_name = [
            'Program Files (x86)',
            'Program Files',
            'ProgramData',
        ]
        possible_dir = []
        for driver in get_drivers():
            for each_dir in possible_dir_name:
                possible_dir.append(os.path.join(driver, os.sep, each_dir))

        possible_dir.append(os.path.abspath(os.curdir))

        for each_possible_dir in possible_dir:
            for java_path in find_wrapper(each_possible_dir, 'java'):
                try:
                    version_info = _build_version_info(java_path)
                except NotBelongToJDKError:
                    pass
                else:
                    color.print_info('')
                    version_infos.append(version_info)
    
    else:
        JAVA_PATTERN = '^.*/java/jdk[^/]*/bin/java$'
        for item in sh.locate('-A', '-r', JAVA_PATTERN):
            java_path = item.__str__().strip()

            try:
                version_info = _build_version_info(java_path)
            except NotBelongToJDKError:
                pass
            else:
                color.print_info('')
                version_infos.append(version_info)

    return version_infos


def json_dump(version_infos):
    json.dump(version_infos,
              open(TAG_LIST_CONFIG_PATH, 'w'),
              default=lambda o: o.__str__(),
              indent=4)


def json_load():
    return json.load(open(TAG_LIST_CONFIG_PATH, 'r'), object_pairs_hook=OrderedDict)


def ensure_dir_exists(path):
    if not os.path.isdir(path):
        if os.path.exists(path):
            raise DirectoryConflictError(path)
        else:
            os.makedirs(path)


def has_config_file():
    return os.path.exists(TAG_LIST_CONFIG_PATH)


def handle_directory_conflict(ex):
    color.print_err('directory %s conflict' % ex.args[0])


def init_config():
    ensure_dir_exists(CONFIG_DIR)
    version_infos = build_version_infos()
    json_dump(version_infos)


def get_config():
    if not has_config_file():
        init_config()
        color.print_ok('init config in %s' % TAG_LIST_CONFIG_PATH)

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

    if not version_infos:
        color.print_warn('empty')


def find_version(tag: str):
    for version_info in get_config():
        if version_info['tag'].startswith(tag):
            return version_info


def create_activate_s(virtual_env, java_home, java_tag):
    if iswin():
        from jvirtualenv.template.activate_template_bat import template
        if java_tag.startswith('1'):
            class_path = '.:%JAVA_HOME%\\lib\\dt.jar;%JAVA_HOME%\\lib\\tools.jar'
        else:
            class_path = '.'
        funcs = [
            partial(re.sub, '"__VIRTUAL_ENV__"', '"%s"' % virtual_env.encode('unicode_escape').decode()),
            partial(re.sub, '"__JAVA_HOME__"', '"%s"' % java_home.encode('unicode_escape').decode()),
            partial(re.sub, '"__JAVA_TAG__"', '"%s"' % java_tag),
            partial(re.sub, '"__CLASSPATH__"', '"%s"' % class_path.encode('unicode_escape').decode())
        ]
    else:
        from jvirtualenv.template.activate_template import template
        funcs = [
            partial(re.sub, '"__VIRTUAL_ENV__"', '"%s"' % virtual_env),
            partial(re.sub, '"__JAVA_HOME__"', '"%s"' % java_home),
            partial(re.sub, '"__JAVA_TAG__"', '"%s"' % java_tag)
        ]

    return chain_apply(funcs, template)


def write_activate_file(virtual_env, java_home, java_tag, force=False):
    virtual_env = os.path.abspath(virtual_env)

    if os.path.lexists(virtual_env) and not force:
        color.print_warn('project diretory %s exists already\n'
                         'you can use -f argument to continue.' % virtual_env)
        return

    ensure_dir_exists(virtual_env)

    activate_dir = os.path.join(virtual_env, 'bin')
    ensure_dir_exists(os.path.join(activate_dir))

    if iswin():
        activate_path = os.path.join(activate_dir, 'activate.bat')
        deactivate_path = os.path.join(activate_dir, 'deactivate.bat')

        with open(activate_path, 'w') as fw_activate, open(deactivate_path, 'w') as fw_deactivate:
            fw_activate.write(create_activate_s(virtual_env, java_home, java_tag))

            from jvirtualenv.template.deactivate_template_bat import template
            fw_deactivate.write(template)
        
        color.print_info('create active file {0}'.format(activate_path))
        color.print_info('run "{0}" to activate it'.format(activate_path))
        color.print_info('run "{0}" to deactivate it'.format(deactivate_path))

    else:
        activate_path = os.path.join(activate_dir, 'activate')

        with open(activate_path, 'w') as fw:
            fw.write(create_activate_s(virtual_env, java_home, java_tag))

        color.print_info('create active file {0}'.format(activate_path))
        color.print_info('run `source {0}` to activate it'.format(path_to(os.curdir, activate_path)))


@handle_excpetion(handle_directory_conflict, DirectoryConflictError)
def cli():
    global GLOBAL_MODE
    global CONFIG_DIR
    global TAG_LIST_CONFIG_PATH
    global SEARCH_PATTERN_CONFIG_PATH

    arguments = docopt(__doc__, version=__version__)

    GLOBAL_MODE = bool(arguments['--global'])

    if GLOBAL_MODE:
        if iswin():
            CONFIG_DIR = os.path.join(os.path.dirname(get_home_dir()), 'All Users', '.jvirtualenv.d')
        else:
            CONFIG_DIR = '/etc/jvirtualenv.d'
            
    else:
        CONFIG_DIR = os.path.join(get_home_dir(), '.jvirtualenv.d')
    
    TAG_LIST_CONFIG_PATH = os.path.join(CONFIG_DIR, 'tag-list.json')
    SEARCH_PATTERN_CONFIG_PATH = os.path.join(CONFIG_DIR, 'search-pattern.json')

    if arguments['list-tag']:
        pretty_print_config(get_config())

    elif arguments['reinit-tag']:
        if not iswin():
            with sh.contrib.sudo:
                sh.updatedb()

        init_config()
        color.print_ok('reinit config in %s' % TAG_LIST_CONFIG_PATH)

    elif arguments['--java']:
        version_info = find_version(arguments['--java'])
        if version_info is None:
            color.print_err('No matched tag')
            return

        project_path = arguments['<project>']
        write_activate_file(project_path, version_info['home'], version_info['tag'], bool(arguments['--force']))


if __name__ == '__main__':
    cli()
