#!/usr/bin/python
# coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: lkq <lkq@bt.cn>
# -------------------------------------------------------------------
# Time: 2022-08-10
# -------------------------------------------------------------------
# Mysql 弱口令检测
# -------------------------------------------------------------------

import  public, os
_title = 'Mysql 弱口令检测'
_version = 1.0  # 版本
_ps = "Mysql 弱口令检测"  # 描述
_level = 3  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-8-10'  # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_mysql_pass.pl")
_tips = [
    "如果检测出为弱口令请及时修改密码"
]
_help = ''


def check_run():
    '''
        @name Mysql 弱口令检测
        @time 2022-08-12
        @author lkq@bt.cn
    '''
    pass_info = public.ReadFile("/www/server/panel/config/weak_pass.txt")
    if not pass_info: return True, '无风险'
    pass_list = pass_info.split('\n')
    data=public.M("databases").select()
    ret=""
    for i in data:
        if i['password'] in pass_list:
            ret+="数据库："+i['name']+"存在弱口密码："+i['password']+"\n"
    if ret:
        return False, ret
    else:
        return True, '无风险'

