#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_demo1.py
@time:2023/1/31
@email:tao.xu2008@outlook.com
@description: 
"""
import time
import allure


@allure.epic("OM")
@allure.story("登录")
@allure.feature("正常")
class TestDemo1(object):
    def test_1(self):
        time.sleep(1)
        print("TestDemo1--->>> test_1")
        assert 3 + 2 == 5

    def test_2(self):
        assert 3 + 2 == 6

    def test_3(self):
        assert 3 + 2 == 5

    def test_4(self):
        assert 3 + 2 == 5


@allure.epic("OM")
@allure.story("首页")
@allure.feature("正常")
class TestDemo22(object):
    def test_221(self):
        print("TestDemo1--->>> test_1")
        assert 3 + 2 == 5

    def test_222(self):
        assert 3 + 2 == 6

    def test_223(self):
        assert 3 + 2 == 5

    def test_224(self):
        assert 3 + 2 == 5


if __name__ == '__main__':
    pass
