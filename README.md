[![PyPI version](https://badge.fury.io/py/jvirtualenv.svg)](https://badge.fury.io/py/jvirtualenv)
[![codebeat badge](https://codebeat.co/badges/7bd988f9-7f2c-4701-951e-92dfe16be5ab)](https://codebeat.co/projects/github-com-minghu6-jvirtualenv-master)
# jvirtualenv
A micro Java environment switch which reference `virtualenv`.

## OS Supports:
Linux and any other OS whose shell is bash or zsh.

Windows support is a TBD (low priority though).

## Requirements:
1. JDK(*Oracle JDK*) should be placed on a folder whose name is `java`
and its name should startswith `jdk`. (maybe need `sudo updatedb`)

    Exp: `/opt/java/jdk-9`,`/opt/java/jdk1.8.0_144`

    Or you can edit the config file directly. (not recommented)
    
    The config file should be as followed:
    ```
    [
        {
            "tag": "9",
            "version": "9",
            "bit": "64",
            "home": "/opt/java/jdk-9"
        },
        {
            "tag": "1.8:0:64",
            "version": "1.8.0_144",
            "bit": "32",
            "home": "/opt/java/jdk1.8.0_144"
        }
   ]
   
    ```
    
2. Python3
    
## Usage:

1. `pip3 install jvirtualenv`
2. `jvirtualenv list-tag` (view all jdk tag)
3. `jvirtualenv -j 1.8 <myproject>` (if 1.8 is prefix of someone tag)
4. `source <myproject>/bin/activate` (activate virtual java env)
5. `deactivate` (deactivate the virtualenv)


**FOR EXCELLENT PYTHON3 AND VIRTUALENV!**

