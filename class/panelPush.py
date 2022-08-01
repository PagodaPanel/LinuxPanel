#coding: utf-8
# +-------------------------------------------------------------------
# | 宝塔Linux面板
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2016 宝塔软件(http://www.bt.cn) All rights reserved.
# +-------------------------------------------------------------------
# | Author: 沐落 <cjx@bt.cn>
# | Author: lx
# | 消息推送管理
# | 对外方法 get_modules_list、install_module、uninstall_module、get_module_template、set_push_config、get_push_config、del_push_config
# +-------------------------------------------------------------------
from ast import mod
import os, sys
panelPath = "/www/server/panel"
os.chdir(panelPath)
sys.path.insert(0,panelPath + "/class/")
import public,re,json,time
try:
    from BTPanel import session
except :
    pass
class panelPush:

    __conf_path =  "{}/class/push/push.json".format(panelPath)
    def __init__(self):
        spath = '{}/class/push'.format(panelPath)
        if not os.path.exists(spath): os.makedirs(spath)

    """
    @获取推送模块列表
    """
    def get_modules_list(self,get):
        cpath = '{}/class/push/push_list.json'.format(panelPath)
        try:
            spath = os.path.dirname(cpath)
            if not os.path.exists(spath): os.makedirs(spath)

            if 'force' in get or not os.path.exists(cpath):
                if not 'download_url' in session: session['download_url'] = public.get_url()
                public.downloadFile('{}/linux/panel/push/push_list.json'.format(session['download_url']),cpath)
        except : pass

        if not os.path.exists(cpath):
            return {}

        data = {}
        push_list = self._get_conf()
        module_list = public.get_modules('class/push')

        configs = json.loads(public.readFile(cpath))
        for p_info in configs:
            p_info['data'] = {}
            p_info['setup'] = False
            p_info['info'] = False
            key = p_info['name']
            try:
                if hasattr(module_list, key):
                    p_info['setup'] = True
                    # if key in module_list:
                    #     print(dir(module_list))
                    #     print(dir(module_list[key]))
                    #     print(dir(getattr(module_list[key], key)))
                    push_module = getattr(module_list[key], key)()
                    p_info['info'] = push_module.get_version_info(None);
                    #格式化消息通道
                    if key in push_list:
                        p_info['data'] = self.__get_push_list(push_list[key])
                    #格式化返回执行周期
                    if hasattr(push_module,'get_push_cycle'):
                        p_info['data'] = push_module.get_push_cycle(p_info['data'])
            except :
                return public.get_error_object(None)
            data[key] = p_info
        return data

    """
    安装/更新消息通道模块
    @name 需要安装的模块名称
    """
    def install_module(self,get):
        module_name = get.name
        down_url = public.get_url()

        local_path = '{}/class/push'.format(panelPath)
        if not os.path.exists(local_path): os.makedirs(local_path)

        sfile = '{}/{}.py'.format(local_path,module_name)
        public.downloadFile('{}/linux/panel/push/{}.py'.format(down_url,module_name),sfile)
        if not os.path.exists(sfile): return public.returnMsg(False, '【{}】模块安装失败'.format(module_name))
        if os.path.getsize(sfile) < 1024: return public.returnMsg(False, '【{}】模块安装失败'.format(module_name))

        sfile = '{}/class/push/{}.html'.format(panelPath,module_name)
        public.downloadFile('{}/linux/panel/push/{}.html'.format(down_url,module_name),sfile)

        return public.returnMsg(True, '【{}】模块安装成功.'.format(module_name))

    """
    卸载消息通道模块
    @name 需要卸载的模块名称
    """
    def uninstall_module(self,get):
        module_name = get.name
        sfile = '{}/class/push/{}.py'.format(panelPath,module_name)
        if os.path.exists(sfile): os.remove(sfile)

        return public.returnMsg(True, '【{}】模块卸载成功'.format(module_name))


    """
    @获取模块执行日志
    """
    def get_module_logs(self,get):
        module_name = get.name
        id = get.id
        return []

    """
    获取模块模板
    """
    def get_module_template(self,get):
        sfile = '{}/class/push/{}.html'.format(panelPath,get.module_name)

        if not os.path.exists(sfile):
            return public.returnMsg(False, '模板文件不存在.')

        shtml = public.readFile(sfile)
        return public.returnMsg(True, shtml)


    """
    @获取模块推送参数，如：panel_push ssl到期，服务停止
    """
    def get_module_config(self,get):
        module = get.name
        p_list = public.get_modules('class/push')
        push_module = getattr(p_list[module], module)()

        if not module in p_list:
            return public.returnMsg(False, '指定模块{}未安装.'.format(module))

        if not hasattr(push_module,'get_module_config'):
            return public.returnMsg(False, '指定模块{}不存在 get_module_config 方法.'.format(module))
        return push_module.get_module_config(get)

    """
    @获取模块配置项
    @优先调用模块内的get_push_config
    """
    def get_push_config(self,get):
        module = get.name
        id = get.id
        p_list = public.get_modules('class/push')

        if not module in p_list:
            return public.returnMsg(False, '指定模块{}未安装.'.format(module))
        push_module = getattr(p_list[module], module)()
        if not hasattr(push_module,'get_push_config'):
            push_list = self._get_conf()
            return push_list[module][id]
        return push_module.get_push_config(get)

    """
    @设置推送配置
    @优先调用模块内的set_push_config
    """
    def set_push_config(self,get):
        module = get.name
        id = get.id
        p_list = public.get_modules('class/push')

        if not module in p_list:
            return public.returnMsg(False, '指定模块{}未安装.'.format(module))

        pdata = json.loads(get.data)
        pdata = self.__get_args(pdata,'cycle',1)
        pdata = self.__get_args(pdata,'count',1)
        pdata = self.__get_args(pdata,'interval',600)
        pdata = self.__get_args(pdata,'key','')
        class_obj = getattr(p_list[module], module)()
        if hasattr(class_obj,'set_push_config'):
            get['data'] = json.dumps(pdata)
            result = class_obj.set_push_config(get)
            if 'status' in result: return result

            data = result
        else:
            data = self._get_conf()
            if not module in data:data[module] = {}
            data[module][id] = pdata

        public.writeFile(self.__conf_path,json.dumps(data))
        return public.returnMsg(True, '保存成功.')

    """
    @设置推送状态
    """
    def set_push_status(self,get):
        id = get.id
        module = get.name

        data = self._get_conf()
        if not module in data: return public.returnMsg(True, '模块名称不存在.')
        if not id in data[module]: return public.returnMsg(True, '指定推送任务不存在.')

        status = int(get.status)
        if status:
            data[module][id]['status'] = True
        else:
            data[module][id]['status'] =  False
        public.writeFile(self.__conf_path,json.dumps(data))
        return public.returnMsg(True, '操作成功.')
    """
    @删除指定配置
    """
    def del_push_config(self,get):
        id = get.id
        module = get.name

        p_list = public.get_modules('class/push')
        if not module in p_list:
            return public.returnMsg(False, '指定模块{}未安装.'.format(module))
        push_module = getattr(p_list[module], module)()
        if not hasattr(push_module,'del_push_config'):
            data = self._get_conf()
            del data[module][id]
            public.writeFile(self.__conf_path,json.dumps(data))
            return public.returnMsg(True, '删除成功.')

        return push_module.del_push_config(get)

    """
    获取消息通道配置列表
    """
    def get_push_msg_list(self,get):
        data = {}
        msgs = self.__get_msg_list()
        from panelMessage import panelMessage
        pm = panelMessage()
        for x in msgs:
            x['setup'] = False
            key = x['name']
            try:
                obj =  pm.init_msg_module(key)
                if obj:
                    x['setup'] = True
                    if key == 'sms':x['title'] = '{}<a title="请确保有足够的短信条数，否则您将无法收到通知." href="javascript:;" class="bt-ico-ask">?</a>'.format(x['title'])
            except :
                pass
            data[key] = x
        return data

    """
    @ 获取消息推送配置
    """
    def _get_conf(self):
        data = {}
        if os.path.exists(self.__conf_path):
            data = json.loads(public.readFile(self.__conf_path))
        return data

    """
    @ 获取插件版本信息
    """
    def get_version_info(self):
        """
        获取版本信息
        """
        data = {}
        data['ps'] = ''
        data['version'] = '1.0'
        data['date'] = '2020-07-14'
        data['author'] = '宝塔'
        data['help'] = 'http://www.bt.cn'
        return data

    """
    @格式化推送对象
    """
    def format_push_data(self,push = ['dingding','weixin','feishu'], project = '', type = ''):
        item = {
            'title':'',
            'project':project,
            'type':type,
            'cycle':1,
            'count':1,
            'keys':[],
            'helps':[],
            'push':push
        }
        return item



    def push_message_immediately(self, channel_data):
        """推送消息到指定的消息通道，即时

        Args:
            channel_data(dict):
                key: msg_channel, 消息通道名称，多个用逗号相连
                value: msg obj, 每种消息通道的消息内容格式，可能包含标题

        Returns:
            {
                status: True/False,
                msg: {
                    "email": {"status": msg},
                    ...
                }
            }
        """
        if type(channel_data) != dict:
            return public.returnMsg(False, "参数有误")

        from panelMessage import panelMessage
        pm = panelMessage()
        channel_res = {}
        res = {
            "status": False,
            "msg": channel_res
        }

        for module, msg in channel_data.items():
            modules = []
            if module.find(",") != -1:
                modules = module.split(",")
            else:
                modules.append(module)
            for m_module in modules:
                msg_obj = pm.init_msg_module(m_module)
                if not msg_obj:continue
                ret = msg_obj.push_data(msg)
                if ret and "status" in ret and ret['status']:
                    res["status"] = True
                    channel_res[m_module] = ret
                else:
                    msg = "消息推送失败。"
                    if "msg" in ret:
                        msg = ret["msg"]
                    channel_res[m_module] = public.returnMsg(False, msg)
        return res

    """
    @格式为消息通道格式
    """
    def format_msg_data(self):
        data = {
            'title':'',
            'to_email':'',
            'sms_type':'',
            'sms_argv':{},
            'msg':''
        }
        return data

    def __get_msg_list(self):
        """
        获取消息通道列表
        """
        data = []
        cpath = '{}/data/msg.json'.format(panelPath)
        if not os.path.exists(cpath):
            return data
        try:
            conf = public.readFile(cpath)
            data = json.loads(conf)
        except :
            try:
                time.sleep(0.5)
                conf = public.readFile(cpath)
                data = json.loads(conf)
            except:pass

        return data

    def __get_args(self,data,key,val = ''):
        """
        @获取默认参数
        """
        if not key in data: data[key] = val
        if type(data[key]) != type(val):
            data[key] = val
        return data


    def __get_push_list(self,data):
        """
        @格式化列表数据
        """
        m_data = {}
        result = {}
        for x in self.__get_msg_list(): m_data[x['name']] = x

        for skey in data:
            result[skey] = data[skey]

            m_list = []
            for x in data[skey]['module'].split(','):
                if x in m_data: m_list.append(m_data[x]['title'])
            result[skey]['m_title'] = '、'.join(m_list)

            m_cycle =[]
            if data[skey]['cycle'] > 1:
                m_cycle.append('每{}秒'.format(data[skey]['cycle']))
            m_cycle.append('{}次，间隔{}秒'.format(data[skey]['count'],data[skey]['interval']))
            result[skey]['m_cycle'] = ''.join(m_cycle)

        return result


    #************************************************推送
    """
    @推送data/push目录的所有文件
    """
    def push_messages_from_file(self):

        path = "{}/data/push".format(panelPath)
        if not os.path.exists(path): os.makedirs(path)

        from panelMessage import panelMessage
        pm = panelMessage()

        for x in os.listdir(path):
            try:
                spath = '{}/{}'.format(path,x)
                data = json.loads(public.readFile(spath))

                msg_obj = pm.init_msg_module(data['module'])
                if not msg_obj:continue;

                ret = msg_obj.push_data(data)
                if ret['status']: pass

                os.remove(spath)
            except :
                print(public.get_error_info())

    """
    @消息推送线程
    """
    def start(self):

        total = 0
        interval = 5
        try:
            if True:
                # 推送文件
                self.push_messages_from_file()

                # 调用推送子模块
                data = {}
                is_write = False
                path = "{}/class/push/push.json".format(panelPath)

                if os.path.exists(path):
                    data = public.readFile(path)
                    data = json.loads(data)

                p = public.get_modules('class/push')

                from panelMessage import panelMessage
                pm = panelMessage()

                for skey in data:
                    if len(data[skey]) <= 0: continue
                    if skey in ['panelLogin_push']: continue #面板登录主动触发

                    total = None
                    obj = getattr(p[skey], skey)()

                    for x in data[skey]:
                        try:
                            item = data[skey][x]
                            if not item['status']: continue
                            if not 'index' in item: item['index'] = 0


                            if not total: total = obj.get_total()
                            rdata = obj.get_push_data(item,total)

                            for m_module in item['module'].split(','):
                                print(m_module,rdata)
                                if not m_module in rdata: continue

                                msg_obj = pm.init_msg_module(m_module)
                                if not msg_obj:continue;


                                ret = msg_obj.push_data(rdata[m_module])

                                if ret['status']:
                                    is_write = True
                                    data[skey][x]['index'] = rdata['index']
                                    #print(ret)
                        except :
                            print(public.get_error_info())

                if is_write: public.writeFile(path,json.dumps(data));
                # time.sleep(interval)
        except :

            print(public.get_error_info())

        # self.start()

if __name__ == '__main__':
    panelPush().start()