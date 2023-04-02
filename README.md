# pytest-flexreport

### 1、介绍
pytest-flexreport是针对pytest的生成html报告的插件，自动收集用例执行的详细日志信息，以及相关错误和输出信息。
使用起来非常简单，安装好pytest-testreport之后，运行用例时加上参数即可生成报告   

### 2、安装

pytest-testreport是基于python3.7+开发的，安装前请确认你的python版本>3.7

安装命令

```pip install pytest-flexreport```

### 3、快速开始

###### 注意：如果安装了pytest-html这个插件，可能会有冲突，如果冲突则先卸载pytest-html

##### 3.1 template介绍
- --template=1：白底报告，以用例为维度，含详情
- --template=2：蓝底报告，以用例为维度，含详情
- --template=3：蓝底报告，结果概述，统计模块通过率（使用场景：邮件发送summary）

##### 3.2 使用案例

- ###### 命令行执行： pytest 运行测试时加上参数--report 指定报告文件名

    ```shell
    # 指定报告文件名
    pytest --report=demo-report.html
    
    #其他配置参数
    --template=3, 测试报告模板选择(1,2,3)
    --report=/*/*.html, 报告生成绝对路径
    --history_dir=history.json的目录路径,默认使用html文件同级目录
    --title=测试报告标题, 回填到报告
    --tester=测试人员,回填到报告
    --desc=测试构建描述,回填到报告
    --log_path=测试日志路径, 回填到报告(template=3)
    --report_path=测试报告详情路径, 回填到报告(template=3)
    --testcase_basename=测试用例root-dir basename, 供遍历__init__.py查找模块名(template=3)
    
    # 同时使用多个参数
    pytest --report=report.html --history_dir=./reports --title=测试报告 --tester=txu --desc=项目描述
    ```
    
- ###### pytest.main执行

    ```shell
    import pytest
    
    pytest.main(['--report=demo-report.html',
                 '--history_dir=./reports',
                 '--title=测试报告标题',
                 '--tester=txu',
                 '--desc=报告描述信息'])
    ```



