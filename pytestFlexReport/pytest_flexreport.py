#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:pytest_flexreport
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import datetime
import json
import os
import time
import shutil
from typing import Text, Dict, List
from collections import defaultdict
from pydantic import BaseModel
import pytest
from jinja2 import Environment, FileSystemLoader
from pytestFlexReport.module_define_init_ import ModuleDefineInit
from pytestFlexReport import utils


# 结果统计
class StatisticsOutcome(BaseModel):
    """结果统计 - 数据模型"""
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    total: int = 0
    pass_rate: float = 0
    duration: int = 0  # 耗时 秒


# 模块树统计测试结果
class ModuleResult(BaseModel):
    idx: int = 0  # 序号
    name: Text = ''  # 模块名称
    first: bool = False  # 标记是否第一个模块/子模块
    subs_len: int = 0  # 子模块数量
    subs_len_v3: int = 0  # 包含三级模块数量
    subs: Dict = {}  # 子模块：name=StatisticsModule()
    outcome: StatisticsOutcome = StatisticsOutcome()  # 结果统计


# 测试结果
class TestResult(StatisticsOutcome):
    """测试结果信息 - 数据模型"""
    title: Text = ''
    tester: Text = ''
    desc: Text = ''
    log_path: Text = ''
    report_path: Text = ''

    start_time: int = 0
    begin_time: Text = ''

    cases: Dict = {}
    modules: List = []
    history: List = []
    module_result: Dict = defaultdict(dict)  # 按模块统计测试结果
    module_outcome: Dict = defaultdict(dict)  # 按模块统计测试结果
    report_sort: bool = False  # 参数报告中模块按名称排序


result = TestResult()


def format_module_result(module_result: ModuleResult) -> ModuleResult:
    module_result.outcome.duration = utils.seconds_to_hms(module_result.outcome.duration)
    if module_result.outcome.total != 0:
        rate = module_result.outcome.passed / module_result.outcome.total * 100
        module_result.outcome.pass_rate = utils.remove_decimal0(float('{:.1f}'.format(rate)))
    else:
        module_result.outcome.pass_rate = 0
    return module_result


def pytest_make_parametrize_id(config, val, argname):
    if isinstance(val, dict):
        return val.get('title') or val.get('desc')


def pytest_runtest_logreport(report):
    if report.moduleName not in result.modules:
        result.modules.append(report.moduleName)  # template1/template2
    m1, m2, m3 = report.module_name_v3
    if m1 not in result.module_result:
        result.module_result[m1] = ModuleResult(name=m1)
        result.module_result[m1].idx = len(result.module_result)
    if m2 not in result.module_result[m1].subs:
        result.module_result[m1].subs_len += 1
        result.module_result[m1].subs[m2] = ModuleResult(name=m2)
        result.module_result[m1].subs[m2].idx = len(result.module_result[m1].subs)
    if m3 not in result.module_result[m1].subs[m2].subs:
        result.module_result[m1].subs[m2].subs_len += 1
        result.module_result[m1].subs[m2].subs[m3] = ModuleResult(name=m3)
        result.module_result[m1].subs[m2].subs[m3].idx = len(result.module_result[m1].subs[m2].subs)
        # subs_len_v3
        result.module_result[m1].subs_len_v3 += 1
        result.module_result[m1].subs[m2].subs_len_v3 += 1

    if report.when == 'setup':
        result.total += 1
        result.module_result[m1].outcome.total += 1
        result.module_result[m1].subs[m2].outcome.total += 1
        result.module_result[m1].subs[m2].subs[m3].outcome.total += 1
        if report.outcome != 'passed':
            result.error += 1
            result.module_result[m1].outcome.error += 1
            result.module_result[m1].subs[m2].outcome.error += 1
            result.module_result[m1].subs[m2].subs[m3].outcome.error += 1
    elif report.when == 'call':
        setattr(result, report.outcome, getattr(result, report.outcome)+1)
        setattr(result.module_result[m1].outcome, report.outcome, getattr(result.module_result[m1].outcome, report.outcome)+1)
        setattr(result.module_result[m1].subs[m2].outcome, report.outcome, getattr(result.module_result[m1].subs[m2].outcome, report.outcome)+1)
        setattr(result.module_result[m1].subs[m2].subs[m3].outcome, report.outcome, getattr(result.module_result[m1].subs[m2].subs[m3].outcome, report.outcome)+1)

    result.module_result[m1].outcome.duration += report.duration
    result.module_result[m1].subs[m2].outcome.duration += report.duration
    result.module_result[m1].subs[m2].subs[m3].outcome.duration += report.duration
    result.duration += report.duration

    report.duration = '{:.2f}'.format(float(report.duration))
    result.cases[report.nodeid] = report


def pytest_sessionstart(session):
    start_ts = datetime.datetime.now()
    result.start_time = start_ts.timestamp()
    result.begin_time = start_ts.strftime("%Y-%m-%d %H:%M:%S")


def handle_history_data(report_dir, result: TestResult):
    """
    处理历史数据
    :return:
    """
    try:
        with open(os.path.join(report_dir, 'history.json'), 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []
    history.append(
        {'success': result.passed,
         'total': result.total,
         'fail': result.failed,
         'skip': result.skipped,
         'error': result.error,
         'duration': result.duration,
         'begin_time': result.begin_time,
         'pass_rate': result.pass_rate,
         }
    )

    with open(os.path.join(report_dir, 'history.json'), 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=True)
    return history


def pytest_sessionfinish(session):
    """在整个测试运行完成之后调用的钩子函数,可以在此处生成测试报告"""
    default_report_path = os.path.join('reports', time.strftime("%Y-%m-%d_%H_%M_%S") + '.html')
    templates_name = session.config.getoption('--template') or '1'
    report_path = session.config.getoption('--report') or default_report_path
    history_dir = session.config.getoption('--history_dir')
    result.title = session.config.getoption('--title') or '测试报告'
    result.tester = session.config.getoption('--tester') or 'NA'
    result.desc = session.config.getoption('--desc') or 'NA'
    result.log_path = session.config.getoption('--log_path') or 'NA'
    result.report_path = session.config.getoption('--report_path') or 'NA'
    result.report_sort = session.config.getoption('--report_sort') or False
    if not report_path.endswith('.html'):
        report_path = report_path + '.html'

    report_dir = os.path.dirname(report_path) or 'reports'
    report_static_dir = os.path.join(report_dir, "static")
    history_dir = history_dir or report_dir
    if os.path.isdir(report_dir):
        pass
    else:
        os.makedirs(report_dir, exist_ok=True)
    if os.path.isdir(report_static_dir):
        pass
    else:
        os.makedirs(report_static_dir, exist_ok=True)

    result.duration = utils.seconds_to_hms((time.time() - result.start_time))
    if result.total != 0:
        rate = result.passed / result.total * 100
        result.pass_rate = utils.remove_decimal0(float('{:.1f}'.format(rate)))
    else:
        result.pass_rate = 0

    # 处理模块统计数据
    for m1 in result.module_result.keys():
        result.module_result[m1] = format_module_result(result.module_result[m1])
        for m2 in result.module_result[m1].subs.keys():
            result.module_result[m1].subs[m2] = format_module_result(result.module_result[m1].subs[m2])
            for m3 in result.module_result[m1].subs[m2].subs.keys():
                result.module_result[m1].subs[m2].subs[m3] = format_module_result(result.module_result[m1].subs[m2].subs[m3])
    # 保存历史数据
    result.history = handle_history_data(history_dir, result)
    # 渲染报告
    template_path = os.path.join(os.path.dirname(__file__), './templates')
    template_static_path = os.path.join(template_path, 'static')
    # 复制渲染文件 css、js
    shutil.copyfile(os.path.join(template_static_path, "bootstrap.min.css"), os.path.join(report_static_dir, "bootstrap.min.css"))
    shutil.copyfile(os.path.join(template_static_path, "echarts.min.js"), os.path.join(report_static_dir, "echarts.min.js"))
    shutil.copyfile(os.path.join(template_static_path, "jquery.slim.min.js"), os.path.join(report_static_dir, "jquery.slim.min.js"))
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(f'template{templates_name}.html')
    report = template.render(dict(result))
    with open(report_path, 'wb') as f:
        f.write(report.encode('utf8'))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    fixture_extras = getattr(item.config, "extras", [])
    plugin_extras = getattr(report, "extra", [])
    report.extra = fixture_extras + plugin_extras

    # 获取用例模块名，例如：
    # @allure.epic("对象存储")
    # @allure.story("桶")
    # @allure.feature("对象")
    module_dict = defaultdict(str)
    if hasattr(item.instance, 'pytestmark'):
        for pm in item.instance.pytestmark:
            if 'label_type' in pm.kwargs:
                module_dict[pm.kwargs["label_type"]] = pm.args[0]
    for om in item.own_markers:
        if 'label_type' in om.kwargs:
            module_dict[om.kwargs["label_type"]] = om.args[0]

    # 三级模块
    module_name_v3 = [
        module_dict['epic'],
        module_dict['story'],
        module_dict['feature'],
    ]

    # 未设置allure模块名，则获取__init__.py中定义的模块名称，例如：
    # __module_zh__ = 'tests'
    if not (module_dict['epic'] or module_dict['story'] or module_dict['feature']):
        testcase_basename = item.config.getoption('--testcase_basename')
        test_case_modules = ModuleDefineInit().get_testcase_module_list(
            item.fspath.dirname, testcase_basename or item.config.rootdir.basename
        )
        # 如果__init__.py中也未定义的模块名称，取py模块名称
        if len(test_case_modules) == 0:
            test_case_modules = [item.location[0]]
        # 赋值到三级模块列表
        for idx, m in enumerate(test_case_modules):
            module_name_v3[idx] = m

    # print(module_name_list)
    report.moduleName = '/'.join(module_name_v3)
    report.module_name_v3 = module_name_v3

    if hasattr(item, 'callspec'):
        report.desc = item.callspec.id or item._obj.__doc__
    else:
        report.desc = item._obj.__doc__
    report.method = item.location[2].split('[')[0]


def pytest_addoption(parser):
    group = parser.getgroup("flex_report")
    group.addoption(
        "--template",
        action="store",
        metavar="path",
        default=None,
        help="测试报告模板选择（1，2，3）",
    )
    group.addoption(
        "--report",
        action="store",
        metavar="path",
        default=None,
        help="报告生成绝对路径，/*/*.html.",
    )
    group.addoption(
        "--history_dir",
        action="store",
        metavar="path",
        default=None,
        help="测报告历史记录history.json的目录路径，默认使用html文件同级目录",
    )
    group.addoption(
        "--title",
        action="store",
        metavar="path",
        default="测试报告",
        help="测试报告标题，回填到报告",
    )
    group.addoption(
        "--tester",
        action="store",
        metavar="path",
        default=None,
        help="测试人员，回填到报告",
    )
    group.addoption(
        "--desc",
        action="store",
        metavar="path",
        default=None,
        help="测试构建描述，回填到报告",
    )
    group.addoption(
        "--log_path",
        action="store",
        metavar="path",
        default=None,
        help="测试日志路径，回填到报告（template=3）",
    )
    group.addoption(
        "--report_path",
        action="store",
        metavar="path",
        default=None,
        help="测试报告路径，回填到报告（template=3）",
    )
    group.addoption(
        "--testcase_basename",
        action="store",
        metavar="path",
        default=None,
        help="测试用例root-dir basename，供遍历__init__.py查找模块名",
    )
    group.addoption(
        "--report_sort",
        action="store_true",
        default=False,
        dest="report_sort",
        help="测试报告中，模块列表按名称排序",
    )


if __name__ == '__main__':
    pass
    print(dict(TestResult()))
