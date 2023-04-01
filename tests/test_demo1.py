#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_demo.py
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import time
import allure


@allure.epic("一级模块")
@allure.story("二级模块")
@allure.feature("Demo1")
@allure.suite("正常")
class TestDemo1(object):

    def test_1(self):
        time.sleep(1)
        assert 3 + 2 == 5

    def test_2(self):
        assert 3 + 2 == 6

    def test_3(self):
        assert 3 + 2 == 5

    def test_4(self):
        assert 3 + 2 == 5


if __name__ == '__main__':
    pass
