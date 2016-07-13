#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, platform, time
from python_tools import dependency_reader
from python_tools import property
import commands, traceback

ARTIFACTORY_FILE_NAME = 'artifactory_version.properties'
KEY_MAVEN_TYPE = 'maven_type'
SNAPSHOT_SUFFIX = '-SNAPSHOT'
log_result = None

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


def do_deploy(lib_module_name, is_reverse):
    print 'start to deploy module:--------------      %s      ---------------------' % lib_module_name
    command = '{0} :{1}:clean :{1}:assembleRelease :{1}:generatePomFileForAarPublication :{1}:artifactoryPublish'.format(get_command(), lib_module_name)
    print command
    if log_result:
        result = os.system(command)
    else:
        result,log = commands.getstatusoutput(command)
        if result != 0:
            print log
    if result != 0:
        print "ERROR:artifactory error %d. please check module dependencies" % result
    else:
        deploy_version = get_deploy_version(lib_module_name)
        gradle_version = get_gradle_version(lib_module_name)
        # 如果本次发布的版本号与之前一致，则不升级传递依赖的module版本号
        if gradle_version == deploy_version:
            is_reverse = 0
            print 'module %s:%s:%s refreshed' % (group_id, lib_module_name, deploy_version)
        else:
            # 修改gradle.properties文件中的版本号（=module刚发布成功的版本号=被依赖的版本号）
            gradle_properties.put(gradle_key_prefix + lib_module_name, deploy_version)
            print 'modify gradle.properties: [%s: %s -> %s]' % (gradle_key_prefix + lib_module_name, gradle_version, deploy_version)
        print 'DEPLOY SUCCESS: %s:%s:%s' % (group_id, lib_module_name, deploy_version)
        if is_reverse:
            modules = module_dependencies.get_all_reverse_dependencies(lib_module_name)
            print 'start deploying reverse dependency modules:'
            print modules
            success_modules = []
            failed_modules = []
            for m in modules:
                version_level_up(m)
                if do_deploy(m, 0) == 0:
                    success_modules.append(m)
                else:
                    failed_modules.append(m)
            print 'deploying reverse dependency modules finished.'
            print 'success_modules:' + str(len(success_modules))
            print success_modules
            print 'failed_modules:' + str(len(failed_modules))
            print failed_modules

    return result

# 从release切到snapshot时进行版本升级
def version_level_up(module):
    dv = version_properties.get(module)
    gv = get_gradle_version(module)
    #gv不带-SNAPSHOT后缀，表明当前是release版本
    #并且当前版本号与artifactory_version.properties中设置的发布版本号一致
    #要发布的版本为snapshot版
    #说明当前的deploy操作是：从release版切换到snapshot版，版本号自动升级
    #自动升级版本号只是升级一个小版本：最后一位数字（非数字自动忽略），若要升级大版本，可手动修改artifactory_veresion.properties中的版本号
    if dv == gv and snapshot:
        arr = dv.split('.')
        last_index = len(arr) - 1
        while last_index > -1:
            try:
                to_last_lvl = str(int(arr[last_index]) + 1)
                arr[last_index] = to_last_lvl
                break
            except Exception, ne:
                last_index -= 1
        if last_index > -1:
            version = '.'.join(arr)
            version_properties.put(module, version)
            print 'modify %s: [%s: %s -> %s]' % (ARTIFACTORY_FILE_NAME, module, dv, version)
        else:
            print 'Error: auto level up %s: [%s: %s] failed!' % (ARTIFACTORY_FILE_NAME, module, dv)


def get_gradle_version(module):
    return gradle_properties.get(gradle_key_prefix + module)

def get_deploy_version(module):
    version = version_properties.get(module)
    if snapshot:
        version += SNAPSHOT_SUFFIX
    return version


### deploy的主方法
### name: 要发布的模块名称
### is_reverse: 是否更新发布（直接/间接）依赖本module的其它module（反向查找依赖module）
def main(name, is_reverse):
    result = -1
    print ''
    if version_properties.has_key(name):
        version_level_up(name)
        result = do_deploy(name, is_reverse)
    else:
        print "\n\t\tDEPLOY SKIP: module \":%s\" is undefined in %s\n" % (name, ARTIFACTORY_FILE_NAME)
    return result

def show_help():
    print '     +--------------------------------------------------------------------------------------------------------'
    print '     |    发布module到maven服务器                                                                               '
    print '     |    usage:                                                                                              '
    print '     |            python deploy.py [-c] [-l] [-r] [-a] module_name                                             '
    print '     |                -c： 可选，只发布当前指定的module（默认同时更新依赖本module的其它module）                       '
    print '     |                -l： mac可选，打印发布信息的log日志                                                         '
    print '     |                -r： 可选，发布成release版本，默认为snapshot版本                                             '
    print '     |                -a： 可选，发布artifactory_veresion.properties中配置的所有module                            '
    print '     |       module_name： 无-a参数时必填，当前发布的module名称                                                    '
    print '     +---------------------------------------------------------------------------------------------------------'

### 直接调用打球py文件
if  __name__ == '__main__':
    argLen = len(sys.argv)
    if argLen < 2:
        show_help()
    else:
        index = 1   #取参数的索引
        reverse = 1  #deploy依赖该module的所有module
        mavenType = 'snapshot'
        snapshot = True
        deploy_all = None
        while argLen > index:
            value = sys.argv[index].strip()
            if value.startswith('-'):
                if value == '-h':
                    show_help()
                    sys.exit(0)
                elif value == '-c':
                    reverse = 0
                elif value == '-l':
                    log_result = True
                elif value == '-r':
                    mavenType = 'release'
                    snapshot = None
                elif value == '-a':
                    deploy_all = True
            else:
                break
            index += 1
        module_name = ''
        if not deploy_all:
            if argLen > index:
                module_name = sys.argv[index]   #要deploy的module名称
                index += 1
            else:
                show_help()
                sys.exit()

        if platform.system() == 'Windows':  #windows环境执行commands.getstatusoutput(command)时报错
            log_result = True
        project_abs_path = os.path.abspath(os.curdir)   #默认为当前目录

        gradle_properties = property.parse(os.path.join(project_abs_path, 'gradle.properties'))
        version_properties = property.parse(os.path.join(project_abs_path, ARTIFACTORY_FILE_NAME))

        group_id = gradle_properties.get('maven_groupId')
        gradle_key_prefix = gradle_properties.get('version_prefix')

        cur_maven_type = version_properties.get(KEY_MAVEN_TYPE)
        version_properties.put(KEY_MAVEN_TYPE, mavenType)
        module_dependencies = dependency_reader.get_project_dependencies(project_abs_path)

        start = time.time()
        start_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start))
        print '\n++++++++++++++++++++++++++++++++   deploy start working  (start at: %s)    ++++++++++++++++++++++++++++++++++++++++++' % start_time

        try:
            if deploy_all: #deploy所有在artifactory_version.properties中配置的module
                print 'deploy below modules:'
                print module_dependencies.sorted_modules
                success = []
                failed = []
                for module in module_dependencies.sorted_modules: #按照依赖关系的顺序进行发布
                    if main(module, 0) == 0:
                        success.append(module)
                    else:
                        failed.append(module)
                print 'deploy finished!'
                print 'success:' + str(len(success))
                print success
                print 'failed:' + str(len(failed))
                print failed
            else:
                main(module_name, reverse)
        except Exception, e:
            print traceback.format_exc()
        finally:
            version_properties.put(KEY_MAVEN_TYPE, cur_maven_type)

        end_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        print '++++++++++++++++++++++++++++++++  deploy completed   (end at: %s, cost: %ds) ++++++++++++++++++++++++++++++++++++++++\n' % (end_time, time.time() - start)