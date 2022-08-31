#coding: utf-8
import sys,os
os.chdir('/www/server/panel/')
sys.path.insert(0,"class/")
import PluginLoader
import public
import time


def flush_cache():
    '''
        @name 更新缓存
        @author hwliang
        @return void
    '''
    try:
        start_time = time.time()
        res = PluginLoader.get_plugin_list(1)
        spath = '{}/data/pay_type.json'.format(public.get_panel_path())
        public.downloadFile(public.get_url() + '/install/lib/pay_type.json',spath)
        import plugin_deployment
        plugin_deployment.plugin_deployment().GetCloudList(None)

        timeout = time.time() - start_time
        if res['ip']:
            public.print_log("缓存更新成功,耗时: %.2f 秒" % timeout)
        else:
            if isinstance(res,dict) and not 'msg' in res: res['msg'] = '连接服务器失败!'
            public.print_log("缓存更新失败: {}".format(res['msg']))
    except:
        public.print_log("缓存更新失败: {}".format(public.get_error_info()))





if __name__ == '__main__':
    flush_cache()
