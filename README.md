#Android studio基于artifactory的maven私服一键deploy工具

OKDALM = One Key to Deploy Android Library to Maven

##适用范围

有公司内部的lib工程并希望（或已经）存放在公司maven私服，lib模块之间、app引用lib模块的方式使用maven方式进行依赖

尤其适合作者当前的项目结构：

    +--------------------------+---------------------+------------------+
    |   CommonLib              |     business1       |    business2     |
    |        lib_module_1      |          app_1      |         app_1    |
    |        lib_module_...    |          app_...    |         app_...  |
    |        lib_module_n      |          app_n      |         app_n    |
    +--------------------------+---------------------+------------------+
    
##作用
- 规范代码管理：公共库专人维护
- 便于使用Jenkins进行持续集成
- 一条命令即可deploy发生修改的module及依赖该module的其它module，并立即生效
- 可以按照工程中module依赖关系的顺序deploy all
- 便于管理module是否进行deploy管理（通过是否在artifactory_version.properties中进行配置确定）

##使用方式

###涉及到的文件有

- python_tools 文件夹          （新建：脚本库）
- artifactory.gradle          （新建：artifactory设置）
- artifactory_version.properties    （新建：module通过artifactory发布到maven的版本配置）
- build.gradle                （修改：工程的构建脚本，需要添加对artifactory的支持）
- deploy.py                     （新建：deploy的入口，作者当前用的python版本为2.7.10，python3未测试）
- gradle.properties             （修改：添加deploy相关设置项）
- 各module目录下的build.gradle文件 （修改：将module间的依赖改为maven方式）

###初次使用
假定当前lib工程名称为：CommonLib

- 使用artifactory搭建maven私服
    - 这一步非常简单：只需下载最新版本的[artifactory](https://www.jfrog.com/open-source)，解压文件，然后运行与你的平台对应的artifactory可执行文件即可
    
- 复制以下文件到CommonLib根目录
    - python_tools 文件夹
    - artifactory.gradle
    - artifactory_version.properties
    - deploy.py
- 修改build.gradle文件
    - 添加对artifactory.gradle的引用：
    
            apply from: "artifactory.gradle"
        
    - buildscript -> dependencies下添加
    
            classpath(group: 'org.jfrog.buildinfo', name: 'build-info-extractor-gradle', version: '4.1.1')
        
- 修改CommonLib根目录的gradle.properties文件
    - 将以下内容复制到CommonLib/gradle.properties中，并进行相应的修改
    
        <pre>
        maven_groupId=your.group.id
        artifactory_user=admin
        artifactory_password=password
        artifactory_contextUrl=http://localhost:8081/artifactory
        artifactory_snapshot_repoKey=libs-snapshot-local
        artifactory_release_repoKey=libs-release-local
        version_prefix=
        </pre>
        
- 修改CommonLib/artifactory_version.properties

    - 将demo里的lib版本号信息去除（lib_module_a等）
    - 将需要deploy到maven私服的module配置按照moduleName=versionName的方式进行配置（如：lib_module_a=1.0.0）
    
- 执行命令将上一步配置的版本deploy到maven私服(snapshot版本)
    
        python deploy.py -a
    
- 修改所有module中的依赖配置，从module依赖改为maven依赖的方式： 
    
        compile project(':lib_module_a') -> compile "${maven_groupId}:lib_module_a:${lib_module_a}"
        or
        compile project(':lib_module_a') -> compile group:maven_groupId, name:'lib_module_a', version: lib_module_a
        
- 执行命令发布正式版，（作为以后修改发布的最初始版本）

        python deploy.py -r -a

###后续使用

- 当前为release版的module发生修改，发布snapshot版，将同时发布依赖该module的所有module
    
        python deploy.py module_name
        
- 当前为snapshot版的module发生修改，发布snapshot版，将仅发布当前module，命令相同

        python deploy.py module_name
        
- 当前为snapshot的module修改测试完毕，发布release版，将同时发布依赖该module的所有module

        python deploy.py -r module_name
        
        
- 新建lib module
    - 在artifactory_version.properties中添加对应的版本号（否则将不能进行deploy）
    - deploy到maven私服： 
        - <code>python -r -c deploy.py module_name</code>
    - 依赖该module的module使用maven方式添加依赖，版本号为上一步在gradle.properties中生成的版本号变量名
    - 再次deploy到maven私服：脚本自动将所有依赖该module的所有module deploy一遍
        - <code>python deploy.py module_name</code>
    - 测试&修改
    - deploy正式版：
        - <code>python deploy.py -r module_name</code>
        
        
        
