#Android studio基于artifactory的maven私服一键deploy工具

OKDALM = One Key to Deploy Android Library to Maven

##适用范围

中型团队进行多人协作，有公司内部的lib工程并存放在公司maven私服，lib模块之间、app引用lib模块的方式使用maven方式进行依赖

尤其适合作者当前的项目结构：

    +--------------------------+---------------------+------------------+
    |   CommonLib              |     business1       |    business2     |
    |        lib_module_1      |          app_1      |         app_1    |
    |        lib_module_...    |          app_...    |         app_...  |
    |        lib_module_n      |          app_n      |         app_n    |
    +--------------------------+---------------------+------------------+
    


##使用方式

###涉及到的文件有

- python_tools 文件夹
- artifactory.gradle
- artifactory_version.properties
- build.gradle
- deploy.py
- gradle.properties
- 各module目录下的build.gradle文件

###初次使用
假定当前lib工程名称为：CommonLib

- 使用artifactory搭建maven私服
    - 这一步非常简单：只需下载最新版本的[artifactory](https://www.jfrog.com/open-source)，解压文件，然后运行与你的平台对应的artifactory可执行文件即可
    
- 复制以下文件到CommonLib根目录
    - python_tools 文件夹
    - artifactory.gradle
    - artifactory_version.properties
    - deploy.py
- 修改CommonLib根目录的gradle.properties文件
    - 将以下内容复制到CommonLib/gradle.properties中，并进行相应的修改
    

        maven_groupId=your.group.id
        artifactory_user=admin
        artifactory_password=password
        artifactory_contextUrl=http://localhost:8081/artifactory
        artifactory_snapshot_repoKey=libs-snapshot-local
        artifactory_release_repoKey=libs-release-local
        #version_prefix一般可保留为空字符串，不用修改
        version_prefix=
        
        
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
        - <code>python -r deploy.py module_name</code>
        
        
        
