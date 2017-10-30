# -*- Coding:utf-8 -*-

template = """
@echo off
set "VIRTUAL_ENV="__VIRTUAL_ENV__""

if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
) else (
    if not defined PROMPT (
        set "PROMPT=$P$G"
    )
    set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
)
set "PROMPT=("__JAVA_TAG__") %PROMPT%"


set "_OLD_VIRTUAL_JAVA_HOME=%JAVA_HOME%"
if defined JAVA_HOME (
    set "_OLD_VIRTUAL_JAVA_HOME=%JAVA_HOME%"
) else (
    set "_OLD_VIRTUAL_JAVA_HOME="
)
set "JAVA_HOME="__JAVA_HOME__""

if defined CLASSPATH (
    set "_OLD_VIRTUAL_CLASSPATH=%CLASSPATH%"
) else (
    set "_OLD_VIRTUAL_CLASSPATH="
)
set "CLASSPATH="__CLASSPATH__""

REM if defined _OLD_VIRTUAL_PATH (
if not defined _OLD_VIRTUAL_PATH goto ENDIFVPATH1
    set "PATH=%_OLD_VIRTUAL_PATH%"
:ENDIFVPATH1
REM ) else (
if defined _OLD_VIRTUAL_PATH goto ENDIFVPATH2
    set "_OLD_VIRTUAL_PATH=%PATH%"
:ENDIFVPATH2

set "PATH=%JAVA_HOME%\\bin;%PATH%"
"""
