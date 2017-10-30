# -*- coding:utf-8 -*-
template = """
# This file must be used with "source bin/activate" *from bash*
# you cannot run it directly

deactivate () {

    # reset old environment variables
    # ! [ -z ${VAR+_} ] returns true if VAR is declared at all
    if ! [ -z "${_OLD_VIRTUAL_PATH+_}" ] ; then
        PATH="$_OLD_VIRTUAL_PATH"
        export PATH
        unset _OLD_VIRTUAL_PATH
    fi

    if ! [ -z "${_OLD_VIRTUAL_JAVA_HOME+_}" ] ; then
        JAVA_HOME="$_OLD_VIRTUAL_JAVA_HOME"
        export JAVA_HOME
        unset _OLD_VIRTUAL_JAVA_HOME
    fi

    JAVA_TAG="$_OLD_VIRTUAL_JAVA_TAG"
    export JAVA_TAG
    unset _OLD_VIRTUAL_JAVA_TAG

    if ! [ -z "${_OLD_VIRTUAL_CLASSPATH+_}" ] ; then
        CLASSPATH="$_OLD_VIRTUAL_CLASSPATH"
        export CLASSPATH
        unset _OLD_VIRTUAL_CLASSPATH
    fi

    # This should detect bash and zsh, which have a hash command that must
    # be called to get it to forget past commands.  Without forgetting
    # past commands the $PATH changes we made may not be respected
    if [ -n "${BASH-}" ] || [ -n "${ZSH_VERSION-}" ] ; then
        hash -r 2>/dev/null
    fi

    if ! [ -z "${_OLD_VIRTUAL_PS1+_}" ] ; then
        PS1="$_OLD_VIRTUAL_PS1"
        export PS1
        unset _OLD_VIRTUAL_PS1
    fi

    unset VIRTUAL_ENV
    if [ ! "${1-}" = "nondestructive" ] ; then
    # Self destruct!
        unset -f deactivate
    fi
}

# unset irrelevant variables
deactivate nondestructive

VIRTUAL_ENV="__VIRTUAL_ENV__"
export VIRTUAL_ENV

# save PATH
_OLD_VIRTUAL_PATH="$PATH"
PATH="$VIRTUAL_ENV/bin:$PATH"

# unset JAVA_HOME if set
if ! [ -z "${JAVA_HOME+_}" ] ; then
    _OLD_VIRTUAL_JAVA_HOME="$JAVA_HOME"
    unset JAVA_HOME
fi
# set new JAVA_HOME
JAVA_HOME="__JAVA_HOME__"
export JAVA_HOME

# unset JAVA_TAG if set
if ! [ -z "${JAVA_TAG+_}" ] ; then
    _OLD_VIRTUAL_JAVA_TAG="$JAVA_TAG"
    unset JAVA_TAG
fi
# set new JAVA_TAG
JAVA_TAG="__JAVA_TAG__"
export JAVA_TAG

# unset CLASSPATH if set
if ! [ -z "${CLASSPATH+_}" ] ; then
    _OLD_VIRTUAL_CLASSPATH="$CLASSPATH"
    unset CLASSPATH
fi
# set new CLASSPATH
if [ "$JAVA_TAG" != "9" ] ; then
    CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
else
    CLASSPATH=.
fi
export CLASSPATH

PATH="$JAVA_HOME/bin:$PATH"
export PATH

if [ -z "${VIRTUAL_ENV_DISABLE_PROMPT-}" ] ; then
    _OLD_VIRTUAL_PS1="$PS1"
    if [ "x" != x ] ; then
        PS1="$PS1"
    else
        PS1="(`basename \"$VIRTUAL_ENV\"`: $JAVA_TAG) $PS1"
    fi
    export PS1
fi

# This should detect bash and zsh, which have a hash command that must
# be called to get it to forget past commands.  Without forgetting
# past commands the $PATH changes we made may not be respected
if [ -n "${BASH-}" ] || [ -n "${ZSH_VERSION-}" ] ; then
    hash -r 2>/dev/null
fi
"""
