#coding: utf-8
import sys,os
os.chdir('/www/server/panel/')
sys.path.insert(0,"class/")
import public
import http_requests
http_requests.DEFAULT_TYPE = 'src'

#url1 = 'https://check.bt.cn/api/panel/check_files'
pdata = {'panel_version': public.version(), 'address': public.get_ipaddress()}
#result = http_requests.post(url1, pdata).text
result = '{"status":false,"msg":"\u5f53\u524d\u7248\u672c\u65e0\u9700\u6821\u9a8c\u6587\u4ef6\u5b8c\u6574\u6027"}'
print(result)
