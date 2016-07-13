#!/usr/bin/python
# -*- coding: utf-8 -*-


import os, platform


# 获取gradle命令
def get_command():
    plat = platform.system()
    if 'Darwin' == plat:
        return './gradlew '
    elif 'Windows' == plat:
        return 'gradlew '
    elif 'Linux' == plat:
        return './gradlew '
    else:
        return './gradlew '

if __name__ == '__main__':
    command = get_command() + 'build --refresh-dependencies'
    os.system(command)