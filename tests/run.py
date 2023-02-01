#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:run.py
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import json
import pytest


def main():
    # - 构建pytest 参数
    print("构建pytest 参数...")
    pytest_files_set = ['./test_demo.py']
    argv = pytest_files_set + [
        # pytest-testreport
        '--report=demo',
        '--title=测试报告：demo（ID=xxx）',
        '--template=2',
    ]
    print("pytest 命令：{}\n".format(json.dumps(argv, indent=2)))

    pytest.main(argv)


if __name__ == '__main__':
    main()
