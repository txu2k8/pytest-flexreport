#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:utils
@time:2023/04/02
@email:tao.xu2008@outlook.com
@description:
"""


def seconds_to_hms(seconds) -> str:
    """
    秒数转换为字符串 "时:分:秒"
    :param seconds:
    :return:时:分:秒，如 3:40:33
    """
    if seconds < 60:
        return "{:.1f} s".format(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(m, 24)
    if d > 0:
        return "%d天%d小时%d分%d秒" % (d, h, m, s)
    elif h > 0:
        return "%d小时%d分%d秒" % (h, m, s)
    elif m > 0:
        return "%d分%d秒" % (m, s)

    return "%d:%02d:%02d" % (h, m, s)


def remove_decimal0(num):
    """
    去掉小数后面的0，例如：
    0.0  --> 0
    100.0 --> 100
    33.20 --> 33.2
    :param num:
    :return:
    """
    int_num = int(num)
    float_num = float(num)
    return int_num if float_num == int_num else float_num


if __name__ == '__main__':
    print(remove_decimal0(float('{:.1f}'.format(33.01))))
