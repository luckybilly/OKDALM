#!/usr/bin/python
# -*- coding: utf-8 -*-

import property
import re
import os
import sys

ARTIFACTORY_FILE_NAME = 'artifactory_version.properties'
#作为gradle.properties中module的key名称与artifactory_version.properties的差异，如：'version_' 表示： lib_db -> version_lib_db
### 匹配分段写的依赖
linePattern = re.compile(r'(((group)|(name)|(version)|(\w+))\s*\:([^\)]*)){3}')
### 匹配写成一个字符串的依赖
linePattern2 = re.compile(r'[\'\"].*[\'\"]')
artifactIdPattern = re.compile(r'name[^\,]+')


###读取指定工程中的依赖关系
###读取范围：在artifactory_version.properties中声明过的module
###读取内容：groupId为gradle.properties中声明的maven_groupId
###读取结果：字典形式：以module名为key，依赖项数组为value
###读取结果：按照依赖顺序排序的module名称列表
class Dependency:

    def __init__(self, root_dir):
        gradle_properties = property.parse(os.path.join(root_dir, 'gradle.properties'))
        version_properties = property.parse(os.path.join(root_dir, ARTIFACTORY_FILE_NAME))
        self.root_dir = root_dir
        # 过滤含有build.gradle文件的文件夹（为module）,并解析出build.gradle中对当前工程中各module的依赖项
        self.modules = {}
        ### 匹配当前groupId的依赖项
        self.pattern = re.compile(r'.*ompile.*((' + gradle_properties.get('maven_groupId') + ')|(maven_groupId)).*')
        for file in os.listdir(root_dir):
            if version_properties.has_key(file):
                path = os.path.join(root_dir, file)
                gradle = os.path.join(path, 'build.gradle')
                if os.path.isdir(path) and os.path.isfile(gradle):
                    self.modules[file] = read_gradle_dependencies(self.pattern, gradle)

        self.sorted_modules = self.sort_by_dependency_relationship()


    #获取直接或间接依赖name的所有module
    def get_all_reverse_dependencies(self, name):
        rev_modules = []
        find_reverse_dependency_module(self.modules, name, rev_modules)
        return rev_modules

    #按照依赖关系进行排序，被依赖的排在前面先发布
    def sort_by_dependency_relationship(self):
        sorted_modules = []
        m_with_no_deps = []
        for k,v in self.modules.items():
            if len(v) == 0:                 #先取出未依赖其它module的module
                sorted_modules.append(k)
                m_with_no_deps.append(k)
        for m in m_with_no_deps:            #再遍历未依赖的module
            arr = self.get_all_reverse_dependencies(m)  #计算其被依赖的所有module
            tmp = []
            #将数组排入序列，确保被依赖的module排在前面
            #如： ['a', 'b', 'c', 'd']        和       ['A', 'f', 'c', 'e']
            #排列成： ['a', 'b', 'A', 'f', 'c', 'd', 'e']
            for value in arr:
                if value in sorted_modules:#该module出现在序列中，将tmp内的module添加到序列里的value之前
                    if len(tmp) > 0:
                        index = sorted_modules.index(value)
                        for t in tmp:
                            sorted_modules.insert(index, t)
                            index += 1
                        tmp = []
                else:#不在序列中，缓存起来
                    tmp.append(value)
            if len(tmp) > 0:
                sorted_modules.extend(tmp)
        return sorted_modules




### 读取build.gradle中配置的（当前工程中的）依赖项
def read_gradle_dependencies(pattern, gradle):
    try:
        pro_file = open(gradle, 'r')
        list = []
        annotation=None
        for line in pro_file:
            line = line.strip()
            if annotation:
                annotation = line.endswith('*/')
            elif line.startswith('/*'):
                annotation = True
            else:
                if pattern.search(line) and not line.startswith('//'):
                    name = read_dependency_line(line)
                    if name != '' and name not in list:
                        list.append(name)
    except Exception, e:
        raise e
    else:
        pro_file.close()
        return list

### 读取依赖项的module名称
def read_dependency_line(line):
    sep = None
    if ',' in line: # 类似于： compile group:maven_groupId, name:'lib_module_c', version: lib_module_c
        sep = True
        p = linePattern
    else:
        p = linePattern2

    match = p.search(line)
    if match:
        # 去除引号
        line = re.sub(r'[\'\"]', '', match.group())
        # 截取module名称
        if sep:
            match = artifactIdPattern.search(line)
            if match:
                return match.group().split(':')[1].strip()
        else:
            return line.split(':')[1].strip()
    else:
        return ''

### 反向查找指定module的依赖（直接和间接依赖该module的module）
def find_reverse_dependency_module(modules, name, rev_modules):
    for i in modules:
        if name in modules[i]:
            if i not in rev_modules:
                rev_modules.append(i)
            find_reverse_dependency_module(modules, i, rev_modules)


#读取工程中的依赖关系
def get_project_dependencies(root_dir):
    return Dependency(root_dir)


#在工程根目录执行以下代码，打印出当前工程下的依赖关系：
# python python_tools/dependency_reader.py
if __name__ == '__main__':
    project_abs_path = os.path.abspath(os.curdir)   #默认为当前目录
    if len(sys.argv) > 1:
        project_abs_path = os.path.join(project_abs_path, sys.argv[1])
    dependency = get_project_dependencies(project_abs_path)
    module_dependencies = dependency.modules
    for key in module_dependencies:
        print "module:" + key
        print module_dependencies[key]
        print ''

    print '----------------------------------------------------'
    sorted = dependency.sorted_modules
    print 'sorted modules:'
    print sorted
