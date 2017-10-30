# -*- Coding:utf-8 -*-

template = """
@echo off

set VIRTUAL_ENV=

REM Don't use () to avoid problems with them in %PATH%
if not defined _OLD_VIRTUAL_PROMPT goto ENDIFVPROMPT
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
    set _OLD_VIRTUAL_PROMPT=
:ENDIFVPROMPT

if not defined _OLD_VIRTUAL_CLASSPATH (
    set "CLASSPATH="
) else (
    set "CLASSPATH=%_OLD_VIRTUAL_CLASSPATH%"
)

if not defined _OLD_VIRTUAL_JAVA_HOME (
    set "JAVA_HOME="
) else (
    set "JAVA_HOME=%_OLD_VIRTUAL_JAVA_HOME%"
)

if not defined _OLD_VIRTUAL_PATH goto ENDIFVPATH
    set "PATH=%_OLD_VIRTUAL_PATH%"
    set _OLD_VIRTUAL_PATH=
:ENDIFVPATH
"""
