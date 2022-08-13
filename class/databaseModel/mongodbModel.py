#coding: utf-8
#-------------------------------------------------------------------
# 宝塔Linux面板
#-------------------------------------------------------------------
# Copyright (c) 2015-2099 宝塔软件(http://bt.cn) All rights reserved.
#-------------------------------------------------------------------
# Author: hwliang <hwl@bt.cn>
#-------------------------------------------------------------------
#角色说明：
#read：允许用户读取指定数据库
#readWrite：允许用户读写指定数据库
#dbAdmin：允许用户在指定数据库中执行管理函数，如索引创建、删除，查看统计或访问system.profile
#userAdmin：允许用户向system.users集合写入，可以找指定数据库里创建、删除和管理用户
#clusterAdmin：只在admin数据库中可用，赋予用户所有分片和复制集相关函数的管理权限。
#readAnyDatabase：只在admin数据库中可用，赋予用户所有数据库的读权限
#readWriteAnyDatabase：只在admin数据库中可用，赋予用户所有数据库的读写权限
#userAdminAnyDatabase：只在admin数据库中可用，赋予用户所有数据库的userAdmin权限
#dbAdminAnyDatabase：只在admin数据库中可用，赋予用户所有数据库的dbAdmin权限。
#root：只在admin数据库中可用。超级账号，超级权限

# sqlite模型
#------------------------------
import os,re,json,time
from databaseModel.base import databaseBase
import public
try:
    import pymongo
except:
    public.ExecShell("btpip install pymongo")
    import pymongo
try:
    from BTPanel import session
except :pass


class panelMongoDB():

    __DB_PASS = None
    __DB_USER = None
    __DB_PORT = 27017
    __DB_HOST = '127.0.0.1'
    __DB_CONN = None
    __DB_ERR = None

    __DB_CLOUD = None
    def __init__(self):
        self.__config = self.get_options(None)

    def __Conn(self,auth):

        if not self.__DB_CLOUD:
            path = '{}/data/mongo.root'.format(public.get_panel_path())
            if os.path.exists(path): self.__DB_PASS = public.readFile(path)
            self.__DB_PORT = int(self.__config['port'])

        try:
            if not self.__DB_USER and auth:
                self.__DB_USER = "root"
            self.__DB_CONN = pymongo.MongoClient(host=self.__DB_HOST, port=self.__DB_PORT, username = self.__DB_USER, password=self.__DB_PASS)
            self.__DB_CONN.admin.command({"listDatabases":1})
            return True
        except :
            try:
                self.__DB_CONN = pymongo.MongoClient(host=self.__DB_HOST, port=self.__DB_PORT, username = self.__DB_USER, password=self.__DB_PASS)
                self.__DB_CONN.admin.authenticate('root', self.__DB_PASS)
                return True
            except :
                self.__DB_ERR = public.get_error_info()
        return False


    def get_db_obj(self,db_name = 'admin',auth=0):
        """
        @获取连接对象
        """
        if not self.__Conn(auth): return self.__DB_ERR

        return self.__DB_CONN[db_name]

    def set_host(self,host,port,name,username,password,prefix = ''):
        self.__DB_HOST = host
        self.__DB_PORT = int(port)
        self.__DB_NAME = name
        if self.__DB_NAME: self.__DB_NAME = str(self.__DB_NAME)
        self.__DB_USER = str(username)
        self._USER = str(username)
        self.__DB_PASS = str(password)
        self.__DB_PREFIX = prefix
        self.__DB_CLOUD = 1
        return self



    #获取配置文件
    def get_config(self,get):
        filename =  '{}/mongodb/config.conf'.format(public.get_setup_path())
        if os.path.exists(filename):
            return public.readFile(filename);
        return ""

    #获取配置项
    def get_options(self,get):
        options = ['port','bind_ip','logpath','dbpath','authorization']
        data = {}
        conf = self.get_config(None)

        for opt in options:
            tmp = re.findall(opt + ":\s+(.+)",conf)
            if not tmp: continue;
            data[opt] = tmp[0]

        if not 'authorization' in data:data['authorization'] = "disabled"

        public.writeFile('/www/server/1.txt',json.dumps(data))
        return data


class main(databaseBase):

    __conf_path = '{}/mongodb/config.conf'.format(public.get_setup_path())
    def __init__(self):
        pass


    def get_list(self,args):
        """
        @获取数据库列表
        @sql_type = sqlserver
        """
        return self.get_base_list(args, sql_type = 'mongodb')

    def GetCloudServer(self,args):
        '''
            @name 获取远程服务器列表
            @author hwliang<2021-01-10>
            @return list
        '''
        return self.GetBaseCloudServer(args)


    def AddCloudServer(self,args):
        '''
        @添加远程数据库
        '''
        return self.AddBaseCloudServer(args)

    def RemoveCloudServer(self,args):
        '''
        @删除远程数据库
        '''
        return self.RemoveBaseCloudServer(args)

    def ModifyCloudServer(self,args):
        '''
        @修改远程数据库
        '''
        return self.ModifyBaseCloudServer(args)

    #获取数据库列表
    def exists_databases(self,get):
        db_name = get
        if type(get) != str:db_name = get['db_name']
        auth_status = self.get_local_auth(get)
        db_obj = self.get_obj_by_sid(self.sid).get_db_obj('admin',auth=auth_status)
        data = db_obj.command({"listDatabases":1})
        if 'databases' in data:
            for x in data['databases']:
                if x['name'] == db_name:
                    return True
        return False

    def __set_auth_open(self,status):
        """
        @设置数据库密码访问开关
        @状态 status:1 开启，2：关闭
        """

        conf = public.readFile(self.__conf_path)
        if status:
            conf = re.sub('authorization\s*\:\s*disabled','authorization: enabled',conf)
        else:
            conf = re.sub('authorization\s*\:\s*enabled','authorization: disabled',conf)

        public.writeFile(self.__conf_path,conf)
        self.restart_services()

        return True


    def set_auth_status(self,get):
        """
        @设置密码认证状态
        @status int 0：关闭，1：开启
        """

        if not public.process_exists("mongod") :
            return public.returnMsg(False,"Mongodb服务还未开启！")

        status = int(get.status)
        path = '{}/data/mongo.root'.format(public.get_panel_path())
        if status:
            if hasattr(get,'password'):
                password = get['password'].strip()
                if not password or not re.search("^[\w@\.]+$", password):
                    return public.returnMsg(False, '数据库密码不能为空或带有特殊字符')

                if re.search('[\u4e00-\u9fa5]',password):
                    return public.returnMsg(False,'数据库密码不能为中文，请换个名称!')
            else:
                password = public.GetRandomString(16)
            self.__set_auth_open(0)

            _client = panelMongoDB().get_db_obj('admin')
            try:
                _client.command("dropUser", "root")
            except : pass

            _client.command("createUser", "root", pwd=password, roles=[
                {'role':'root','db':'admin'},
                {'role':'clusterAdmin','db':'admin'},
                {'role':'readAnyDatabase','db':'admin'},
                {'role':'readWriteAnyDatabase','db':'admin'},
                {'role':'userAdminAnyDatabase','db':'admin'},
                {'role':'dbAdminAnyDatabase','db':'admin'},
                {'role':'userAdmin','db':'admin'},
                {'role':'dbAdmin','db':'admin'}
               ])

            self.__set_auth_open(1)

            public.writeFile(path,password)
        else:
            if os.path.exists(path): os.remove(path)
            self.__set_auth_open(0)

        return public.returnMsg(True,'操作成功.')

    def restart_services(self):
        """
        @重启服务
        """
        public.ExecShell('/etc/init.d/mongodb restart')
        return True

    def get_obj_by_sid(self,sid = 0,conn_config = None):
        """
        @取mssql数据库对像 By sid
        @sid 数据库分类，0：本地
        """
        if type(sid) == str:
            try:
                sid = int(sid)
            except :sid = 0

        if sid:
            if not conn_config: conn_config = public.M('database_servers').where("id=?" ,sid).find()
            db_obj = panelMongoDB()

            try:
                db_obj = db_obj.set_host(conn_config['db_host'],conn_config['db_port'],None,conn_config['db_user'],conn_config['db_password'])
            except Exception as e:
                raise public.PanelError(e)
        else:
            db_obj = panelMongoDB()
        return db_obj



    def get_local_auth(self,get):
        """
        @验证本地数据库是否需要密码
        """
        self.sid = get.get('sid/d',0)
        if self.sid != 0: return True

        conf = panelMongoDB().get_options(None)
        if conf['authorization'] == 'enabled':
            return True
        return False

    def AddDatabase(self,args):
        """
        @添加数据库
        """
        try:
            int(args.sid)
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not int(args.sid) and not public.process_exists("mongod"):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        username = ''
        password = ''
        auth_status = self.get_local_auth(args) #auth为true时如果__DB_USER为空则将它赋值为 root，用于开启本地认证后数据库用户为空的情况
        data_name = args.name.strip()
        if not data_name:
            return public.returnMsg(False, "数据库名不能为空！")
        if auth_status:
            res = self.add_base_database(args)
            if not res['status']: return res

            data_name = res['data_name']
            username = res['username']
            password = res['data_pwd']
        else:
            username = data_name
        db_obj = self.get_obj_by_sid(self.sid).get_db_obj(data_name,auth=auth_status)
        dtype = 'MongoDB'
        if not hasattr(args,'ps'): args['ps'] = public.getMsg('INPUT_PS');
        addTime = time.strftime('%Y-%m-%d %X',time.localtime())

        pid = 0
        if hasattr(args,'pid'): pid = args.pid

        if hasattr(args,'contact'):
            site = public.M('sites').where("id=?",(args.contact,)).field('id,name').find()
            if site:
                pid = int(args.contact)
                args['ps'] = site['name']

        db_type = 0
        if self.sid: db_type = 2

        db_obj.chat.insert_one({})
        if auth_status:
            db_obj.command("createUser", username, pwd=password, roles=[{'role':'dbOwner','db':data_name},{'role':'userAdmin','db':data_name}])

        public.set_module_logs('linux_mongodb','AddDatabase',1)

        #添加入SQLITE
        public.M('databases').add('pid,sid,db_type,name,username,password,accept,ps,addtime,type',(pid,self.sid,db_type,data_name,username,password,'127.0.0.1',args['ps'],addTime,dtype))
        public.WriteLog("TYPE_DATABASE", 'DATABASE_ADD_SUCCESS',(data_name,))
        return public.returnMsg(True,'ADD_SUCCESS')


    def DeleteDatabase(self,args):
        """
        @删除数据库
        """
        id = args['id']
        find = public.M('databases').where("id=?",(id,)).field('id,pid,name,username,password,type,accept,ps,addtime,sid,db_type').find()
        if not find: return public.returnMsg(False,'指定数据库不存在.')
        try:
            int(find['sid'])
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(find['sid']):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        name = args['name']
        username = find['username']
        auth_status = self.get_local_auth(args)
        db_obj = self.get_obj_by_sid(find['sid']).get_db_obj(name,auth_status)
        try:
            db_obj.command("dropUser", username)
        except :
            pass

        db_obj.command('dropDatabase')
        #删除SQLITE
        public.M('databases').where("id=?",(id,)).delete()
        public.WriteLog("TYPE_DATABASE", 'DATABASE_DEL_SUCCESS',(name,))
        return public.returnMsg(True, 'DEL_SUCCESS')


    def get_info_by_db_id(self,db_id):
        """
        @获取数据库连接详情
        @db_id 数据库id
        """
        find = public.M('databases').where("id=?" ,db_id).find()
        if not find: return False

        data = {
            'db_host':'127.0.0.1',
            'db_port':int(panelMongoDB().get_options(None)['port']),
            'db_user':find['username'],
            'db_password':find['password']
        }

        if int(find['sid']):
            conn_config = public.M('database_servers').where("id=?" ,find['sid']).find()

            data['db_host'] = conn_config['db_host']
            data['db_port'] = int(conn_config['db_port'])


        return data

        #导入
    def InputSql(self,args):
        name = args.name
        file = args.file

        find = public.M('databases').where("name=?",(name,)).find()
        if not find: return public.returnMsg(False,'数据库不存在!')

        get = public.dict_obj()
        get.sid = find['sid']
        try:
            sid = int(find['sid'])
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(find['sid']):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        info = self.get_info_by_db_id(find['id'])
        sql_dump = '{}/mongodb/bin/mongo'.format(public.get_setup_path())
        if not os.path.exists(sql_dump): return public.returnMsg(False,'缺少备份工具，请先通过软件管理安装MongoDB!')

        if self.get_local_auth(get):
            shell = "{} -h {} --port {} -u {} -p {} -d {} --drop {} ".format(sql_dump,info['db_host'],info['db_port'],info['db_user'],info['db_password'],find['name'] ,file)
        else:
            shell = "{} -h {} --port {} -d {} --drop {}".format(sql_dump,info['db_host'],info['db_port'],find['name'] ,file)
        public.ExecShell(shell)

        public.WriteLog("TYPE_DATABASE", '导入数据库[{}]成功'.format(name))
        return public.returnMsg(True, 'DATABASE_INPUT_SUCCESS');


    def ToBackup(self,args):
        """
        @备份数据库 id 数据库id
        """
        id = args['id']
        find = public.M('databases').where("id=?",(id,)).find()
        if not find: return public.returnMsg(False,'数据库不存在!')

        fileName = find['name'] + '_' + time.strftime('%Y%m%d_%H%M%S',time.localtime())
        backupName = session['config']['backup_path'] + '/database/mongodb/' + fileName

        spath = os.path.dirname(backupName)
        if not os.path.exists(spath): os.makedirs(spath)

        get = public.dict_obj()
        get.sid = find['sid']
        try:
            sid = int(find['sid'])
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(find['sid']):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        info = self.get_info_by_db_id(id)

        sql_dump = '{}/mongodb/bin/mongodump'.format(public.get_setup_path())
        if not os.path.exists(sql_dump): return public.returnMsg(False,'缺少备份工具，请先通过软件管理安装MongoDB!')

        if self.get_local_auth(get):
            if not info['db_password']:
                return public.returnMsg(False,'Mongodb已经开启密码认证，数据库备份时密码不能为空，请设置密码后再试！')
            shell = "{}  -h {} --port {} -u {} -p {} -d {} -o {} ".format(sql_dump,info['db_host'],info['db_port'],info['db_user'],info['db_password'],find['name'] ,backupName)
        else:
            shell = "{}  -h {} --port {} -d {} -o {} ".format(sql_dump,info['db_host'],info['db_port'],find['name'] ,backupName)

        ret = public.ExecShell(shell)
        if not os.path.exists(backupName):
            return public.returnMsg(False,'数据库备份失败，文件不存在');

        sfile = '{}/{}/chat.bson'.format(backupName,find['name'])
        public.M('backup').add('type,name,pid,filename,size,addtime',(1,fileName,id,sfile,0,time.strftime('%Y-%m-%d %X',time.localtime())))
        public.WriteLog("TYPE_DATABASE", "DATABASE_BACKUP_SUCCESS",(find['name'],))

        if os.path.getsize(sfile) < 1:
            return public.returnMsg(True, '备份执行成功，备份文件小于1b，请检查备份完整性.')
        else:
            return public.returnMsg(True, 'BACKUP_SUCCESS')

    def DelBackup(self,args):
        """
        @删除备份文件
        """
        return self.delete_base_backup(args)

    #同步数据库到服务器
    def SyncToDatabases(self,get):
        type = int(get['type'])
        n = 0
        sql = public.M('databases')
        if type == 0:
            data = sql.field('id,name,username,password,accept,type,sid,db_type').where('type=?',('MongoDB',)).select()

            for value in data:
                if value['db_type'] in ['1',1]:
                    continue # 跳过远程数据库
                result = self.ToDataBase(value)
                if result == 1: n +=1
        else:
            import json
            data = json.loads(get.ids)
            for value in data:
                find = sql.where("id=?",(value,)).field('id,name,username,password,sid,db_type,accept,type').find()
                result = self.ToDataBase(find)
                if result == 1: n +=1

        return public.returnMsg(True,'DATABASE_SYNC_SUCCESS',(str(n),))

    #添加到服务器
    def ToDataBase(self,find):
        if find['username'] == 'bt_default': return 0
        if len(find['password']) < 3 :
            find['username'] = find['name']
            find['password'] = public.md5(str(time.time()) + find['name'])[0:10]
            public.M('databases').where("id=?",(find['id'],)).save('password,username',(find['password'],find['username']))

        self.sid = find['sid']
        try:
           int(find['sid'])
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(find['sid']):
            return public.returnMsg(False,"Mongodb服务还未开启！")


        get = public.dict_obj()
        get.sid = self.sid
        auth_status = self.get_local_auth(get)
        if auth_status:
            db_obj = self.get_obj_by_sid(self.sid).get_db_obj(find['name'], auth_status)
            try:
                db_obj.chat.insert_one({})
                db_obj.command("dropUser", find['username'])
            except :pass
            try:
                db_obj.command("createUser", find['username'], pwd=find['password'], roles=[{'role':'dbOwner','db':find['name']},{'role':'userAdmin','db':find['name']}])
            except:
                pass
        return 1

    def SyncGetDatabases(self,get):
        """
        @从服务器获取数据库
        """
        n = 0;s = 0;
        db_type = 0
        self.sid = get.get('sid/d',0)
        if self.sid: db_type = 2
        try:
            int(get.sid)
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(get.sid):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        auth_status = self.get_local_auth(get)
        data = self.get_obj_by_sid(self.sid).get_db_obj('admin',auth=auth_status).command({"listDatabases":1})

        sql = public.M('databases')
        nameArr = ['information_schema','performance_schema','mysql','sys','master','model','msdb','tempdb','config','local','admin']
        for item in data['databases']:
            dbname = item['name']
            if sql.where("name=?",(dbname,)).count(): continue
            if not dbname in nameArr:
                if sql.table('databases').add('name,username,password,accept,ps,addtime,type,sid,db_type',(dbname,dbname,'','',public.getMsg('INPUT_PS'),time.strftime('%Y-%m-%d %X',time.localtime()),'MongoDB',self.sid,db_type)): n +=1

        return public.returnMsg(True,'DATABASE_GET_SUCCESS',(str(n),))


    def ResDatabasePassword(self,args):
        """
        @修改用户密码
        """
        id = args['id']
        username = args['name'].strip()
        newpassword = public.trim(args['password'])

        try:
            if not newpassword:
                return public.returnMsg(False, '修改失败，数据库[' + username + ']密码不能为空.');
            if len(re.search("^[\w@\.]+$", newpassword).groups()) > 0:
                return public.returnMsg(False, '数据库密码不能为空或带有特殊字符')

            if re.search('[\u4e00-\u9fa5]',newpassword):
                return public.returnMsg(False,'数据库密码不能为中文，请换个名称!')
        except :
            return public.returnMsg(False, '数据库密码不能为空或带有特殊字符')

        find = public.M('databases').where("id=?",(id,)).field('id,pid,name,username,password,type,accept,ps,addtime,sid').find();
        if not find: return public.returnMsg(False, '修改失败，指定数据库不存在.');

        get = public.dict_obj()
        get.sid = find['sid']
        try:
           int(find['sid'])
        except:
            return public.returnMsg(False, '数据库类型sid需要int类型！')
        if not public.process_exists("mongod") and not int(find['sid']):
            return public.returnMsg(False,"Mongodb服务还未开启！")
        auth_status = self.get_local_auth(args)
        if auth_status:
            db_obj = self.get_obj_by_sid(find['sid']).get_db_obj(username,auth=auth_status)
            try:
                print(db_obj.command("updateUser", username, pwd = newpassword))
            except :
                print(db_obj.command("createUser", username, pwd=newpassword, roles=[{'role':'dbOwner','db':find['name']},{'role':'userAdmin','db':find['name']}]))
        else:
            return public.returnMsg(False, '修改失败，数据库未开启密码访问.')

        #修改SQLITE
        public.M('databases').where("id=?",(id,)).setField('password',newpassword)

        public.WriteLog("TYPE_DATABASE",'DATABASE_PASS_SUCCESS',(find['name'],))
        return public.returnMsg(True,'DATABASE_PASS_SUCCESS',(find['name'],))

    def get_root_pwd(self,args):
        """
        @获取root密码
        """
        config = panelMongoDB().get_options(None)
        sa_path = '{}/data/mongo.root'.format(public.get_panel_path())
        if os.path.exists(sa_path):
            config['msg'] = public.readFile(sa_path)
        else:
            config['msg'] = ''
        config['root'] = config['msg']
        return config

    def get_database_size_by_id(self, args):
        """
        @获取数据库尺寸（批量删除验证）
        @args json/int 数据库id
        """
        # if not public.process_exists("mongod"):
        #     return public.returnMsg(False,"Mongodb服务还未开启！")
        total = 0
        db_id = args
        if not isinstance(args, int): db_id = args['db_id']

        find = public.M('databases').where('id=?', db_id).find()
        try:
            int(find['sid'])
        except:
            return 0
        if not public.process_exists("mongod") and not int(find['sid']):
            return 0
        try:
            auth_status = self.get_local_auth(args)
            db_obj = self.get_obj_by_sid(find['sid']).get_db_obj(find['name'], auth=auth_status)
            print(db_obj)
            print(db_obj.stats())

            total = tables[0][1]
            if not total: total = 0
        except:
            print(public.get_error_info())



        return total

    def check_del_data(self,args):
        """
        @删除数据库前置检测
        """
        return self.check_base_del_data(args)


    def check_cloud_database_status(self,conn_config):
        """
        @检测远程数据库是否连接
        @conn_config 远程数据库配置，包含host port pwd等信息
        """
        try:
            if not 'db_name' in conn_config: conn_config['db_name'] = None
            sql_obj = panelMongoDB().set_host(conn_config['db_host'],conn_config['db_port'],conn_config['db_name'],conn_config['db_user'],conn_config['db_password'])

            db_obj = sql_obj.get_db_obj('admin')
            data = db_obj.command({"listDatabases":1})

            if 'databases' in data:
                return True
            return False
        except Exception as ex:
            return public.returnMsg(False,ex)