#!/usr/bin/python
#coding: utf-8
# -------------------------------------------------------------------
# 宝塔Linux面板
# -------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
# -------------------------------------------------------------------
# Author: lkq <lkq@bt.cn>
# -------------------------------------------------------------------
# Time: 2022-08-10
# -------------------------------------------------------------------
# PHP未禁用函数
# -------------------------------------------------------------------


import sys,os
os.chdir('/www/server/panel')
sys.path.append("class/")

import public,re,os

_title = 'PHP未禁用危险函数'
_version = 1.0                              # 版本
_ps = "PHP未禁用危险函数"          # 描述
_level = 3                                  # 风险级别： 1.提示(低)  2.警告(中)  3.危险(高)
_date = '2022-8-10'                        # 最后更新时间
_ignore = os.path.exists("data/warning/ignore/sw_php_php_disable_funcation.pl")
_tips = [
    "在【php.ini】文件中设置【disable_functions】未配置system,exec,passthru,shell_exec,popen,proc_open等危险函数",
    "提示：【php.ini】未配置system,exec,passthru,shell_exec,popen,proc_open等危险函数"
    ]

_help = ''

def check_run():
    path ="/www/server/php"
    #获取目录下的文件夹
    dirs = os.listdir(path)
    result={}
    for dir in dirs:
        if dir in ["52","53","54","55","56","70","71","72","73","74","80","81"]:
            file_path=path+"/"+dir+"/etc/php.ini"
            if os.path.exists(file_path):
                #获取文件内容
                try:
                    php_ini = public.readFile(file_path)
                    if re.search("\ndisable_functions\\s?=\\s?(.+)",php_ini):
                        disable_functions = re.findall("\ndisable_functions\\s?=\\s?(.+)",php_ini)
                        disa_fun=["system","exec","passthru","shell_exec","popen","proc_open","putenv"]
                        if len(disable_functions) > 0:
                            disable_functions= disable_functions[0].split(",")
                            for i2 in disa_fun:
                                if i2 not in disable_functions:
                                    if dir in  result:
                                        result[dir].append(i2)
                                    else:
                                        result[dir]=[i2]
                except:
                    pass
    if result:
        ret=""
        for i in result:
            ret+="【PHP"+i+"】未禁用的危险函数如下:"+",".join(result[i])+"\n"
        return False,ret
    else:
        return True, "无风险"

