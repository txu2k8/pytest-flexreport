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
from pydantic import BaseModel
import pytest
from jinja2 import Environment, FileSystemLoader


# 文件信息
class TestResult(BaseModel):
    """测试结果信息 - 数据模型"""
    title: Text = ''
    tester: Text = ''
    desc: Text = ''

    cases: Dict = {}
    modules: List = []
    history: List = []

    rerun: int = 0
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    error: int = 0
    pass_rate: int = 0

    start_time: int = 0
    run_time: int = 0
    begin_time: Text = ''


test_result = TestResult()


def pytest_make_parametrize_id(config, val, argname):
    if isinstance(val, dict):
        return val.get('title') or val.get('desc')


def pytest_runtest_logreport(report):
    report.duration = '{:.6f}'.format(report.duration)
    test_result.modules.append(report.fileName)
    if report.when == 'call':
        if report.outcome == 'passed':
            test_result.passed += 1
        elif report.outcome == 'failed':
            test_result.passed += 1
        elif report.outcome == 'skipped':
            test_result.skipped += 1
        elif report.outcome == 'error':
            test_result.error += 1
        test_result.cases[report.nodeid] = report
    elif report.outcome == 'failed':
        test_result.failed += 1
        test_result.cases[report.nodeid] = report
    elif report.outcome == 'error':
        test_result.error += 1
        test_result.cases[report.nodeid] = report
    elif report.outcome == 'skipped':
        test_result.skipped += 1
        test_result.cases[report.nodeid] = report


def pytest_sessionstart(session):
    start_ts = datetime.datetime.now()
    test_result.start_time = start_ts.timestamp()
    test_result.begin_time = start_ts.strftime("%Y-%m-%d %H:%M:%S")


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
         'run_time': result.run_time,
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
    report_path = session.config.getoption('--report') or default_report_path
    history_dir = session.config.getoption('--history_dir')
    test_result.title = session.config.getoption('--title') or '测试报告'
    test_result.tester = session.config.getoption('--tester') or 'NA'
    test_result.desc = session.config.getoption('--desc') or 'NA'
    templates_name = session.config.getoption('--template') or '1'
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

    test_result.run_time = '{:.2f} s'.format(time.time() - test_result.start_time)
    test_result.total = len(test_result.cases)
    if test_result.total != 0:
        test_result.pass_rate = '{:.2f}'.format(test_result.passed / test_result.total * 100)
    else:
        test_result.pass_rate = 0
    # 保存历史数据
    test_result.history = handle_history_data(history_dir, test_result)
    # 渲染报告
    template_path = os.path.join(os.path.dirname(__file__), './templates')
    template_static_path = os.path.join(template_path, 'static')
    # 复制渲染文件 css、js
    shutil.copyfile(os.path.join(template_static_path, "bootstrap.min.css"), os.path.join(report_static_dir, "bootstrap.min.css"))
    shutil.copyfile(os.path.join(template_static_path, "echarts.min.js"), os.path.join(report_static_dir, "echarts.min.js"))
    shutil.copyfile(os.path.join(template_static_path, "jquery.slim.min.js"), os.path.join(report_static_dir, "jquery.slim.min.js"))
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template(f'template{templates_name}.html')
    report = template.render(dict(test_result))
    with open(report_path, 'wb') as f:
        f.write(report.encode('utf8'))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    fixture_extras = getattr(item.config, "extras", [])
    plugin_extras = getattr(report, "extra", [])
    report.extra = fixture_extras + plugin_extras
    report.fileName = item.location[0]
    if hasattr(item, 'callspec'):
        report.desc = item.callspec.id or item._obj.__doc__
    else:
        report.desc = item._obj.__doc__
    report.method = item.location[2].split('[')[0]


def pytest_addoption(parser):
    group = parser.getgroup("testreport")
    group.addoption(
        "--report",
        action="store",
        metavar="path",
        default=None,
        help="create html report file at given path.",
    )
    group.addoption(
        "--history_dir",
        action="store",
        metavar="path",
        default=None,
        help="create html report history dir path.",
    )
    group.addoption(
        "--title",
        action="store",
        metavar="path",
        default=None,
        help="pytest-testreport Generate a title of the repor",
    )
    group.addoption(
        "--tester",
        action="store",
        metavar="path",
        default=None,
        help="pytest-testreport Generate a tester of the report",
    )
    group.addoption(
        "--desc",
        action="store",
        metavar="path",
        default=None,
        help="pytest-testreport Generate a description of the report",
    )
    group.addoption(
        "--template",
        action="store",
        metavar="path",
        default=None,
        help="pytest-testreport Generate a template of the report",
    )


if __name__ == '__main__':
    pass
    print(dict(TestResult()))
