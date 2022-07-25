import os ,sys ,time ,json ,re ,datetime ,shutil ,threading #line:13
os .chdir ('/www/server/panel')#line:14
sys .path .append ("class/")#line:15
import public #line:16
from projectModel .base import projectBase #line:17
from panelMysql import panelMysql #line:18
from panelBackup import backup #line:19
import db_mysql #line:20
try :#line:21
    import oss2 #line:22
    from qcloud_cos import CosConfig #line:23
    from qcloud_cos import CosS3Client #line:24
    from qiniu import Auth ,put_file ,etag #line:25
    from baidubce .bce_client_configuration import BceClientConfiguration #line:26
    from baidubce .auth .bce_credentials import BceCredentials #line:27
    from baidubce .services .bos .bos_client import BosClient #line:28
    from obs import ObsClient #line:29
except :#line:30
    pass #line:31
class main (projectBase ):#line:32
    _setup_path ='/www/server/panel/'#line:33
    _binlog_id =''#line:34
    _db_name =''#line:35
    _zip_password =''#line:36
    _backup_end_time =''#line:37
    _backup_start_time =''#line:38
    _backup_type =''#line:39
    _cloud_name =''#line:40
    _full_zip_name =''#line:41
    _full_file =''#line:42
    _inc_file =''#line:43
    _file =''#line:44
    _pdata ={}#line:45
    _echo_info ={}#line:46
    _inode_min =100 #line:47
    _temp_path ='./temp/'#line:48
    _tables =[]#line:49
    _new_tables =[]#line:50
    _backup_fail_list =[]#line:51
    _backup_full_list =[]#line:52
    _cloud_upload_not =[]#line:53
    _full_info =[]#line:54
    _inc_info =[]#line:55
    _mysql_bin_index ='/www/server/data/mysql-bin.index'#line:56
    _save_cycle =3600 #line:57
    _compress =True #line:58
    _mysqlbinlog_bin ='/www/server/mysql/bin/mysqlbinlog'#line:59
    _save_default_path ='/www/backup/mysql_bin_log/'#line:60
    _mysql_root_password =public .M ('config').where ('id=?',(1 ,)).getField ('mysql_root')#line:61
    _install_path ='{}script/binlog_cloud.sh'.format (_setup_path )#line:62
    _config_path ='{}config/mysqlbinlog_info'.format (_setup_path )#line:63
    _python_path ='{}pyenv/bin/python'.format (_setup_path )#line:64
    _binlogModel_py ='{}class/projectModel/binlogModel.py'.format (_setup_path )#line:65
    _mybackup =backup ()#line:66
    _plugin_path ='{}plugin/'.format (_setup_path )#line:67
    _binlog_conf ='{}config/mysqlbinlog_info/binlog.conf'.format (_setup_path )#line:68
    _start_time_list =[]#line:69
    _db_mysql =db_mysql .panelMysql ()#line:70
    def __init__ (O0OOO0OO00OO00O0O ):#line:73
        if not os .path .exists (O0OOO0OO00OO00O0O ._save_default_path ):#line:74
            os .makedirs (O0OOO0OO00OO00O0O ._save_default_path )#line:75
        if not os .path .exists (O0OOO0OO00OO00O0O ._temp_path ):#line:76
            os .makedirs (O0OOO0OO00OO00O0O ._temp_path )#line:77
        if not os .path .exists (O0OOO0OO00OO00O0O ._config_path ):#line:78
            os .makedirs (O0OOO0OO00OO00O0O ._config_path )#line:79
        O0OOO0OO00OO00O0O .create_table ()#line:80
        O0OOO0OO00OO00O0O .kill_process ()#line:81
    def get_path (O0O0O0OO0OOO000O0 ,O00O0OOOO0O00O0OO ):#line:83
        ""#line:87
        if O00O0OOOO0O00O0OO =='/':O00O0OOOO0O00O0OO =''#line:88
        if O00O0OOOO0O00O0OO [:1 ]=='/':#line:89
            O00O0OOOO0O00O0OO =O00O0OOOO0O00O0OO [1 :]#line:90
            if O00O0OOOO0O00O0OO [-1 :]!='/':O00O0OOOO0O00O0OO +='/'#line:91
        return O00O0OOOO0O00O0OO .replace ('//','/')#line:92
    def install_cloud_module (O0OO0OO000000OO0O ):#line:94
        ""#line:98
        O00OO0O00O0OO0O0O =["oss2","cos-python-sdk-v5","qiniu","bce-python-sdk","esdk-obs-python"]#line:99
        O00OO0O00O0OO0O0O =["oss2==2.5.0","cos-python-sdk-v5==1.7.7","qiniu==7.4.1 -I","bce-python-sdk==0.8.62","esdk-obs-python==3.21.8 --trusted-host pypi.org"]#line:100
        for O0000O00OOOO000OO in O00OO0O00O0OO0O0O :#line:101
            public .ExecShell ('nohup btpip install {} >/dev/null 2>&1 &'.format (O0000O00OOOO000OO ))#line:102
            time .sleep (1 )#line:103
    def get_start_end_binlog (OOO000O00OOOOO00O ,O000O0OOOOOOOO00O ,O0000O000OO000OO0 ,is_backup =None ):#line:107
        ""#line:114
        OO0O0OO0OOO0OO0OO ={}#line:116
        OOO0O00000O0O0O0O =['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']#line:117
        OO0O0OO0OOO0OO0OO ['start']=OOO0O00000O0O0O0O [(int (O000O0OOOOOOOO00O .split ()[1 ].split (':')[0 ])):]#line:118
        if is_backup :#line:119
            OO0O0OO0OOO0OO0OO ['end']=OOO0O00000O0O0O0O [:(int (O0000O000OO000OO0 .split ()[1 ].split (':')[0 ])+1 )]#line:120
        else :#line:121
            OO0O0OO0OOO0OO0OO ['end']=OOO0O00000O0O0O0O [:(int (O0000O000OO000OO0 .split ()[1 ].split (':')[0 ])+1 )]#line:122
        OO0O0OO0OOO0OO0OO ['all']=OOO0O00000O0O0O0O #line:123
        return OO0O0OO0OOO0OO0OO #line:125
    def traverse_all_files (O00O0000OO0O00O00 ,O0OO00O0OOO0O0000 ,O00OO0OO00O000OO0 ,OO00000O0OO000000 ):#line:128
        ""#line:135
        OOOO00O00O0O0000O ={}#line:136
        O000000OO0OO000OO =[]#line:137
        OOOO00OO00OOOOOO0 =[]#line:138
        for OOO0O0O0OO0O0O000 in range (0 ,len (O00OO0OO00O000OO0 )):#line:139
            O00OO0OOO0O0OOO00 =O0OO00O0OOO0O0000 +O00OO0OO00O000OO0 [OOO0O0O0OO0O0O000 ]+'/'#line:140
            OOO00O0OOOO000OO0 =False #line:141
            OOOOO0OOO0O0OO0O0 =False #line:142
            if O00OO0OO00O000OO0 [OOO0O0O0OO0O0O000 ]==O00OO0OO00O000OO0 [0 ]:#line:143
                OOO00O00000OOO0O0 =OO00000O0OO000000 ['start']#line:144
                OOO00O0OOOO000OO0 =True #line:145
            elif O00OO0OO00O000OO0 [OOO0O0O0OO0O0O000 ]==O00OO0OO00O000OO0 [len (O00OO0OO00O000OO0 )-1 ]:#line:146
                OOO00O00000OOO0O0 =OO00000O0OO000000 ['end']#line:147
                OOOOO0OOO0O0OO0O0 =True #line:148
            else :#line:149
                OOO00O00000OOO0O0 =OO00000O0OO000000 ['all']#line:150
            if len (O00OO0OO00O000OO0 )==1 :#line:152
                OOO00O00000OOO0O0 =sorted (list (set (OO00000O0OO000000 ['end']).intersection (OO00000O0OO000000 ['start'])))#line:153
                OOO00O0OOOO000OO0 =True #line:155
                OOOOO0OOO0O0OO0O0 =True #line:156
            if OOO00O00000OOO0O0 :#line:157
                O0OO0O000OOO00OOO =O00O0000OO0O00O00 .splice_file_name (O00OO0OOO0O0OOO00 ,O00OO0OO00O000OO0 [OOO0O0O0OO0O0O000 ],OOO00O00000OOO0O0 )#line:158
                if OOO00O0OOOO000OO0 :#line:159
                    OOOO00O00O0O0000O ['first']=O0OO0O000OOO00OOO [0 ]#line:160
                if OOOOO0OOO0O0OO0O0 :#line:161
                    OOOO00O00O0O0000O ['last']=O0OO0O000OOO00OOO [len (O0OO0O000OOO00OOO )-1 ]#line:162
                OOOO00OO00OOOOOO0 .append (O0OO0O000OOO00OOO )#line:163
                O00OO0O0OOOO0O000 =O00O0000OO0O00O00 .check_foler_file (O0OO0O000OOO00OOO )#line:164
                if O00OO0O0OOOO0O000 :#line:165
                    O000000OO0OO000OO .append (O00OO0O0OOOO0O000 )#line:166
        OOOO00O00O0O0000O ['data']=OOOO00OO00OOOOOO0 #line:167
        OOOO00O00O0O0000O ['file_lists_not']=O000000OO0OO000OO #line:168
        if O000000OO0OO000OO :#line:169
            OOOO00O00O0O0000O ['status']='False'#line:170
        else :#line:171
            OOOO00O00O0O0000O ['status']='True'#line:172
        return OOOO00O00O0O0000O #line:173
    def get_mysql_port (O000OO00000OO0000 ):#line:175
        ""#line:179
        try :#line:180
            OO000O0OOOOOO0O00 =panelMysql ().query ("show global variables like 'port'")[0 ][1 ]#line:181
            if not OO000O0OOOOOO0O00 :#line:182
                return 0 #line:183
            else :#line:184
                return OO000O0OOOOOO0O00 #line:185
        except :#line:186
            return 0 #line:187
    def get_info (O000OOOOO0O00O000 ,O0OO00O00O000O000 ,OOO0OOOOOO0O000OO ):#line:189
        ""#line:196
        OOOO00O0O000O0O0O ={}#line:197
        for OO00O0O00000O0OO0 in OOO0OOOOOO0O000OO :#line:198
            if OO00O0O00000O0OO0 ['full_name']==O0OO00O00O000O000 :#line:199
                OOOO00O0O000O0O0O =OO00O0O00000O0OO0 #line:200
        return OOOO00O0O000O0O0O #line:201
    def auto_download_file (OOO0OO00O00OO00OO ,OO0OO00OOOO00000O ,OOOOO0O0OOOO0000O ,size =1024 ):#line:203
        ""#line:206
        OOO0O0OO00O00OO00 =''#line:208
        for OOO000O0O00OOO00O in OO0OO00OOOO00000O :#line:209
            OOO0O0OO00O00OO00 =OOO000O0O00OOO00O .download_file (OOOOO0O0OOOO0000O .replace ('/www/backup','bt_backup'))#line:210
            if OOO0O0OO00O00OO00 :OOO0OO00O00OO00OO .download_big_file (OOOOO0O0OOOO0000O ,OOO0O0OO00O00OO00 ,size )#line:211
            if os .path .isfile (OOOOO0O0OOOO0000O ):#line:212
                print ('已从远程存储器下载{}'.format (OOOOO0O0OOOO0000O ))#line:213
                break #line:214
    def download_big_file (O000OOO0OOOOOO00O ,OO00OO0000000O0OO ,O00OO0OOOO00000O0 ,OOOO0OO0OOOO0OO00 ):#line:216
        ""#line:219
        OOO0000O0000OO00O =0 #line:220
        import requests #line:221
        try :#line:222
            if int (OOOO0OO0OOOO0OO00 )<1024 *1024 *100 :#line:224
                OO0000OOO0OOOO000 =requests .get (O00OO0OOOO00000O0 )#line:226
                with open (OO00OO0000000O0OO ,"wb")as O000O000OO0OO0OO0 :#line:227
                    O000O000OO0OO0OO0 .write (OO0000OOO0OOOO000 .content )#line:228
            else :#line:231
                OO0000OOO0OOOO000 =requests .get (O00OO0OOOO00000O0 ,stream =True )#line:232
                with open (OO00OO0000000O0OO ,'wb')as O000O000OO0OO0OO0 :#line:233
                    for OOOOO00O0OOO00O0O in OO0000OOO0OOOO000 .iter_content (chunk_size =1024 ):#line:234
                        if OOOOO00O0OOO00O0O :#line:235
                            O000O000OO0OO0OO0 .write (OOOOO00O0OOO00O0O )#line:236
        except :#line:238
            time .sleep (3 )#line:239
            OOO0000O0000OO00O +=1 #line:240
            if OOO0000O0000OO00O <2 :#line:241
                O000OOO0OOOOOO00O .download_big_file (OO00OO0000000O0OO ,O00OO0OOOO00000O0 ,OOOO0OO0OOOO0OO00 )#line:243
        return False #line:244
    def check_binlog_complete (O00OO00O0000OOO0O ,O0O00OO000O0OO000 ,end_time =None ):#line:247
        ""#line:254
        OO0O00OO0OOOO0OOO ,O00OOO0OOO0OOO0OO ,O0O0O0OOOO0000O0O ,O0OOOOO000O00OO00 ,OOO0OOOO000000OO0 ,O0000OOO00000000O ,OOO0O00OOO0O00OO0 ,O000OOO0O000O0000 =O00OO00O0000OOO0O .check_cloud_oss (O0O00OO000O0OO000 )#line:255
        OOOOOOOO0O0OOO0O0 ={}#line:256
        OOO0O0O00OOO000OO =[]#line:257
        OOO0O00O00O000OO0 =''#line:259
        if not os .path .isfile (O00OO00O0000OOO0O ._full_file ):#line:260
            O00OO00O0000OOO0O .auto_download_file (OOO0O00OOO0O00OO0 ,O00OO00O0000OOO0O ._full_file )#line:262
        if not os .path .isfile (O00OO00O0000OOO0O ._full_file ):OOO0O0O00OOO000OO .append (O00OO00O0000OOO0O ._full_file )#line:263
        if OOO0O0O00OOO000OO :#line:264
            OOOOOOOO0O0OOO0O0 ['file_lists_not']=OOO0O0O00OOO000OO #line:265
            return OOOOOOOO0O0OOO0O0 #line:266
        if os .path .isfile (O00OO00O0000OOO0O ._full_file ):#line:268
            try :#line:269
                O00OO00O0000OOO0O ._full_info =json .loads (public .readFile (O00OO00O0000OOO0O ._full_file ))[0 ]#line:270
            except :#line:271
                O00OO00O0000OOO0O ._full_info =[]#line:272
        if 'full_name'in O00OO00O0000OOO0O ._full_info and not os .path .isfile (O00OO00O0000OOO0O ._full_info ['full_name']):#line:273
            OOO0O0O00OOO000OO .append (O00OO00O0000OOO0O ._full_info ['full_name'])#line:274
            OOOOOOOO0O0OOO0O0 ['file_lists_not']=OOO0O0O00OOO000OO #line:275
            return OOOOOOOO0O0OOO0O0 #line:276
        if not O00OO00O0000OOO0O ._full_info or 'time'not in O00OO00O0000OOO0O ._full_info :#line:277
            return OOOOOOOO0O0OOO0O0 #line:278
        else :#line:279
            OOO0O00O00O000OO0 =O00OO00O0000OOO0O ._full_info ['time']#line:280
        if OOO0O00O00O000OO0 !=end_time :#line:281
            if not os .path .isfile (O00OO00O0000OOO0O ._inc_file ):#line:283
                O00OO00O0000OOO0O .auto_download_file (OOO0O00OOO0O00OO0 ,O00OO00O0000OOO0O ._inc_file )#line:284
            if not os .path .isfile (O00OO00O0000OOO0O ._inc_file ):OOO0O0O00OOO000OO .append (O00OO00O0000OOO0O ._inc_file )#line:285
            if OOO0O0O00OOO000OO :#line:286
                OOOOOOOO0O0OOO0O0 ['file_lists_not']=OOO0O0O00OOO000OO #line:287
                return OOOOOOOO0O0OOO0O0 #line:288
            if os .path .isfile (O00OO00O0000OOO0O ._inc_file ):#line:289
                try :#line:290
                    O00OO00O0000OOO0O ._inc_info =json .loads (public .readFile (O00OO00O0000OOO0O ._inc_file ))#line:291
                except :#line:292
                    O00OO00O0000OOO0O ._inc_info =[]#line:293
            O00OOOO00OOO0OO0O =O00OO00O0000OOO0O .splicing_save_path ()#line:295
            O0OOOO00OO00OOOOO =O00OO00O0000OOO0O .get_every_day (OOO0O00O00O000OO0 .split ()[0 ],end_time .split ()[0 ])#line:296
            O0OO0O0OOOOOO0OOO =O00OO00O0000OOO0O .get_start_end_binlog (OOO0O00O00O000OO0 ,end_time )#line:297
            OOOOOOOO0O0OOO0O0 =O00OO00O0000OOO0O .traverse_all_files (O00OOOO00OOO0OO0O ,O0OOOO00OO00OOOOO ,O0OO0O0OOOOOO0OOO )#line:299
        if OOOOOOOO0O0OOO0O0 and OOOOOOOO0O0OOO0O0 ['file_lists_not']:#line:301
            for OO00OOOOOO00000OO in OOOOOOOO0O0OOO0O0 ['file_lists_not']:#line:302
                for O00O00OO0OOOO00OO in OO00OOOOOO00000OO :#line:303
                    O0O0O000O0OO00O0O =public .M ('mysqlbinlog_backups').where ('sid=? and local_name=?',(O0O00OO000O0OO000 ['id'],O00O00OO0OOOO00OO )).find ()#line:304
                    O000OO0000O0O0OOO =1024 #line:305
                    if O0O0O000O0OO00O0O and 'size'in O0O0O000O0OO00O0O :O000OO0000O0O0OOO =O0O0O000O0OO00O0O ['size']#line:306
                    O00OO00O0000OOO0O .auto_download_file (OOO0O00OOO0O00OO0 ,O00O00OO0OOOO00OO ,O000OO0000O0O0OOO )#line:307
            OOOOOOOO0O0OOO0O0 =O00OO00O0000OOO0O .traverse_all_files (O00OOOO00OOO0OO0O ,O0OOOO00OO00OOOOO ,O0OO0O0OOOOOO0OOO )#line:308
        return OOOOOOOO0O0OOO0O0 #line:309
    def restore_to_database (OO0OO0OOO00OO0OOO ,O0000O0000O0OO00O ):#line:312
        ""#line:320
        public .set_module_logs ('binlog','restore_to_database')#line:321
        O00000O00O0000OO0 =public .M ('mysqlbinlog_backup_setting').where ('id=?',str (O0000O0000O0OO00O .backup_id ,)).find ()#line:323
        if not O00000O00O0000OO0 :return public .returnMsg (False ,'增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试恢复！')#line:324
        if O00000O00O0000OO0 and 'zip_password'in O00000O00O0000OO0 :OO0OO0OOO00OO0OOO ._zip_password =O00000O00O0000OO0 ['zip_password']#line:325
        else :OO0OO0OOO00OO0OOO ._zip_password =''#line:326
        OO0OO0OOO00OO0OOO ._db_name =O0000O0000O0OO00O .datab_name #line:327
        OO0OO0OOO00OO0OOO ._tables =''if 'table_name'not in O0000O0000O0OO00O else O0000O0000O0OO00O .table_name #line:328
        O000O00O0OOOO00O0 ='/tables/'+OO0OO0OOO00OO0OOO ._tables +'/'if OO0OO0OOO00OO0OOO ._tables else '/databases/'#line:329
        O00OO00OO00O0O00O =OO0OO0OOO00OO0OOO ._save_default_path +OO0OO0OOO00OO0OOO ._db_name +O000O00O0OOOO00O0 #line:330
        OO0OO0OOO00OO0OOO ._full_file =O00OO00OO00O0O00O +'full_record.json'#line:331
        OO0OO0OOO00OO0OOO ._inc_file =O00OO00OO00O0O00O +'inc_record.json'#line:332
        O0O000O00OOO00O0O =os .path .join (O00OO00OO00O0O00O ,'test')#line:333
        OO00O00000OOOO00O =OO0OO0OOO00OO0OOO .check_binlog_complete (O00000O00O0000OO0 ,O0000O0000O0OO00O .end_time )#line:334
        if 'file_lists_not'in OO00O00000OOOO00O and OO00O00000OOOO00O ['file_lists_not']:return public .returnMsg (False ,'恢复所需要的文件不完整')#line:335
        if not OO0OO0OOO00OO0OOO ._full_info :return public .returnMsg (False ,'全量备份记录文件内容不完整')#line:336
        if OO0OO0OOO00OO0OOO ._full_info ['full_name'].split ('.')[-1 ]=='gz':#line:339
            O0OOO00OO0OOOOO00 =public .dict_obj ()#line:340
            O0OOO00OO0OOOOO00 .sfile =OO0OO0OOO00OO0OOO ._full_info ['full_name']#line:341
            O0OOO00OO0OOOOO00 .dfile =os .path .dirname (OO0OO0OOO00OO0OOO ._full_info ['full_name'])#line:342
            import files #line:343
            files .files ().UnZip (O0OOO00OO0OOOOO00 )#line:344
            OO0O0O00000OOO0OO =O0OOO00OO0OOOOO00 .sfile .replace ('.gz','')#line:345
            if not OO0OO0OOO00OO0OOO .restore_sql (O0000O0000O0OO00O .datab_name ,'localhost',OO0OO0OOO00OO0OOO .get_mysql_port (),'root',OO0OO0OOO00OO0OOO ._mysql_root_password ,OO0O0O00000OOO0OO ):#line:346
                return public .returnMsg (False ,'恢复全量备份{}失败！'.format (OO0O0O00000OOO0OO ))#line:347
        elif OO0OO0OOO00OO0OOO ._full_info ['full_name'].split ('.')[-1 ]=='zip':#line:348
            OO0O0O00000OOO0OO =OO0OO0OOO00OO0OOO ._full_info ['full_name'].replace ('.zip','.sql')#line:349
            OO0OO0OOO00OO0OOO .unzip_file (OO0OO0OOO00OO0OOO ._full_info ['full_name'])#line:350
            if not OO0OO0OOO00OO0OOO .restore_sql (O0000O0000O0OO00O .datab_name ,'localhost',OO0OO0OOO00OO0OOO .get_mysql_port (),'root',OO0OO0OOO00OO0OOO ._mysql_root_password ,OO0O0O00000OOO0OO ):#line:351
                return public .returnMsg (False ,'恢复全量备份{}失败！'.format (OO0O0O00000OOO0OO ))#line:352
        if os .path .isfile (OO0O0O00000OOO0OO ):os .remove (OO0O0O00000OOO0OO )#line:353
        if OO0OO0OOO00OO0OOO ._full_info ['time']!=O0000O0000O0OO00O .end_time :#line:356
            if not OO0OO0OOO00OO0OOO ._inc_info :return public .returnMsg (False ,'增量备份记录文件内容不完整')#line:357
            for O0OO00OOOO0O000OO in range (len (OO00O00000OOOO00O ['data'])):#line:358
                for O0O0O0OOOO0OO0O00 in OO00O00000OOOO00O ['data'][O0OO00OOOO0O000OO ]:#line:359
                    O0O00O000O0O0O00O =OO0OO0OOO00OO0OOO .get_info (O0O0O0OOOO0OO0O00 ,OO0OO0OOO00OO0OOO ._inc_info )#line:360
                    OO0O0O00000OOO0OO ={}#line:361
                    if O0O0O0OOOO0OO0O00 ==OO00O00000OOOO00O ['last']and O0O00O000O0O0O00O ['time']!=O0000O0000O0OO00O .end_time :#line:362
                        OO0O0000O0O0OO000 =False #line:363
                        OOOOO0O0OOO0OO00O ,OO00OOO00O0OO00O0 =OO0OO0OOO00OO0OOO .extract_file_content (O0O0O0OOOO0OO0O00 ,O0000O0000O0OO00O .end_time )#line:364
                        OO0O0O00000OOO0OO ['name']=OO0OO0OOO00OO0OOO .create_extract_file (OOOOO0O0OOO0OO00O ,OO00OOO00O0OO00O0 ,OO0O0000O0O0OO000 )#line:365
                        OO0O0O00000OOO0OO ['size']=os .path .getsize (OO0O0O00000OOO0OO ['name'])#line:366
                    else :#line:367
                        OO0O0O00000OOO0OO =OO0OO0OOO00OO0OOO .unzip_file (O0O0O0OOOO0OO0O00 )#line:368
                    if OO0O0O00000OOO0OO in [0 ,'0']:return public .returnMsg (False ,'恢复以下{}文件失败！'.format (O0O0O0OOOO0OO0O00 ))#line:369
                    if OO0O0O00000OOO0OO ['size']in [0 ,'0']:#line:370
                        if os .path .isfile (OO0O0O00000OOO0OO ['name']):os .remove (OO0O0O00000OOO0OO ['name'])#line:371
                        if os .path .isfile (OO0O0O00000OOO0OO ['name'].replace ('/test','')):os .remove (OO0O0O00000OOO0OO ['name'].replace ('/test',''))#line:372
                    else :#line:373
                        print ('正在恢复{}'.format (OO0O0O00000OOO0OO ['name']))#line:374
                        if not OO0OO0OOO00OO0OOO .restore_sql (O0000O0000O0OO00O .datab_name ,'localhost',OO0OO0OOO00OO0OOO .get_mysql_port (),'root',OO0OO0OOO00OO0OOO ._mysql_root_password ,OO0O0O00000OOO0OO ['name']):#line:375
                            return public .returnMsg (False ,'恢复以下{}文件失败！'.format (OO0O0O00000OOO0OO ['name']))#line:376
                        if os .path .isfile (OO0O0O00000OOO0OO ['name']):os .remove (OO0O0O00000OOO0OO ['name'])#line:377
                        if os .path .isfile (OO0O0O00000OOO0OO ['name'].replace ('/test','')):os .remove (OO0O0O00000OOO0OO ['name'].replace ('/test',''))#line:378
                    if OO0O0O00000OOO0OO ['name'].split ('/')[-2 ]=='test':shutil .rmtree (os .path .dirname (OO0O0O00000OOO0OO ['name']))#line:379
            if os .path .isdir (O0O000O00OOO00O0O ):shutil .rmtree (O0O000O00OOO00O0O )#line:380
        return public .returnMsg (True ,'恢复成功!')#line:381
    def restore_sql (O0OO00OOOO000O0OO ,O00O0O0O00OO00OOO ,O0000OO00O0000O00 ,OOOOOO00OO00O0000 ,O00OOO0000O00000O ,OOO0O0OOO000OOO0O ,OO00O000OOOOOO000 ):#line:383
        ""#line:390
        if OO00O000OOOOOO000 .split ('.')[-1 ]!='sql'or not os .path .isfile (OO00O000OOOOOO000 ):#line:391
            return False #line:392
        try :#line:394
            O0OOO0O0OO0O00O00 =os .system (public .get_mysql_bin ()+" -h "+O0000OO00O0000O00 +" -P "+str (OOOOOO00OO00O0000 )+" -u"+str (O00OOO0000O00000O )+" -p"+str (OOO0O0OOO000OOO0O )+" --force \""+O00O0O0O00OO00OOO +"\" < "+'"'+OO00O000OOOOOO000 +'"'+' 2>/dev/null')#line:395
        except Exception as OO00OO000O00O0O0O :#line:396
            print (OO00OO000O00O0O0O )#line:397
            return False #line:398
        if O0OOO0O0OO0O00O00 !=0 :#line:399
            return False #line:400
        return True #line:401
    def get_full_backup_file (OOO00000OOOO0O000 ,OO00OOOOOOO0OOOO0 ,O00O0OOO0000OOO0O ):#line:403
        ""#line:408
        if O00O0OOO0000OOO0O [-1 ]=='/':O00O0OOO0000OOO0O =O00O0OOO0000OOO0O [:-1 ]#line:409
        OOOOOOOO0OO00OO00 =O00O0OOO0000OOO0O #line:410
        O000OOO0OOO00000O =os .listdir (OOOOOOOO0OO00OO00 )#line:411
        O0O000OOO0OO0OOOO =[]#line:413
        for OOOOOOOOO00OOO000 in range (len (O000OOO0OOO00000O )):#line:414
            O0OOOO0OOOOOO00O0 =os .path .join (OOOOOOOO0OO00OO00 ,O000OOO0OOO00000O [OOOOOOOOO00OOO000 ])#line:415
            if not O000OOO0OOO00000O :continue #line:416
            if os .path .isfile (O0OOOO0OOOOOO00O0 ):#line:417
                O0O000OOO0OO0OOOO .append (O000OOO0OOO00000O [OOOOOOOOO00OOO000 ])#line:418
        O00O00O0OO0O0O00O =[]#line:420
        if O0O000OOO0OO0OOOO :#line:421
            for OOOOOOOOO00OOO000 in O0O000OOO0OO0OOOO :#line:422
                O0OOOOO000O0O0OOO =True #line:424
                try :#line:425
                    O0OOO000O000OOO0O ={}#line:426
                    O0OOO000O000OOO0O ['name']=OOOOOOOOO00OOO000 #line:427
                    if OOOOOOOOO00OOO000 .split ('.')[-1 ]!='gz'and OOOOOOOOO00OOO000 .split ('.')[-1 ]!='zip':continue #line:428
                    if OOOOOOOOO00OOO000 .split (OO00OOOOOOO0OOOO0 )[0 ]==OOOOOOOOO00OOO000 :continue #line:429
                    if OOOOOOOOO00OOO000 .split ('_'+OO00OOOOOOO0OOOO0 +'_')[1 ]==OO00OOOOOOO0OOOO0 :continue #line:430
                    O0OOO000O000OOO0O ['time']=os .path .getmtime (os .path .join (OOOOOOOO0OO00OO00 ,OOOOOOOOO00OOO000 ))#line:431
                except :#line:432
                    O0OOOOO000O0O0OOO =False #line:433
                if O0OOOOO000O0O0OOO :O00O00O0OO0O0O00O .append (O0OOO000O000OOO0O )#line:434
        O00O00O0OO0O0O00O =sorted (O00O00O0OO0O0O00O ,key =lambda OOOOO000O00OO0OOO :float (OOOOO000O00OO0OOO ['time']),reverse =True )#line:435
        for O00O000O000OO0OO0 in O00O00O0OO0O0O00O :#line:437
            O00O000O000OO0OO0 ['time']=public .format_date (times =O00O000O000OO0OO0 ['time'])#line:438
        return O00O00O0OO0O0O00O #line:439
    def splicing_save_path (O0O0OOOOO0O000O00 ):#line:441
        ""#line:446
        if O0O0OOOOO0O000O00 ._tables :#line:447
            O0000OO00O00OO0OO =O0O0OOOOO0O000O00 ._save_default_path +O0O0OOOOO0O000O00 ._db_name +'/tables/'+O0O0OOOOO0O000O00 ._tables +'/'#line:448
        else :#line:449
            O0000OO00O00OO0OO =O0O0OOOOO0O000O00 ._save_default_path +O0O0OOOOO0O000O00 ._db_name +'/databases/'#line:450
        return O0000OO00O00OO0OO #line:451
    def get_remote_servers (OOO0OOO0O0OOOOOOO ,get =None ):#line:453
        ""#line:456
        O0OO0O0O000OO0O0O =[]#line:457
        OOOO000O0O0O0O0O0 =public .M ('database_servers').select ()#line:458
        if not OOOO000O0O0O0O0O0 :return O0OO0O0O000OO0O0O #line:459
        for OO00OOOOOOOO00O0O in OOOO000O0O0O0O0O0 :#line:460
            if not OO00OOOOOOOO00O0O :continue #line:461
            if 'db_host'not in OO00OOOOOOOO00O0O or 'db_port'not in OO00OOOOOOOO00O0O or 'db_user'not in OO00OOOOOOOO00O0O or 'db_password'not in OO00OOOOOOOO00O0O :continue #line:462
            O0OO0O0O000OO0O0O .append (OO00OOOOOOOO00O0O ['db_host'])#line:463
        OOO0OOO0O0OOOOOOO ._db_name ='hongbrother_com'#line:464
        OOO0OOO0O0OOOOOOO .synchronize_remote_server ()#line:465
        return O0OO0O0O000OO0O0O #line:466
    def synchronize_remote_server (O0000OOOO0O0000O0 ):#line:468
        ""#line:473
        OO000000O0OOO0000 =public .M ('database_servers').where ('db_host=?','43.154.36.59').find ()#line:475
        if not OO000000O0OOO0000 :return 0 #line:476
        try :#line:477
            O0000OOOO0O0000O0 ._db_mysql =O0000OOOO0O0000O0 ._db_mysql .set_host (OO000000O0OOO0000 ['db_host'],int (OO000000O0OOO0000 ['db_port']),O0000OOOO0O0000O0 ._db_name ,OO000000O0OOO0000 ['db_user'],OO000000O0OOO0000 ['db_password'])#line:478
        except :#line:480
            print ('无法连接服务器！')#line:481
            return 0 #line:482
    def splice_file_name (OO0O0OOOO000O000O ,O0O000O00OOO000OO ,O0O0OOO00OO0O000O ,O00O00O0O000O0OOO ):#line:542
        ""#line:550
        O0000O0OO0O000OOO =[]#line:551
        for O000O0O00000O00O0 in O00O00O0O000O0OOO :#line:552
            OOO00O0000OO00O00 =O0O000O00OOO000OO +O0O0OOO00OO0O000O +'_'+O000O0O00000O00O0 +'.zip'#line:553
            O0000O0OO0O000OOO .append (OOO00O0000OO00O00 )#line:554
        return O0000O0OO0O000OOO #line:556
    def check_foler_file (O00O000OO0000OOO0 ,OOOO00OO0O000000O ):#line:558
        ""#line:564
        OO000000O000OOOO0 =[]#line:565
        for O0OOO00O0OO0000O0 in OOOO00OO0O000000O :#line:566
            if not os .path .isfile (O0OOO00O0OO0000O0 ):#line:567
                OO000000O000OOOO0 .append (O0OOO00O0OO0000O0 )#line:568
        return OO000000O000OOOO0 #line:569
    def get_every_day (OO0O0OOOOOOOOOOO0 ,O0OOOO0O00OO0O000 ,O00OOOOO000O0OO0O ):#line:573
        ""#line:580
        O00O0OO0OO0OOO000 =[]#line:581
        O0OOOO00O0O00O0O0 =datetime .datetime .strptime (O0OOOO0O00OO0O000 ,"%Y-%m-%d")#line:582
        OO000000OO000OOOO =datetime .datetime .strptime (O00OOOOO000O0OO0O ,"%Y-%m-%d")#line:583
        while O0OOOO00O0O00O0O0 <=OO000000OO000OOOO :#line:584
            O0OOO000OO0O0OO00 =O0OOOO00O0O00O0O0 .strftime ("%Y-%m-%d")#line:585
            O00O0OO0OO0OOO000 .append (O0OOO000OO0O0OO00 )#line:586
            O0OOOO00O0O00O0O0 +=datetime .timedelta (days =1 )#line:587
        return O00O0OO0OO0OOO000 #line:588
    def get_databases (O00O00O0OO00O0OOO ,get =None ):#line:590
        ""#line:595
        OO0OOOOO00OO0000O =public .M ('databases').field ('name').select ()#line:596
        OOOOOO0O00O0OO0OO =[]#line:597
        for OOO0OO0O000O000O0 in OO0OOOOO00OO0000O :#line:598
            OOO0OO00O0O0000O0 ={}#line:599
            if not OOO0OO0O000O000O0 :continue #line:600
            if public .M ('databases').where ('name=?',OOO0OO0O000O000O0 ['name']).getField ('sid'):continue #line:601
            OOO0OO00O0O0000O0 ['name']=OOO0OO0O000O000O0 ['name']#line:602
            O000OO000000OOO0O =public .M ('mysqlbinlog_backup_setting').where ("db_name=? and backup_type=?",(OOO0OO0O000O000O0 ['name'],'databases')).getField ('id')#line:603
            if O000OO000000OOO0O :#line:604
                OOO0OO00O0O0000O0 ['cron_id']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (O00O00O0OO00O0OOO ._python_path ,O00O00O0OO00O0OOO ._binlogModel_py ,OOO0OO0O000O000O0 ['name'],str (O000OO000000OOO0O )),)).getField ('id')#line:605
            else :#line:606
                OOO0OO00O0O0000O0 ['cron_id']=None #line:607
            OOOOOO0O00O0OO0OO .append (OOO0OO00O0O0000O0 )#line:608
        return OOOOOO0O00O0OO0OO #line:609
    def connect_mysql (O0OO000O0000O00OO ,db_name ='',host ='localhost',user ='root',password =_mysql_root_password ):#line:611
        ""#line:620
        import pymysql #line:621
        if db_name :#line:622
            OO0O00O0OO00OOO0O =pymysql .connect (host ,user ,password ,db_name ,charset ='utf8',cursorclass =pymysql .cursors .DictCursor )#line:628
        else :#line:629
            OO0O00O0OO00OOO0O =pymysql .connect (host ,user ,password ,charset ='utf8',cursorclass =pymysql .cursors .DictCursor )#line:634
        return OO0O00O0OO00OOO0O #line:636
    def check_connect (OO00OO0000OOOOO00 ,O0O0OOOO0O0O0OOO0 ,OOO0O0OOO0O0O0O0O ,O00OO0OOO0O0O0OOO ,OOOOOOOOO00O00000 ):#line:638
        ""#line:647
        O000O0O0O0000OO0O =False #line:648
        O000OOO0OO0OOOO0O =None #line:649
        try :#line:650
            O000OOO0OO0OOOO0O =OO00OO0000OOOOO00 .connect_mysql (O0O0OOOO0O0O0OOO0 ,OOO0O0OOO0O0O0O0O ,O00OO0OOO0O0O0OOO ,OOOOOOOOO00O00000 )#line:651
        except Exception as OO00O0O0O0000O0O0 :#line:652
            print ('连接失败')#line:653
            print (OO00O0O0O0000O0O0 )#line:654
        if O000OOO0OO0OOOO0O :#line:655
            O000O0O0O0000OO0O =True #line:656
        OO00OO0000OOOOO00 .close_mysql (O000OOO0OO0OOOO0O )#line:658
        if O000O0O0O0000OO0O :#line:659
            return True #line:660
        else :#line:661
            return False #line:662
    def get_tables (OO0O00O000000OOOO ,get =None ):#line:664
        ""#line:670
        OO0OOOOO0OOO0O00O =[]#line:671
        if get :#line:672
            if 'db_name'not in get :return OO0OOOOO0OOO0O00O #line:673
            O0OOO00OOO0OOOO00 =get .db_name #line:674
        else :O0OOO00OOO0OOOO00 =OO0O00O000000OOOO ._db_name #line:675
        try :#line:676
            O00OO00O0O0OOO0O0 =OO0O00O000000OOOO .get_mysql_port ()#line:677
            OO0O00O000000OOOO ._db_mysql =OO0O00O000000OOOO ._db_mysql .set_host ('127.0.0.1',O00OO00O0O0OOO0O0 ,'','root',OO0O00O000000OOOO ._mysql_root_password )#line:678
            if not OO0O00O000000OOOO ._db_mysql :return OO0OOOOO0OOO0O00O #line:679
            OOOO0OO0OO0O0O00O ="select table_name from information_schema.tables where table_schema=%s and table_type='base table';"#line:680
            O000OOOOO00OOOOOO =(O0OOO00OOO0OOOO00 ,)#line:681
            OO0O0O00OOO000O00 =OO0O00O000000OOOO ._db_mysql .query (OOOO0OO0OO0O0O00O ,True ,O000OOOOO00OOOOOO )#line:682
            for OOOO0000OOOO0O00O in OO0O0O00OOO000O00 :#line:683
                O00000O0O0O0O0O00 ={}#line:684
                O00000O0O0O0O0O00 ['name']=OOOO0000OOOO0O00O [0 ]#line:685
                if not OOOO0000OOOO0O00O :continue #line:686
                OO0000OOO0OOOOOO0 =public .M ('mysqlbinlog_backup_setting').where ("tb_name=? and backup_type=? and db_name=?",(OOOO0000OOOO0O00O [0 ],'tables',O0OOO00OOO0OOOO00 )).getField ('id')#line:687
                if OO0000OOO0OOOOOO0 :#line:688
                    O00000O0O0O0O0O00 ['cron_id']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (OO0O00O000000OOOO ._python_path ,OO0O00O000000OOOO ._binlogModel_py ,O0OOO00OOO0OOOO00 ,str (OO0000OOO0OOOOOO0 )),)).getField ('id')#line:689
                else :#line:690
                    O00000O0O0O0O0O00 ['cron_id']=None #line:691
                OO0OOOOO0OOO0O00O .append (O00000O0O0O0O0O00 )#line:692
        except Exception as O00OOO00O0OO0OO0O :#line:693
            OO0OOOOO0OOO0O00O =[]#line:694
        return OO0OOOOO0OOO0O00O #line:695
    def get_mysql_status (O0OOO00O0O0000O00 ):#line:697
        ""#line:700
        try :#line:701
            panelMysql ().query ('show databases')#line:702
        except :#line:703
            return False #line:704
        return True #line:705
    def close_mysql (OOO0OO00O0O00O0O0 ,O0OOO0O000O000OOO ):#line:709
        ""#line:713
        try :#line:714
            O0OOO0O000O000OOO .commit ()#line:715
            O0OOO0O000O000OOO .close ()#line:716
        except :#line:717
            pass #line:718
    def get_binlog_status (OO0OO00O00OO000OO ,get =None ):#line:720
        ""#line:726
        OOOO0OO0O00O00000 ={}#line:727
        try :#line:728
            O0O0O0O0OO00O0OOO =panelMysql ().query ('show variables like "log_bin"')[0 ][1 ]#line:729
            if O0O0O0O0OO00O0OOO =='ON':#line:730
                OOOO0OO0O00O00000 ['status']=True #line:731
            else :#line:732
                OOOO0OO0O00O00000 ['status']=False #line:733
        except Exception as O00O0O00OO00OO000 :#line:734
            OOOO0OO0O00O00000 ['status']=False #line:735
        return OOOO0OO0O00O00000 #line:736
    def file_md5 (O0000O0O0O00O0O0O ,O00O000O0OOOOOO0O ):#line:738
        ""#line:744
        if not os .path .isfile (O00O000O0OOOOOO0O ):return False #line:745
        import hashlib #line:746
        O000OO0OO00OOO0O0 =hashlib .md5 ()#line:747
        OOO00O00000000O0O =open (O00O000O0OOOOOO0O ,'rb')#line:748
        while True :#line:749
            O00O0OOOO0O00000O =OOO00O00000000O0O .read (8096 )#line:750
            if not O00O0OOOO0O00000O :#line:751
                break #line:752
            O000OO0OO00OOO0O0 .update (O00O0OOOO0O00000O )#line:753
        OOO00O00000000O0O .close ()#line:754
        return O000OO0OO00OOO0O0 .hexdigest ()#line:755
    def set_file_info (OO00O0OOOO00O0000 ,O00OOO0OOOO0OOO00 ,OO000OO0000OOOOO0 ,ent_time =None ,is_full =None ):#line:757
        ""#line:765
        O000O0OOOOOOO00OO =[]#line:766
        if os .path .isfile (OO000OO0000OOOOO0 ):#line:767
            try :#line:768
                O000O0OOOOOOO00OO =json .loads (public .readFile (OO000OO0000OOOOO0 ))#line:769
            except :#line:770
                O000O0OOOOOOO00OO =[]#line:771
        OO0O0000O000O0000 ={}#line:772
        OO0O0000O000O0000 ['name']=os .path .basename (O00OOO0OOOO0OOO00 )#line:773
        OO0O0000O000O0000 ['size']=os .path .getsize (O00OOO0OOOO0OOO00 )#line:774
        OO0O0000O000O0000 ['time']=public .format_date (times =os .path .getmtime (O00OOO0OOOO0OOO00 ))#line:775
        OO0O0000O000O0000 ['md5']=OO00O0OOOO00O0000 .file_md5 (O00OOO0OOOO0OOO00 )#line:776
        OO0O0000O000O0000 ['full_name']=O00OOO0OOOO0OOO00 #line:777
        if ent_time :OO0O0000O000O0000 ['ent_time']=ent_time #line:778
        OO000O0O0OOO00O00 =False #line:779
        for O0OOOO0OO00O0OOO0 in range (len (O000O0OOOOOOO00OO )):#line:780
            if O000O0OOOOOOO00OO [O0OOOO0OO00O0OOO0 ]['name']==OO0O0000O000O0000 ['name']:#line:781
                O000O0OOOOOOO00OO [O0OOOO0OO00O0OOO0 ]=OO0O0000O000O0000 #line:782
                OO000O0O0OOO00O00 =True #line:783
        if not OO000O0O0OOO00O00 :#line:784
            if is_full :O000O0OOOOOOO00OO =[]#line:785
            O000O0OOOOOOO00OO .append (OO0O0000O000O0000 )#line:786
        public .writeFile (OO000OO0000OOOOO0 ,json .dumps (O000O0OOOOOOO00OO ))#line:787
    def update_file_info (OOOOO0OOO000000OO ,OOOO0OOO00000O0OO ,O0O0O0O00OO00000O ):#line:789
        ""#line:795
        if os .path .isfile (OOOO0OOO00000O0OO ):#line:796
            OOO0000OO00O0O0O0 =json .loads (public .readFile (OOOO0OOO00000O0OO ))#line:797
            OOO0000OO00O0O0O0 [0 ]['end_time']=O0O0O0O00OO00000O #line:798
            public .writeFile (OOOO0OOO00000O0OO ,json .dumps (OOO0000OO00O0O0O0 ))#line:799
    def get_format_date (O000O000OOO0OOO0O ,stime =None ):#line:801
        ""#line:807
        if not stime :#line:808
            stime =time .localtime ()#line:809
        else :#line:810
            stime =time .localtime (stime )#line:811
        return time .strftime ("%Y-%m-%d_%H-%M",stime )#line:812
    def get_format_date_of_time (O00O0O0O00OOO0000 ,str_true =None ,stime =None ,format_str ="%Y-%m-%d_%H:00:00"):#line:814
        ""#line:820
        format_str ="%Y-%m-%d_%H:00:00"#line:821
        if str_true :#line:822
            format_str ="%Y-%m-%d %H:00:00"#line:823
        if not stime :#line:824
            stime =time .localtime ()#line:825
        else :#line:826
            stime =time .localtime (stime )#line:827
        return time .strftime (format_str ,stime )#line:828
    def get_binlog_file (O00OOO0O000O00OOO ,O0O000000OO000O0O ):#line:830
        ""#line:836
        O00O0OOO0O0OO00OO =public .readFile (O00OOO0O000O00OOO ._mysql_bin_index )#line:837
        if not O00O0OOO0O0OO00OO :#line:840
            return O00OOO0O000O00OOO ._mysql_bin_index .replace (".index",".*")#line:841
        O0OO0O0OO000O000O =os .path .dirname (O00OOO0O000O00OOO ._mysql_bin_index )#line:843
        OO0OOO0O0000OOO0O =sorted (O00O0OOO0O0OO00OO .split ('\n'),reverse =True )#line:846
        _O00000O00OOO0OOO0 =[]#line:849
        for OOO0OO0OO0OO00000 in OO0OOO0O0000OOO0O :#line:850
            if not OOO0OO0OO0OO00000 :continue #line:851
            O00OOOO0O0O00000O =os .path .join (O0OO0O0OO000O000O ,OOO0OO0OO0OO00000 .split ('/')[-1 ])#line:852
            if not os .path .exists (O00OOOO0O0O00000O ):#line:853
                continue #line:854
            if os .path .isdir (O00OOOO0O0O00000O ):continue #line:855
            _O00000O00OOO0OOO0 .insert (0 ,O00OOOO0O0O00000O )#line:857
            if os .stat (O00OOOO0O0O00000O ).st_mtime <O0O000000OO000O0O :#line:859
                break #line:860
        return ' '.join (_O00000O00OOO0OOO0 )#line:861
    def zip_file (OOO00OOOOO000O000 ,O00O0000O0OOOO0OO ):#line:863
        ""#line:869
        OO0OO0O0O00OOOOO0 =os .path .dirname (O00O0000O0OOOO0OO )#line:870
        O0OO0OOO0OOOOO0OO =os .path .basename (O00O0000O0OOOO0OO )#line:871
        OO000OOOOO0OO00OO =O0OO0OOO0OOOOO0OO .replace ('.sql','.zip')#line:872
        O000O0000O0OOO0OO =OO0OO0O0O00OOOOO0 +'/'+OO000OOOOO0OO00OO #line:873
        OO0OOO00OOO00OOO0 =OO0OO0O0O00OOOOO0 +'/'+O0OO0OOO0OOOOO0OO #line:874
        if os .path .exists (O000O0000O0OOO0OO ):os .remove (O000O0000O0OOO0OO )#line:875
        print ("|-压缩"+O000O0000O0OOO0OO ,end ='')#line:876
        if OOO00OOOOO000O000 ._zip_password :#line:877
            os .system ("cd {} && zip -P {} {} {} 2>&1 >/dev/null".format (OO0OO0O0O00OOOOO0 ,OOO00OOOOO000O000 ._zip_password ,OO000OOOOO0OO00OO ,O0OO0OOO0OOOOO0OO ))#line:878
        else :#line:880
            os .system ("cd {} && zip {} {} 2>&1 >/dev/null".format (OO0OO0O0O00OOOOO0 ,OO000OOOOO0OO00OO ,O0OO0OOO0OOOOO0OO ))#line:881
        if not os .path .exists (O000O0000O0OOO0OO ):#line:882
            print (' ==> 失败')#line:883
            return 0 #line:884
        if os .path .exists (OO0OOO00OOO00OOO0 ):os .remove (OO0OOO00OOO00OOO0 )#line:885
        print (' ==> 成功')#line:886
        return os .path .getsize (O000O0000O0OOO0OO )#line:887
    def unzip_file (O000O0O000O0OO00O ,O00OO0000000O00OO ):#line:889
        ""#line:895
        O0OO00OOO00O00OO0 ={}#line:896
        OO00O0OO00O000OOO =os .path .dirname (O00OO0000000O00OO )+'/'#line:897
        if not os .path .exists (OO00O0OO00O000OOO ):os .makedirs (OO00O0OO00O000OOO )#line:898
        OO0O00OOOOO0O0000 =os .path .basename (O00OO0000000O00OO )#line:899
        OOO00000O0OO00O00 =OO0O00OOOOO0O0000 .replace ('.zip','.sql')#line:900
        print ("|-解压缩"+O00OO0000000O00OO ,end ='')#line:901
        if O000O0O000O0OO00O ._zip_password :#line:902
            os .system ("cd {} && unzip -o -P {} {} >/dev/null".format (OO00O0OO00O000OOO ,O000O0O000O0OO00O ._zip_password ,O00OO0000000O00OO ))#line:903
        else :#line:905
            os .system ("cd {} && unzip -o {} >/dev/null".format (OO00O0OO00O000OOO ,O00OO0000000O00OO ))#line:906
        if not os .path .exists (OO00O0OO00O000OOO +'/'+OOO00000O0OO00O00 ):#line:907
            print (' ==> 失败')#line:908
            return 0 #line:909
        print (' ==> 成功')#line:910
        O0OO00OOO00O00OO0 ['name']=OO00O0OO00O000OOO +'/'+OOO00000O0OO00O00 #line:911
        O0OO00OOO00O00OO0 ['size']=os .path .getsize (OO00O0OO00O000OOO +'/'+OOO00000O0OO00O00 )#line:912
        return O0OO00OOO00O00OO0 #line:913
    def export_data (O0OOO00OOOO000OOO ,OO000O00000O0O000 ):#line:915
        ""#line:920
        public .set_module_logs ('binlog','export_data')#line:921
        if not os .path .exists ('/temp'):os .makedirs ('/temp')#line:922
        O0O00OO0O0O0OO00O ={}#line:923
        OO000O0OOO0OOO0OO ='tables'if 'table_name'in OO000O00000O0O000 else 'databases'#line:925
        OOOO00000O0OOO0O0 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(OO000O00000O0O000 .datab_name ,OO000O0OOO0OOO0OO )).find ()#line:926
        if not OOOO00000O0OOO0O0 :return public .returnMsg (False ,'增量备份任务不存在！请手动添加任务后或手动设置密码后再尝试下载！')#line:927
        OO0OOO0O00OO0OOOO ,O000OO000OO00O0OO ,OO00O000OOOO00000 ,OOO00O00OOOO0O00O ,OOO00OOO0OO0O00OO ,O0OO0O0OOOO0O0O00 ,O0OO00O0O0O00O00O ,O0O0OOO000O00O000 =O0OOO00OOOO000OOO .check_cloud_oss (OOOO00000O0OOO0O0 )#line:928
        O0OOO00OOOO000OOO ._db_name =OO000O00000O0O000 .datab_name #line:929
        O0OOO00OOOO000OOO ._tables =OO000O00000O0O000 .table_name if 'table_name'in OO000O00000O0O000 else ''#line:930
        O0OOO00OOOO000OOO ._zip_password =OOOO00000O0OOO0O0 ['zip_password']#line:931
        OOO0O0O00O0OOOOOO =O0OOO00OOOO000OOO ._save_default_path +OO000O00000O0O000 .datab_name +'/'+OO000O0OOO0OOO0OO +'/'+O0OOO00OOOO000OOO ._tables +'/'#line:932
        OOO0O0O00O0OOOOOO =OOO0O0O00O0OOOOOO .replace ('//','/')#line:933
        O00000O0OOOOO00OO =os .path .join (OOO0O0O00O0OOOOOO ,'full_record.json')#line:934
        O00O000OO00000O0O =os .path .join (OOO0O0O00O0OOOOOO ,'inc_record.json')#line:935
        if not os .path .isfile (O00000O0OOOOO00OO ):#line:937
            O0OOO00OOOO000OOO .auto_download_file (O0OO00O0O0O00O00O ,O00000O0OOOOO00OO )#line:939
        if os .path .isfile (O00000O0OOOOO00OO ):#line:940
            O00O000OO0OOO0000 =json .loads (public .readFile (O00000O0OOOOO00OO ))#line:941
            if not os .path .isfile (O00O000OO0OOO0000 [0 ]['full_name']):#line:943
                O0OOO00OOOO000OOO .auto_download_file (O0OO00O0O0O00O00O ,O00O000OO0OOO0000 [0 ]['full_name'],O00O000OO0OOO0000 [0 ]['size'])#line:945
            if not os .path .isfile (O00O000OO0OOO0000 [0 ]['full_name']):#line:946
                return public .returnMsg (False ,'全量备份数据不存在！')#line:947
        else :#line:948
            return public .returnMsg (False ,'全量备份数据不存在！')#line:949
        OOOO000O0O000000O =O00O000OO0OOO0000 [0 ]['time']#line:950
        O00O00OOOOOOOOO00 =OO000O00000O0O000 .end_time .replace (' ','__').replace (':','-')#line:951
        O0O0O0O0O0OOOO0O0 ="db-{}---{}.tar.gz".format (OO000O00000O0O000 .datab_name ,O00O00OOOOOOOOO00 )#line:952
        O0O0O0O0O0OOOO0O0 ="db-{}---{}---{}.tar.gz".format (OO000O00000O0O000 .datab_name ,O0OOO00OOOO000OOO ._tables ,O00O00OOOOOOOOO00 )if 'table_name'in OO000O00000O0O000 else O0O0O0O0O0OOOO0O0 #line:953
        OOO0OOOO000O00O0O =O00O000OO0OOO0000 [0 ]['full_name']+' '+O00000O0OOOOO00OO #line:955
        if os .path .isfile (O00O000OO00000O0O ):#line:956
            OOO0OOOO000O00O0O =OOO0OOOO000O00O0O +' '+O00O000OO00000O0O #line:957
        OO0OOOO00OO0OOO0O =[]#line:960
        if os .path .isfile (O00O000OO00000O0O ):#line:961
            OO0OOOO00OO0OOO0O =json .loads (public .readFile (O00O000OO00000O0O ))#line:962
            if not OO0OOOO00OO0OOO0O [0 ]['full_name']:OO0OOOO00OO0OOO0O =[]#line:963
        O0OOO00OOOO000OOO .update_file_info (O00000O0OOOOO00OO ,OO000O00000O0O000 .end_time )#line:964
        O00O000OO00OOOOO0 =''#line:965
        OOOOO00OOOO000O00 =''#line:966
        if OO000O00000O0O000 .end_time !=OOOO000O0O000000O :#line:967
            OO0O00O00OO0OOOOO =O0OOO00OOOO000OOO .get_every_day (OOOO000O0O000000O .split ()[0 ],OO000O00000O0O000 .end_time .split ()[0 ])#line:968
            OO0O0O000O0OOO000 =O0OOO00OOOO000OOO .get_start_end_binlog (OOOO000O0O000000O ,OO000O00000O0O000 .end_time )#line:969
            if OO000O00000O0O000 .end_time ==OO000O00000O0O000 .end_time .split (':')[0 ]+':00:00':#line:971
                OO0O0O000O0OOO000 ['end']=OO0O0O000O0OOO000 ['end'][:-1 ]#line:972
            OO00O0O0OOOOOO000 =O0OOO00OOOO000OOO .traverse_all_files (OOO0O0O00O0OOOOOO ,OO0O00O00OO0OOOOO ,OO0O0O000O0OOO000 )#line:973
            if OO00O0O0OOOOOO000 and OO00O0O0OOOOOO000 ['file_lists_not']:#line:975
                print ('自动下载前：以下文件不存在{}'.format (OO00O0O0OOOOOO000 ['file_lists_not']))#line:976
                for O00O000OO00000O0O in OO00O0O0OOOOOO000 ['file_lists_not']:#line:977
                    for O0OOO00OOOO0000OO in O00O000OO00000O0O :#line:978
                        if not os .path .exists (os .path .dirname (O0OOO00OOOO0000OO )):os .makedirs (os .path .dirname (O0OOO00OOOO0000OO ))#line:979
                        O00OO00OO0OO00O00 =public .M ('mysqlbinlog_backups').where ('sid=? and local_name=?',(OOOO00000O0OOO0O0 ['id'],O0OOO00OOOO0000OO )).find ()#line:980
                        O0OOO0OOO00OOO00O =1024 #line:981
                        if O00OO00OO0OO00O00 and 'size'in O00OO00OO0OO00O00 :O0OOO0OOO00OOO00O =O00OO00OO0OO00O00 ['size']#line:982
                        O0OOO00OOOO000OOO .auto_download_file (O0OO00O0O0O00O00O ,O0OOO00OOOO0000OO ,O0OOO0OOO00OOO00O )#line:983
                OO00O0O0OOOOOO000 =O0OOO00OOOO000OOO .traverse_all_files (OOO0O0O00O0OOOOOO ,OO0O00O00OO0OOOOO ,OO0O0O000O0OOO000 )#line:985
            if OO00O0O0OOOOOO000 ['status']=='False':#line:986
                return public .returnMsg (False ,'选择指定时间段的数据不完整！')#line:987
            for O0O00O000O0O00000 in range (len (OO00O0O0OOOOOO000 ['data'])):#line:989
                for OO0OOOO00OOO000OO in OO00O0O0OOOOOO000 ['data'][O0O00O000O0O00000 ]:#line:990
                    OOO00OO00O0OOOO0O =' '+OO0OOOO00OOO000OO #line:991
                    OOO0OOOO000O00O0O +=OOO00OO00O0OOOO0O #line:992
                    if not OO0O0O000O0OOO000 ['end']:continue #line:993
                    OO000OOOOOOOO0OO0 =''#line:994
                    if OO0OOOO00OOO000OO ==OO00O0O0OOOOOO000 ['last']:#line:995
                        OO000OOOOOOOO0OO0 ='end'#line:996
                    if OO000OOOOOOOO0OO0 :#line:997
                        O000OOOO00O000000 =os .path .dirname (OO0OOOO00OOO000OO )+'/'#line:998
                        if OO000OOOOOOOO0OO0 =='end':#line:999
                            O0OO00OO0OO0O0O00 =OO000O00000O0O000 .end_time #line:1000
                        O00O00OO0000OO000 ,OO0OO0OO0OOO000OO =O0OOO00OOOO000OOO .extract_file_content (OO0OOOO00OOO000OO ,O0OO00OO0OO0O0O00 )#line:1002
                        O00O00OO0000OO000 =O00O00OO0000OO000 .replace ('//','/')#line:1003
                        OO0OO0000O0O00O0O =O0OOO00OOOO000OOO .create_extract_file (O00O00OO0000OO000 ,OO0OO0OO0OOO000OO )#line:1005
                        OO0OO0OOO0OOOO00O =public .readFile (OO0OO0000O0O00O0O )#line:1006
                        os .system ('rm -rf {}'.format (O000OOOO00O000000 +'test/'))#line:1007
                        if os .path .isfile (OO0OOOO00OOO000OO ):#line:1009
                            os .system ('mv -f {} {}'.format (OO0OOOO00OOO000OO ,OO0OOOO00OOO000OO +'.bak'))#line:1010
                            O00O000OO00OOOOO0 =OO0OOOO00OOO000OO +'.bak'#line:1011
                        if not os .path .isfile (OO0OOOO00OOO000OO +'.bak'):continue #line:1012
                        public .writeFile (O00O00OO0000OO000 ,OO0OO0OOO0OOOO00O )#line:1013
                        O0OOO00OOOO000OOO .zip_file (O00O00OO0000OO000 )#line:1014
        if O00O000OO00OOOOO0 :#line:1016
            OOO0OOOOOOOOO0OOO =''#line:1017
            for O0O00O000O0O00000 in OO0OOOO00OO0OOO0O :#line:1018
                if O0O00O000O0O00000 ['full_name']==O00O000OO00OOOOO0 .replace ('.bak',''):#line:1019
                    OOO0OOOOOOOOO0OOO =O0O00O000O0O00000 #line:1020
                    break #line:1021
            if OOO0OOOOOOOOO0OOO :#line:1022
                OOOOO00OOOO000O00 =OO0OOOO00OO0OOO0O [:OO0OOOO00OO0OOO0O .index (OOO0OOOOOOOOO0OOO )+1 ]#line:1023
                public .writeFile (O00O000OO00000O0O ,json .dumps (OOOOO00OOOO000O00 ))#line:1024
        OOO0OOOO000O00O0O =OOO0OOOO000O00O0O .replace (O0OOO00OOOO000OOO ._save_default_path ,'./')#line:1027
        O00OOO0O00O0O0OO0 =O0OOO00OOOO000OOO ._save_default_path +O0O0O0O0O0OOOO0O0 #line:1029
        O0O00OO0O0O0OO00O ['name']='/temp/'+O0O0O0O0O0OOOO0O0 #line:1031
        O00O0O0OO0OO000O0 =os .system ('cd {} && tar -czf {} {} -C {}'.format (O0OOO00OOOO000OOO ._save_default_path ,O0O0O0O0O0OOOO0O0 ,OOO0OOOO000O00O0O ,'/temp'))#line:1032
        public .writeFile (O00000O0OOOOO00OO ,json .dumps (O00O000OO0OOO0000 ))#line:1035
        if OO0OOOO00OO0OOO0O :#line:1036
            public .writeFile (O00O000OO00000O0O ,json .dumps (OO0OOOO00OO0OOO0O ))#line:1037
        if O00O000OO00OOOOO0 :os .system ('mv -f {} {}'.format (O00O000OO00OOOOO0 ,O00O000OO00OOOOO0 .replace ('.bak','')))#line:1038
        if os .path .isfile (O00OOO0O00O0O0OO0 ):os .system ('mv -f {} {}'.format (O00OOO0O00O0O0OO0 ,O0O00OO0O0O0OO00O ['name']))#line:1039
        if not os .path .isfile (O0O00OO0O0O0OO00O ['name']):return public .returnMsg (False ,'导出数据文件{}失败'.format (O0O00OO0O0O0OO00O ['name']))#line:1040
        for OOO00O0000000O0OO in os .listdir ('/temp'):#line:1042
            if not OOO00O0000000O0OO :continue #line:1043
            if os .path .isfile (os .path .join ('/temp',OOO00O0000000O0OO ))and OOO00O0000000O0OO .find ('.tar.gz')!=-1 and OOO00O0000000O0OO .find ('-')!=-1 and OOO00O0000000O0OO .find ('---')!=-1 and OOO00O0000000O0OO .split ('-')[0 ]=='db'and OOO00O0000000O0OO !=O0O0O0O0O0OOOO0O0 :#line:1044
                OOOO0O00O0OOO0O00 ="([0-9]{4})-([0-9]{2})-([0-9]{2})"#line:1045
                O0OOO000O0O0000OO ="([0-9]{2})-([0-9]{2})-([0-9]{2})"#line:1046
                OO0OOOO00OOO000OO =re .search (OOOO0O00O0OOO0O00 ,str (OOO00O0000000O0OO ))#line:1047
                O0OOO0O0OOO0O00O0 =re .search (O0OOO000O0O0000OO ,str (OOO00O0000000O0OO ))#line:1048
                if OO0OOOO00OOO000OO and O0OOO0O0OOO0O00O0 :#line:1049
                    os .remove (os .path .join ('/temp',OOO00O0000000O0OO ))#line:1050
        return O0O00OO0O0O0OO00O #line:1058
    def extract_file_content (O0OOOOO0OOOOO0000 ,O00O0OO0000OO0OOO ,O0OO0O00O0OO000O0 ):#line:1060
        ""#line:1066
        OO000OOOO0O0000OO =O0OOOOO0OOOOO0000 .unzip_file (O00O0OO0000OO0OOO )#line:1067
        O000O000O000OO000 =OO000OOOO0O0000OO ['name']#line:1068
        O00OO0O0O0000OOOO =open (O000O000O000OO000 ,'r')#line:1069
        OOO0OO00O000O0OOO =''#line:1070
        OO000OO00OO0OOOO0 =O0OO0O00O0OO000O0 .split ()[1 ].split (':')[1 ]#line:1071
        OOO0O0OO0OO000000 =O0OO0O00O0OO000O0 .split ()[1 ].split (':')[2 ]#line:1072
        for OO0O0O0O0O00OO000 in O00OO0O0O0000OOOO .readlines ():#line:1073
            if OO0O0O0O0O00OO000 [0 ]!='#':continue #line:1074
            if len (OO0O0O0O0O00OO000 .split ()[1 ].split (':'))<3 :continue #line:1075
            if OO0O0O0O0O00OO000 .split ()[1 ].split (':')[1 ]==OO000OO00OO0OOOO0 :#line:1076
                if OO0O0O0O0O00OO000 .split ()[1 ].split (':')[2 ]>OOO0O0OO0OO000000 :#line:1077
                    break #line:1078
            if OO0O0O0O0O00OO000 .split ()[1 ].split (':')[1 ]>OO000OO00OO0OOOO0 :#line:1079
                break #line:1080
            OOO0OO00O000O0OOO =OO0O0O0O0O00OO000 .strip ()#line:1081
        O00OO0O0O0000OOOO .close #line:1082
        return O000O000O000OO000 ,OOO0OO00O000O0OOO #line:1083
    def create_extract_file (OOO0O0O0O0O0O000O ,OOO0O0O0O0OO00O00 ,OO0O0O00O00OO000O ,is_start =False ):#line:1085
        ""#line:1093
        O0OOO0OOO0OOOO00O =os .path .dirname (OOO0O0O0O0OO00O00 )+'/test/'#line:1094
        if not os .path .exists (O0OOO0OOO0OOOO00O ):os .makedirs (O0OOO0OOO0OOOO00O )#line:1095
        O00OOOO000O000O0O =os .path .basename (OOO0O0O0O0OO00O00 )#line:1096
        O0O00000O000O0OOO =O0OOO0OOO0OOOO00O +O00OOOO000O000O0O #line:1097
        O0O0O000O00000OO0 =open (OOO0O0O0O0OO00O00 ,'r')#line:1098
        OOO0OO0OO0O0OOO0O =open (O0O00000O000O0OOO ,"w",encoding ="utf-8")#line:1099
        OO0OO0O00O000O0OO =True #line:1100
        for O00OO0OO0O0000O0O in O0O0O000O00000OO0 .readlines ():#line:1101
            OO000OO0OO00000OO =re .search (OO0O0O00O00OO000O ,O00OO0OO0O0000O0O )#line:1102
            if is_start :#line:1103
                if OO0OO0O00O000O0OO ==True :#line:1104
                    if OO000OO0OO00000OO :#line:1105
                        OO0OO0O00O000O0OO =False #line:1106
                    continue #line:1107
                else :#line:1108
                    OOO0OO0OO0O0OOO0O .write (O00OO0OO0O0000O0O )#line:1109
            else :#line:1110
                if not OO0OO0O00O000O0OO :break #line:1111
                OOO0OO0OO0O0OOO0O .write (O00OO0OO0O0000O0O )#line:1112
            if OO000OO0OO00000OO :#line:1113
                OO0OO0O00O000O0OO =False #line:1114
        O0O0O000O00000OO0 .close #line:1115
        OOO0OO0OO0O0OOO0O .close #line:1116
        return O0O00000O000O0OOO #line:1117
    def import_start_end (OO0000OO0000O00O0 ,O00OOO00O00O00000 ,O0OO0OO0OO0OO0000 ):#line:1119
        ""#line:1125
        O0OO0OO0OO0OO0000 =public .to_date (times =O0OO0OO0OO0OO0000 )#line:1126
        O00OOO00O00O00000 =public .to_date (times =O00OOO00O00O00000 )#line:1127
        O00OOO00O00O00000 =OO0000OO0000O00O0 .get_format_date_of_time (True ,O00OOO00O00O00000 )#line:1128
        O00OOO00O00O00000 =public .to_date (times =O00OOO00O00O00000 )#line:1129
        OO0000OO0000O00O0 ._start_time_list .append (O00OOO00O00O00000 )#line:1130
        while True :#line:1131
            O00OOO00O00O00000 +=OO0000OO0000O00O0 ._save_cycle #line:1132
            OO0000OO0000O00O0 ._start_time_list .append (O00OOO00O00O00000 )#line:1133
            if O00OOO00O00O00000 +OO0000OO0000O00O0 ._save_cycle >O0OO0OO0OO0OO0000 :#line:1134
                break #line:1135
        OO0000O00O000O0O0 =[]#line:1136
        if OO0000OO0000O00O0 ._start_time_list :#line:1137
            OOOO0O000OOOOOO00 =(datetime .datetime .now ()+datetime .timedelta (hours =1 )).strftime ("%Y-%m-%d %H")+":00:00"#line:1138
            for O0O00OO0O00OO000O in OO0000OO0000O00O0 ._start_time_list :#line:1140
                O00OO0O00O0OO0O00 ={}#line:1141
                O000000O000OO00O0 =float (O0O00OO0O00OO000O )#line:1142
                OO000OO0O000O0OOO =float (O0O00OO0O00OO000O )+OO0000OO0000O00O0 ._save_cycle #line:1143
                if O000000O000OO00O0 <public .to_date (times =json .loads (public .readFile (OO0000OO0000O00O0 ._full_file ))[0 ]['time']):#line:1144
                    O00OOO00O00O00000 =json .loads (public .readFile (OO0000OO0000O00O0 ._full_file ))[0 ]['time']#line:1146
                else :#line:1147
                    O00OOO00O00O00000 =public .format_date (times =O000000O000OO00O0 )#line:1148
                if public .to_date (times =O00OOO00O00O00000 )>public .to_date (times =OOOO0O000OOOOOO00 ):continue #line:1149
                if OO000OO0O000O0OOO >public .to_date (times =OOOO0O000OOOOOO00 ):continue #line:1150
                O0OO0OO0OO0OO0000 =public .format_date (times =OO000OO0O000O0OOO )#line:1151
                O00OO0O00O0OO0O00 ['start_time']=O00OOO00O00O00000 #line:1152
                O00OO0O00O0OO0O00 ['end_time']=O0OO0OO0OO0OO0000 #line:1153
                OO0000O00O000O0O0 .append (O00OO0O00O0OO0O00 )#line:1154
        return OO0000O00O000O0O0 #line:1155
    def import_date (OOO0OOO0000O0000O ,O0O0000000000OO00 ,O0000000O0OO00OO0 ):#line:1157
        ""#line:1163
        O0OOOO000OO00OO00 =time .time ()#line:1165
        OOO000O0OO0OO0000 =public .to_date (times =O0O0000000000OO00 )#line:1166
        OO000O000O0000000 =OOO0OOO0000O0000O .get_format_date (OOO000O0OO0OO0000 )#line:1167
        O0O0O000O000OOO00 =OO000O000O0000000 .split ('_')[0 ]#line:1168
        if OOO0OOO0000O0000O ._save_default_path [-1 ]=='/':OOO0OOO0000O0000O ._save_default_path =OOO0OOO0000O0000O ._save_default_path [:-1 ]#line:1170
        O00O00O0O00OO00O0 =OOO0OOO0000O0000O ._save_default_path +'/'+O0O0O000O000OOO00 +'/'#line:1171
        OOOOOOOOO0OOOO00O =OOO0OOO0000O0000O ._temp_path +OOO0OOO0000O0000O ._db_name +'/'+O0O0O000O000OOO00 +'/'#line:1172
        if not os .path .exists (O00O00O0O00OO00O0 ):os .makedirs (O00O00O0O00OO00O0 )#line:1173
        if not os .path .exists (OOOOOOOOO0OOOO00O ):os .makedirs (OOOOOOOOO0OOOO00O )#line:1174
        if OOO0OOO0000O0000O ._save_cycle ==3600 :#line:1175
            OO000O000O0000000 =OO000O000O0000000 .split ('_')[0 ]+'_'+OO000O000O0000000 .split ('_')[1 ].split ('-')[0 ]#line:1176
        else :#line:1177
            pass #line:1178
        OOO00OOO0O00O0000 ='{}{}.sql'.format (O00O00O0O00OO00O0 ,OO000O000O0000000 )#line:1179
        O0O000OO000OO00OO ='{}{}.sql'.format (OOOOOOOOO0OOOO00O ,OO000O000O0000000 )#line:1180
        O00000O0OOOOOOOO0 =OOO00OOO0O00O0000 .replace ('.sql','.zip')#line:1181
        OOO0OOO0000O0000O ._backup_full_list .append (O00000O0OOOOOOOO0 )#line:1182
        if O0000000O0OO00OO0 ==OOO0OOO0000O0000O ._backup_end_time :#line:1183
            if os .path .isfile (O00000O0OOOOOOOO0 ):os .remove (O00000O0OOOOOOOO0 )#line:1184
        print ("|-导出{}".format (OOO00OOO0O00O0000 ),end ='')#line:1185
        if not os .path .exists (O0O000OO000OO00OO ):#line:1186
            O0O0OOO0OOOO00000 ="{} --open-files-limit=1024 --start-datetime='{}' --stop-datetime='{}' -d {} {} > {} 2>/dev/null".format (OOO0OOO0000O0000O ._mysqlbinlog_bin ,O0O0000000000OO00 ,O0000000O0OO00OO0 ,OOO0OOO0000O0000O ._db_name ,OOO0OOO0000O0000O .get_binlog_file (OOO000O0OO0OO0000 ),O0O000OO000OO00OO )#line:1187
            os .system (O0O0OOO0OOOO00000 )#line:1188
        if not os .path .exists (O0O000OO000OO00OO ):#line:1189
            OOO0OOO0000O0000O ._backup_fail_list .append (O00000O0OOOOOOOO0 )#line:1190
            raise Exception ('从二进制日志导出sql文件失败!')#line:1191
        OOOOOOOOOOO0OO000 =''#line:1192
        if not OOO0OOO0000O0000O ._tables :#line:1193
            if OOO0OOO0000O0000O ._pdata and OOO0OOO0000O0000O ._pdata ['table_list']:#line:1194
                OOOOOOOOOOO0OO000 ='|'.join (list (set (OOO0OOO0000O0000O ._pdata ['table_list'].split ('|')).union (set (OOO0OOO0000O0000O ._new_tables ))))#line:1195
        else :#line:1196
            OOOOOOOOOOO0OO000 =OOO0OOO0000O0000O ._tables #line:1197
        os .system ('cat {} |grep -Ee "({})" > {}'.format (O0O000OO000OO00OO ,OOOOOOOOOOO0OO000 ,OOO00OOO0O00O0000 ))#line:1202
        if os .path .exists (O0O000OO000OO00OO ):os .remove (O0O000OO000OO00OO )#line:1204
        if not os .path .exists (OOO00OOO0O00O0000 ):#line:1205
            OOO0OOO0000O0000O ._backup_fail_list .append (O00000O0OOOOOOOO0 )#line:1206
            raise Exception ('导出sql文件失败!')#line:1207
        print (" ==> 成功")#line:1208
        if OOO0OOO0000O0000O ._compress :#line:1209
            _O000OO000OO0000O0 =OOO0OOO0000O0000O .zip_file (OOO00OOO0O00O0000 )#line:1210
        else :#line:1211
            _O000OO000OO0000O0 =os .path .getsize (OOO00OOO0O00O0000 )#line:1212
        print ("|-文件大小: {}MB, 耗时: {}秒".format (round (_O000OO000OO0000O0 /1024 /1024 ,2 ),round (time .time ()-O0OOOO000OO00OO00 ,2 )))#line:1213
        print ("-"*60 )#line:1214
    def get_date_folder (OO000OO000O0OOO00 ,O000OOOO0O0O0000O ):#line:1216
        ""#line:1222
        O0OO00OO0O0OOOOOO =[]#line:1223
        for OO0OO0O000OOO0O00 in os .listdir (O000OOOO0O0O0000O ):#line:1224
            if os .path .isdir (os .path .join (O000OOOO0O0O0000O ,OO0OO0O000OOO0O00 )):#line:1225
                O00OO0OOO00O0O0O0 ="([0-9]{4})-([0-9]{2})-([0-9]{2})"#line:1226
                O0O0O0O00O0OO000O =re .search (O00OO0OOO00O0O0O0 ,str (OO0OO0O000OOO0O00 ))#line:1227
                if O0O0O0O00O0OO000O :#line:1228
                    O0OO00OO0O0OOOOOO .append (O0O0O0O00O0OO000O [0 ])#line:1229
        return O0OO00OO0O0OOOOOO #line:1230
    def kill_process (O000OO0OO0000OOOO ):#line:1232
        ""#line:1236
        for OOO0OO0OO0O0O0O0O in range (3 ):#line:1237
            O0O0O0O0OO0OOOOOO ="'{} {} --db_name {} --binlog_id'".format (O000OO0OO0000OOOO ._python_path ,O000OO0OO0000OOOO ._binlogModel_py ,O000OO0OO0000OOOO ._db_name )#line:1238
            O00O00OOOO0O00OOO =os .popen ('ps aux | grep {} |grep -v grep'.format (O0O0O0O0OO0OOOOOO ))#line:1239
            O000OOO0000OO0000 =O00O00OOOO0O00OOO .read ()#line:1240
            for OOO0OO0OO0O0O0O0O in O000OOO0000OO0000 .strip ().split ('\n'):#line:1241
                if len (OOO0OO0OO0O0O0O0O .split ())<16 :continue #line:1242
                O0O000OO0O0O00O0O =int (OOO0OO0OO0O0O0O0O .split ()[9 ].split (':')[0 ])#line:1243
                OO0O0O00O00OO00OO =OOO0OO0OO0O0O0O0O .split ()[1 ]#line:1244
                if not public .M ('mysqlbinlog_backup_setting').where ('id=?',OOO0OO0OO0O0O0O0O .split ()[15 ]).count ()and O0O000OO0O0O00O0O >10 :#line:1245
                    os .kill (OO0O0O00O00OO00OO )#line:1246
                if O0O000OO0O0O00O0O >50 :#line:1247
                    os .kill (OO0O0O00O00OO00OO )#line:1248
                if O000OO0OO0000OOOO ._binlog_id :#line:1249
                    if OOO0OO0OO0O0O0O0O .split ()[15 ]==str (O000OO0OO0000OOOO ._binlog_id )and O0O000OO0O0O00O0O >0 :#line:1250
                        os .kill (OO0O0O00O00OO00OO )#line:1251
        O00O00OOOO0O00OOO =os .popen ('ps aux | grep {} |grep -v grep'.format (O0O0O0O0OO0OOOOOO ))#line:1252
        return O00O00OOOO0O00OOO .read ().strip ().split ('\n')#line:1253
    def full_backup (OOOOO0OO00OO000O0 ):#line:1255
        ""#line:1260
        OOO0OOOO00O0000OO =OOOOO0OO00OO000O0 ._save_default_path +'full_record.json'#line:1261
        O00000OO00O000OO0 =OOO0OOOO00O0000OO .replace ('full','inc')#line:1262
        OO0OO0OO0OO00O0OO =public .get_mysqldump_bin ()#line:1263
        O0O0O00OOO00OOO00 =public .format_date ("%Y%m%d_%H%M%S")#line:1264
        if OOOOO0OO00OO000O0 ._tables :#line:1266
            OO00O00OO00OO000O =OOOOO0OO00OO000O0 ._save_default_path +'db_{}_{}_{}.sql'.format (OOOOO0OO00OO000O0 ._db_name ,OOOOO0OO00OO000O0 ._tables ,O0O0O00OOO00OOO00 )#line:1267
            O00O000O00OO0O00O ='{} -uroot -p{} {} {} > {} 2>/dev/null'.format (OO0OO0OO0OO00O0OO ,OOOOO0OO00OO000O0 ._mysql_root_password ,OOOOO0OO00OO000O0 ._db_name ,OOOOO0OO00OO000O0 ._tables ,OO00O00OO00OO000O )#line:1268
        else :#line:1270
            OO00O00OO00OO000O =OOOOO0OO00OO000O0 ._save_default_path +'db_{}_{}.sql'.format (OOOOO0OO00OO000O0 ._db_name ,O0O0O00OOO00OOO00 )#line:1271
            O00O000O00OO0O00O =OO0OO0OO0OO00O0OO +" -E -R --default-character-set="+public .get_database_character (OOOOO0OO00OO000O0 ._db_name )+" --force --hex-blob --opt "+OOOOO0OO00OO000O0 ._db_name +" -u root -p"+str (OOOOO0OO00OO000O0 ._mysql_root_password )+"> {} 2>/dev/null".format (OO00O00OO00OO000O )#line:1272
        try :#line:1273
            os .system (O00O000O00OO0O00O )#line:1274
            if not os .path .isfile (OO00O00OO00OO000O ):return False #line:1275
            OOOOO0OO00OO000O0 .zip_file (OO00O00OO00OO000O )#line:1276
        except Exception as O0O0O00OOOO0OOO00 :#line:1277
            print (O0O0O00OOOO0OOO00 )#line:1278
            return False #line:1279
        OO0O0O0000O0OO0O0 =OO00O00OO00OO000O .replace ('.sql','.zip')#line:1280
        if not os .path .isfile (OO0O0O0000O0OO0O0 ):return False #line:1281
        OOOOO0OO00OO000O0 .clean_local_full_backups (OOO0OOOO00O0000OO ,os .path .basename (OO0O0O0000O0OO0O0 ),is_backup =True )#line:1283
        print ('|-已从磁盘清理过期备份文件')#line:1284
        OOOOO0OO00OO000O0 .clean_local_inc_backups (O00000OO00O000OO0 )#line:1286
        OOOOO0OO00OO000O0 ._full_zip_name =OOOOO0OO00OO000O0 ._save_default_path +os .path .basename (OO0O0O0000O0OO0O0 )#line:1287
        if OOOOO0OO00OO000O0 ._tables :#line:1288
            print ('|-完全备份数据库{}中表{}成功！'.format (OOOOO0OO00OO000O0 ._db_name ,OOOOO0OO00OO000O0 ._tables ))#line:1289
        else :#line:1290
            print ('|-完全备份数据库{}成功！'.format (OOOOO0OO00OO000O0 ._db_name ))#line:1291
        return True #line:1292
    def clean_local_inc_backups (OOO0O0OOO00O0OOO0 ,OO00OO0OOOO00O000 ):#line:1294
        ""#line:1299
        OO000O0O000O000OO =OOO0O0OOO00O0OOO0 .get_date_folder (OOO0O0OOO00O0OOO0 ._save_default_path )#line:1300
        if OO000O0O000O000OO :#line:1301
            for O0OOOO0OOO0OO00OO in OO000O0O000O000OO :#line:1302
                OO00000OOO0O0OOOO =os .path .join (OOO0O0OOO00O0OOO0 ._save_default_path ,O0OOOO0OOO0OO00OO )#line:1303
                if os .path .exists (OO00000OOO0O0OOOO ):shutil .rmtree (OO00000OOO0O0OOOO )#line:1304
        if os .path .isfile (OO00OO0OOOO00O000 ):#line:1305
            os .remove (OO00OO0OOOO00O000 )#line:1306
    def clean_local_full_backups (OO0000OO0O0OOOOOO ,OOOO0000OO0OO0000 ,check_name =None ,is_backup =False ,path =None ):#line:1308
        ""#line:1314
        if os .path .isfile (OOOO0000OO0OO0000 ):#line:1315
            OOO0OO0OOO0O00O0O =OO0000OO0O0OOOOOO .get_full_backup_file (OO0000OO0O0OOOOOO ._db_name ,OO0000OO0O0OOOOOO ._save_default_path )#line:1316
            for O0O000000O00OO00O in OOO0OO0OOO0O00O0O :#line:1317
                OOO00OOO00O00OO00 =os .path .join (OO0000OO0O0OOOOOO ._save_default_path ,O0O000000O00OO00O ['name'])#line:1318
                if is_backup :#line:1319
                    if O0O000000O00OO00O ['name']!=check_name :OO0000OO0O0OOOOOO .delete_file (OOO00OOO00O00OO00 )#line:1320
                else :#line:1321
                    OO0000OO0O0OOOOOO .delete_file (OOO00OOO00O00OO00 )#line:1322
            if not is_backup :OO0000OO0O0OOOOOO .delete_file (OOOO0000OO0OO0000 )#line:1323
    def check_cloud_oss (O00OOO000O000O0OO ,O000OOOO00OOO000O ):#line:1324
        ""#line:1329
        OO00OO000OO00OO0O =alioss_main ()#line:1331
        OO0O00O00O0OO0O0O =txcos_main ()#line:1332
        OO00000OOO0OOOOOO =qiniu_main ()#line:1333
        O00O00O0O00000O00 =bos_main ()#line:1334
        OO0OO000O0OO00O00 =obs_main ()#line:1335
        OOOOO0OO0OOO0OO0O =ftp_main ()#line:1336
        O0O0OO0OO00OO0O00 =[]#line:1337
        O0OOO0OO0000OO000 =[]#line:1338
        O000O0O0O0OOO0O00 =O00O00000OO00O0O0 =O00O00OOO0OOOOO0O =O000OOOO00OOO0OO0 =OO0OOOO0OO0O0OOOO =OOO0000OOOOOOO0OO =False #line:1340
        if O000OOOO00OOO000O ['upload_alioss']=='alioss':#line:1342
            if OO00OO000OO00OO0O .check_config ():#line:1343
                O0O0OO0OO00OO0O00 .append (OO00OO000OO00OO0O )#line:1344
                O000O0O0O0OOO0O00 =True #line:1345
            else :O0OOO0OO0000OO000 .append ('alioss')#line:1346
        if O000OOOO00OOO000O ['upload_txcos']=='txcos':#line:1348
            if OO0O00O00O0OO0O0O .check_config ():#line:1349
                O0O0OO0OO00OO0O00 .append (OO0O00O00O0OO0O0O )#line:1350
                O00O00000OO00O0O0 =True #line:1351
            else :O0OOO0OO0000OO000 .append ('txcos')#line:1352
        if O000OOOO00OOO000O ['upload_qiniu']=='qiniu':#line:1354
            if OO00000OOO0OOOOOO .check_config ():#line:1355
                O0O0OO0OO00OO0O00 .append (OO00000OOO0OOOOOO )#line:1356
                O00O00OOO0OOOOO0O =True #line:1357
            else :O0OOO0OO0000OO000 .append ('qiniu')#line:1358
        if O000OOOO00OOO000O ['upload_bos']=='bos':#line:1360
            if O00O00O0O00000O00 .check_config ():#line:1361
                O0O0OO0OO00OO0O00 .append (O00O00O0O00000O00 )#line:1362
                O000OOOO00OOO0OO0 =True #line:1363
            else :O0OOO0OO0000OO000 .append ('bos')#line:1364
        if O000OOOO00OOO000O ['upload_obs']=='obs':#line:1366
            if OO0OO000O0OO00O00 .check_config ():#line:1367
                O0O0OO0OO00OO0O00 .append (OO0OO000O0OO00O00 )#line:1368
                OO0OOOO0OO0O0OOOO =True #line:1369
            else :O0OOO0OO0000OO000 .append ('obs')#line:1370
        if O000OOOO00OOO000O ['upload_ftp']=='ftp':#line:1372
            if OOOOO0OO0OOO0OO0O .check_config ():#line:1373
                O0O0OO0OO00OO0O00 .append (OOOOO0OO0OOO0OO0O )#line:1374
                OOO0000OOOOOOO0OO =True #line:1375
        return O000O0O0O0OOO0O00 ,O00O00000OO00O0O0 ,O00O00OOO0OOOOO0O ,O000OOOO00OOO0OO0 ,OO0OOOO0OO0O0OOOO ,OOO0000OOOOOOO0OO ,O0O0OO0OO00OO0O00 ,O0OOO0OO0000OO000 #line:1376
    def execute_by_comandline (O0000OO00OO00OO00 ,get =None ):#line:1379
        ""#line:1385
        O0000OO00OO00OO00 .install_cloud_module ()#line:1386
        if get :#line:1387
            O0000OO00OO00OO00 ._db_name =get .databname #line:1388
            O0000OO00OO00OO00 ._binlog_id =get .backup_id #line:1389
        OOOO00OOOO0OO0000 =[]#line:1390
        OO0OOOO000O0OO0OO =O0000OO00OO00OO00 .kill_process ()#line:1393
        if len (OO0OOOO000O0OO0OO )>0 :#line:1394
            time .sleep (0.01 )#line:1395
        O00000O00O00O00O0 =False #line:1396
        O00OOOO0OO00OOO00 =O0000OO00OO00OO00 .get_binlog_status ()#line:1398
        if O00OOOO0OO00OOO00 ['status']==False :#line:1399
            OOO0OO00OO0000OO0 ='请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！'#line:1400
            print (OOO0OO00OO0000OO0 )#line:1401
            O00000O00O00O00O0 =True #line:1402
        O0000OO00OO00OO00 ._db_mysql =O0000OO00OO00OO00 ._db_mysql .set_host ('127.0.0.1',O0000OO00OO00OO00 .get_mysql_port (),'','root',O0000OO00OO00OO00 ._mysql_root_password )#line:1404
        O00O00OOO000OOO00 ,O00OO0O0O0O0OOOOO ,OO0000OO0OO0OO0OO =O0000OO00OO00OO00 ._mybackup .get_disk_free (O0000OO00OO00OO00 ._save_default_path )#line:1405
        if not O00000O00O00O00O0 :#line:1406
            OO00OO0OOO00O0O0O =''#line:1407
            try :#line:1408
                OOOOOO00O0000OOOO ="select sum(DATA_LENGTH)+sum(INDEX_LENGTH) from information_schema.tables where table_schema=%s"#line:1409
                OOOOO0O00OO00O00O =(O0000OO00OO00OO00 ._db_name ,)#line:1410
                O0OO00O00O0OO0OO0 =O0000OO00OO00OO00 ._db_mysql .query (OOOOOO00O0000OOOO ,True ,OOOOO0O00OO00O00O )#line:1411
                OO00OO0OOO00O0O0O =O0000OO00OO00OO00 ._mybackup .map_to_list (O0OO00O00O0OO0OO0 )[0 ][0 ]#line:1412
            except :#line:1413
                O00000O00O00O00O0 =True #line:1414
                OOO0OO00OO0000OO0 ="数据库连接异常，请检查root用户权限或者数据库配置参数是否正确。"#line:1415
                print (OOO0OO00OO0000OO0 )#line:1416
                OOOO00OOOO0OO0000 .append (OOO0OO00OO0000OO0 )#line:1417
            if OO00OO0OOO00O0O0O ==None :#line:1419
                OOO0OO00OO0000OO0 ='指定数据库 `{}` 没有任何数据!'.format (O0000OO00OO00OO00 ._db_name )#line:1420
                O00000O00O00O00O0 =True #line:1421
                print (OOO0OO00OO0000OO0 )#line:1422
                OOOO00OOOO0OO0000 .append (OOO0OO00OO0000OO0 )#line:1423
            if O00O00OOO000OOO00 :#line:1425
                if OO00OO0OOO00O0O0O :#line:1426
                    if O00OO0O0O0O0OOOOO <OO00OO0OOO00O0O0O :#line:1427
                        OOO0OO00OO0000OO0 ="目标分区可用的磁盘空间小于{},无法完成备份，请增加磁盘容量!".format (public .to_size (OO00OO0OOO00O0O0O ))#line:1428
                        print (OOO0OO00OO0000OO0 )#line:1429
                        O00000O00O00O00O0 =True #line:1430
                        OOOO00OOOO0OO0000 .append (OOO0OO00OO0000OO0 )#line:1431
                if OO0000OO0OO0OO0OO <O0000OO00OO00OO00 ._inode_min :#line:1433
                    OOO0OO00OO0000OO0 ="目标分区可用的Inode小于{},无法完成备份，请增加磁盘容量!".format (O0000OO00OO00OO00 ._inode_min )#line:1434
                    print (OOO0OO00OO0000OO0 )#line:1435
                    O00000O00O00O00O0 =True #line:1436
                    OOOO00OOOO0OO0000 .append (OOO0OO00OO0000OO0 )#line:1437
        O0000OO00OO00OO00 ._pdata =OO0OOO000OO00O000 =public .M ('mysqlbinlog_backup_setting').where ('id=?',str (O0000OO00OO00OO00 ._binlog_id )).find ()#line:1440
        OOO0OOO0O0000OOOO =OO0OOO000OO00O000 ['database_table']if OO0OOO000OO00O000 else O0000OO00OO00OO00 ._db_name #line:1441
        O0000OO00OO00OO00 ._echo_info ['echo']=public .M ('crontab').where ("sBody=?",('{} {} --db_name {} --binlog_id {}'.format (O0000OO00OO00OO00 ._python_path ,O0000OO00OO00OO00 ._binlogModel_py ,O0000OO00OO00OO00 ._db_name ,str (O0000OO00OO00OO00 ._binlog_id )),)).getField ('echo')#line:1443
        O0000OO00OO00OO00 ._mybackup =backup (cron_info =O0000OO00OO00OO00 ._echo_info )#line:1444
        if not OO0OOO000OO00O000 :#line:1445
            print ('未在数据库备份记录中找到id为{}的计划任务'.format (O0000OO00OO00OO00 ._binlog_id ))#line:1446
            O00000O00O00O00O0 =True #line:1447
        if O0000OO00OO00OO00 ._db_name not in O0000OO00OO00OO00 .get_tables_list (O0000OO00OO00OO00 .get_databases ()):#line:1448
            print ('备份的数据库不存在')#line:1449
            O00000O00O00O00O0 =True #line:1450
        if O00000O00O00O00O0 :#line:1451
            O0000OO00OO00OO00 .send_failture_notification (OOOO00OOOO0OO0000 ,target =OOO0OOO0O0000OOOO )#line:1453
            return public .returnMsg (False ,'备份失败')#line:1454
        O0000OO00OO00OO00 ._zip_password =OO0OOO000OO00O000 ['zip_password']#line:1455
        if OO0OOO000OO00O000 ['backup_type']=='tables':O0000OO00OO00OO00 ._tables =OO0OOO000OO00O000 ['tb_name']#line:1456
        O0000OO00OO00OO00 ._save_default_path =OO0OOO000OO00O000 ['save_path']#line:1457
        print ("|-分区{}可用磁盘空间为：{},可用Inode为:{}".format (O00O00OOO000OOO00 ,public .to_size (O00OO0O0O0O0OOOOO ),OO0000OO0OO0OO0OO ))#line:1458
        if not os .path .exists (O0000OO00OO00OO00 ._save_default_path ):#line:1460
            os .makedirs (O0000OO00OO00OO00 ._save_default_path )#line:1461
            OOO0OO0O0OOOOOO0O =True #line:1462
        O0000OO00OO00OO00 ._full_file =O0000OO00OO00OO00 ._save_default_path +'full_record.json'#line:1463
        O0000OO00OO00OO00 ._inc_file =OO0O00OO00O0O0O00 =O0000OO00OO00OO00 ._save_default_path +'inc_record.json'#line:1464
        OO0OOO000OO00O000 ['last_excute_backup_time']=O0000OO00OO00OO00 ._backup_end_time =public .format_date ()#line:1465
        O0000OO00OO00OO00 ._tables =OO0OOO000OO00O000 ['tb_name']#line:1466
        O0OOO00OOO00OOOO0 ='/tables/'+O0000OO00OO00OO00 ._tables +'/'if O0000OO00OO00OO00 ._tables else '/databases/'#line:1467
        O0000OO00OO00OO00 ._backup_type ='tables'if O0000OO00OO00OO00 ._tables else 'databases'#line:1468
        O000000000O00000O =OO0OOO000OO00O000 ['start_backup_time']#line:1470
        OO00000000000OO0O =OO0OOO000OO00O000 ['end_backup_time']#line:1471
        OOO0OO0O0OOOOOO0O =False #line:1472
        O0O0O0000O00OO000 ={'alioss':'阿里云OSS','txcos':'腾讯云COS','qiniu':'七牛云存储','bos':'百度云存储','obs':'华为云存储'}#line:1473
        OO0O0OO0OOO000O00 ,OOOO0000O0OO00OOO ,OOOOO0OO00000OO00 ,O0OOO00OO00OO0O00 ,O000O00O00000OO00 ,O00000O00OOOO0OOO ,OOO0O0O0OO0OO000O ,O0OOOOO000OO000O0 =O0000OO00OO00OO00 .check_cloud_oss (OO0OOO000OO00O000 )#line:1475
        if O0OOOOO000OO000O0 :#line:1476
            OO000OOOO0O000OOO =[]#line:1477
            print ('检测到无法连接上以下云存储：')#line:1478
            for OO0O00000O00O000O in O0OOOOO000OO000O0 :#line:1479
                if not OO0O00000O00O000O :continue #line:1480
                OO000OOOO0O000OOO .append (O0O0O0000O00OO000 [OO0O00000O00O000O ])#line:1481
                print ('{}'.format (O0O0O0000O00OO000 [OO0O00000O00O000O ]))#line:1482
            OOO0OO00OO0000OO0 ='检测到无法连接上以下云存储：{}'.format (OO000OOOO0O000OOO )#line:1483
            print ('请检查配置或者更改备份设置！')#line:1484
            O0000OO00OO00OO00 .send_failture_notification (OOO0OO00OO0000OO0 ,target =OOO0OOO0O0000OOOO )#line:1486
            return public .returnMsg (False ,'备份失败')#line:1487
        if not os .path .isfile (O0000OO00OO00OO00 ._full_file ):#line:1489
            O0000OO00OO00OO00 .auto_download_file (OOO0O0O0OO0OO000O ,O0000OO00OO00OO00 ._full_file )#line:1491
        OOOO00O0OO0000000 ={}#line:1492
        if os .path .isfile (O0000OO00OO00OO00 ._full_file ):#line:1493
            try :#line:1494
                OOOO00O0OO0000000 =json .loads (public .readFile (O0000OO00OO00OO00 ._full_file ))[0 ]#line:1495
                if 'name'not in OOOO00O0OO0000000 or 'size'not in OOOO00O0OO0000000 or 'time'not in OOOO00O0OO0000000 :OOO0OO0O0OOOOOO0O =True #line:1496
                if 'end_time'in OOOO00O0OO0000000 :#line:1497
                    if OOOO00O0OO0000000 ['end_time']!=OOOO00O0OO0000000 ['end_time'].split (':')[0 ]+':00:00':#line:1498
                        OO00000000000OO0O =OOOO00O0OO0000000 ['end_time'].split (':')[0 ]+':00:00'#line:1499
                if 'full_name'in OOOO00O0OO0000000 and os .path .isfile (OOOO00O0OO0000000 ['full_name'])and time .time ()-public .to_date (times =O000000000O00000O )>604800 :#line:1500
                    OOO0OO0O0OOOOOO0O =True #line:1501
                if 'time'in OOOO00O0OO0000000 :#line:1503
                    O000000000O00000O =OOOO00O0OO0000000 ['time']#line:1504
                    if not os .path .isfile (O0000OO00OO00OO00 ._inc_file )and OO00000000000OO0O !=OOOO00O0OO0000000 ['time']:#line:1505
                        O0000OO00OO00OO00 .auto_download_file (OOO0O0O0OO0OO000O ,O0000OO00OO00OO00 ._inc_file )#line:1507
                    if not os .path .isfile (O0000OO00OO00OO00 ._inc_file )and OO00000000000OO0O !=OOOO00O0OO0000000 ['time']:#line:1508
                        print ('增量备份记录文件不存在,将执行完全备份')#line:1509
                        OOO0OO0O0OOOOOO0O =True #line:1510
            except :#line:1511
                OOOO00O0OO0000000 ={}#line:1512
                OOO0OO0O0OOOOOO0O =True #line:1513
        else :#line:1514
            OOO0OO0O0OOOOOO0O =True #line:1515
        OO0O000O0OO0OOO00 =False #line:1516
        if OOO0OO0O0OOOOOO0O :#line:1519
            print ('☆☆☆完全备份开始☆☆☆')#line:1520
            O00O000OO0O00OO0O =[]#line:1521
            if not O0000OO00OO00OO00 .full_backup ():#line:1522
                OOO0OO00OO0000OO0 ='全量备份数据库[{}]'.format (O0000OO00OO00OO00 ._db_name )#line:1523
                O0000OO00OO00OO00 .send_failture_notification (OOO0OO00OO0000OO0 ,target =OOO0OOO0O0000OOOO )#line:1524
                return public .returnMsg (False ,OOO0OO00OO0000OO0 )#line:1525
            if os .path .isfile (O0000OO00OO00OO00 ._full_file ):#line:1526
                try :#line:1527
                    O00O000OO0O00OO0O =json .loads (public .readFile (O0000OO00OO00OO00 ._full_file ))#line:1528
                except :#line:1529
                    O00O000OO0O00OO0O =[]#line:1530
            O0000OO00OO00OO00 .set_file_info (O0000OO00OO00OO00 ._full_zip_name ,O0000OO00OO00OO00 ._full_file ,is_full =True )#line:1532
            try :#line:1533
                OOOO00O0OO0000000 =json .loads (public .readFile (O0000OO00OO00OO00 ._full_file ))[0 ]#line:1534
            except :#line:1535
                print ('|-文件写入失败，检查是否有安装安全软件！')#line:1536
                print ('|-备份失败！')#line:1537
                return #line:1538
            OO0OOO000OO00O000 ['start_backup_time']=OO0OOO000OO00O000 ['end_backup_time']=OOOO00O0OO0000000 ['time']#line:1539
            public .M ('mysqlbinlog_backup_setting').where ('id=?',OO0OOO000OO00O000 ['id']).update (OO0OOO000OO00O000 )#line:1540
            O00000O0O0O0OOOO0 ='/bt_backup/mysql_bin_log/'+O0000OO00OO00OO00 ._db_name +O0OOO00OOO00OOOO0 #line:1541
            OOO000O0O0O000O00 =O00000O0O0O0OOOO0 +OOOO00O0OO0000000 ['name']#line:1542
            O0OOO00OO000OOOO0 =O00000O0O0O0OOOO0 +'full_record.json'#line:1543
            OOO000O0O0O000O00 =OOO000O0O0O000O00 .replace ('//','/')#line:1544
            O0OOO00OO000OOOO0 =O0OOO00OO000OOOO0 .replace ('//','/')#line:1545
            if OO0O0OO0OOO000O00 :#line:1547
                O0OOO0O0O0OOO0O0O =alioss_main ()#line:1548
                if not O0OOO0O0O0OOO0O0O .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):#line:1549
                        O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1550
                if not O0OOO0O0O0OOO0O0O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1551
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O0OOO0O0O0OOO0O0O ,O0O0O0000O00OO000 ['alioss'])#line:1553
            else :#line:1554
                if OO0OOO000OO00O000 ['upload_alioss']=='alioss':#line:1555
                    OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['alioss'],O0O0O0000O00OO000 ['alioss'])#line:1556
                    OO0O000O0OO0OOO00 =True #line:1557
                    print (OOO0OO00OO0000OO0 )#line:1558
            if OOOO0000O0OO00OOO :#line:1560
                O00OO0OO0O0O00000 =txcos_main ()#line:1561
                if not O00OO0OO0O0O00000 .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):#line:1562
                    O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1563
                if not O00OO0OO0O0O00000 .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):#line:1564
                    O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1565
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O00OO0OO0O0O00000 ,O0O0O0000O00OO000 ['txcos'])#line:1567
            else :#line:1568
                if OO0OOO000OO00O000 ['upload_txcos']=='txcos':#line:1569
                    OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['txcos'],O0O0O0000O00OO000 ['txcos'])#line:1570
                    OO0O000O0OO0OOO00 =True #line:1571
                    print (OOO0OO00OO0000OO0 )#line:1572
            if OOOOO0OO00000OO00 :#line:1574
                O00OOO0O00OOO0OO0 =qiniu_main ()#line:1575
                if not O00OOO0O00OOO0OO0 .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1576
                if not O00OOO0O00OOO0OO0 .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1577
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O00OOO0O00OOO0OO0 ,O0O0O0000O00OO000 ['qiniu'])#line:1579
            else :#line:1580
                if OO0OOO000OO00O000 ['upload_qiniu']=='qiniu':#line:1581
                        OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['qiniu'],O0O0O0000O00OO000 ['qiniu'])#line:1582
                        OO0O000O0OO0OOO00 =True #line:1583
                        print (OOO0OO00OO0000OO0 )#line:1584
            if O0OOO00OO00OO0O00 :#line:1586
                O00OO00OO0OOO00OO =bos_main ()#line:1587
                if not O00OO00OO0OOO00OO .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1588
                if not O00OO00OO0OOO00OO .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1589
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O00OO00OO0OOO00OO ,O0O0O0000O00OO000 ['bos'])#line:1591
            else :#line:1592
                if OO0OOO000OO00O000 ['upload_bos']=='bos':#line:1593
                        OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['bos'],O0O0O0000O00OO000 ['bos'])#line:1594
                        OO0O000O0OO0OOO00 =True #line:1595
                        print (OOO0OO00OO0000OO0 )#line:1596
            if O000O00O00000OO00 :#line:1599
                O00O000O00OOOOO0O =obs_main ()#line:1600
                if not O00O000O00OOOOO0O .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1601
                if not O00O000O00OOOOO0O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1602
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O00O000O00OOOOO0O ,O0O0O0000O00OO000 ['obs'])#line:1604
            else :#line:1605
                if OO0OOO000OO00O000 ['upload_obs']=='obs':#line:1606
                        OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['obs'],O0O0O0000O00OO000 ['obs'])#line:1607
                        OO0O000O0OO0OOO00 =True #line:1608
                        print (OOO0OO00OO0000OO0 )#line:1609
            if O00000O00OOOO0OOO :#line:1612
                O0O00OO000OOO000O =ftp_main ()#line:1613
                if not O0O00OO000OOO000O .upload_file_by_path (OOOO00O0OO0000000 ['full_name'],OOO000O0O0O000O00 ):O0000OO00OO00OO00 ._cloud_upload_not .append (OOOO00O0OO0000000 ['full_name'])#line:1614
                if not O0O00OO000OOO000O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,O0OOO00OO000OOOO0 ):O0000OO00OO00OO00 ._cloud_upload_not .append (O0000OO00OO00OO00 ._full_file )#line:1615
                O0000OO00OO00OO00 .clean_cloud_backups (O00000O0O0O0OOOO0 ,O0000OO00OO00OO00 ._full_file ,O0O00OO000OOO000O ,O0O0O0000O00OO000 ['ftp'])#line:1617
            else :#line:1618
                if OO0OOO000OO00O000 ['upload_ftp']=='ftp':#line:1619
                        OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['ftp'],O0O0O0000O00OO000 ['ftp'])#line:1620
                        OO0O000O0OO0OOO00 =True #line:1621
                        print (OOO0OO00OO0000OO0 )#line:1622
            OOO0OO00OO0000OO0 ='以下文件上传失败：{}'.format (O0000OO00OO00OO00 ._cloud_upload_not )#line:1623
            if O0000OO00OO00OO00 ._cloud_upload_not or OO0O000O0OO0OOO00 :#line:1624
                O0000OO00OO00OO00 .send_failture_notification (OOO0OO00OO0000OO0 ,target =OOO0OOO0O0000OOOO )#line:1625
                if O00O000OO0O00OO0O :public .writeFile (O0000OO00OO00OO00 ._full_file ,json .dumps (O00O000OO0O00OO0O ))#line:1626
            print ('☆☆☆完全备份结束☆☆☆')#line:1627
            OOO0O00O0O0O0O00O ='full'#line:1628
            O0O0O0O000O0OOOOO =json .loads (public .readFile (O0000OO00OO00OO00 ._full_file ))#line:1629
            O0000OO00OO00OO00 .write_backups (OOO0O00O0O0O0O00O ,O0O0O0O000O0OOOOO )#line:1630
            if OO0OOO000OO00O000 ['upload_local']==''and os .path .isfile (O0000OO00OO00OO00 ._full_file ):#line:1632
                O0000OO00OO00OO00 .clean_local_full_backups (O0000OO00OO00OO00 ._full_file )#line:1633
                if os .path .isfile (O0000OO00OO00OO00 ._inc_file ):O0000OO00OO00OO00 .clean_local_inc_backups (O0000OO00OO00OO00 ._inc_file )#line:1634
                print ('|-用户设置不保留本地备份，已从本地服务器清理备份')#line:1635
            return public .returnMsg (True ,'完全备份成功！')#line:1636
        O0000OO00OO00OO00 ._backup_add_time =OO0OOO000OO00O000 ['start_backup_time']#line:1638
        O0000OO00OO00OO00 ._backup_start_time =OO00000000000OO0O #line:1639
        O0000OO00OO00OO00 ._new_tables =O0000OO00OO00OO00 .get_tables_list (O0000OO00OO00OO00 .get_tables ())#line:1640
        if O0000OO00OO00OO00 ._backup_start_time and O0000OO00OO00OO00 ._backup_end_time :#line:1641
            OO0O0000O0OOO0000 =O0000OO00OO00OO00 .import_start_end (O0000OO00OO00OO00 ._backup_start_time ,O0000OO00OO00OO00 ._backup_end_time )#line:1642
            for O0OOO00O0OO000OO0 in OO0O0000O0OOO0000 :#line:1643
                if not O0OOO00O0OO000OO0 :continue #line:1644
                O0000OO00OO00OO00 ._backup_fail_list =[]#line:1645
                if public .to_date (times =O0OOO00O0OO000OO0 ['end_time'])>public .to_date (times =O0000OO00OO00OO00 ._backup_end_time ):O0OOO00O0OO000OO0 ['end_time']=O0000OO00OO00OO00 ._backup_end_time #line:1646
                O0000OO00OO00OO00 .import_date (O0OOO00O0OO000OO0 ['start_time'],O0OOO00O0OO000OO0 ['end_time'])#line:1647
        OOO0OOO0OOO0OO000 =OO0OOO000OO00O000 ['save_path']#line:1649
        O0O00OOO00O00OO00 =O0000OO00OO00OO00 .get_every_day (O0000OO00OO00OO00 ._backup_start_time .split ()[0 ],O0000OO00OO00OO00 ._backup_end_time .split ()[0 ])#line:1650
        OO00O0OO00OO0000O ='True'#line:1651
        OO0OOOOO00OOOO000 =O0000OO00OO00OO00 .get_start_end_binlog (O0000OO00OO00OO00 ._backup_start_time ,O0000OO00OO00OO00 ._backup_end_time ,OO00O0OO00OO0000O )#line:1652
        OOOOO0000OO0OOOOO =O0000OO00OO00OO00 .traverse_all_files (OOO0OOO0OOO0OO000 ,O0O00OOO00O00OO00 ,OO0OOOOO00OOOO000 )#line:1653
        if O0000OO00OO00OO00 ._backup_fail_list or OOOOO0000OO0OOOOO ['file_lists_not']:#line:1654
            OOOOO00OOOOOOOOOO =''#line:1655
            if O0000OO00OO00OO00 ._backup_fail_list :OOOOO00OOOOOOOOOO =O0000OO00OO00OO00 ._backup_fail_list #line:1656
            else :OOOOO00OOOOOOOOOO =OOOOO0000OO0OOOOO ['file_lists_not']#line:1657
            OOO0OO00OO0000OO0 ='以下文件备份失败{}'.format (OOOOO00OOOOOOOOOO )#line:1659
            O0000OO00OO00OO00 .send_failture_notification (OOO0OO00OO0000OO0 ,target =OOO0OOO0O0000OOOO )#line:1661
            print (OOO0OO00OO0000OO0 )#line:1662
            return public .returnMsg (False ,OOO0OO00OO0000OO0 )#line:1663
        O0O0000O0OOO0OO00 =json .loads (public .readFile (O0000OO00OO00OO00 ._full_file ))#line:1664
        OO0OOO000OO00O000 ['end_backup_time']=O0000OO00OO00OO00 ._backup_end_time #line:1666
        OO0OOO000OO00O000 ['table_list']='|'.join (O0000OO00OO00OO00 ._new_tables )#line:1668
        O0000OO00OO00OO00 .update_file_info (O0000OO00OO00OO00 ._full_file ,O0000OO00OO00OO00 ._backup_end_time )#line:1669
        OO0OO000OOO0OOOOO =OO0O00000O00OOOO0 =False #line:1671
        for OO000OOO0O0O0O0O0 in OOOOO0000OO0OOOOO ['data']:#line:1672
            if OO000OOO0O0O0O0O0 ==OOOOO0000OO0OOOOO ['data'][-1 ]:OO0OO000OOO0OOOOO =True #line:1673
            for O000O0O00OO0OOO00 in OO000OOO0O0O0O0O0 :#line:1674
                if O000O0O00OO0OOO00 ==OO000OOO0O0O0O0O0 [-1 ]:OO0O00000O00OOOO0 =True #line:1675
                O0000OO00OO00OO00 .set_file_info (O000O0O00OO0OOO00 ,OO0O00OO00O0O0O00 )#line:1676
                O0OOO0OO00000OOO0 ='/bt_backup/mysql_bin_log/'+O0000OO00OO00OO00 ._db_name +O0OOO00OOO00OOOO0 #line:1677
                OOOOO0000OOO0OOOO =O0OOO0OO00000OOO0 +'full_record.json'#line:1678
                OO0O000OO0O000O0O =O0OOO0OO00000OOO0 +'inc_record.json'#line:1679
                OOO000O0O0O000O00 ='/bt_backup/mysql_bin_log/'+O0000OO00OO00OO00 ._db_name +O0OOO00OOO00OOOO0 +O000O0O00OO0OOO00 .split ('/')[-2 ]+'/'+O000O0O00OO0OOO00 .split ('/')[-1 ]#line:1680
                if OO0O0OO0OOO000O00 :#line:1681
                    O0OOO0O0O0OOO0O0O =alioss_main ()#line:1682
                    if not O0OOO0O0O0OOO0O0O .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1683
                        O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1684
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O0OOO0O0O0OOO0O0O .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1685
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O0OOO0O0O0OOO0O0O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,OOOOO0000OOO0OOOO )#line:1686
                else :#line:1687
                    if OO0OOO000OO00O000 ['upload_alioss']=='alioss':#line:1688
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['alioss'],O0O0O0000O00OO000 ['alioss'])#line:1689
                            OO0O000O0OO0OOO00 =True #line:1690
                            print (OOO0OO00OO0000OO0 )#line:1691
                if OOOO0000O0OO00OOO :#line:1692
                    O00OO0OO0O0O00000 =txcos_main ()#line:1693
                    if not O00OO0OO0O0O00000 .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1694
                       O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1695
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OO0OO0O0O00000 .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1696
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OO0OO0O0O00000 .upload_file_by_path (OO0O00OO00O0O0O00 ,OOOOO0000OOO0OOOO )#line:1697
                else :#line:1698
                    if OO0OOO000OO00O000 ['upload_txcos']=='txcos':#line:1699
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['txcos'],O0O0O0000O00OO000 ['txcos'])#line:1700
                            OO0O000O0OO0OOO00 =True #line:1701
                            print (OOO0OO00OO0000OO0 )#line:1702
                if OOOOO0OO00000OO00 :#line:1703
                    O00OOO0O00OOO0OO0 =qiniu_main ()#line:1704
                    if not O00OOO0O00OOO0OO0 .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1705
                        O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1706
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OOO0O00OOO0OO0 .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1707
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OOO0O00OOO0OO0 .upload_file_by_path (OO0O00OO00O0O0O00 ,OOOOO0000OOO0OOOO )#line:1708
                else :#line:1709
                    if OO0OOO000OO00O000 ['upload_qiniu']=='qiniu':#line:1710
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['qiniu'],O0O0O0000O00OO000 ['qiniu'])#line:1711
                            OO0O000O0OO0OOO00 =True #line:1712
                            print (OOO0OO00OO0000OO0 )#line:1713
                if O0OOO00OO00OO0O00 :#line:1714
                    O00OO00OO0OOO00OO =bos_main ()#line:1715
                    if not O00OO00OO0OOO00OO .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1716
                        O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1717
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OO00OO0OOO00OO .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1718
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00OO00OO0OOO00OO .upload_file_by_path (OO0O00OO00O0O0O00 ,OOOOO0000OOO0OOOO )#line:1719
                else :#line:1720
                    if OO0OOO000OO00O000 ['upload_bos']=='bos':#line:1721
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['bos'],O0O0O0000O00OO000 ['bos'])#line:1722
                            OO0O000O0OO0OOO00 =True #line:1723
                            print (OOO0OO00OO0000OO0 )#line:1724
                if O000O00O00000OO00 :#line:1726
                    O00O000O00OOOOO0O =obs_main ()#line:1727
                    if not O00O000O00OOOOO0O .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1728
                        O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1729
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00O000O00OOOOO0O .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1730
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O00O000O00OOOOO0O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,OOOOO0000OOO0OOOO )#line:1731
                else :#line:1732
                    if OO0OOO000OO00O000 ['upload_obs']=='obs':#line:1733
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['obs'],O0O0O0000O00OO000 ['obs'])#line:1734
                            OO0O000O0OO0OOO00 =True #line:1735
                            print (OOO0OO00OO0000OO0 )#line:1736
                if O00000O00OOOO0OOO :#line:1738
                    O0OOOOOO00O0O000O =ftp_main ()#line:1739
                    if not O0OOOOOO00O0O000O .upload_file_by_path (O000O0O00OO0OOO00 ,OOO000O0O0O000O00 ):#line:1740
                        O0000OO00OO00OO00 ._cloud_upload_not .append (O000O0O00OO0OOO00 )#line:1741
                    if os .path .isfile (OO0O00OO00O0O0O00 )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :O0OOOOOO00O0O000O .upload_file_by_path (OO0O00OO00O0O0O00 ,OO0O000OO0O000O0O )#line:1742
                    if os .path .isfile (O0000OO00OO00OO00 ._full_file )and OO0OO000OOO0OOOOO and OO0O00000O00OOOO0 :#line:1743
                        OOOOO0000OOO0OOOO =os .path .join ('/www/wwwroot/ahongtest',OOOOO0000OOO0OOOO )#line:1744
                        O0OOOOOO00O0O000O .upload_file_by_path (O0000OO00OO00OO00 ._full_file ,OOOOO0000OOO0OOOO )#line:1745
                else :#line:1746
                    if OO0OOO000OO00O000 ['upload_ftp']=='ftp':#line:1747
                            OOO0OO00OO0000OO0 ='|-无法连接上{}，无法上传到{}'.format (O0O0O0000O00OO000 ['ftp'],O0O0O0000O00OO000 ['ftp'])#line:1748
                            OO0O000O0OO0OOO00 =True #line:1749
                            print (OOO0OO00OO0000OO0 )#line:1750
        OOO0OO00OO0000OO0 ='以下文件上传失败：{}'.format (O0000OO00OO00OO00 ._cloud_upload_not )#line:1751
        if O0000OO00OO00OO00 ._cloud_upload_not or OO0O000O0OO0OOO00 :#line:1752
            O0000OO00OO00OO00 .send_failture_notification (OOO0OO00OO0000OO0 ,target =OOO0OOO0O0000OOOO )#line:1753
            if O0O0000O0OOO0OO00 :public .writeFile (O0000OO00OO00OO00 ._full_file ,json .dumps (O0O0000O0OOO0OO00 ))#line:1754
            return public .returnMsg (False ,'增量备份失败！')#line:1755
        public .M ('mysqlbinlog_backup_setting').where ('id=?',OO0OOO000OO00O000 ['id']).update (OO0OOO000OO00O000 )#line:1756
        if not OOO0OO0O0OOOOOO0O :#line:1757
            OOO0O00O0O0O0O00O ='inc'#line:1758
            O0O0O0O000O0OOOOO =json .loads (public .readFile (OO0O00OO00O0O0O00 ))#line:1759
            O0000OO00OO00OO00 .write_backups (OOO0O00O0O0O0O00O ,O0O0O0O000O0OOOOO )#line:1760
        if OO0OOO000OO00O000 ['upload_local']==''and os .path .isfile (O0000OO00OO00OO00 ._inc_file ):#line:1761
                if os .path .isfile (O0000OO00OO00OO00 ._full_file ):#line:1762
                    O0000OO00OO00OO00 .clean_local_full_backups (O0000OO00OO00OO00 ._full_file )#line:1763
                if os .path .isfile (O0000OO00OO00OO00 ._inc_file ):#line:1765
                    O0000OO00OO00OO00 .clean_local_inc_backups (O0000OO00OO00OO00 ._inc_file )#line:1766
                print ('|-用户设置不保留本地备份，已从本地服务器清理备份')#line:1768
        return public .returnMsg (True ,'执行备份任务成功！')#line:1769
    def write_backups (OOOO00OO000O000O0 ,O000O000OOO00000O ,OOOOO000O000O0OO0 ):#line:1772
        ""#line:1775
        O00O0OOO00OO00000 =OOOO00OO000O000O0 ._full_file if O000O000OOO00000O =='full'else ''#line:1776
        O000O0O000000O00O =OOOO00OO000O000O0 ._inc_file if O000O000OOO00000O =='full'else ''#line:1777
        for OO0OOO0OO00O0O0O0 in OOOOO000O000O0OO0 :#line:1778
            OOO00000O000O000O =OO0OOO0OO00O0O0O0 ['full_name'].replace ('/www/backup','bt_backup')#line:1779
            OOOO0O00000000000 ={"sid":OOOO00OO000O000O0 ._binlog_id ,"size":OO0OOO0OO00O0O0O0 ['size'],"type":O000O000OOO00000O ,"full_json":O00O0OOO00OO00000 ,"inc_json":O000O0O000000O00O ,"local_name":OO0OOO0OO00O0O0O0 ['full_name'],"ftp_name":'',"alioss_name":OOO00000O000O000O ,"txcos_name":OOO00000O000O000O ,"qiniu_name":OOO00000O000O000O ,"aws_name":'',"upyun_name":'',"obs_name":OOO00000O000O000O ,"bos_name":OOO00000O000O000O ,"gcloud_storage_name":'',"gdrive_name":'',"msonedrive_name":''}#line:1798
            if O000O000OOO00000O =='full'and public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',(O000O000OOO00000O ,OOOO00OO000O000O0 ._binlog_id )).count ():#line:1800
                OO0O0OOO000OO000O =public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',(O000O000OOO00000O ,OOOO00OO000O000O0 ._binlog_id )).getField ('id')#line:1801
                public .M ('mysqlbinlog_backups').delete (OO0O0OOO000OO000O )#line:1802
            if O000O000OOO00000O =='full':#line:1804
                OOO00OO00000OOOOO =public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',('inc',OOOO00OO000O000O0 ._binlog_id )).select ()#line:1805
                if OOO00OO00000OOOOO :#line:1806
                    for O0O00000OO0O0OO00 in OOO00OO00000OOOOO :#line:1807
                        if not O0O00000OO0O0OO00 :continue #line:1808
                        if 'id'in O0O00000OO0O0OO00 :public .M ('mysqlbinlog_backups').delete (O0O00000OO0O0OO00 ['id'])#line:1809
            if not public .M ('mysqlbinlog_backups').where ('type=? AND local_name=? AND sid=?',(O000O000OOO00000O ,OO0OOO0OO00O0O0O0 ['full_name'],OOOO00OO000O000O0 ._binlog_id )).count ():#line:1811
                public .M ('mysqlbinlog_backups').insert (OOOO0O00000000000 )#line:1812
            else :#line:1814
                OO0O0OOO000OO000O =public .M ('mysqlbinlog_backups').where ('type=? AND local_name=? AND sid=?',(O000O000OOO00000O ,OO0OOO0OO00O0O0O0 ['full_name'],OOOO00OO000O000O0 ._binlog_id )).getField ('id')#line:1815
                public .M ('mysqlbinlog_backups').where ('id=?',OO0O0OOO000OO000O ).update (OOOO0O00000000000 )#line:1816
            if O000O000OOO00000O =='inc'and not public .M ('mysqlbinlog_backups').where ('type=? AND sid=?',('full',OOOO00OO000O000O0 ._binlog_id )).count ():#line:1818
                try :#line:1819
                    O0000O0O0O00O0OO0 =json .loads (public .readFile (OOOO00OO000O000O0 ._full_file ))[0 ]#line:1820
                except :#line:1821
                    O0000O0O0O00O0OO0 ={}#line:1822
                if O0000O0O0O00O0OO0 :#line:1823
                    public .M ('mysqlbinlog_backups').insert (OOOO0O00000000000 )#line:1824
    def get_tables_list (OOO0OO0OOOO0OOO0O ,O0O0000OO0OO0OOO0 ,type =False ):#line:1826
        ""#line:1829
        O0O00O0000O00O0O0 =[]#line:1830
        for OOOOO0OOO0OOOO0OO in O0O0000OO0OO0OOO0 :#line:1831
            if not OOOOO0OOO0OOOO0OO :continue #line:1832
            if type :#line:1833
                if OOOOO0OOO0OOOO0OO .get ('type')!='F':continue #line:1834
            O0O00O0000O00O0O0 .append (OOOOO0OOO0OOOO0OO ['name'])#line:1835
        return O0O00O0000O00O0O0 #line:1836
    def clean_cloud_backups (O00O0000000O0O00O ,O00000O0000000OO0 ,O0OOO0000O0000O00 ,OO000OO0OOOOO0O0O ,O00OOO000O0OOOO00 ):#line:1839
        ""#line:1842
        try :#line:1843
            O0O0000OOO000OO0O =json .loads (public .readFile (O0OOO0000O0000O00 ))[0 ]#line:1844
        except :#line:1845
            O0O0000OOO000OO0O =[]#line:1846
        OOOO0O000OO00O0OO =OOO0O0OOO0000O0OO =OO0O0O00OO0OO00O0 =OO00OOO0000O0000O =OO00OO000OO0OOO0O =public .dict_obj ()#line:1847
        OOOO0O000OO00O0OO .path =O00000O0000000OO0 #line:1848
        O0O0OOOO0OO0OO00O =OO000OO0OOOOO0O0O .get_list (OOOO0O000OO00O0OO )#line:1849
        if 'list'in O0O0OOOO0OO0OO00O :#line:1850
            for O0O000000O0O0O00O in O0O0OOOO0OO0OO00O ['list']:#line:1851
                if not O0O000000O0O0O00O :continue #line:1852
                if O0O000000O0O0O00O ['name'][-1 ]=='/':#line:1853
                    OOO0O0OOO0000O0OO .path =O00000O0000000OO0 +O0O000000O0O0O00O ['name']#line:1854
                    OOO0O0OOO0000O0OO .filename =O0O000000O0O0O00O ['name']#line:1855
                    O00O00O000OO00OO0 =OO000OO0OOOOO0O0O .get_list (OOO0O0OOO0000O0OO )#line:1856
                    OOO0O0OOO0000O0OO .path =O00000O0000000OO0 #line:1857
                    if O00O00O000OO00OO0 ['list']:#line:1859
                        for O0O0000OO0OOOOO00 in O00O00O000OO00OO0 ['list']:#line:1860
                            OO0O0O00OO0OO00O0 .path =O00000O0000000OO0 +O0O000000O0O0O00O ['name']#line:1861
                            OO0O0O00OO0OO00O0 .filename =O0O0000OO0OOOOO00 ['name']#line:1862
                            OO000OO0OOOOO0O0O .remove_file (OO0O0O00OO0OO00O0 )#line:1863
                    else :#line:1865
                        OO000OO0OOOOO0O0O .remove_file (OOO0O0OOO0000O0OO )#line:1866
                if not O0O0000OOO000OO0O :continue #line:1868
                if O0O000000O0O0O00O ['name'].split ('.')[-1 ]in ['zip','gz','json']and O0O000000O0O0O00O ['name']!=O0O0000OOO000OO0O ['name']and O0O000000O0O0O00O ['name']!='full_record.json':#line:1869
                    OO00OOO0000O0000O .path =O00000O0000000OO0 #line:1870
                    OO00OOO0000O0000O .filename =O0O000000O0O0O00O ['name']#line:1871
                    OO000OO0OOOOO0O0O .remove_file (OO00OOO0000O0000O )#line:1872
                OOO000OO0O00OO0OO =False #line:1873
                if 'dir'not in O0O000000O0O0O00O :continue #line:1874
                if O0O000000O0O0O00O ['dir']==True :#line:1875
                    try :#line:1876
                        O00000O0O0000O00O =datetime .datetime .strptime (O0O000000O0O0O00O ['name'],'%Y-%m-%d')#line:1877
                        OOO000OO0O00OO0OO =True #line:1878
                    except :#line:1879
                        pass #line:1880
                O0OO0OOOO0OO000O0 =''#line:1881
                if OOO000OO0O00OO0OO :O0OO0OOOO0OO000O0 =os .path .join (O00000O0000000OO0 ,O0O000000O0O0O00O ['name'])#line:1882
                if O0OO0OOOO0OO000O0 :#line:1883
                    OO00OO000OO0OOO0O .path =O0OO0OOOO0OO000O0 #line:1884
                    OO00OO000OO0OOO0O .filename =''#line:1885
                    OO00OO000OO0OOO0O .is_inc =True #line:1886
                    OO000OO0OOOOO0O0O .remove_file (OO00OO000OO0OOO0O )#line:1887
        print ('|-已从{}清理过期备份文件'.format (O00OOO000O0OOOO00 ))#line:1888
    def add_binlog_inc_backup_task (O0O0O00O0O0OO00O0 ,O0OO00O0O000O00OO ,OO000O0O0O00OOO00 ):#line:1891
        ""#line:1897
        O00OO0OO00OO0OOOO ={"name":"[勿删]数据库增量备份[{}]".format (O0OO00O0O000O00OO ['database_table']),"type":O0OO00O0O000O00OO ['cron_type'],"where1":O0OO00O0O000O00OO ['backup_cycle'],"hour":'',"minute":'0',"sType":'enterpriseBackup',"sName":O0OO00O0O000O00OO ['backup_type'],"backupTo":OO000O0O0O00OOO00 ,"save":'1',"save_local":'1',"notice":O0OO00O0O000O00OO ['notice'],"notice_channel":O0OO00O0O000O00OO ['notice_channel'],"sBody":'{} {} --db_name {} --binlog_id {}'.format (O0O0O00O0O0OO00O0 ._python_path ,O0O0O00O0O0OO00O0 ._binlogModel_py ,O0O0O00O0O0OO00O0 ._db_name ,str (O0OO00O0O000O00OO ['id'])),"urladdress":'{}|{}|{}'.format (O0OO00O0O000O00OO ['db_name'],O0OO00O0O000O00OO ['tb_name'],O0OO00O0O000O00OO ['id'])}#line:1913
        import crontab #line:1914
        O0OOO0000O0O0OOOO =crontab .crontab ().AddCrontab (O00OO0OO00OO0OOOO )#line:1915
        if O0OOO0000O0O0OOOO and "id"in O0OOO0000O0O0OOOO .keys ():#line:1916
            return True #line:1917
        return False #line:1918
    def create_table (OO00OO0O0O00O0000 ):#line:1920
        ""#line:1925
        if not public .M ('sqlite_master').where ('type=? AND name=?',('table','mysqlbinlog_backup_setting')).count ():#line:1927
            public .M ('').execute ('''CREATE TABLE "mysqlbinlog_backup_setting" (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "save_path" DEFAULT '',
                                "temp_path" DEFAULT '',
                                "database_table" DEFAULT '',
                                "db_name" DEFAULT '',
                                "tb_name" DEFAULT '',
                                "backup_type" DEFAULT '',
                                "backup_cycle" TEXT DEFAULT '',
                                "zip_password" TEXT DEFAULT '',
                                "cron_type" TEXT DEFAULT '',
                                "where_1" TEXT DEFAULT '',
                                "where_2" INTEGER DEFAULT 0,
                                "table_list" TEXT,
                                "upload_local" TEXT DEFAULT '',
                                "upload_ftp" TEXT DEFAULT '',
                                "upload_alioss" TEXT DEFAULT '',
                                "upload_txcos" TEXT DEFAULT '',
                                "upload_qiniu" TEXT DEFAULT '',
                                "upload_aws" TEXT DEFAULT '',
                                "upload_upyun" TEXT DEFAULT '',
                                "upload_obs" TEXT DEFAULT '',
                                "upload_bos" TEXT DEFAULT '',
                                "upload_gcloud_storage" TEXT DEFAULT '',
                                "upload_gdrive" TEXT DEFAULT '',
                                "upload_msonedrive" ITEXT DEFAULT '',
                                "notice" DEFAULT 0,
                                "notice_channel" ITEXT DEFAULT '',
                                "cron_status"  INTEGER DEFAULT 1,
                                "sync_remote_status" INTEGER DEFAULT 0,
                                'sync_remote_time' INTEGER DEFAULT 0,
                                "start_backup_time"  INTEGER DEFAULT 0,
                                "end_backup_time"  INTEGER DEFAULT 0,
                                "last_excute_backup_time"  INTEGER DEFAULT 1,
                                "add_time" INTEGER);''')#line:1962
        if not public .M ('sqlite_master').where ('type=? AND name=?',('table','mysqlbinlog_backups')).count ():#line:1965
            public .M ('').execute ('''CREATE TABLE "mysqlbinlog_backups" (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "sid" INTEGER DEFAULT 0,
                                "size" INTEGER DEFAULT 0,
                                "type" DEFAULT '',
                                "full_json" DEFAULT '',
                                "inc_json" DEFAULT '',
                                "local_name" DEFAULT '',
                                "ftp_name" DEFAULT '',
                                "alioss_name" DEFAULT '',
                                "txcos_name" DEFAULT '',
                                "qiniu_name" DEFAULT '',
                                "aws_name" DEFAULT '',
                                "upyun_name" DEFAULT '',
                                "obs_name" DEFAULT '',
                                "bos_name" DEFAULT '',
                                "gcloud_storage_name" DEFAULT '',
                                "gdrive_name" DEFAULT '',
                                "msonedrive_name" DEFAULT '',
                                "where_1" DEFAULT '',
                                "where_2" DEFAULT '',
                                "where_3" DEFAULT '',
                                "where_4" TEXT DEFAULT '');''')#line:1988
    def add_mysqlbinlog_backup_setting (OO00OO00O000O0000 ,O00000O00OOO0OO0O ):#line:1991
        ""#line:1997
        public .set_module_logs ('binlog','add_mysqlbinlog_backup_setting')#line:1998
        if not O00000O00OOO0OO0O .get ('datab_name/str',0 ):return public .returnMsg (False ,'当前没有数据库，不能添加！')#line:1999
        if O00000O00OOO0OO0O .datab_name in [0 ,'0']:return public .returnMsg (False ,'当前没有数据库，不能添加！')#line:2000
        if not O00000O00OOO0OO0O .get ('backup_cycle/d',0 )>0 :return public .returnMsg (False ,'备份周期不正确，只能为正整数！')#line:2001
        O0OO0OO0O0OO0OOO0 =O0O000O00O000O0OO ={}#line:2005
        O0O0O00OO00OO0OO0 =OO00OO00O000O0000 .get_binlog_status ()#line:2006
        if O0O0O00OO00OO0OO0 ['status']==False :return public .returnMsg (False ,'请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')#line:2007
        OO00OO00O000O0000 ._db_name =O0O000O00O000O0OO ['db_name']=O00000O00OOO0OO0O .datab_name #line:2008
        O00OOOO0000O0O00O ='databases'if O00000O00OOO0OO0O .backup_type =='databases'else 'tables'#line:2009
        OO00OO00O000O0000 ._tables =''if 'table_name'not in O00000O00OOO0OO0O else O00000O00OOO0OO0O .table_name #line:2010
        O00O0OO0O000O0O00 =False #line:2011
        O00O0OOO0O0O0O00O =''#line:2013
        O0OO00O0OO0OO0OO0 =''#line:2014
        if OO00OO00O000O0000 ._tables :#line:2015
            O00O0OOO0O0O0O00O =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=? and tb_name=?',(O00000O00OOO0OO0O .datab_name ,O00OOOO0000O0O00O ,OO00OO00O000O0000 ._tables )).find ()#line:2016
            if O00O0OOO0O0O0O00O :#line:2017
                O0OO0OO0O0OO0OOO0 =O00O0OOO0O0O0O00O #line:2018
                O00O0OO0O000O0O00 =True #line:2019
                O0OO00O0OO0OO0OO0 =public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (OO00OO00O000O0000 ._python_path ,OO00OO00O000O0000 ._binlogModel_py ,O00O0OOO0O0O0O00O ['db_name'],str (O00O0OOO0O0O0O00O ['id']))).getField ('id')#line:2020
                if O0OO00O0OO0OO0OO0 :#line:2021
                    return public .returnMsg (False ,'指定的数据库或者表已经存在备份，不能重复添加！')#line:2022
        else :#line:2023
            O00O0OOO0O0O0O00O =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(O00000O00OOO0OO0O .datab_name ,O00OOOO0000O0O00O )).find ()#line:2024
            if O00O0OOO0O0O0O00O :#line:2025
                O0OO0OO0O0OO0OOO0 =O00O0OOO0O0O0O00O #line:2026
                O00O0OO0O000O0O00 =True #line:2027
                O0OO00O0OO0OO0OO0 =public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (OO00OO00O000O0000 ._python_path ,OO00OO00O000O0000 ._binlogModel_py ,O00O0OOO0O0O0O00O ['db_name'],str (O00O0OOO0O0O0O00O ['id']))).getField ('id')#line:2028
                if O0OO00O0OO0OO0OO0 :#line:2029
                    return public .returnMsg (False ,'指定的数据库或者表已经存在备份，不能重复添加！')#line:2030
        O0OO0OO0O0OO0OOO0 ['database_table']=O00000O00OOO0OO0O .datab_name if O00000O00OOO0OO0O .backup_type =='databases'else O00000O00OOO0OO0O .datab_name +'---'+O00000O00OOO0OO0O .table_name #line:2031
        O0OO0OO0O0OO0OOO0 ['backup_type']=O00OOOO0000O0O00O #line:2032
        O0OO0OO0O0OO0OOO0 ['backup_cycle']=O00000O00OOO0OO0O .backup_cycle #line:2033
        O0OO0OO0O0OO0OOO0 ['cron_type']=O00000O00OOO0OO0O .cron_type #line:2034
        O0OO0OO0O0OO0OOO0 ['notice']=O00000O00OOO0OO0O .notice #line:2035
        if O00000O00OOO0OO0O .notice =='1':#line:2036
            O0OO0OO0O0OO0OOO0 ['notice_channel']=O00000O00OOO0OO0O .notice_channel #line:2037
        else :#line:2038
            O0OO0OO0O0OO0OOO0 ['notice_channel']=''#line:2039
        OOOO0OO00OO0OO0OO =public .format_date ()#line:2040
        if O00O0OOO0O0O0O00O :O0OO0OO0O0OO0OOO0 ['zip_password']=O00O0OOO0O0O0O00O ['zip_password']#line:2041
        else :O0OO0OO0O0OO0OOO0 ['zip_password']=O00000O00OOO0OO0O .zip_password #line:2042
        O0OO0OO0O0OO0OOO0 ['start_backup_time']=OOOO0OO00OO0OO0OO #line:2043
        O0OO0OO0O0OO0OOO0 ['end_backup_time']=OOOO0OO00OO0OO0OO #line:2044
        O0OO0OO0O0OO0OOO0 ['last_excute_backup_time']=OOOO0OO00OO0OO0OO #line:2045
        O0OO0OO0O0OO0OOO0 ['table_list']='|'.join (OO00OO00O000O0000 .get_tables_list (OO00OO00O000O0000 .get_tables ()))#line:2046
        O0OO0OO0O0OO0OOO0 ['cron_status']=1 #line:2047
        O0OO0OO0O0OO0OOO0 ['sync_remote_status']=0 #line:2048
        O0OO0OO0O0OO0OOO0 ['sync_remote_time']=0 #line:2049
        O0OO0OO0O0OO0OOO0 ['add_time']=OOOO0OO00OO0OO0OO #line:2050
        O0OO0OO0O0OO0OOO0 ['db_name']=O00000O00OOO0OO0O .datab_name #line:2051
        O0OO0OO0O0OO0OOO0 ['tb_name']=OO00OO00O000O0000 ._tables =''if 'table_name'not in O00000O00OOO0OO0O else O00000O00OOO0OO0O .table_name #line:2052
        O0OO0OO0O0OO0OOO0 ['save_path']=OO00OO00O000O0000 .splicing_save_path ()#line:2053
        O0OO0OO0O0OO0OOO0 ['temp_path']=''#line:2054
        OO0000O000O0OO0OO ='|'#line:2058
        OO000OO0O000OOO00 =OOO0OOO0O0O0000OO =OO00OO0O00O0OOO0O =O0000O000OOO0OO0O =OOOO00OOOO00O0OO0 =OOO00O0O0OO0OO0OO =O0000000O0OO0O0OO =OO00OO0O0OO000OO0 =OO0O00O0O0OO0O000 =OOO00OO00OOOOOO0O ='|'#line:2059
        O0O000O0OO0O0O0O0 =''#line:2060
        if 'upload_localhost'in O00000O00OOO0OO0O :#line:2061
            O0OO0OO0O0OO0OOO0 ['upload_local']=O00000O00OOO0OO0O .upload_localhost #line:2062
            OO0000O000O0OO0OO ='localhost|'#line:2063
        else :#line:2064
            O0OO0OO0O0OO0OOO0 ['upload_local']=''#line:2065
        if 'upload_alioss'in O00000O00OOO0OO0O :#line:2066
            O0OO0OO0O0OO0OOO0 ['upload_alioss']=O00000O00OOO0OO0O .upload_alioss #line:2067
            OO000OO0O000OOO00 ='alioss|'#line:2068
        else :#line:2069
            O0OO0OO0O0OO0OOO0 ['upload_alioss']=''#line:2070
        if 'upload_ftp'in O00000O00OOO0OO0O :#line:2071
            O0OO0OO0O0OO0OOO0 ['upload_ftp']=O00000O00OOO0OO0O .upload_ftp #line:2072
            OOO0OOO0O0O0000OO ='ftp|'#line:2073
        else :#line:2074
            O0OO0OO0O0OO0OOO0 ['upload_ftp']=''#line:2075
        if 'upload_txcos'in O00000O00OOO0OO0O :#line:2076
            O0OO0OO0O0OO0OOO0 ['upload_txcos']=O00000O00OOO0OO0O .upload_txcos #line:2077
            OO00OO0O00O0OOO0O ='txcos|'#line:2078
        else :#line:2079
            O0OO0OO0O0OO0OOO0 ['upload_txcos']=''#line:2080
        if 'upload_qiniu'in O00000O00OOO0OO0O :#line:2081
            O0OO0OO0O0OO0OOO0 ['upload_qiniu']=O00000O00OOO0OO0O .upload_qiniu #line:2082
            O0000O000OOO0OO0O ='qiniu|'#line:2083
        else :#line:2084
            O0OO0OO0O0OO0OOO0 ['upload_qiniu']=''#line:2085
        if 'upload_aws'in O00000O00OOO0OO0O :#line:2086
            O0OO0OO0O0OO0OOO0 ['upload_aws']=O00000O00OOO0OO0O .upload_aws #line:2087
            OOOO00OOOO00O0OO0 ='aws|'#line:2088
        else :#line:2089
            O0OO0OO0O0OO0OOO0 ['upload_aws']=''#line:2090
        if 'upload_upyun'in O00000O00OOO0OO0O :#line:2091
            O0OO0OO0O0OO0OOO0 ['upload_upyun']=O00000O00OOO0OO0O .upload_upyun #line:2092
            OOO00O0O0OO0OO0OO ='upyun|'#line:2093
        else :#line:2094
            O0OO0OO0O0OO0OOO0 ['upload_upyun']=''#line:2095
        if 'upload_obs'in O00000O00OOO0OO0O :#line:2096
            O0OO0OO0O0OO0OOO0 ['upload_obs']=O00000O00OOO0OO0O .upload_obs #line:2097
            O0000000O0OO0O0OO ='obs|'#line:2098
        else :#line:2099
            O0OO0OO0O0OO0OOO0 ['upload_obs']=''#line:2100
        if 'upload_bos'in O00000O00OOO0OO0O :#line:2101
            O0OO0OO0O0OO0OOO0 ['upload_bos']=O00000O00OOO0OO0O .upload_bos #line:2102
            OO00OO0O0OO000OO0 ='bos|'#line:2103
        else :#line:2104
            O0OO0OO0O0OO0OOO0 ['upload_bos']=''#line:2105
        if 'upload_gcloud_storage'in O00000O00OOO0OO0O :#line:2106
            O0OO0OO0O0OO0OOO0 ['upload_gcloud_storage']=O00000O00OOO0OO0O .upload_gcloud_storage #line:2107
            OO0O00O0O0OO0O000 ='gcloud_storage|'#line:2108
        else :#line:2109
            O0OO0OO0O0OO0OOO0 ['upload_gcloud_storage']=''#line:2110
        if 'upload_gdrive'in O00000O00OOO0OO0O :#line:2111
            O0OO0OO0O0OO0OOO0 ['upload_gdrive']=O00000O00OOO0OO0O .upload_gdrive #line:2112
            OOO00OO00OOOOOO0O ='gdrive|'#line:2113
        else :#line:2114
            O0OO0OO0O0OO0OOO0 ['upload_gdrive']=''#line:2115
        if 'upload_msonedrive'in O00000O00OOO0OO0O :#line:2116
            O0OO0OO0O0OO0OOO0 ['upload_msonedrive']=O00000O00OOO0OO0O .upload_msonedrive #line:2117
            O0O000O0OO0O0O0O0 ='msonedrive'#line:2118
        else :#line:2119
            O0OO0OO0O0OO0OOO0 ['upload_msonedrive']=''#line:2120
        OO0000O000O0OO0OO =OO0000O000O0OO0OO +OO000OO0O000OOO00 +OOO0OOO0O0O0000OO +OO00OO0O00O0OOO0O +O0000O000OOO0OO0O +OOOO00OOOO00O0OO0 +OOO00O0O0OO0OO0OO +O0000000O0OO0O0OO +OO00OO0O0OO000OO0 +OO0O00O0O0OO0O000 +OOO00OO00OOOOOO0O +O0O000O0OO0O0O0O0 #line:2121
        if not O00O0OO0O000O0O00 :#line:2122
            O0OO0OO0O0OO0OOO0 ['id']=public .M ('mysqlbinlog_backup_setting').insert (O0OO0OO0O0OO0OOO0 )#line:2123
        else :#line:2124
            public .M ('mysqlbinlog_backup_setting').where ('id=?',int (O0OO0OO0O0OO0OOO0 ['id'])).update (O0OO0OO0O0OO0OOO0 )#line:2125
            time .sleep (0.01 )#line:2126
        if not O0OO00O0OO0OO0OO0 :#line:2128
            OO00OO00O000O0000 .add_binlog_inc_backup_task (O0OO0OO0O0OO0OOO0 ,OO0000O000O0OO0OO )#line:2129
        return public .returnMsg (True ,'添加成功!')#line:2130
    def modify_mysqlbinlog_backup_setting (O0OO00O0OOO00OO0O ,OOOO0OOO00O0OOO0O ):#line:2132
        ""#line:2138
        public .set_module_logs ('binlog','modify_mysqlbinlog_backup_setting')#line:2139
        if 'backup_id'not in OOOO0OOO00O0OOO0O :return public .returnMsg (False ,'错误的参数!')#line:2140
        if not OOOO0OOO00O0OOO0O .get ('backup_cycle/d',0 )>0 :return public .returnMsg (False ,'备份周期不正确，只能为正整数！')#line:2141
        O0OO0OOOO0O0OOOOO =O0OO00O0OOO00OO0O .get_binlog_status ()#line:2143
        if O0OO0OOOO0O0OOOOO ['status']==False :return public .returnMsg (False ,'请检查数据库是否正常运行或者请先开启二进制日志,否则可能导致备份的数据不完整！')#line:2144
        O0OOO0OOOOOO000O0 =public .M ('mysqlbinlog_backup_setting').where ('id=?',OOOO0OOO00O0OOO0O .backup_id ).find ()#line:2146
        O0OOO0OOOOOO000O0 ['backup_cycle']=OOOO0OOO00O0OOO0O .backup_cycle #line:2147
        O0OOO0OOOOOO000O0 ['notice']=OOOO0OOO00O0OOO0O .notice #line:2148
        O0OO00O0OOO00OO0O ._db_name =O0OOO0OOOOOO000O0 ['db_name']#line:2149
        if OOOO0OOO00O0OOO0O .notice =='1':#line:2150
            O0OOO0OOOOOO000O0 ['notice_channel']=OOOO0OOO00O0OOO0O .notice_channel #line:2151
        else :#line:2152
            O0OOO0OOOOOO000O0 ['notice_channel']=''#line:2153
        OOO0OO00OO00O0O00 ='|'#line:2155
        OOOOO0O0O0OO0OOO0 =OOO00O0000O0O0OO0 =OO0O000OOOO000OO0 =OOOOO000O00O0OOO0 =O0OOOOO000000OO00 =OO0O0OO0OO0OOOO0O =OOO0O0OOO00O000O0 =O0O0O0OO00O00OOOO =O0OOO0O00O0O00O00 =OOOOOO00OO00OO000 ='|'#line:2156
        O0O0OOO0OOO00O0OO =''#line:2157
        if 'upload_localhost'not in OOOO0OOO00O0OOO0O :#line:2158
            O0OOO0OOOOOO000O0 ['upload_local']=''#line:2159
        else :#line:2160
            O0OOO0OOOOOO000O0 ['upload_local']=OOOO0OOO00O0OOO0O .upload_localhost #line:2161
            OOO0OO00OO00O0O00 ='localhost|'#line:2162
        if 'upload_alioss'not in OOOO0OOO00O0OOO0O :#line:2163
            O0OOO0OOOOOO000O0 ['upload_alioss']=''#line:2164
        else :#line:2165
            O0OOO0OOOOOO000O0 ['upload_alioss']=OOOO0OOO00O0OOO0O .upload_alioss #line:2166
            OOOOO0O0O0OO0OOO0 ='alioss|'#line:2167
        if 'upload_ftp'not in OOOO0OOO00O0OOO0O :#line:2168
            O0OOO0OOOOOO000O0 ['upload_ftp']=''#line:2169
        else :#line:2170
            O0OOO0OOOOOO000O0 ['upload_ftp']=OOOO0OOO00O0OOO0O .upload_ftp #line:2171
            OOO00O0000O0O0OO0 ='ftp|'#line:2172
        if 'upload_txcos'not in OOOO0OOO00O0OOO0O :#line:2173
             O0OOO0OOOOOO000O0 ['upload_txcos']=''#line:2174
        else :#line:2175
            O0OOO0OOOOOO000O0 ['upload_txcos']=OOOO0OOO00O0OOO0O .upload_txcos #line:2176
            OO0O000OOOO000OO0 ='txcos|'#line:2177
        if 'upload_qiniu'not in OOOO0OOO00O0OOO0O :#line:2178
            O0OOO0OOOOOO000O0 ['upload_qiniu']=''#line:2179
        else :#line:2180
            O0OOO0OOOOOO000O0 ['upload_qiniu']=OOOO0OOO00O0OOO0O .upload_qiniu #line:2181
            OOOOO000O00O0OOO0 ='qiniu|'#line:2182
        if 'upload_aws'not in OOOO0OOO00O0OOO0O :#line:2183
            O0OOO0OOOOOO000O0 ['upload_aws']=''#line:2184
        else :#line:2185
            O0OOO0OOOOOO000O0 ['upload_aws']=OOOO0OOO00O0OOO0O .upload_aws #line:2186
            O0OOOOO000000OO00 ='aws|'#line:2187
        if 'upload_upyun'not in OOOO0OOO00O0OOO0O :#line:2188
            O0OOO0OOOOOO000O0 ['upload_upyun']=''#line:2189
        else :#line:2190
            O0OOO0OOOOOO000O0 ['upload_upyun']=OOOO0OOO00O0OOO0O .upload_upyun #line:2191
            OO0O0OO0OO0OOOO0O ='upyun|'#line:2192
        if 'upload_obs'not in OOOO0OOO00O0OOO0O :#line:2193
            O0OOO0OOOOOO000O0 ['upload_obs']=''#line:2194
        else :#line:2195
            O0OOO0OOOOOO000O0 ['upload_obs']=OOOO0OOO00O0OOO0O .upload_obs #line:2196
            OOO0O0OOO00O000O0 ='obs|'#line:2197
        if 'upload_bos'not in OOOO0OOO00O0OOO0O :#line:2198
            O0OOO0OOOOOO000O0 ['upload_bos']=''#line:2199
        else :#line:2200
            O0OOO0OOOOOO000O0 ['upload_bos']=OOOO0OOO00O0OOO0O .upload_bos #line:2201
            O0O0O0OO00O00OOOO ='bos|'#line:2202
        if 'upload_gcloud_storage'not in OOOO0OOO00O0OOO0O :#line:2203
            O0OOO0OOOOOO000O0 ['upload_gcloud_storage']=''#line:2204
        else :#line:2205
            O0OOO0OOOOOO000O0 ['upload_gcloud_storage']=OOOO0OOO00O0OOO0O .upload_gcloud_storage #line:2206
            O0OOO0O00O0O00O00 ='gcloud_storage|'#line:2207
        if 'upload_gdrive'not in OOOO0OOO00O0OOO0O :#line:2208
            O0OOO0OOOOOO000O0 ['upload_gdrive']=''#line:2209
        else :#line:2210
            O0OOO0OOOOOO000O0 ['upload_gdrive']=OOOO0OOO00O0OOO0O .upload_gdrive #line:2211
            OOOOOO00OO00OO000 ='gdrive|'#line:2212
        if 'upload_msonedrive'not in OOOO0OOO00O0OOO0O :#line:2213
            O0OOO0OOOOOO000O0 ['upload_msonedrive']=''#line:2214
        else :#line:2215
            O0OOO0OOOOOO000O0 ['upload_msonedrive']=OOOO0OOO00O0OOO0O .upload_msonedrive #line:2216
            O0O0OOO0OOO00O0OO ='msonedrive'#line:2217
        OOO0OO00OO00O0O00 =OOO0OO00OO00O0O00 +OOOOO0O0O0OO0OOO0 +OOO00O0000O0O0OO0 +OO0O000OOOO000OO0 +OOOOO000O00O0OOO0 +O0OOOOO000000OO00 +OO0O0OO0OO0OOOO0O +OOO0O0OOO00O000O0 +O0O0O0OO00O00OOOO +O0OOO0O00O0O00O00 +OOOOOO00OO00OO000 +O0O0OOO0OOO00O0OO #line:2218
        public .M ('mysqlbinlog_backup_setting').where ('id=?',int (OOOO0OOO00O0OOO0O .backup_id )).update (O0OOO0OOOOOO000O0 )#line:2219
        if 'cron_id'in OOOO0OOO00O0OOO0O :#line:2221
            if OOOO0OOO00O0OOO0O .cron_id :#line:2222
                O000OOO0O00OO0OOO ={"id":OOOO0OOO00O0OOO0O .cron_id ,"name":public .M ('crontab').where ("id=?",(OOOO0OOO00O0OOO0O .cron_id ,)).getField ('name'),"type":O0OOO0OOOOOO000O0 ['cron_type'],"where1":O0OOO0OOOOOO000O0 ['backup_cycle'],"hour":'',"minute":'0',"sType":'enterpriseBackup',"sName":O0OOO0OOOOOO000O0 ['backup_type'],"backupTo":OOO0OO00OO00O0O00 ,"save":O0OOO0OOOOOO000O0 ['notice'],"save_local":'1',"notice":O0OOO0OOOOOO000O0 ['notice'],"notice_channel":O0OOO0OOOOOO000O0 ['notice_channel'],"sBody":public .M ('crontab').where ("id=?",(OOOO0OOO00O0OOO0O .cron_id ,)).getField ('sBody'),"urladdress":'{}|{}|{}'.format (O0OOO0OOOOOO000O0 ['db_name'],O0OOO0OOOOOO000O0 ['tb_name'],O0OOO0OOOOOO000O0 ['id'])}#line:2239
                import crontab #line:2240
                crontab .crontab ().modify_crond (O000OOO0O00OO0OOO )#line:2241
                return public .returnMsg (True ,'编辑成功!')#line:2242
            else :#line:2243
                O0OO00O0OOO00OO0O .add_binlog_inc_backup_task (O0OOO0OOOOOO000O0 ,OOO0OO00OO00O0O00 )#line:2244
                return public .returnMsg (True ,'已恢复计划任务!')#line:2245
        else :#line:2246
            O0OO00O0OOO00OO0O .add_binlog_inc_backup_task (O0OOO0OOOOOO000O0 ,OOO0OO00OO00O0O00 )#line:2247
            return public .returnMsg (True ,'已恢复计划任务!')#line:2248
    def delete_mysql_binlog_setting (O0OOO0OO0OOO00O00 ,O0O0OO0OOO0O0OO0O ):#line:2250
        ""#line:2255
        public .set_module_logs ('binlog','delete_mysql_binlog_setting')#line:2256
        if 'backup_id'not in O0O0OO0OOO0O0OO0O and 'cron_id'not in O0O0OO0OOO0O0OO0O :return public .returnMsg (False ,'不存在此增量备份任务!')#line:2257
        O00O00OO0000OOO00 =''#line:2258
        if O0O0OO0OOO0O0OO0O .backup_id :#line:2259
            O00O00OO0000OOO00 =public .M ('mysqlbinlog_backup_setting').where ('id=?',(O0O0OO0OOO0O0OO0O .backup_id ,)).find ()#line:2260
            O0OOO0OO0OOO00O00 ._save_default_path =O00O00OO0000OOO00 ['save_path']#line:2261
            O0OOO0OO0OOO00O00 ._db_name =O00O00OO0000OOO00 ['db_name']#line:2262
        if 'cron_id'in O0O0OO0OOO0O0OO0O and O0O0OO0OOO0O0OO0O .cron_id :#line:2264
            if public .M ('crontab').where ('id=?',(O0O0OO0OOO0O0OO0O .cron_id ,)).count ():#line:2265
                O00O0OOO0O0000000 ={"id":O0O0OO0OOO0O0OO0O .cron_id }#line:2266
                import crontab #line:2267
                crontab .crontab ().DelCrontab (O00O0OOO0O0000000 )#line:2268
        if O0O0OO0OOO0O0OO0O .type =='manager'and O00O00OO0000OOO00 :#line:2270
            if public .M ('mysqlbinlog_backup_setting').where ('id=?',(O0O0OO0OOO0O0OO0O .backup_id ,)).count ():#line:2271
                public .M ('mysqlbinlog_backup_setting').where ('id=?',(O0O0OO0OOO0O0OO0O .backup_id ,)).delete ()#line:2272
            O0O0000O0O0OOOO0O =O00O00OO0000OOO00 ['save_path']+'full_record.json'#line:2273
            O0O000O0OO0O000OO =O00O00OO0000OOO00 ['save_path']+'inc_record.json'#line:2274
            if os .path .isfile (O0O0000O0O0OOOO0O ):O0OOO0OO0OOO00O00 .clean_local_full_backups (O0O0000O0O0OOOO0O )#line:2275
            if os .path .isfile (O0O000O0OO0O000OO ):O0OOO0OO0OOO00O00 .clean_local_inc_backups (O0O000O0OO0O000OO )#line:2276
            O0OO0000O0O000000 =public .M ('mysqlbinlog_backups').where ('sid=?',O0O0OO0OOO0O0OO0O .backup_id ).select ()#line:2277
            for OO0000O0O00OO0O0O in O0OO0000O0O000000 :#line:2278
                if not OO0000O0O00OO0O0O :continue #line:2279
                if 'id'not in OO0000O0O00OO0O0O :continue #line:2280
                public .M ('mysqlbinlog_backups').delete (OO0000O0O00OO0O0O ['id'])#line:2281
        return public .returnMsg (True ,'删除成功')#line:2282
    def get_inc_size (O0OO000000OO0O00O ,OO0O0000O000OOOOO ):#line:2284
        ""#line:2290
        O0OO00O0O0O000OOO =0 #line:2291
        if os .path .isfile (OO0O0000O000OOOOO ):#line:2292
            try :#line:2293
                O00O00OO0O00O00OO =json .loads (public .readFile (OO0O0000O000OOOOO ))#line:2294
                for OOO00000O0O0O00O0 in O00O00OO0O00O00OO :#line:2295
                    O0OO00O0O0O000OOO +=int (OOO00000O0O0O00O0 ['size'])#line:2296
            except :#line:2297
                O0OO00O0O0O000OOO =0 #line:2298
        return O0OO00O0O0O000OOO #line:2299
    def get_time_size (OOO0O0O0OOOO0O000 ,O00OOOOO0O00000O0 ,OOOO0000000O0000O ):#line:2301
        ""#line:2306
        OO0O00OO000OO0O0O =json .loads (public .readFile (O00OOOOO0O00000O0 ))[0 ]#line:2308
        OOOO0000000O0000O ['start_time']=OO0O00OO000OO0O0O ['time']#line:2309
        if 'end_time'in OO0O00OO000OO0O0O :#line:2310
            OOOO0000000O0000O ['end_time']=OO0O00OO000OO0O0O ['end_time']#line:2311
            OOOO0000000O0000O ['excute_time']=OO0O00OO000OO0O0O ['end_time']#line:2312
        else :#line:2313
            OOOO0000000O0000O ['end_time']=OO0O00OO000OO0O0O ['time']#line:2314
            OOOO0000000O0000O ['excute_time']=OO0O00OO000OO0O0O ['time']#line:2315
        OOOO0000000O0000O ['full_size']=OO0O00OO000OO0O0O ['size']#line:2316
        return OOOO0000000O0000O #line:2317
    def get_database_info (OO0O0OO0O0OOOOO00 ,get =None ):#line:2319
        ""#line:2324
        O0OOOOO0000O00O00 =OO0O0OO0O0OOOOO00 .get_databases ()#line:2325
        OOOOOOOOOOO0OOOO0 ={}#line:2326
        OOO000OOOOOOO0000 =[]#line:2327
        OO0OOOO00O00OO0OO =[]#line:2328
        if O0OOOOO0000O00O00 :#line:2329
            for O0OOO0000OO000OO0 in O0OOOOO0000O00O00 :#line:2330
                if not O0OOO0000OO000OO0 :continue #line:2331
                O0O0OOO0OOOO00OOO ={}#line:2332
                OO0O0OO0O0OOOOO00 ._db_name =O0O0OOO0OOOO00OOO ['name']=O0OOO0000OO000OO0 ['name']#line:2333
                O0OOO0O0000OO0OO0 =OO0O0OO0O0OOOOO00 ._save_default_path +O0OOO0000OO000OO0 ['name']+'/databases/'#line:2334
                OOOO0O0OO0OO0O0O0 =OO0O0OO0O0OOOOO00 ._save_default_path +O0OOO0000OO000OO0 ['name']+'/tables/'#line:2335
                OO0O000O0OOOO00O0 =O0OOO0O0000OO0OO0 +'full_record.json'#line:2336
                OO00O00O0000O00OO =O0OOO0O0000OO0OO0 +'inc_record.json'#line:2337
                O0O0OOO0OOOO00OOO ['inc_size']=0 if not os .path .isfile (OO00O00O0000O00OO )else OO0O0OO0O0OOOOO00 .get_inc_size (OO00O00O0000O00OO )#line:2338
                O0OOO00O00OOO0OOO =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(str (O0OOO0000OO000OO0 ['name']),'databases')).find ()#line:2340
                if O0OOO00O00OOO0OOO :#line:2341
                    O0O0OOO0OOOO00OOO ['cron_id']=public .M ('crontab').where ('name=?','[勿删]数据库增量备份[{}]'.format (O0OOO00O00OOO0OOO ['db_name'])).getField ('id')#line:2342
                    O0O0OOO0OOOO00OOO ['backup_id']=O0OOO00O00OOO0OOO ['id']#line:2343
                    O0O0OOO0OOOO00OOO ['upload_localhost']=O0OOO00O00OOO0OOO ['upload_local']#line:2344
                    O0O0OOO0OOOO00OOO ['upload_alioss']=O0OOO00O00OOO0OOO ['upload_alioss']#line:2345
                    O0O0OOO0OOOO00OOO ['upload_ftp']=O0OOO00O00OOO0OOO ['upload_ftp']#line:2346
                    O0O0OOO0OOOO00OOO ['upload_txcos']=O0OOO00O00OOO0OOO ['upload_txcos']#line:2347
                    O0O0OOO0OOOO00OOO ['upload_qiniu']=O0OOO00O00OOO0OOO ['upload_qiniu']#line:2348
                    O0O0OOO0OOOO00OOO ['upload_obs']=O0OOO00O00OOO0OOO ['upload_obs']#line:2349
                    O0O0OOO0OOOO00OOO ['upload_bos']=O0OOO00O00OOO0OOO ['upload_bos']#line:2350
                    O0O0OOO0OOOO00OOO ['backup_cycle']=O0OOO00O00OOO0OOO ['backup_cycle']#line:2351
                    O0O0OOO0OOOO00OOO ['notice']=O0OOO00O00OOO0OOO ['notice']#line:2352
                    O0O0OOO0OOOO00OOO ['notice_channel']=O0OOO00O00OOO0OOO ['notice_channel']#line:2353
                    O0O0OOO0OOOO00OOO ['zip_password']=O0OOO00O00OOO0OOO ['zip_password']#line:2354
                    O0O0OOO0OOOO00OOO ['start_time']=O0OOO00O00OOO0OOO ['start_backup_time']#line:2356
                    O0O0OOO0OOOO00OOO ['end_time']=O0OOO00O00OOO0OOO ['end_backup_time']#line:2357
                    O0O0OOO0OOOO00OOO ['excute_time']=O0OOO00O00OOO0OOO ['last_excute_backup_time']#line:2358
                else :#line:2359
                    O0O0OOO0OOOO00OOO ['cron_id']=O0O0OOO0OOOO00OOO ['backup_id']=O0O0OOO0OOOO00OOO ['notice']=O0O0OOO0OOOO00OOO ['upload_alioss']=O0O0OOO0OOOO00OOO ['backup_cycle']=O0O0OOO0OOOO00OOO ['zip_password']=None #line:2360
                    O0O0OOO0OOOO00OOO ['upload_localhost']=O0O0OOO0OOOO00OOO ['upload_alioss']=O0O0OOO0OOOO00OOO ['upload_ftp']=O0O0OOO0OOOO00OOO ['upload_txcos']=O0O0OOO0OOOO00OOO ['upload_qiniu']=O0O0OOO0OOOO00OOO ['upload_obs']=O0O0OOO0OOOO00OOO ['upload_bos']=''#line:2361
                if os .path .isfile (OO0O000O0OOOO00O0 ):#line:2363
                    O0O0OOO0OOOO00OOO =OO0O0OO0O0OOOOO00 .get_time_size (OO0O000O0OOOO00O0 ,O0O0OOO0OOOO00OOO )#line:2364
                    if O0OOO00O00OOO0OOO :O0O0OOO0OOOO00OOO ['excute_time']=O0OOO00O00OOO0OOO ['last_excute_backup_time']#line:2365
                    O0O0OOO0OOOO00OOO ['full_size']=public .to_size (O0O0OOO0OOOO00OOO ['full_size']+O0O0OOO0OOOO00OOO ['inc_size'])#line:2366
                    OOO000OOOOOOO0000 .append (O0O0OOO0OOOO00OOO )#line:2367
                else :#line:2369
                    if O0OOO00O00OOO0OOO :#line:2370
                        O0O0OOO0OOOO00OOO ['full_size']=0 #line:2371
                        O000O0OO0O0000OO0 =public .M ('mysqlbinlog_backups').where ('sid=?',O0OOO00O00OOO0OOO ['id']).select ()#line:2373
                        for OOO00OO000O0000OO in O000O0OO0O0000OO0 :#line:2374
                            if not OOO00OO000O0000OO :continue #line:2375
                            if 'size'not in OOO00OO000O0000OO :continue #line:2376
                            O0O0OOO0OOOO00OOO ['full_size']+=OOO00OO000O0000OO ['size']#line:2377
                        O0O0OOO0OOOO00OOO ['full_size']=public .to_size (O0O0OOO0OOOO00OOO ['full_size'])#line:2378
                        OOO000OOOOOOO0000 .append (O0O0OOO0OOOO00OOO )#line:2379
                O0OOO00O00OOO0OOO =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and backup_type=?',(str (O0OOO0000OO000OO0 ['name']),'tables')).select ()#line:2381
                O0O0O0OO0000000OO ={}#line:2382
                O0O0O0OO0000000OO ['name']=O0OOO0000OO000OO0 ['name']#line:2383
                O0O0OOO0OOO0000O0 =[]#line:2384
                O0OO00O0000O0OO0O =OO0O0OO0O0OOOOO00 .get_tables_list (OO0O0OO0O0OOOOO00 .get_tables ())#line:2385
                for O0OOO0O0O00O00O0O in O0OO00O0000O0OO0O :#line:2386
                    if not O0OO00O0000O0OO0O :continue #line:2387
                    O0O00O0O00OO0OO00 =public .M ('mysqlbinlog_backup_setting').where ('db_name=? and tb_name=? ',(OO0O0OO0O0OOOOO00 ._db_name ,O0OOO0O0O00O00O0O )).find ()#line:2388
                    OO0OO0OO0OOO00O00 =OOOO0O0OO0OO0O0O0 +O0OOO0O0O00O00O0O +'/full_record.json'#line:2389
                    O0O000O0OO000O00O =OOOO0O0OO0OO0O0O0 +O0OOO0O0O00O00O0O +'/inc_record.json'#line:2390
                    O0O0OOO0OOOO00OOO ={}#line:2391
                    O0O0OOO0OOOO00OOO ['name']=O0OOO0O0O00O00O0O #line:2392
                    O0O0OOO0OOOO00OOO ['inc_size']=OO0O0OO0O0OOOOO00 .get_inc_size (O0O000O0OO000O00O )#line:2394
                    if O0O00O0O00OO0OO00 :#line:2396
                        O0O0OOO0OOOO00OOO ['cron_id']=public .M ('crontab').where ('sBody=?','{} {} --db_name {} --binlog_id {}'.format (OO0O0OO0O0OOOOO00 ._python_path ,OO0O0OO0O0OOOOO00 ._binlogModel_py ,O0O00O0O00OO0OO00 ['db_name'],str (O0O00O0O00OO0OO00 ['id']))).getField ('id')#line:2397
                        O0O0OOO0OOOO00OOO ['backup_id']=O0O00O0O00OO0OO00 ['id']#line:2398
                        O0O0OOO0OOOO00OOO ['upload_localhost']=O0O00O0O00OO0OO00 ['upload_local']#line:2399
                        O0O0OOO0OOOO00OOO ['upload_alioss']=O0O00O0O00OO0OO00 ['upload_alioss']#line:2400
                        O0O0OOO0OOOO00OOO ['backup_cycle']=O0O00O0O00OO0OO00 ['backup_cycle']#line:2401
                        O0O0OOO0OOOO00OOO ['notice']=O0O00O0O00OO0OO00 ['notice']#line:2402
                        O0O0OOO0OOOO00OOO ['notice_channel']=O0O00O0O00OO0OO00 ['notice_channel']#line:2403
                        O0O0OOO0OOOO00OOO ['excute_time']=O0O00O0O00OO0OO00 ['last_excute_backup_time']#line:2404
                        O0O0OOO0OOOO00OOO ['zip_password']=O0O00O0O00OO0OO00 ['zip_password']#line:2405
                        O0O0OOO0OOOO00OOO ['upload_ftp']=O0O00O0O00OO0OO00 ['upload_ftp']#line:2406
                        O0O0OOO0OOOO00OOO ['upload_txcos']=O0O00O0O00OO0OO00 ['upload_txcos']#line:2407
                        O0O0OOO0OOOO00OOO ['upload_qiniu']=O0O00O0O00OO0OO00 ['upload_qiniu']#line:2408
                        O0O0OOO0OOOO00OOO ['upload_obs']=O0O00O0O00OO0OO00 ['upload_obs']#line:2409
                        O0O0OOO0OOOO00OOO ['upload_bos']=O0O00O0O00OO0OO00 ['upload_bos']#line:2410
                    else :#line:2412
                        O0O0OOO0OOOO00OOO ['cron_id']=O0O0OOO0OOOO00OOO ['backup_id']=O0O0OOO0OOOO00OOO ['notice']=O0O0OOO0OOOO00OOO ['upload_alioss']=O0O0OOO0OOOO00OOO ['backup_cycle']=O0O0OOO0OOOO00OOO ['zip_password']=None #line:2413
                        O0O0OOO0OOOO00OOO ['upload_localhost']=O0O0OOO0OOOO00OOO ['upload_alioss']=O0O0OOO0OOOO00OOO ['upload_ftp']=O0O0OOO0OOOO00OOO ['upload_txcos']=O0O0OOO0OOOO00OOO ['upload_qiniu']=O0O0OOO0OOOO00OOO ['upload_obs']=O0O0OOO0OOOO00OOO ['upload_bos']=''#line:2414
                    if os .path .isfile (OO0OO0OO0OOO00O00 ):#line:2416
                        O0O0OOO0OOOO00OOO =OO0O0OO0O0OOOOO00 .get_time_size (OO0OO0OO0OOO00O00 ,O0O0OOO0OOOO00OOO )#line:2417
                        if O0O00O0O00OO0OO00 :O0O0OOO0OOOO00OOO ['excute_time']=O0O00O0O00OO0OO00 ['last_excute_backup_time']#line:2418
                        O0O0OOO0OOOO00OOO ['full_size']=public .to_size (O0O0OOO0OOOO00OOO ['full_size']+O0O0OOO0OOOO00OOO ['inc_size'])#line:2419
                        O0O0OOO0OOO0000O0 .append (O0O0OOO0OOOO00OOO )#line:2420
                    else :#line:2422
                        if not O0O00O0O00OO0OO00 :continue #line:2423
                        O0O0OOO0OOOO00OOO ['start_time']=O0O00O0O00OO0OO00 ['start_backup_time']#line:2424
                        O0O0OOO0OOOO00OOO ['end_time']=O0O00O0O00OO0OO00 ['end_backup_time']#line:2425
                        O0O0OOO0OOOO00OOO ['excute_time']=O0O00O0O00OO0OO00 ['last_excute_backup_time']#line:2426
                        O0O0OOO0OOOO00OOO ['full_size']=0 #line:2431
                        O000O0OO0O0000OO0 =public .M ('mysqlbinlog_backups').where ('sid=?',O0O00O0O00OO0OO00 ['id']).select ()#line:2433
                        for O00OO0OOOOO00OOOO in O000O0OO0O0000OO0 :#line:2434
                            if not O00OO0OOOOO00OOOO :continue #line:2435
                            if 'size'not in O00OO0OOOOO00OOOO :continue #line:2436
                            O0O0OOO0OOOO00OOO ['full_size']+=O00OO0OOOOO00OOOO ['size']#line:2437
                        O0O0OOO0OOOO00OOO ['full_size']=public .to_size (O0O0OOO0OOOO00OOO ['full_size'])#line:2438
                        O0O0OOO0OOO0000O0 .append (O0O0OOO0OOOO00OOO )#line:2439
                if O0O0OOO0OOO0000O0 :#line:2440
                    O0O0O0OO0000000OO ['data']=O0O0OOO0OOO0000O0 #line:2441
                    OO0OOOO00O00OO0OO .append (O0O0O0OO0000000OO )#line:2442
        OOOOOOOOOOO0OOOO0 ['databases']=OOO000OOOOOOO0000 #line:2443
        OOOOOOOOOOO0OOOO0 ['tables']=OO0OOOO00O00OO0OO #line:2444
        return public .returnMsg (True ,OOOOOOOOOOO0OOOO0 )#line:2445
    def get_databases_info (O00O00O0OO0OOO000 ,OO0000OOO0O00OO0O ):#line:2447
        ""#line:2451
        public .set_module_logs ('binlog','get_databases_info')#line:2452
        O00OO0O0O00O0000O =O00O00O0OO0OOO000 .get_database_info ()#line:2453
        O00OOO00OO00OO00O =[]#line:2454
        for O0OOO0O00OO0OOO0O in O00OO0O0O00O0000O ['msg']['databases']:#line:2455
            O0OOO0O00OO0OOO0O ['type']='databases'#line:2456
            O00OOO00OO00OO00O .append (O0OOO0O00OO0OOO0O )#line:2457
        return O00O00O0OO0OOO000 .get_page (O00OOO00OO00OO00O ,OO0000OOO0O00OO0O )#line:2458
    def get_specified_database_info (O000000O000O00O0O ,O00O0OO000OOOOOO0 ):#line:2460
        ""#line:2464
        public .set_module_logs ('binlog','get_specified_database_info')#line:2465
        O0O00OOOO0OOO0000 =O000000O000O00O0O .get_database_info ()#line:2466
        OO00OOO0OO0OO0000 =[]#line:2467
        OOO00O00OO00O0O00 =['databases','all']#line:2468
        O0OOOOO00OO0OOO0O =['tables','all']#line:2469
        for OOO0O0OOOOO000000 in O0O00OOOO0OOO0000 ['msg']['databases']:#line:2470
            if OOO0O0OOOOO000000 ['name']==O00O0OO000OOOOOO0 .datab_name :#line:2471
                OOO0O0OOOOO000000 ['type']='databases'#line:2472
                if hasattr (O00O0OO000OOOOOO0 ,'type')and O00O0OO000OOOOOO0 .type not in OOO00O00OO00O0O00 :continue #line:2473
                OO00OOO0OO0OO0000 .append (OOO0O0OOOOO000000 )#line:2474
        for OOO0O0OOOOO000000 in O0O00OOOO0OOO0000 ['msg']['tables']:#line:2475
            if OOO0O0OOOOO000000 ['name']==O00O0OO000OOOOOO0 .datab_name :#line:2476
                for O00OO0O0OO00O0OOO in OOO0O0OOOOO000000 ['data']:#line:2477
                    O00OO0O0OO00O0OOO ['type']='tables'#line:2478
                    if hasattr (O00O0OO000OOOOOO0 ,'type')and O00O0OO000OOOOOO0 .type not in O0OOOOO00OO0OOO0O :continue #line:2479
                    OO00OOO0OO0OO0000 .append (O00OO0O0OO00O0OOO )#line:2480
        return O000000O000O00O0O .get_page (OO00OOO0OO0OO0000 ,O00O0OO000OOOOOO0 )#line:2481
    def get_page (OO0O00OO000OOO000 ,OO000O000O0OO000O ,O0O00O00OO00OO0OO ):#line:2484
        ""#line:2488
        import page #line:2490
        page =page .Page ()#line:2492
        OOOO0O0O00000O000 ={}#line:2494
        OOOO0O0O00000O000 ['count']=len (OO000O000O0OO000O )#line:2495
        OOOO0O0O00000O000 ['row']=10 #line:2496
        OOOO0O0O00000O000 ['p']=1 #line:2497
        if hasattr (O0O00O00OO00OO0OO ,'p'):#line:2498
            OOOO0O0O00000O000 ['p']=int (O0O00O00OO00OO0OO ['p'])#line:2499
        OOOO0O0O00000O000 ['uri']={}#line:2500
        OOOO0O0O00000O000 ['return_js']=''#line:2501
        OOOO00OO0OO000O0O ={}#line:2503
        OOOO00OO0OO000O0O ['page']=page .GetPage (OOOO0O0O00000O000 ,limit ='1,2,3,4,5,8')#line:2504
        O0OO00O0O00OO00O0 =0 #line:2505
        OOOO00OO0OO000O0O ['data']=[]#line:2506
        for O00O0OOO0O00O0O00 in range (OOOO0O0O00000O000 ['count']):#line:2507
            if O0OO00O0O00OO00O0 >=page .ROW :break #line:2508
            if O00O0OOO0O00O0O00 <page .SHIFT :continue #line:2509
            O0OO00O0O00OO00O0 +=1 #line:2510
            OOOO00OO0OO000O0O ['data'].append (OO000O000O0OO000O [O00O0OOO0O00O0O00 ])#line:2511
        return OOOO00OO0OO000O0O #line:2512
    def delete_file (OOOO0OO0000O000OO ,OOO0O0OO000000O00 ):#line:2515
        ""#line:2520
        if os .path .exists (OOO0O0OO000000O00 ):#line:2521
            os .remove (OOO0O0OO000000O00 )#line:2522
    def send_failture_notification (OOO000OO00O00OOOO ,O0O000000000O00OO ,target ="",remark =""):#line:2524
        ""#line:2529
        OO00O00OOOOO0000O ='数据库增量备份[ {} ]'.format (target )#line:2530
        O00O0OO000OO000O0 =OOO000OO00O00OOOO ._pdata ['notice']#line:2531
        O00OO00OO0OOOOOOO =OOO000OO00O00OOOO ._pdata ['notice_channel']#line:2532
        if O00O0OO000OO000O0 in [0 ,'0']or not O00OO00OO0OOOOOOO :#line:2533
            return #line:2534
        if O00O0OO000OO000O0 in [1 ,'1',2 ,'2']:#line:2535
            OO0O0O0O000O0O000 ="宝塔计划任务备份失败提醒"#line:2536
            OOO0O0000OOOOOO00 =OO00O00OOOOO0000O #line:2537
            O0000O00O0O0OO0O0 =OOO000OO00O00OOOO ._mybackup .generate_failture_notice (OOO0O0000OOOOOO00 ,O0O000000000O00OO ,remark )#line:2538
            OO000O0O0O0000O0O =OOO000OO00O00OOOO ._mybackup .send_notification (O00OO00OO0OOOOOOO ,OO0O0O0O000O0O000 ,O0000O00O0O0OO0O0 )#line:2539
            if OO000O0O0O0000O0O :#line:2540
                print ('|-消息通知已发送。')#line:2541
    def sync_date (O0000O00OO0000000 ):#line:2543
        ""#line:2546
        import config #line:2547
        config .config ().syncDate (None )#line:2548
def set_config (O0O00O00000000O0O ,O0O0OO0OO0OO00OOO ):#line:2553
    ""#line:2556
class alioss_main :#line:2559
    __OO0O000OO0OOOO0OO =None #line:2560
    __O0O000O0O0O0O0OO0 =0 #line:2561
    def __OO00O0O0OOOOO0O00 (O00OO0OOOO000OOOO ):#line:2562
        ""#line:2566
        if O00OO0OOOO000OOOO .__OO0O000OO0OOOO0OO :return #line:2567
        OOO0O00OOOOOO0O0O =O00OO0OOOO000OOOO .get_config ()#line:2569
        O00OO0OOOO000OOOO .__O000O0OO0OOO0O000 =OOO0O00OOOOOO0O0O [2 ]#line:2571
        if OOO0O00OOOOOO0O0O [3 ].find (OOO0O00OOOOOO0O0O [2 ])!=-1 :OOO0O00OOOOOO0O0O [3 ]=OOO0O00OOOOOO0O0O [3 ].replace (OOO0O00OOOOOO0O0O [2 ]+'.','')#line:2572
        O00OO0OOOO000OOOO .__OOOO0O0OOO00OOOOO =OOO0O00OOOOOO0O0O [3 ]#line:2573
        O00OO0OOOO000OOOO .__OO0OO0000O00O0O00 =main ().get_path (OOO0O00OOOOOO0O0O [4 ]+'/bt_backup/')#line:2574
        if O00OO0OOOO000OOOO .__OO0OO0000O00O0O00 [:1 ]=='/':O00OO0OOOO000OOOO .__OO0OO0000O00O0O00 =O00OO0OOOO000OOOO .__OO0OO0000O00O0O00 [1 :]#line:2575
        try :#line:2577
            O00OO0OOOO000OOOO .__OO0O000OO0OOOO0OO =oss2 .Auth (OOO0O00OOOOOO0O0O [0 ],OOO0O00OOOOOO0O0O [1 ])#line:2579
        except Exception as OO0O0OOOOOO0OOO00 :#line:2580
            pass #line:2581
    def get_config (O00O00O0000O0O0OO ):#line:2584
        ""#line:2589
        O0O0000OOOO000000 =main ()._config_path +'/alioss.conf'#line:2590
        if not os .path .isfile (O0O0000OOOO000000 ):#line:2592
            O00OOOO0OOOOOO0O0 =''#line:2593
            if os .path .isfile (main ()._plugin_path +'/alioss/config.conf'):#line:2594
                O00OOOO0OOOOOO0O0 =main ()._plugin_path +'/alioss/config.conf'#line:2595
            elif os .path .isfile (main ()._setup_path +'/data/aliossAS.conf'):#line:2596
                O00OOOO0OOOOOO0O0 =main ()._setup_path +'/data/aliossAS.conf'#line:2597
            if O00OOOO0OOOOOO0O0 :#line:2598
                O0O000O00000O0OO0 =json .loads (public .readFile (main ()._setup_path +'/data/aliossAS.conf'))#line:2599
                OOO00O0O00000O000 =O0O000O00000O0OO0 ['access_key']+'|'+O0O000O00000O0OO0 ['secret_key']+'|'+O0O000O00000O0OO0 ['bucket_name']+'|'+O0O000O00000O0OO0 ['bucket_domain']+'|'+O0O000O00000O0OO0 ['backup_path']#line:2600
                public .writeFile (O0O0000OOOO000000 ,OOO00O0O00000O000 )#line:2601
        if not os .path .isfile (O0O0000OOOO000000 ):return ['','','','','/']#line:2602
        OOO0000OO00O0O00O =public .readFile (O0O0000OOOO000000 )#line:2603
        if not OOO0000OO00O0O00O :return ['','','','','/']#line:2605
        OOO00OO00000O00OO =OOO0000OO00O0O00O .split ('|')#line:2606
        if len (OOO00OO00000O00OO )<5 :OOO00OO00000O00OO .append ('/')#line:2607
        return OOO00OO00000O00OO #line:2608
    def check_config (OO0O00O0OO0O0000O ):#line:2610
        ""#line:2615
        try :#line:2616
            OO0O00O0OO0O0000O .__OO00O0O0OOOOO0O00 ()#line:2617
            from itertools import islice #line:2619
            OOOOO00O00OOOOO0O =oss2 .Bucket (OO0O00O0OO0O0000O .__OO0O000OO0OOOO0OO ,OO0O00O0OO0O0000O .__OOOO0O0OOO00OOOOO ,OO0O00O0OO0O0000O .__O000O0OO0OOO0O000 )#line:2620
            OOOOOOO0OOOOO000O =oss2 .ObjectIterator (OOOOO00O00OOOOO0O )#line:2621
            OO0000O00O00OOOO0 =[]#line:2622
            OO00O0OO0OO00O0OO ='/'#line:2623
            '''key, last_modified, etag, type, size, storage_class'''#line:2624
            for O00OOO00000OOOO0O in islice (oss2 .ObjectIterator (OOOOO00O00OOOOO0O ,delimiter ='/',prefix ='/'),1000 ):#line:2625
                O00OOO00000OOOO0O .key =O00OOO00000OOOO0O .key .replace ('/','')#line:2626
                if not O00OOO00000OOOO0O .key :continue #line:2627
                O00OO000O0OO0OOO0 ={}#line:2628
                O00OO000O0OO0OOO0 ['name']=O00OOO00000OOOO0O .key #line:2629
                O00OO000O0OO0OOO0 ['size']=O00OOO00000OOOO0O .size #line:2630
                O00OO000O0OO0OOO0 ['type']=O00OOO00000OOOO0O .type #line:2631
                O00OO000O0OO0OOO0 ['download']=OO0O00O0OO0O0000O .download_file (OO00O0OO0OO00O0OO +O00OOO00000OOOO0O .key ,False )#line:2632
                O00OO000O0OO0OOO0 ['time']=O00OOO00000OOOO0O .last_modified #line:2633
                OO0000O00O00OOOO0 .append (O00OO000O0OO0OOO0 )#line:2634
            return True #line:2635
        except :#line:2636
            return False #line:2637
    def get_list (O000O0O00OOO0OO00 ,get =None ):#line:2639
        ""#line:2644
        O000O0O00OOO0OO00 .__OO00O0O0OOOOO0O00 ()#line:2646
        if not O000O0O00OOO0OO00 .__OO0O000OO0OOOO0OO :#line:2647
            return False #line:2648
        try :#line:2650
            from itertools import islice #line:2651
            O00O0OO00O0O0O00O =oss2 .Bucket (O000O0O00OOO0OO00 .__OO0O000OO0OOOO0OO ,O000O0O00OOO0OO00 .__OOOO0O0OOO00OOOOO ,O000O0O00OOO0OO00 .__O000O0OO0OOO0O000 )#line:2652
            OO000OOOO0OO0O0O0 =oss2 .ObjectIterator (O00O0OO00O0O0O00O )#line:2653
            O0OO000O0OO0O00OO =[]#line:2654
            O0O0OOO000O00O0OO =main ().get_path (get .path )#line:2655
            '''key, last_modified, etag, type, size, storage_class'''#line:2656
            for O0O00O000OO0OOO0O in islice (oss2 .ObjectIterator (O00O0OO00O0O0O00O ,delimiter ='/',prefix =O0O0OOO000O00O0OO ),1000 ):#line:2657
                O0O00O000OO0OOO0O .key =O0O00O000OO0OOO0O .key .replace (O0O0OOO000O00O0OO ,'')#line:2658
                if not O0O00O000OO0OOO0O .key :continue #line:2659
                O0OOO00OO0OO00000 ={}#line:2660
                O0OOO00OO0OO00000 ['name']=O0O00O000OO0OOO0O .key #line:2661
                O0OOO00OO0OO00000 ['size']=O0O00O000OO0OOO0O .size #line:2662
                O0OOO00OO0OO00000 ['type']=O0O00O000OO0OOO0O .type #line:2663
                O0OOO00OO0OO00000 ['download']=O000O0O00OOO0OO00 .download_file (O0O0OOO000O00O0OO +O0O00O000OO0OOO0O .key )#line:2664
                O0OOO00OO0OO00000 ['time']=O0O00O000OO0OOO0O .last_modified #line:2665
                O0OO000O0OO0O00OO .append (O0OOO00OO0OO00000 )#line:2666
            O0O0O0O00O000OOO0 ={}#line:2667
            O0O0O0O00O000OOO0 ['path']=get .path #line:2668
            O0O0O0O00O000OOO0 ['list']=O0OO000O0OO0O00OO #line:2669
            return O0O0O0O00O000OOO0 #line:2670
        except Exception as OOO0OO000O0OO0OO0 :#line:2671
            return public .returnMsg (False ,str (OOO0OO000O0OO0OO0 ))#line:2672
    def upload_file_by_path (OOO00000O00O0OOOO ,O0O0O000O0OOOO00O ,OO000OOOOOO0O0O0O ):#line:2674
        ""#line:2681
        OOO00000O00O0OOOO .__OO00O0O0OOOOO0O00 ()#line:2683
        if not OOO00000O00O0OOOO .__OO0O000OO0OOOO0OO :#line:2684
            return False #line:2685
        try :#line:2686
            OOO00000O000O0O00 =main ().get_path (os .path .dirname (OO000OOOOOO0O0O0O ))+os .path .basename (OO000OOOOOO0O0O0O )#line:2688
            try :#line:2690
                print ('|-正在上传{}到阿里云OSS'.format (O0O0O000O0OOOO00O ),end ='')#line:2691
                OO0O00O00O0OO00OO =oss2 .Bucket (OOO00000O00O0OOOO .__OO0O000OO0OOOO0OO ,OOO00000O00O0OOOO .__OOOO0O0OOO00OOOOO ,OOO00000O00O0OOOO .__O000O0OO0OOO0O000 )#line:2692
                oss2 .defaults .connection_pool_size =4 #line:2694
                OO0OO000O000OO0OO =oss2 .resumable_upload (OO0O00O00O0OO00OO ,OOO00000O000O0O00 ,O0O0O000O0OOOO00O ,store =oss2 .ResumableStore (root ='/tmp'),multipart_threshold =1024 *1024 *2 ,part_size =1024 *1024 ,num_threads =1 )#line:2699
                print (' ==> 成功')#line:2700
            except :#line:2701
                print ('|-无法上传{}到阿里云OSS！请检查阿里云OSS配置是否正确！'.format (O0O0O000O0OOOO00O ))#line:2702
            return True #line:2706
        except Exception as OOOO0000O0OOOOOO0 :#line:2707
            print (OOOO0000O0OOOOOO0 )#line:2708
            if OOOO0000O0OOOOOO0 .status ==403 :#line:2709
                time .sleep (5 )#line:2710
                OOO00000O00O0OOOO .__O0O000O0O0O0O0OO0 +=1 #line:2711
                if OOO00000O00O0OOOO .__O0O000O0O0O0O0OO0 <2 :#line:2712
                    OOO00000O00O0OOOO .upload_file_by_path (O0O0O000O0OOOO00O ,OO000OOOOOO0O0O0O )#line:2714
            return False #line:2715
    def download_file (OOOOO000O0OOOO00O ,OO0O0OO0OO0O0O00O ):#line:2717
        ""#line:2723
        OOOOO000O0OOOO00O .__OO00O0O0OOOOO0O00 ()#line:2725
        if not OOOOO000O0OOOO00O .__OO0O000OO0OOOO0OO :#line:2726
            return None #line:2727
        try :#line:2728
            OOOO00000OO0OOO00 =oss2 .Bucket (OOOOO000O0OOOO00O .__OO0O000OO0OOOO0OO ,OOOOO000O0OOOO00O .__OOOO0O0OOO00OOOOO ,OOOOO000O0OOOO00O .__O000O0OO0OOO0O000 )#line:2729
            O0O00OOOO000O0000 =OOOO00000OO0OOO00 .sign_url ('GET',OO0O0OO0OO0O0O00O ,3600 )#line:2730
            return O0O00OOOO000O0000 #line:2731
        except :#line:2732
            print (OOOOO000O0OOOO00O .__O0OO0OOO000O00000 )#line:2733
            return None #line:2734
    def alioss_delete_file (OO000OOO00OOOO000 ,O0OOOO00000OO00OO ):#line:2736
        ""#line:2742
        OO000OOO00OOOO000 .__OO00O0O0OOOOO0O00 ()#line:2744
        if not OO000OOO00OOOO000 .__OO0O000OO0OOOO0OO :#line:2745
            return False #line:2746
        try :#line:2748
            OO0O0O00OO0O0OO00 =oss2 .Bucket (OO000OOO00OOOO000 .__OO0O000OO0OOOO0OO ,OO000OOO00OOOO000 .__OOOO0O0OOO00OOOOO ,OO000OOO00OOOO000 .__O000O0OO0OOO0O000 )#line:2749
            O00O00O0OOO0OOO0O =OO0O0O00OO0O0OO00 .delete_object (O0OOOO00000OO00OO )#line:2750
            return O00O00O0OOO0OOO0O .status #line:2751
        except Exception as OOO0OO00O000O0000 :#line:2752
            if OOO0OO00O000O0000 .status ==403 :#line:2753
                OO000OOO00OOOO000 .__O0O000O0O0O0O0OO0 +=1 #line:2754
                if OO000OOO00OOOO000 .__O0O000O0O0O0O0OO0 <2 :#line:2755
                    OO000OOO00OOOO000 .alioss_delete_file (O0OOOO00000OO00OO )#line:2757
            print ('删除失败!')#line:2759
            return None #line:2760
    def remove_file (O0000O00O0OOOO0O0 ,OO0OOO0O0O0OOO0O0 ):#line:2762
        ""#line:2769
        OO0O0OOO0O0O0OO00 =main ().get_path (OO0OOO0O0O0OOO0O0 .path )#line:2770
        OOOO0O0OO0O00O0OO =OO0O0OOO0O0O0OO00 +OO0OOO0O0O0OOO0O0 .filename #line:2771
        O0000O00O0OOOO0O0 .alioss_delete_file (OOOO0O0OO0O00O0OO )#line:2772
        return public .returnMsg (True ,'删除文件成功!{}----{}'.format (OO0O0OOO0O0O0OO00 ,OOOO0O0OO0O00O0OO ))#line:2773
class txcos_main :#line:2776
    __OO0OOO0OO00OOOO0O =None #line:2777
    __O000O0000000O0O00 =None #line:2778
    __OOO00O00OOO0OO000 =0 #line:2779
    __OO0OOO0O00OO00OOO =None #line:2780
    __O000OO00O0O00OOOO =None #line:2781
    __OO0OOOO00O000OO0O =None #line:2782
    __O0O0OO0OO0O0000OO =None #line:2783
    __O0OOOOOO0O0OOO0O0 ="ERROR: 无法连接腾讯云COS !"#line:2784
    def __init__ (O0000000OO0OO0OO0 ):#line:2787
        O0000000OO0OO0OO0 .__OOO000O0000O0O0OO ()#line:2788
    def __OOO000O0000O0O0OO (OO00O000OO0O000OO ):#line:2790
        ""#line:2793
        if OO00O000OO0O000OO .__OO0OOO0OO00OOOO0O :return #line:2794
        O00OOOO0OOO000OOO =OO00O000OO0O000OO .get_config ()#line:2796
        OO00O000OO0O000OO .__OO0OOO0O00OO00OOO =O00OOOO0OOO000OOO [0 ]#line:2797
        OO00O000OO0O000OO .__O000OO00O0O00OOOO =O00OOOO0OOO000OOO [1 ]#line:2798
        OO00O000OO0O000OO .__OO0OOOO00O000OO0O =O00OOOO0OOO000OOO [2 ]#line:2799
        OO00O000OO0O000OO .__O0O0OO0OO0O0000OO =O00OOOO0OOO000OOO [3 ]#line:2800
        OO00O000OO0O000OO .__O000O0000000O0O00 =main ().get_path (O00OOOO0OOO000OOO [4 ])#line:2801
        try :#line:2802
            O0O00O0OOO000O000 =CosConfig (Region =OO00O000OO0O000OO .__OO0OOOO00O000OO0O ,SecretId =OO00O000OO0O000OO .__OO0OOO0O00OO00OOO ,SecretKey =OO00O000OO0O000OO .__O000OO00O0O00OOOO ,Token =None ,Scheme ='http')#line:2803
            OO00O000OO0O000OO .__OO0OOO0OO00OOOO0O =CosS3Client (O0O00O0OOO000O000 )#line:2804
        except Exception as OO00OOO0O0OO00OOO :#line:2805
            pass #line:2806
    def get_config (OOO0OO0OO0OO0O0O0 ,get =None ):#line:2810
        ""#line:2813
        OO0OOOOO00OOO0000 =main ()._config_path +'/txcos.conf'#line:2814
        if not os .path .isfile (OO0OOOOO00OOO0000 ):#line:2816
            O0OOOO0O0OOO0OOOO =''#line:2817
            if os .path .isfile (main ()._plugin_path +'/txcos/config.conf'):#line:2818
                O0OOOO0O0OOO0OOOO =main ()._plugin_path +'/txcos/config.conf'#line:2819
            elif os .path .isfile (main ()._setup_path +'/data/txcosAS.conf'):#line:2820
                O0OOOO0O0OOO0OOOO =main ()._setup_path +'/data/txcosAS.conf'#line:2821
            if O0OOOO0O0OOO0OOOO :#line:2822
                OOOO0O0OO00OO000O =json .loads (public .readFile (O0OOOO0O0OOO0OOOO ))#line:2823
                O00OO0OO000O00O00 =OOOO0O0OO00OO000O ['secret_id']+'|'+OOOO0O0OO00OO000O ['secret_key']+'|'+OOOO0O0OO00OO000O ['region']+'|'+OOOO0O0OO00OO000O ['bucket_name']+'|'+OOOO0O0OO00OO000O ['backup_path']#line:2824
                public .writeFile (OO0OOOOO00OOO0000 ,O00OO0OO000O00O00 )#line:2825
        if not os .path .isfile (OO0OOOOO00OOO0000 ):return ['','','','','/']#line:2826
        O0O000O00OOO000O0 =public .readFile (OO0OOOOO00OOO0000 )#line:2827
        if not O0O000O00OOO000O0 :return ['','','','','/']#line:2828
        O00O0O00OOOOO00O0 =O0O000O00OOO000O0 .split ('|')#line:2829
        if len (O00O0O00OOOOO00O0 )<5 :O00O0O00OOOOO00O0 .append ('/')#line:2830
        return O00O0O00OOOOO00O0 #line:2831
    def check_config (OOOOO0000O00000OO ):#line:2834
        try :#line:2835
            O0000OOOOO00OO00O =[]#line:2836
            O0O0OO0000O0OO0OO =[]#line:2837
            OO00OOOO00OO0O000 =OOOOO0000O00000OO .__O000O0000000O0O00 +main ().get_path ('/')#line:2838
            O0OO0000OOO00O000 =OOOOO0000O00000OO .__OO0OOO0OO00OOOO0O .list_objects (Bucket =OOOOO0000O00000OO .__O0O0OO0OO0O0000OO ,MaxKeys =100 ,Delimiter ='/',Prefix =OO00OOOO00OO0O000 )#line:2839
            return True #line:2840
        except :#line:2841
            return False #line:2842
    def upload_file (O0O0O0O0OO0O00OO0 ,OO0O0OO0OOOOO0OO0 ):#line:2844
        ""#line:2848
        O0O0O0O0OO0O00OO0 .__OOO000O0000O0O0OO ()#line:2850
        if not O0O0O0O0OO0O00OO0 .__OO0OOO0OO00OOOO0O :#line:2851
            return False #line:2852
        try :#line:2854
            OO00O000000O00000 ,OOO00O00OOO00OO0O =os .path .split (OO0O0OO0OOOOO0OO0 )#line:2856
            OOO00O00OOO00OO0O =O0O0O0O0OO0O00OO0 .__O000O0000000O0O00 +OOO00O00OOO00OO0O #line:2857
            O0000O0OOO0OO0OOO =O0O0O0O0OO0O00OO0 .__OO0OOO0OO00OOOO0O .upload_file (Bucket =O0O0O0O0OO0O00OO0 .__O0O0OO0OO0O0000OO ,Key =OOO00O00OOO00OO0O ,MAXThread =10 ,PartSize =5 ,LocalFilePath =OO0O0OO0OOOOO0OO0 )#line:2864
        except :#line:2865
            time .sleep (1 )#line:2866
            O0O0O0O0OO0O00OO0 .__OOO00O00OOO0OO000 +=1 #line:2867
            if O0O0O0O0OO0O00OO0 .__OOO00O00OOO0OO000 <2 :#line:2868
                O0O0O0O0OO0O00OO0 .upload_file (OO0O0OO0OOOOO0OO0 )#line:2870
            print (O0O0O0O0OO0O00OO0 .__O0OOOOOO0O0OOO0O0 )#line:2871
            return None #line:2872
    def upload_file_by_path (O000OOOO0000OOO0O ,OO000OOO0OOOOO0O0 ,O000OOO0OO000OO0O ):#line:2875
        ""#line:2880
        O000OOOO0000OOO0O .__OOO000O0000O0O0OO ()#line:2882
        if not O000OOOO0000OOO0O .__OO0OOO0OO00OOOO0O :#line:2883
            return False #line:2884
        try :#line:2886
            print ('|-正在上传{}到腾讯云COS'.format (OO000OOO0OOOOO0O0 ),end ='')#line:2887
            O00OOO00OO0O0OO00 ,O0OOO00O0O0000OO0 =os .path .split (OO000OOO0OOOOO0O0 )#line:2888
            O000OOOO0000OOO0O .__O000O0000000O0O00 =main ().get_path (os .path .dirname (O000OOO0OO000OO0O ))#line:2889
            O0OOO00O0O0000OO0 =O000OOOO0000OOO0O .__O000O0000000O0O00 +'/'+O0OOO00O0O0000OO0 #line:2890
            O00OOO0O0O000OO00 =O000OOOO0000OOO0O .__OO0OOO0OO00OOOO0O .upload_file (Bucket =O000OOOO0000OOO0O .__O0O0OO0OO0O0000OO ,Key =O0OOO00O0O0000OO0 ,MAXThread =10 ,PartSize =5 ,LocalFilePath =OO000OOO0OOOOO0O0 )#line:2893
            print (' ==> 成功')#line:2895
            return True #line:2896
        except Exception as OO00OOO0OOO0O000O :#line:2897
            time .sleep (1 )#line:2899
            O000OOOO0000OOO0O .__OOO00O00OOO0OO000 +=1 #line:2900
            if O000OOOO0000OOO0O .__OOO00O00OOO0OO000 <2 :#line:2901
                O000OOOO0000OOO0O .upload_file_by_path (OO000OOO0OOOOO0O0 ,O000OOO0OO000OO0O )#line:2903
            return False #line:2904
    def create_dir (O00OO0O0OOOO0OO00 ,get =None ):#line:2907
        ""#line:2910
        O00OO0O0OOOO0OO00 .__OOO000O0000O0O0OO ()#line:2912
        if not O00OO0O0OOOO0OO00 .__OO0OOO0OO00OOOO0O :#line:2913
            return False #line:2914
        OO0000O00OOO0OOO0 =main ().get_path (get .path +get .dirname )#line:2916
        OOOO0O00OOO0OOOOO ='/tmp/dirname.pl'#line:2917
        public .writeFile (OOOO0O00OOO0OOOOO ,'')#line:2918
        OOOOO00O0OO000OOO =O00OO0O0OOOO0OO00 .__OO0OOO0OO00OOOO0O .put_object (Bucket =O00OO0O0OOOO0OO00 .__O0O0OO0OO0O0000OO ,Body =b'',Key =OO0000O00OOO0OOO0 )#line:2919
        os .remove (OOOO0O00OOO0OOOOO )#line:2920
        return public .returnMsg (True ,'创建成功!')#line:2921
    def get_list (O0000OO000OO0OO0O ,get =None ):#line:2923
        ""#line:2926
        O0000OO000OO0OO0O .__OOO000O0000O0O0OO ()#line:2928
        if not O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O :#line:2929
            return False #line:2930
        try :#line:2932
            O00OO0OOOOO0OO0OO =[]#line:2933
            OO0OOOOOO000OOO0O =[]#line:2934
            O0OO000O000OOO00O =main ().get_path (get .path )#line:2935
            if 'Contents'in O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O .list_objects (Bucket =O0000OO000OO0OO0O .__O0O0OO0OO0O0000OO ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO000O000OOO00O ):#line:2936
                for OO0OOO0OO000OOOO0 in O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O .list_objects (Bucket =O0000OO000OO0OO0O .__O0O0OO0OO0O0000OO ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO000O000OOO00O )['Contents']:#line:2937
                    OOO0O000OOO00OOOO ={}#line:2938
                    OO0OOO0OO000OOOO0 ['Key']=OO0OOO0OO000OOOO0 ['Key'].replace (O0OO000O000OOO00O ,'')#line:2939
                    if not OO0OOO0OO000OOOO0 ['Key']:continue #line:2940
                    OOO0O000OOO00OOOO ['name']=OO0OOO0OO000OOOO0 ['Key']#line:2941
                    OOO0O000OOO00OOOO ['size']=OO0OOO0OO000OOOO0 ['Size']#line:2942
                    OOO0O000OOO00OOOO ['type']=OO0OOO0OO000OOOO0 ['StorageClass']#line:2943
                    OOO0O000OOO00OOOO ['download']=O0000OO000OO0OO0O .download_file (O0OO000O000OOO00O +OO0OOO0OO000OOOO0 ['Key'])#line:2944
                    OOO0O000OOO00OOOO ['time']=OO0OOO0OO000OOOO0 ['LastModified']#line:2945
                    O00OO0OOOOO0OO0OO .append (OOO0O000OOO00OOOO )#line:2946
            else :#line:2947
                pass #line:2948
            if 'CommonPrefixes'in O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O .list_objects (Bucket =O0000OO000OO0OO0O .__O0O0OO0OO0O0000OO ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO000O000OOO00O ):#line:2949
                for O00O0000OOO0OO000 in O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O .list_objects (Bucket =O0000OO000OO0OO0O .__O0O0OO0OO0O0000OO ,MaxKeys =100 ,Delimiter ='/',Prefix =O0OO000O000OOO00O )['CommonPrefixes']:#line:2950
                    if not O00O0000OOO0OO000 ['Prefix']:continue #line:2951
                    OOO00O00O00OO0OOO =O00O0000OOO0OO000 ['Prefix'].split ('/')[-2 ]+'/'#line:2952
                    OO0OOOOOO000OOO0O .append (OOO00O00O00OO0OOO )#line:2953
            else :#line:2954
                pass #line:2955
            O000OO0O00O0OO0OO ={}#line:2956
            O000OO0O00O0OO0OO ['path']=get .path #line:2957
            O000OO0O00O0OO0OO ['list']=O00OO0OOOOO0OO0OO #line:2958
            O000OO0O00O0OO0OO ['dir']=OO0OOOOOO000OOO0O #line:2959
            return O000OO0O00O0OO0OO #line:2960
        except :#line:2961
            O000OO0O00O0OO0OO ={}#line:2962
            if O0000OO000OO0OO0O .__OO0OOO0OO00OOOO0O :#line:2963
                O000OO0O00O0OO0OO ['status']=True #line:2964
            else :#line:2965
                O000OO0O00O0OO0OO ['status']=False #line:2966
            O000OO0O00O0OO0OO ['path']=get .path #line:2967
            O000OO0O00O0OO0OO ['list']=O00OO0OOOOO0OO0OO #line:2968
            O000OO0O00O0OO0OO ['dir']=OO0OOOOOO000OOO0O #line:2969
            return O000OO0O00O0OO0OO #line:2970
    def download_file (OO0OO00OO00O0OOO0 ,O0OO0O00OOO0O00OO ,Expired =300 ):#line:2972
        ""#line:2975
        OO0OO00OO00O0OOO0 .__OOO000O0000O0O0OO ()#line:2977
        if not OO0OO00OO00O0OOO0 .__OO0OOO0OO00OOOO0O :#line:2978
            return None #line:2979
        try :#line:2980
            OOO00OO0000OOO0O0 =OO0OO00OO00O0OOO0 .__OO0OOO0OO00OOOO0O .get_presigned_download_url (Bucket =OO0OO00OO00O0OOO0 .__O0O0OO0OO0O0000OO ,Key =O0OO0O00OOO0O00OO )#line:2981
            OOO00OO0000OOO0O0 =re .findall ('([^?]*)?.*',OOO00OO0000OOO0O0 )[0 ]#line:2982
            return OOO00OO0000OOO0O0 #line:2983
        except :#line:2984
            print (OO0OO00OO00O0OOO0 .__O0OOOOOO0O0OOO0O0 )#line:2985
            return None #line:2986
    def delete_file (O0OO000O0OOOOOO0O ,O0OO0O0OOO0OO0000 ):#line:2988
        ""#line:2992
        O0OO000O0OOOOOO0O .__OOO000O0000O0O0OO ()#line:2994
        if not O0OO000O0OOOOOO0O .__OO0OOO0OO00OOOO0O :#line:2995
            return False #line:2996
        try :#line:2998
            OO0OO0OO00OO0O0O0 =O0OO000O0OOOOOO0O .__OO0OOO0OO00OOOO0O .delete_object (Bucket =O0OO000O0OOOOOO0O .__O0O0OO0OO0O0000OO ,Key =O0OO0O0OOO0OO0000 )#line:2999
            return OO0OO0OO00OO0O0O0 #line:3000
        except Exception as OO00O0O0OOO0OO0OO :#line:3001
            O0OO000O0OOOOOO0O .__OOO00O00OOO0OO000 +=1 #line:3002
            if O0OO000O0OOOOOO0O .__OOO00O00OOO0OO000 <2 :#line:3003
                O0OO000O0OOOOOO0O .delete_file (O0OO0O0OOO0OO0000 )#line:3005
            print (O0OO000O0OOOOOO0O .__O0OOOOOO0O0OOO0O0 )#line:3006
            return None #line:3007
    def remove_file (O0O0O0O0O0O0O0O0O ,O0O0OOO00000O0O0O ):#line:3010
        OO00O00OOO0O0O0O0 =main ().get_path (O0O0OOO00000O0O0O .path )#line:3011
        O00O00OOO0O0OOO00 =OO00O00OOO0O0O0O0 +O0O0OOO00000O0O0O .filename #line:3012
        O0O0O0O0O0O0O0O0O .delete_file (O00O00OOO0O0OOO00 )#line:3013
        return public .returnMsg (True ,'删除文件成功!')#line:3014
class ftp_main :#line:3017
    __OO00O00O0O00OOO0O ='/'#line:3018
    def __init__ (O000OO00O000OOO0O ):#line:3020
        O000OO00O000OOO0O .__OO00O00O0O00OOO0O =O000OO00O000OOO0O .get_config (None )[3 ]#line:3021
    def get_config (OO000OOOOO0OO0OOO ,get =None ):#line:3023
        O00O00O0OOO0O0OOO =main ()._config_path +'/ftp.conf'#line:3024
        if not os .path .isfile (O00O00O0OOO0O0OOO ):#line:3026
            OOOO0OO0OOO0O0OOO =''#line:3027
            if os .path .isfile (main ()._plugin_path +'/ftp/config.conf'):#line:3028
                OOOO0OO0OOO0O0OOO =main ()._plugin_path +'/ftp/config.conf'#line:3029
            elif os .path .isfile (main ()._setup_path +'/data/ftpAS.conf'):#line:3030
                OOOO0OO0OOO0O0OOO =main ()._setup_path +'/data/ftpAS.conf'#line:3031
            if OOOO0OO0OOO0O0OOO :#line:3032
                OO0O00OOOOO0O00OO =json .loads (public .readFile (OOOO0OO0OOO0O0OOO ))#line:3033
                OO0O00OOOOOOOO00O =OO0O00OOOOO0O00OO ['ftp_host']+'|'+OO0O00OOOOO0O00OO ['ftp_user']+'|'+OO0O00OOOOO0O00OO ['ftp_pass']+'|'+OO0O00OOOOO0O00OO ['backup_path']#line:3034
                public .writeFile (O00O00O0OOO0O0OOO ,OO0O00OOOOOOOO00O )#line:3035
        if not os .path .exists (O00O00O0OOO0O0OOO ):return ['','','','/']#line:3036
        O0OO00OOOO0000OO0 =public .readFile (O00O00O0OOO0O0OOO )#line:3037
        if not O0OO00OOOO0000OO0 :return ['','','','/']#line:3038
        return O0OO00OOOO0000OO0 .split ('|')#line:3039
    def set_config (O0O0OO00OOOOO00O0 ,OOOO00OO0OOO0OO0O ):#line:3041
        O0O0OOOO0000OOOOO =main ()._config_path +'/ftp.conf'#line:3042
        OOOO000O00O0OOOOO =OOOO00OO0OOO0OO0O .ftp_host +'|'+OOOO00OO0OOO0OO0O .ftp_user +'|'+OOOO00OO0OOO0OO0O .ftp_pass +'|'+OOOO00OO0OOO0OO0O .ftp_path #line:3043
        public .writeFile (O0O0OOOO0000OOOOO ,OOOO000O00O0OOOOO )#line:3044
        return public .returnMsg (True ,'设置成功!')#line:3045
    def connentFtp (O00O00OO00O0000OO ):#line:3048
        from ftplib import FTP #line:3049
        OO00OO000O0OOOO0O =O00O00OO00O0000OO .get_config ()#line:3050
        if OO00OO000O0OOOO0O [0 ].find (':')==-1 :OO00OO000O0OOOO0O [0 ]+=':21'#line:3051
        O0000OOO0OOOOO00O =OO00OO000O0OOOO0O [0 ].split (':')#line:3052
        if O0000OOO0OOOOO00O [1 ]=='':O0000OOO0OOOOO00O [1 ]='21'#line:3053
        O0OO000O00000O0OO =FTP ()#line:3054
        O0OO000O00000O0OO .set_debuglevel (0 )#line:3055
        O0OO000O00000O0OO .connect (O0000OOO0OOOOO00O [0 ],int (O0000OOO0OOOOO00O [1 ]))#line:3056
        O0OO000O00000O0OO .login (OO00OO000O0OOOO0O [1 ],OO00OO000O0OOOO0O [2 ])#line:3057
        if O00O00OO00O0000OO .__OO00O00O0O00OOO0O !='/':#line:3058
            O00O00OO00O0000OO .dirname =O00O00OO00O0000OO .__OO00O00O0O00OOO0O #line:3059
            O00O00OO00O0000OO .path ='/'#line:3060
            O00O00OO00O0000OO .createDir (O00O00OO00O0000OO ,O0OO000O00000O0OO )#line:3061
        O0OO000O00000O0OO .cwd (O00O00OO00O0000OO .__OO00O00O0O00OOO0O )#line:3062
        return O0OO000O00000O0OO #line:3063
    def check_config (OOO00OOOO00O0000O ):#line:3066
        try :#line:3067
            OO000OOOOO000O000 =OOO00OOOO00O0000O .connentFtp ()#line:3068
            if OO000OOOOO000O000 :return True #line:3069
        except :#line:3070
            return False #line:3071
    def createDir (OO0000000000O0O0O ,O0OO00OOOOOO0OOOO ,ftp =None ):#line:3074
        try :#line:3075
            if not ftp :ftp =OO0000000000O0O0O .connentFtp ()#line:3076
            O0OO000O0O0OOO0O0 =O0OO00OOOOOO0OOOO .dirname .split ('/')#line:3077
            ftp .cwd (O0OO00OOOOOO0OOOO .path )#line:3078
            for O0OO0OO00O0O00OOO in O0OO000O0O0OOO0O0 :#line:3079
                if not O0OO0OO00O0O00OOO :continue #line:3080
                if not O0OO0OO00O0O00OOO in ftp .nlst ():ftp .mkd (O0OO0OO00O0O00OOO )#line:3081
                ftp .cwd (O0OO0OO00O0O00OOO )#line:3082
            return public .returnMsg (True ,'目录创建成功!')#line:3083
        except :#line:3084
            return public .returnMsg (False ,'目录创建失败!')#line:3085
    def updateFtp (O0O0O0000OOOOO000 ,O00O00OO00OO00000 ):#line:3088
        try :#line:3089
            O0O00OO0OOO0O0O00 =O0O0O0000OOOOO000 .connentFtp ()#line:3090
            OOO0000OOO0OO00OO =1024 #line:3091
            OO000O0000OOOO000 =open (O00O00OO00OO00000 ,'rb')#line:3092
            O0O00OO0OOO0O0O00 .storbinary ('STOR %s'%os .path .basename (O00O00OO00OO00000 ),OO000O0000OOOO000 ,OOO0000OOO0OO00OO )#line:3093
            OO000O0000OOOO000 .close ()#line:3094
            O0O00OO0OOO0O0O00 .quit ()#line:3095
        except :#line:3096
            if os .path .exists (O00O00OO00OO00000 ):os .remove (O00O00OO00OO00000 )#line:3097
            print ('连接服务器失败!')#line:3098
            return {'status':False ,'msg':'连接服务器失败!'}#line:3099
    def upload_file_by_path (OOO0OOOO0OOOO0O00 ,O0OOOOO0000000OOO ,OOO00OOOO0OO0O00O ):#line:3102
        try :#line:3103
            OOOO0OO000000O000 =OOO0OOOO0OOOO0O00 .connentFtp ()#line:3104
            O00OOO00OO0OO0O00 =OOO0OOOO0OOOO0O00 .get_config (None )[3 ]#line:3105
            OOOOOOO0OO00OO000 =public .dict_obj ()#line:3106
            if OOO00OOOO0OO0O00O [0 ]=="/":#line:3107
                OOO00OOOO0OO0O00O =OOO00OOOO0OO0O00O [1 :]#line:3108
            OOOOOOO0OO00OO000 .path =O00OOO00OO0OO0O00 #line:3109
            OOOOOOO0OO00OO000 .dirname =os .path .dirname (OOO00OOOO0OO0O00O )#line:3110
            OOO0OOOO0OOOO0O00 .createDir (OOOOOOO0OO00OO000 )#line:3111
            O00O000O000OO0000 =os .path .join (O00OOO00OO0OO0O00 ,os .path .dirname (OOO00OOOO0OO0O00O ))#line:3112
            print ("目标上传目录：{}".format (O00O000O000OO0000 ))#line:3113
            OOOO0OO000000O000 .cwd (O00O000O000OO0000 )#line:3114
            O00O00OO00O00O00O =1024 #line:3115
            O0O000O0OOOOO0000 =open (O0OOOOO0000000OOO ,'rb')#line:3116
            try :#line:3117
                OOOO0OO000000O000 .storbinary ('STOR %s'%O00O000O000OO0000 +'/'+os .path .basename (O0OOOOO0000000OOO ),O0O000O0OOOOO0000 ,O00O00OO00O00O00O )#line:3118
            except :#line:3119
                OOOO0OO000000O000 .storbinary ('STOR %s'%os .path .split (O0OOOOO0000000OOO )[1 ],O0O000O0OOOOO0000 ,O00O00OO00O00O00O )#line:3120
            O0O000O0OOOOO0000 .close ()#line:3121
            OOOO0OO000000O000 .quit ()#line:3122
            return True #line:3123
        except :#line:3124
            print (public .get_error_info ())#line:3125
            return False #line:3126
    def deleteFtp (O0OOO000OO0O00OOO ,OO0000O0OO00OO00O ,is_inc =False ):#line:3129
        OO00OOOO0O00OO000 =[]#line:3130
        if os .path .isfile (main ()._full_file ):#line:3131
            try :#line:3132
                OO00OOOO0O00OO000 =json .loads (public .readFile (main ()._full_file ))[0 ]#line:3133
            except :#line:3134
                OO00OOOO0O00OO000 =[]#line:3135
        try :#line:3136
            O00OOO0O00O0O0000 =O0OOO000OO0O00OOO .connentFtp ()#line:3137
            if is_inc :#line:3138
                try :#line:3139
                    O0OOOO0OO0OOO00OO =O00OOO0O00O0O0000 .nlst ()#line:3140
                    for OOO0OO0OO0O0OO00O in O0OOOO0OO0OOO00OO :#line:3149
                        if OOO0OO0OO0O0OO00O =='.'or OOO0OO0OO0O0OO00O =='..':continue #line:3150
                        if OOO0OO0OO0O0OO00O =='full_record.json':continue #line:3151
                        if OO00OOOO0O00OO000 and 'full_name'in OO00OOOO0O00OO000 and os .path .basename (OO00OOOO0O00OO000 ['full_name'])==OOO0OO0OO0O0OO00O :continue #line:3152
                        try :#line:3153
                            O00OOO0O00O0O0000 .rmd (OOO0OO0OO0O0OO00O )#line:3154
                        except :#line:3155
                            O00OOO0O00O0O0000 .delete (OOO0OO0OO0O0OO00O )#line:3156
                        print ('|-已从FTP存储空间清理过期备份文件{}'.format (OOO0OO0OO0O0OO00O ))#line:3157
                    return True #line:3158
                except Exception as OO0OOOOOO00OOO0OO :#line:3159
                    print (OO0OOOOOO00OOO0OO )#line:3160
                    return False #line:3161
            try :#line:3162
                O00OOO0O00O0O0000 .rmd (OO0000O0OO00OO00O )#line:3163
            except :#line:3164
                O00OOO0O00O0O0000 .delete (OO0000O0OO00OO00O )#line:3165
            print ('|-已从FTP存储空间清理过期备份文件{}'.format (OO0000O0OO00OO00O ))#line:3166
            return True #line:3167
        except Exception as OO0O00O0OO0000OO0 :#line:3168
            print (OO0O00O0OO0000OO0 )#line:3169
            return False #line:3170
    def remove_file (O0O000OOO00OO00OO ,O0O0OO0OO00O0000O ):#line:3173
        OO000O00O0OOOO0O0 =O0O000OOO00OO00OO .get_config (None )[3 ]#line:3174
        if O0O0OO0OO00O0000O .path [0 ]=="/":#line:3175
            O0O0OO0OO00O0000O .path =O0O0OO0OO00O0000O .path [1 :]#line:3176
        O0O000OOO00OO00OO .__OO00O00O0O00OOO0O =os .path .join (OO000O00O0OOOO0O0 ,O0O0OO0OO00O0000O .path )#line:3177
        if 'is_inc'not in O0O0OO0OO00O0000O and O0O000OOO00OO00OO .deleteFtp (O0O0OO0OO00O0000O .filename ):#line:3178
            return public .returnMsg (True ,'删除成功!')#line:3179
        if 'is_inc'in O0O0OO0OO00O0000O and O0O0OO0OO00O0000O .is_inc :#line:3180
            if O0O000OOO00OO00OO .deleteFtp (O0O0OO0OO00O0000O .filename ,True ):#line:3181
                return public .returnMsg (True ,'删除成功!')#line:3182
        return public .returnMsg (False ,'删除失败!')#line:3183
    def get_list (O0O00O000O0OO0000 ,get =None ):#line:3186
        try :#line:3187
            O0O00O000O0OO0000 .__OO00O00O0O00OOO0O =get .path #line:3188
            O0O0OOOO00O0OO00O =O0O00O000O0OO0000 .connentFtp ()#line:3189
            OO0O0000OO00O00OO =O0O0OOOO00O0OO00O .nlst ()#line:3190
            O0O0OOO00O00OO00O =[]#line:3192
            OO0000OO00000OOOO =[]#line:3193
            OOOO0O0OOOOOO0OOO =[]#line:3194
            for O00O00000OOOOOO0O in OO0O0000OO00O00OO :#line:3195
                if O00O00000OOOOOO0O =='.'or O00O00000OOOOOO0O =='..':continue #line:3196
                OOOOOO0O00O0000O0 =public .M ('backup').where ('name=?',(O00O00000OOOOOO0O ,)).field ('size,addtime').find ()#line:3197
                if not OOOOOO0O00O0000O0 :#line:3198
                    OOOOOO0O00O0000O0 ={}#line:3199
                    OOOOOO0O00O0000O0 ['addtime']='1970/01/01 00:00:01'#line:3200
                O000OOOOO0O0000OO ={}#line:3201
                O000OOOOO0O0000OO ['name']=O00O00000OOOOOO0O #line:3202
                O000OOOOO0O0000OO ['time']=int (time .mktime (time .strptime (OOOOOO0O00O0000O0 ['addtime'],'%Y/%m/%d %H:%M:%S')))#line:3203
                try :#line:3204
                    O000OOOOO0O0000OO ['size']=O0O0OOOO00O0OO00O .size (O00O00000OOOOOO0O )#line:3205
                    O000OOOOO0O0000OO ['dir']=False #line:3206
                    O000OOOOO0O0000OO ['download']=O0O00O000O0OO0000 .getFile (O00O00000OOOOOO0O )#line:3207
                    OO0000OO00000OOOO .append (O000OOOOO0O0000OO )#line:3208
                except :#line:3209
                    O000OOOOO0O0000OO ['size']=0 #line:3210
                    O000OOOOO0O0000OO ['dir']=True #line:3211
                    O000OOOOO0O0000OO ['download']=''#line:3212
                    O0O0OOO00O00OO00O .append (O000OOOOO0O0000OO )#line:3213
            OOOO0O0OOOOOO0OOO =O0O0OOO00O00OO00O +OO0000OO00000OOOO #line:3215
            O00OO0OO00O0000O0 ={}#line:3216
            O00OO0OO00O0000O0 ['path']=O0O00O000O0OO0000 .__OO00O00O0O00OOO0O #line:3217
            O00OO0OO00O0000O0 ['list']=OOOO0O0OOOOOO0OOO #line:3218
            return O00OO0OO00O0000O0 #line:3219
        except Exception as O00O0O0000O0O0OO0 :#line:3220
            return {'status':False ,'msg':str (O00O0O0000O0O0OO0 )}#line:3221
    def getFile (O0O00OO0O000OO0OO ,OOOO00OOOO00OOOO0 ):#line:3224
        try :#line:3225
            O0O0O0OO0OO0OOOO0 =O0O00OO0O000OO0OO .get_config ()#line:3226
            if O0O0O0OO0OO0OOOO0 [0 ].find (':')==-1 :O0O0O0OO0OO0OOOO0 [0 ]+=':21'#line:3227
            O0OOOOO000OOOO000 =O0O0O0OO0OO0OOOO0 [0 ].split (':')#line:3228
            if O0OOOOO000OOOO000 [1 ]=='':O0OOOOO000OOOO000 [1 ]='21'#line:3229
            OO0000O00OO0OO00O ='ftp://'+O0O0O0OO0OO0OOOO0 [1 ]+':'+O0O0O0OO0OO0OOOO0 [2 ]+'@'+O0OOOOO000OOOO000 [0 ]+':'+O0OOOOO000OOOO000 [1 ]+(O0O00OO0O000OO0OO .__OO00O00O0O00OOO0O +'/'+OOOO00OOOO00OOOO0 ).replace ('//','/')#line:3230
        except :#line:3231
            OO0000O00OO0OO00O =None #line:3232
        return OO0000O00OO0OO00O #line:3233
    def download_file (OOO00O0O0OO0O0O00 ,OOO0OOO0OOO0O0O00 ):#line:3236
        return OOO00O0O0OO0O0O00 .getFile (OOO0OOO0OOO0O0O00 )#line:3237
class qiniu_main :#line:3241
    __O0O0OO0000O0OOOO0 =None #line:3242
    __OO0000OOO0O0O00OO =None #line:3243
    __OOOO0OO0OO0OOO0O0 =None #line:3244
    __OO0000OO0O000O000 =None #line:3245
    __O0O00OO00O0OO0OO0 ="ERROR: 无法连接到七牛云OSS服务器，请检查[AccessKeyId/AccessKeySecret]设置是否正确!"#line:3246
    def __init__ (OO0OOOO0OOOOOO000 ):#line:3248
        OO0OOOO0OOOOOO000 .__O0000O00O0O000O0O ()#line:3249
    def __O0000O00O0O000O0O (OOO000OOO0O00O0O0 ):#line:3251
        if OOO000OOO0O00O0O0 .__O0O0OO0000O0OOOO0 :return #line:3252
        OO00OO0OOOOO0O000 =OOO000OOO0O00O0O0 .get_config ()#line:3254
        OOO000OOO0O00O0O0 .__OO0000OOO0O0O00OO =OO00OO0OOOOO0O000 [2 ]#line:3256
        if OO00OO0OOOOO0O000 [3 ].find (OO00OO0OOOOO0O000 [2 ])!=-1 :OO00OO0OOOOO0O000 [3 ]=OO00OO0OOOOO0O000 [3 ].replace (OO00OO0OOOOO0O000 [2 ]+'.','')#line:3257
        OOO000OOO0O00O0O0 .__OOOO0OO0OO0OOO0O0 =OO00OO0OOOOO0O000 [3 ]#line:3258
        OOO000OOO0O00O0O0 .__OO0000OO0O000O000 =main ().get_path (OO00OO0OOOOO0O000 [4 ]+'/bt_backup/')#line:3259
        if OOO000OOO0O00O0O0 .__OO0000OO0O000O000 [:1 ]=='/':OOO000OOO0O00O0O0 .__OO0000OO0O000O000 =OOO000OOO0O00O0O0 .__OO0000OO0O000O000 [1 :]#line:3260
        try :#line:3262
            OOO000OOO0O00O0O0 .__O0O0OO0000O0OOOO0 =Auth (OO00OO0OOOOO0O000 [0 ],OO00OO0OOOOO0O000 [1 ])#line:3264
        except Exception as O0O0OO0OOOOOO00OO :#line:3265
            pass #line:3266
    def get_config (O0000O0000O00OOOO ,get =None ):#line:3269
        OOO0OOO00000OOO00 =main ()._config_path +'/qiniu.conf'#line:3270
        if not os .path .isfile (OOO0OOO00000OOO00 ):#line:3272
            OO0OO0O0OO00OOO0O =''#line:3273
            if os .path .isfile (main ()._plugin_path +'/qiniu/config.conf'):#line:3274
                OO0OO0O0OO00OOO0O =main ()._plugin_path +'/qiniu/config.conf'#line:3275
            elif os .path .isfile (main ()._setup_path +'/data/qiniuAS.conf'):#line:3276
                OO0OO0O0OO00OOO0O =main ()._plugin_path +'/data/qiniuAS.conf'#line:3277
            if OO0OO0O0OO00OOO0O :#line:3278
                O0000OO00000O0OO0 =json .loads (public .readFile (OO0OO0O0OO00OOO0O ))#line:3279
                OOOO0OO000O000O0O =O0000OO00000O0OO0 ['access_key_id']+'|'+O0000OO00000O0OO0 ['access_key_secret']+'|'+O0000OO00000O0OO0 ['bucket_name']+'|'+O0000OO00000O0OO0 ['bucket_domain']+'|'+O0000OO00000O0OO0 ['backup_path']#line:3280
                public .writeFile (OOO0OOO00000OOO00 ,OOOO0OO000O000O0O )#line:3281
        if not os .path .isfile (OOO0OOO00000OOO00 ):return ['','','','','/']#line:3282
        OOOOOOO00OO00O0OO =public .readFile (OOO0OOO00000OOO00 )#line:3283
        if not OOOOOOO00OO00O0OO :return ['','','','','/']#line:3284
        OOO000OOO00O0OOOO =OOOOOOO00OO00O0OO .split ('|')#line:3285
        if len (OOO000OOO00O0OOOO )<5 :OOO000OOO00O0OOOO .append ('/')#line:3286
        return OOO000OOO00O0OOOO #line:3287
    def set_config (OO00O00000000OOO0 ,OO000OOOO0OO0O00O ):#line:3289
        O0OO000O0O0O0OOO0 =['qiniu','txcos','alioss','bos','ftp','obs']#line:3290
        OO0OO00O00OOOO00O =OO000OOOO0OO0O00O .get ('cloud_name/d',0 )#line:3291
        print (OO0OO00O00OOOO00O )#line:3292
        if OO0OO00O00OOOO00O not in O0OO000O0O0O0OOO0 :return public .returnMsg (False ,'参数不合法！')#line:3293
        O0000O0OO0OOO0OOO =main ()._config_path +'/{}.conf'.format (OO0OO00O00OOOO00O )#line:3294
        O00OOO0000O000OO0 =OO000OOOO0OO0O00O .access_key .strip ()+'|'+OO000OOOO0OO0O00O .secret_key .strip ()+'|'+OO000OOOO0OO0O00O .bucket_name .strip ()+'|'+OO000OOOO0OO0O00O .bucket_domain .strip ()+'|'+OO000OOOO0OO0O00O .bucket_path .strip ()#line:3296
        return public .returnMsg (True ,'设置成功!')#line:3298
    def check_config (OO0O0O00O0O0OOO0O ):#line:3301
        try :#line:3302
            O00000OO00OOOOOOO =''#line:3303
            OOO00000OO0OO0O0O =OO0O0O00O0O0OOO0O .get_bucket ()#line:3304
            O0OO00O00O00000O0 ='/'#line:3305
            OOO000OOOO0OOO0O0 =None #line:3306
            O00000O000OOO0000 =1000 #line:3307
            O00000OO00OOOOOOO =main ().get_path (O00000OO00OOOOOOO )#line:3308
            OOO00OOOOO00O0OOO ,OO0OOO00O00O00OOO ,OOO0OO000OOOO0O00 =OOO00000OO0OO0O0O .list (OO0O0O00O0O0OOO0O .__OO0000OOO0O0O00OO ,O00000OO00OOOOOOO ,OOO000OOOO0OOO0O0 ,O00000O000OOO0000 ,O0OO00O00O00000O0 )#line:3309
            if OOO00OOOOO00O0OOO :#line:3310
                return True #line:3311
            else :#line:3312
                return False #line:3313
        except :#line:3314
            return False #line:3315
    def get_bucket (OOOO0OOOOOO0OOOOO ):#line:3317
        ""#line:3318
        from qiniu import BucketManager #line:3320
        OO0OO0OOOO00OOOO0 =BucketManager (OOOO0OOOOOO0OOOOO .__O0O0OO0000O0OOOO0 )#line:3321
        return OO0OO0OOOO00OOOO0 #line:3322
    def create_dir (OO0O0OOOOO0OO0O00 ,O00OO000O0O0OO0OO ):#line:3324
        ""#line:3329
        try :#line:3331
            O00OO000O0O0OO0OO =main ().get_path (O00OO000O0O0OO0OO )#line:3332
            O0OOOOOOO0O00OOO0 ='/tmp/dirname.pl'#line:3333
            public .writeFile (O0OOOOOOO0O00OOO0 ,'')#line:3334
            OOOOO00O0O0000OO0 =OO0O0OOOOO0OO0O00 .__O0O0OO0000O0OOOO0 .upload_token (OO0O0OOOOO0OO0O00 .__OO0000OOO0O0O00OO ,O00OO000O0O0OO0OO )#line:3335
            OOO00OOO00OO0OO00 ,O000OOO0OO00OOOO0 =put_file (OOOOO00O0O0000OO0 ,O00OO000O0O0OO0OO ,O0OOOOOOO0O00OOO0 )#line:3336
            try :#line:3338
                os .remove (O0OOOOOOO0O00OOO0 )#line:3339
            except :#line:3340
                pass #line:3341
            if O000OOO0OO00OOOO0 .status_code ==200 :#line:3343
                return True #line:3344
            return False #line:3345
        except Exception as OO000OO0000OO0O00 :#line:3346
            raise RuntimeError ("创建目录出现错误:"+str (OO000OO0000OO0O00 ))#line:3347
    def get_list (O0OOO0O0O00O00OOO ,get =None ):#line:3349
        O0O0O0O0OOO0OO0O0 =O0OOO0O0O00O00OOO .get_bucket ()#line:3350
        O000OO00OO0O00O00 ='/'#line:3351
        O00OOO0O00OO0OO0O =None #line:3352
        O0000OO00O0OOOO0O =1000 #line:3353
        OO0000OOO0OO00O00 =main ().get_path (get .path )#line:3354
        O00OO0000OOOOOO00 ,OO00OOO0OO00OOO0O ,O0OO00OOOO0OO00OO =O0O0O0O0OOO0OO0O0 .list (O0OOO0O0O00O00OOO .__OO0000OOO0O0O00OO ,OO0000OOO0OO00O00 ,O00OOO0O00OO0OO0O ,O0000OO00O0OOOO0O ,O000OO00OO0O00O00 )#line:3355
        OOO0000OO0OO000O0 =[]#line:3356
        if O00OO0000OOOOOO00 :#line:3357
            O0OOO000OO0OO0OO0 =O00OO0000OOOOOO00 .get ("commonPrefixes")#line:3358
            if O0OOO000OO0OO0OO0 :#line:3359
                for OO0OOO0000O00OOOO in O0OOO000OO0OO0OO0 :#line:3360
                    O0O00O00O0O0OO0OO ={}#line:3361
                    OOOO000O0OOO0O0OO =OO0OOO0000O00OOOO .replace (OO0000OOO0OO00O00 ,'')#line:3362
                    O0O00O00O0O0OO0OO ['name']=OOOO000O0OOO0O0OO #line:3363
                    O0O00O00O0O0OO0OO ['type']=None #line:3364
                    OOO0000OO0OO000O0 .append (O0O00O00O0O0OO0OO )#line:3365
            O0OO0O00000O0OO00 =O00OO0000OOOOOO00 ['items']#line:3367
            for O00O000O000OOOOOO in O0OO0O00000O0OO00 :#line:3368
                O0O00O00O0O0OO0OO ={}#line:3369
                OOOO000O0OOO0O0OO =O00O000O000OOOOOO .get ("key")#line:3370
                OOOO000O0OOO0O0OO =OOOO000O0OOO0O0OO .replace (OO0000OOO0OO00O00 ,'')#line:3371
                if not OOOO000O0OOO0O0OO :#line:3372
                    continue #line:3373
                O0O00O00O0O0OO0OO ['name']=OOOO000O0OOO0O0OO #line:3374
                O0O00O00O0O0OO0OO ['size']=O00O000O000OOOOOO .get ("fsize")#line:3375
                O0O00O00O0O0OO0OO ['type']=O00O000O000OOOOOO .get ("type")#line:3376
                O0O00O00O0O0OO0OO ['time']=O00O000O000OOOOOO .get ("putTime")#line:3377
                O0O00O00O0O0OO0OO ['download']=O0OOO0O0O00O00OOO .generate_download_url (OO0000OOO0OO00O00 +OOOO000O0OOO0O0OO )#line:3378
                OOO0000OO0OO000O0 .append (O0O00O00O0O0OO0OO )#line:3379
        else :#line:3380
            if hasattr (O0OO00OOOO0OO00OO ,"error"):#line:3381
                raise RuntimeError (O0OO00OOOO0OO00OO .error )#line:3382
        OO0O0O0O0OOO0OO0O ={'path':OO0000OOO0OO00O00 ,'list':OOO0000OO0OO000O0 }#line:3383
        return OO0O0O0O0OOO0OO0O #line:3384
    def generate_download_url (O0O00O000O0OOO0OO ,OO00OOO0OO00OOOOO ,expires =60 *60 ):#line:3386
        ""#line:3387
        O0O000OOOO0O000O0 =O0O00O000O0OOO0OO .__OOOO0OO0OO0OOO0O0 #line:3388
        OOOOO0OO0OO0O0OOO ='http://%s/%s'%(O0O000OOOO0O000O0 ,OO00OOO0OO00OOOOO )#line:3389
        OO0OO0OO0O00O0OOO =O0O00O000O0OOO0OO .__O0O0OO0000O0OOOO0 .private_download_url (OOOOO0OO0OO0O0OOO ,expires =expires )#line:3390
        return OO0OO0OO0O00O0OOO #line:3391
    def resumable_upload (OOOOO0O0O0OOO0000 ,OOOOOO00O0O0OOOOO ,OOOOO0000OO0OO00O ,object_name =None ,progress_callback =None ,progress_file_name =None ,retries =5 ):#line:3393
        ""#line:3402
        try :#line:3404
            OOOO00O0OOO0O00OO =60 *60 #line:3405
            if object_name is None :#line:3407
                OOO0OO0OO0O000O00 ,OOO0O00O000OO0O00 =os .path .split (OOOOOO00O0O0OOOOO )#line:3408
                OOOOO0O0O0OOO0000 .__OO0000OO0O000O000 =main ().get_path (os .path .dirname (OOOOO0000OO0OO00O ))#line:3409
                OOO0O00O000OO0O00 =OOOOO0O0O0OOO0000 .__OO0000OO0O000O000 +'/'+OOO0O00O000OO0O00 #line:3410
                OOO0O00O000OO0O00 =OOO0O00O000OO0O00 .replace ('//','/')#line:3411
                object_name =OOO0O00O000OO0O00 #line:3412
            OOO0OO000O0OOOO00 =OOOOO0O0O0OOO0000 .__O0O0OO0000O0OOOO0 .upload_token (OOOOO0O0O0OOO0000 .__OO0000OOO0O0O00OO ,object_name ,OOOO00O0OOO0O00OO )#line:3413
            if object_name [:1 ]=="/":#line:3415
                object_name =object_name [1 :]#line:3416
            print ("|-正在上传{}到七牛云存储".format (object_name ),end ='')#line:3418
            O00OOO0O0O00O0OO0 ,O000O00OOOO000O0O =put_file (OOO0OO000O0OOOO00 ,object_name ,OOOOOO00O0O0OOOOO ,check_crc =True ,progress_handler =progress_callback ,bucket_name =OOOOO0O0O0OOO0000 .__OO0000OOO0O0O00OO ,part_size =1024 *1024 *4 ,version ="v2")#line:3426
            OOO0O00O0OO0O000O =False #line:3427
            if sys .version_info [0 ]==2 :#line:3428
                OOO0O00O0OO0O000O =O00OOO0O0O00O0OO0 ['key'].encode ('utf-8')==object_name #line:3429
            elif sys .version_info [0 ]==3 :#line:3430
                OOO0O00O0OO0O000O =O00OOO0O0O00O0OO0 ['key']==object_name #line:3431
            if OOO0O00O0OO0O000O :#line:3432
                print (' ==> 成功')#line:3433
                return O00OOO0O0O00O0OO0 ['hash']==etag (OOOOOO00O0O0OOOOO )#line:3434
            return False #line:3435
        except Exception as O0000O0O0O00OOO0O :#line:3436
            print ("文件上传出现错误：",str (O0000O0O0O00OOO0O ))#line:3437
        if retries >0 :#line:3440
            print ("重试上传文件....")#line:3441
            return OOOOO0O0O0OOO0000 .resumable_upload (OOOOOO00O0O0OOOOO ,OOOOO0000OO0OO00O ,object_name =object_name ,progress_callback =progress_callback ,progress_file_name =progress_file_name ,retries =retries -1 ,)#line:3449
        return False #line:3450
    def upload_file_by_path (OOOO0OOO0O00OOO0O ,OO000O00O00O0O0O0 ,OO0O00000OO0000O0 ):#line:3453
        return OOOO0OOO0O00OOO0O .resumable_upload (OO000O00O00O0O0O0 ,OO0O00000OO0000O0 )#line:3454
    def delete_object_by_os (O0000O00OO00O0O00 ,OO0O0OOO000O00OO0 ):#line:3456
        ""#line:3457
        O000OO000O0OO0000 =O0000O00OO00O0O00 .get_bucket ()#line:3459
        OO0OO00O00OOO0OOO ,OO0O0O00OO000OOOO =O000OO000O0OO0000 .delete (O0000O00OO00O0O00 .__OO0000OOO0O0O00OO ,OO0O0OOO000O00OO0 )#line:3460
        return OO0OO00O00OOO0OOO =={}#line:3461
    def get_object_info (OO0O0OO00OOO0000O ,O00OO000O0OO0O0O0 ):#line:3463
        ""#line:3464
        try :#line:3465
            OO000OO00O00OO0O0 =OO0O0OO00OOO0000O .get_bucket ()#line:3466
            O0000O0O0OO00OOOO =OO000OO00O00OO0O0 .stat (OO0O0OO00OOO0000O .__OO0000OOO0O0O00OO ,O00OO000O0OO0O0O0 )#line:3467
            return O0000O0O0OO00OOOO [0 ]#line:3468
        except :#line:3469
            return None #line:3470
    def remove_file (OOOOO00OOO0OO0O0O ,OO0O000O00O00O0OO ):#line:3474
        try :#line:3475
            O0OO000OO00O00OOO =OO0O000O00O00O0OO .filename #line:3476
            O0000OOO00O00OOOO =OO0O000O00O00O0OO .path #line:3477
            if O0000OOO00O00OOOO [-1 ]!="/":#line:3479
                O0000O000OOOO0OOO =O0000OOO00O00OOOO +"/"+O0OO000OO00O00OOO #line:3480
            else :#line:3481
                O0000O000OOOO0OOO =O0000OOO00O00OOOO +O0OO000OO00O00OOO #line:3482
            if O0000O000OOOO0OOO [-1 ]=="/":#line:3484
                return public .returnMsg (False ,"暂时不支持目录删除！")#line:3485
            if O0000O000OOOO0OOO [:1 ]=="/":#line:3487
                O0000O000OOOO0OOO =O0000O000OOOO0OOO [1 :]#line:3488
            if OOOOO00OOO0OO0O0O .delete_object_by_os (O0000O000OOOO0OOO ):#line:3490
                return public .returnMsg (True ,'删除成功')#line:3491
            return public .returnMsg (False ,'文件{}删除失败, path:{}'.format (O0000O000OOOO0OOO ,OO0O000O00O00O0OO .path ))#line:3492
        except :#line:3493
            print (OOOOO00OOO0OO0O0O .__O0O00OO00O0OO0OO0 )#line:3494
            return False #line:3495
class aws_main :#line:3499
    pass #line:3500
class upyun_main :#line:3502
    pass #line:3503
class obs_main :#line:3505
    __O0O00O000O00O0O00 =None #line:3506
    __O00OOO0O000000O00 =None #line:3507
    __O0O0O00O00O00000O =0 #line:3508
    __OOOOO000000000O00 =None #line:3509
    __O00O00O0O0OO0OO00 =None #line:3510
    __O00O0O000O00O000O =None #line:3511
    __OO0OOO00O000O00OO =None #line:3512
    __O00000OO000OOO00O ="ERROR: 无法连接华为云OBS !"#line:3513
    def __init__ (OO0OOOOO0000000O0 ):#line:3516
        OO0OOOOO0000000O0 .__OO0OO0OO0OO00O0O0 ()#line:3517
    def __OO0OO0OO0OO00O0O0 (OO0OO0OO00OO0O000 ):#line:3519
        ""#line:3522
        if OO0OO0OO00OO0O000 .__O0O00O000O00O0O00 :return #line:3523
        O0000O0OO00O0O00O =OO0OO0OO00OO0O000 .get_config ()#line:3525
        OO0OO0OO00OO0O000 .__OOOOO000000000O00 =O0000O0OO00O0O00O [0 ]#line:3526
        OO0OO0OO00OO0O000 .__O00O00O0O0OO0OO00 =O0000O0OO00O0O00O [1 ]#line:3527
        OO0OO0OO00OO0O000 .__O00O0O000O00O000O =O0000O0OO00O0O00O [2 ]#line:3528
        OO0OO0OO00OO0O000 .__OO0OOO00O000O00OO =O0000O0OO00O0O00O [3 ]#line:3529
        OO0OO0OO00OO0O000 .__O00OOO0O000000O00 =main ().get_path (O0000O0OO00O0O00O [4 ])#line:3530
        try :#line:3531
            OO0OO0OO00OO0O000 .__O0O00O000O00O0O00 =ObsClient (access_key_id =OO0OO0OO00OO0O000 .__OOOOO000000000O00 ,secret_access_key =OO0OO0OO00OO0O000 .__O00O00O0O0OO0OO00 ,server =OO0OO0OO00OO0O000 .__OO0OOO00O000O00OO ,)#line:3537
        except Exception as O00O0O0O000O0O00O :#line:3538
            pass #line:3539
    def get_config (OO0000O0O00000OO0 ,get =None ):#line:3543
        ""#line:3546
        OOOOO0O0OOOO0O00O =main ()._config_path +'/obs.conf'#line:3547
        if not os .path .isfile (OOOOO0O0OOOO0O00O ):#line:3549
            O0O0OOO00O00O0OO0 =''#line:3550
            if os .path .isfile (main ()._plugin_path +'/obs/config.conf'):#line:3551
                O0O0OOO00O00O0OO0 =main ()._plugin_path +'/obs/config.conf'#line:3552
            elif os .path .isfile (main ()._setup_path +'/data/obsAS.conf'):#line:3553
                O0O0OOO00O00O0OO0 =main ()._plugin_path +'/data/obsAS.conf'#line:3554
            if O0O0OOO00O00O0OO0 :#line:3555
                O0OO00O0O0000O000 =json .loads (public .readFile (O0O0OOO00O00O0OO0 ))#line:3556
                O000000OO0O0O00OO =O0OO00O0O0000O000 ['access_key']+'|'+O0OO00O0O0000O000 ['secret_key']+'|'+O0OO00O0O0000O000 ['bucket_name']+'|'+O0OO00O0O0000O000 ['bucket_domain']+'|'+O0OO00O0O0000O000 ['backup_path']#line:3557
                public .writeFile (OOOOO0O0OOOO0O00O ,O000000OO0O0O00OO )#line:3558
        if not os .path .isfile (OOOOO0O0OOOO0O00O ):return ['','','','','/']#line:3559
        OOO0O0OO000O0OO0O =public .readFile (OOOOO0O0OOOO0O00O )#line:3560
        if not OOO0O0OO000O0OO0O :return ['','','','','/']#line:3561
        OOOOO00O0OO0O0O0O =OOO0O0OO000O0OO0O .split ('|')#line:3562
        if len (OOOOO00O0OO0O0O0O )<5 :OOOOO00O0OO0O0O0O .append ('/')#line:3563
        return OOOOO00O0OO0O0O0O #line:3564
    def check_config (OO0O0OO0O0O0OO000 ):#line:3567
        try :#line:3568
            OO0000OOOO00OO0OO =[]#line:3569
            O0OO0O0OO00O0000O =main ().get_path ('/')#line:3570
            OO0OOOO0O0OO00OOO =OO0O0OO0O0O0OO000 .__O0O00O000O00O0O00 .listObjects (OO0O0OO0O0O0OO000 .__O00O0O000O00O000O ,prefix =O0OO0O0OO00O0000O ,)#line:3574
            for O0O000OOO00O000OO in OO0OOOO0O0OO00OOO .body .contents :#line:3576
                if O0O000OOO00O000OO .size !=0 :#line:3577
                    if not O0O000OOO00O000OO .key :continue ;#line:3578
                    O0O0OOOOOO0O0O000 ={}#line:3579
                    OOO0O0O0O00O0OO0O =O0O000OOO00O000OO .key #line:3580
                    OOO0O0O0O00O0OO0O =OOO0O0O0O00O0OO0O [OOO0O0O0O00O0OO0O .find (O0OO0O0OO00O0000O )+len (O0OO0O0OO00O0000O ):]#line:3581
                    OOO00O0O0OO00OOOO =O0O000OOO00O000OO .key .split ('/')#line:3582
                    if len (OOO00O0O0OO00OOOO )>1000000 :continue ;#line:3583
                    O00OO0000O0OO00OO =re .compile (r'/')#line:3584
                    if O00OO0000O0OO00OO .search (OOO0O0O0O00O0OO0O )!=None :continue ;#line:3585
                    O0O0OOOOOO0O0O000 ["type"]=True #line:3586
                    O0O0OOOOOO0O0O000 ["name"]=OOO0O0O0O00O0OO0O #line:3587
                    O0O0OOOOOO0O0O000 ['size']=O0O000OOO00O000OO .size #line:3588
                    OO00OO0OOOOOOOOOO =O0O000OOO00O000OO .lastModified #line:3589
                    OO00OO00000OOO0OO =datetime .datetime .strptime (OO00OO0OOOOOOOOOO ,"%Y/%m/%d %H:%M:%S")#line:3590
                    OO00OO00000OOO0OO +=datetime .timedelta (hours =0 )#line:3591
                    O0O00OO0O0OO0OO0O =int ((time .mktime (OO00OO00000OOO0OO .timetuple ())+OO00OO00000OOO0OO .microsecond /1000000.0 ))#line:3592
                    O0O0OOOOOO0O0O000 ['time']=O0O00OO0O0OO0OO0O #line:3593
                    OO0000OOOO00OO0OO .append (O0O0OOOOOO0O0O000 )#line:3594
                elif O0O000OOO00O000OO .size ==0 :#line:3595
                    if not O0O000OOO00O000OO .key :continue ;#line:3596
                    if O0O000OOO00O000OO .key [-1 ]!="/":continue ;#line:3597
                    OOO00O0O0OO00OOOO =O0O000OOO00O000OO .key .split ('/')#line:3598
                    O0O0OOOOOO0O0O000 ={}#line:3599
                    OOO0O0O0O00O0OO0O =O0O000OOO00O000OO .key #line:3600
                    OOO0O0O0O00O0OO0O =OOO0O0O0O00O0OO0O [OOO0O0O0O00O0OO0O .find (O0OO0O0OO00O0000O )+len (O0OO0O0OO00O0000O ):]#line:3601
                    if O0OO0O0OO00O0000O ==""and len (OOO00O0O0OO00OOOO )>2 :continue ;#line:3602
                    if O0OO0O0OO00O0000O !="":#line:3603
                        OOO00O0O0OO00OOOO =OOO0O0O0O00O0OO0O .split ('/')#line:3604
                        if len (OOO00O0O0OO00OOOO )>2 :continue ;#line:3605
                        else :#line:3606
                            OOO0O0O0O00O0OO0O =OOO0O0O0O00O0OO0O #line:3607
                    if not OOO0O0O0O00O0OO0O :continue ;#line:3608
                    O0O0OOOOOO0O0O000 ["type"]=None #line:3609
                    O0O0OOOOOO0O0O000 ["name"]=OOO0O0O0O00O0OO0O #line:3610
                    O0O0OOOOOO0O0O000 ['size']=O0O000OOO00O000OO .size #line:3611
                    OO0000OOOO00OO0OO .append (O0O0OOOOOO0O0O000 )#line:3612
            return True #line:3613
        except :#line:3614
            return False #line:3615
    def upload_file_by_path (OOOOOO00O0O00OO00 ,O000OO0O00OOOO00O ,O0000000OOOO000OO ):#line:3617
        ""#line:3622
        OOOOOO00O0O00OO00 .__OO0OO0OO0OO00O0O0 ()#line:3624
        if not OOOOOO00O0O00OO00 .__O0O00O000O00O0O00 :#line:3625
            return False #line:3626
        if O0000000OOOO000OO !=None :#line:3628
            OOO0000000O00OOOO =OOOOOO00O0O00OO00 .__O0O00O000O00O0O00 .listObjects (OOOOOO00O0O00OO00 .__O00O0O000O00O000O ,prefix ="",)#line:3632
            O0OOOO0O0O0O00000 =O0000000OOOO000OO .split ("/")#line:3633
            OOO00OO00OO0O00OO =""#line:3634
            O000O0O0000O00OOO =[]#line:3635
            for OO0O00O0OOOO00O00 in OOO0000000O00OOOO .body .contents :#line:3636
                    if not OO0O00O0OOOO00O00 .key :continue #line:3637
                    O000O0O0000O00OOO .append (OO0O00O0OOOO00O00 .key )#line:3638
            for OOO00OOOO00O00OO0 in range (0 ,(len (O0OOOO0O0O0O00000 )-1 )):#line:3639
                if OOO00OO00OO0O00OO =="":#line:3640
                    OOO00OO00OO0O00OO =O0OOOO0O0O0O00000 [OOO00OOOO00O00OO0 ]+"/"#line:3641
                else :#line:3642
                    OOO00OO00OO0O00OO =OOO00OO00OO0O00OO +O0OOOO0O0O0O00000 [OOO00OOOO00O00OO0 ]+"/"#line:3643
                if not OOO00OO00OO0O00OO :continue #line:3644
                if main ().get_path (OOO00OO00OO0O00OO )not in O000O0O0000O00OOO :#line:3645
                    OOO0000000O00OOOO =OOOOOO00O0O00OO00 .__O0O00O000O00O0O00 .putContent (OOOOOO00O0O00OO00 .__O00O0O000O00O000O ,objectKey =main ().get_path (OOO00OO00OO0O00OO ),)#line:3649
        try :#line:3651
            print ('|-正在上传{}到华为云存储'.format (O000OO0O00OOOO00O ),end ='')#line:3652
            O000OO0000OOO00O0 ,OO0OOO00O000OOO0O =os .path .split (O000OO0O00OOOO00O )#line:3653
            OOOOOO00O0O00OO00 .__O00OOO0O000000O00 =main ().get_path (os .path .dirname (O0000000OOOO000OO ))#line:3654
            OO0OOO00O000OOO0O =OOOOOO00O0O00OO00 .__O00OOO0O000000O00 +OO0OOO00O000OOO0O #line:3655
            O0O00OOOO0O0OO000 =5 *1024 *1024 #line:3656
            O0O0O0OOO0OOO000O =O000OO0O00OOOO00O #line:3657
            O00OO000O00OO00OO =OO0OOO00O000OOO0O #line:3658
            O000O0000O0OOOO0O =True #line:3659
            OOO0000000O00OOOO =OOOOOO00O0O00OO00 .__O0O00O000O00O0O00 .uploadFile (OOOOOO00O0O00OO00 .__O00O0O000O00O000O ,O00OO000O00OO00OO ,O0O0O0OOO0OOO000O ,O0O00OOOO0O0OO000 ,O000O0000O0OOOO0O ,)#line:3666
            if OOO0000000O00OOOO .status <300 :#line:3667
                print (' ==> 成功')#line:3668
                return True #line:3669
        except Exception as OOOOOO000OOOOOO00 :#line:3670
            time .sleep (1 )#line:3672
            OOOOOO00O0O00OO00 .__O0O0O00O00O00000O +=1 #line:3673
            if OOOOOO00O0O00OO00 .__O0O0O00O00O00000O <2 :#line:3674
                OOOOOO00O0O00OO00 .upload_file_by_path (O000OO0O00OOOO00O ,O0000000OOOO000OO )#line:3676
            return False #line:3677
    def get_list (OOO0OO0OO0O0OO0OO ,get =None ):#line:3680
        ""#line:3683
        OOO0OO0OO0O0OO0OO .__OO0OO0OO0OO00O0O0 ()#line:3685
        if not OOO0OO0OO0O0OO0OO .__O0O00O000O00O0O00 :#line:3686
            return False #line:3687
        O00O00O00O0O00O00 =[]#line:3688
        OOOO00O00O000OO0O =main ().get_path (get .path )#line:3689
        O00OO0O0O0OOOO0O0 =OOO0OO0OO0O0OO0OO .__O0O00O000O00O0O00 .listObjects (OOO0OO0OO0O0OO0OO .__O00O0O000O00O000O ,prefix =OOOO00O00O000OO0O ,)#line:3693
        for O000OOO00O000O0OO in O00OO0O0O0OOOO0O0 .body .contents :#line:3695
            if O000OOO00O000O0OO .size !=0 :#line:3696
                if not O000OOO00O000O0OO .key :continue ;#line:3697
                O00OOOOO0OO00O0O0 ={}#line:3698
                OO000OOO00O00O0OO =O000OOO00O000O0OO .key #line:3699
                OO000OOO00O00O0OO =OO000OOO00O00O0OO [OO000OOO00O00O0OO .find (OOOO00O00O000OO0O )+len (OOOO00O00O000OO0O ):]#line:3700
                OOOOOOO000O0OO000 =O000OOO00O000O0OO .key .split ('/')#line:3701
                if len (OOOOOOO000O0OO000 )>1000000 :continue ;#line:3702
                OOOO000O00O000O00 =re .compile (r'/')#line:3703
                if OOOO000O00O000O00 .search (OO000OOO00O00O0OO )!=None :continue ;#line:3704
                O00OOOOO0OO00O0O0 ["type"]=True #line:3705
                O00OOOOO0OO00O0O0 ["name"]=OO000OOO00O00O0OO #line:3706
                O00OOOOO0OO00O0O0 ['size']=O000OOO00O000O0OO .size #line:3707
                O00OOOOO0OO00O0O0 ['download']=OOO0OO0OO0O0OO0OO .download_file (OOOO00O00O000OO0O +OO000OOO00O00O0OO )#line:3708
                OOO0O0000OO0OO0O0 =O000OOO00O000O0OO .lastModified #line:3709
                O0O0000000OOOO00O =datetime .datetime .strptime (OOO0O0000OO0OO0O0 ,"%Y/%m/%d %H:%M:%S")#line:3710
                O0O0000000OOOO00O +=datetime .timedelta (hours =0 )#line:3711
                O00OOO000OOOOOOO0 =int ((time .mktime (O0O0000000OOOO00O .timetuple ())+O0O0000000OOOO00O .microsecond /1000000.0 ))#line:3712
                O00OOOOO0OO00O0O0 ['time']=O00OOO000OOOOOOO0 #line:3713
                O00O00O00O0O00O00 .append (O00OOOOO0OO00O0O0 )#line:3714
            elif O000OOO00O000O0OO .size ==0 :#line:3715
                if not O000OOO00O000O0OO .key :continue ;#line:3716
                if O000OOO00O000O0OO .key [-1 ]!="/":continue ;#line:3717
                OOOOOOO000O0OO000 =O000OOO00O000O0OO .key .split ('/')#line:3718
                O00OOOOO0OO00O0O0 ={}#line:3719
                OO000OOO00O00O0OO =O000OOO00O000O0OO .key #line:3720
                OO000OOO00O00O0OO =OO000OOO00O00O0OO [OO000OOO00O00O0OO .find (OOOO00O00O000OO0O )+len (OOOO00O00O000OO0O ):]#line:3721
                if OOOO00O00O000OO0O ==""and len (OOOOOOO000O0OO000 )>2 :continue ;#line:3722
                if OOOO00O00O000OO0O !="":#line:3723
                    OOOOOOO000O0OO000 =OO000OOO00O00O0OO .split ('/')#line:3724
                    if len (OOOOOOO000O0OO000 )>2 :continue ;#line:3725
                    else :#line:3726
                        OO000OOO00O00O0OO =OO000OOO00O00O0OO #line:3727
                if not OO000OOO00O00O0OO :continue ;#line:3728
                O00OOOOO0OO00O0O0 ["type"]=None #line:3729
                O00OOOOO0OO00O0O0 ["name"]=OO000OOO00O00O0OO #line:3730
                O00OOOOO0OO00O0O0 ['size']=O000OOO00O000O0OO .size #line:3731
                O00O00O00O0O00O00 .append (O00OOOOO0OO00O0O0 )#line:3732
        OOO00O0O0O00OO00O ={'path':OOOO00O00O000OO0O ,'list':O00O00O00O0O00O00 }#line:3734
        return OOO00O0O0O00OO00O #line:3735
    def download_file (OO0O0O0O00OOO0000 ,O0O0O0OO0OO0O0O00 ):#line:3737
        ""#line:3740
        OO0O0O0O00OOO0000 .__OO0OO0OO0OO00O0O0 ()#line:3742
        if not OO0O0O0O00OOO0000 .__O0O00O000O00O0O00 :#line:3743
            return None #line:3744
        try :#line:3745
            O0OO0OO0OO0O0O000 =OO0O0O0O00OOO0000 .__O0O00O000O00O0O00 .createSignedUrl ('GET',OO0O0O0O00OOO0000 .__O00O0O000O00O000O ,O0O0O0OO0OO0O0O00 ,expires =3600 ,)#line:3750
            O000O0O0O00OO0O0O =O0OO0OO0OO0O0O000 .signedUrl #line:3751
            return O000O0O0O00OO0O0O #line:3752
        except :#line:3753
            print (OO0O0O0O00OOO0000 .__O00000OO000OOO00O )#line:3754
            return None #line:3755
    def delete_file (O0O0OOO00O0000O00 ,O0O0O0OO00OO0OOOO ):#line:3757
        ""#line:3761
        O0O0OOO00O0000O00 .__OO0OO0OO0OO00O0O0 ()#line:3763
        if not O0O0OOO00O0000O00 .__O0O00O000O00O0O00 :#line:3764
            return False #line:3765
        try :#line:3767
            O0OO00O00O0O00OO0 =O0O0OOO00O0000O00 .__O0O00O000O00O0O00 .deleteObject (O0O0OOO00O0000O00 .__O00O0O000O00O000O ,O0O0O0OO00OO0OOOO )#line:3768
            return O0OO00O00O0O00OO0 #line:3769
        except Exception as O0OOOO00OOO0O0OO0 :#line:3770
            O0O0OOO00O0000O00 .__O0O0O00O00O00000O +=1 #line:3771
            if O0O0OOO00O0000O00 .__O0O0O00O00O00000O <2 :#line:3772
                O0O0OOO00O0000O00 .delete_file (O0O0O0OO00OO0OOOO )#line:3774
            print (O0O0OOO00O0000O00 .__O00000OO000OOO00O )#line:3775
            return None #line:3776
    def remove_file (OO000O000OOOO0O00 ,OOO0O0O0O00O00000 ):#line:3779
        OO000O0OOOOOO00O0 =main ().get_path (OOO0O0O0O00O00000 .path )#line:3780
        O0OOOOO00OOOO0OOO =OO000O0OOOOOO00O0 +OOO0O0O0O00O00000 .filename #line:3781
        OO000O000OOOO0O00 .delete_file (O0OOOOO00OOOO0OOO )#line:3782
        return public .returnMsg (True ,'删除文件成功!')#line:3783
class bos_main :#line:3787
    __OO0OOOO00000OOO00 =None #line:3788
    __OOO00O0000OO0OO00 =0 #line:3789
    __OOO000000OO0000O0 =None #line:3790
    __OOO0O000000OOOOOO =None #line:3791
    __OOO0OO00O00000OO0 =None #line:3792
    __O0O0OOOOO0OO0OOO0 ="ERROR: 无法连接百度云存储 !"#line:3793
    def __init__ (O0O0000000OO0OOOO ):#line:3796
        O0O0000000OO0OOOO .__O00O00OO000O0O0OO ()#line:3797
    def __O00O00OO000O0O0OO (O000O00OO0O0O000O ):#line:3799
        ""#line:3802
        if O000O00OO0O0O000O .__OO0OOOO00000OOO00 :return #line:3803
        OO0O0OO00O0O00O0O =O000O00OO0O0O000O .get_config ()#line:3805
        O000O00OO0O0O000O .__OOO000000OO0000O0 =OO0O0OO00O0O00O0O [0 ]#line:3806
        O000O00OO0O0O000O .__OOO0O000000OOOOOO =OO0O0OO00O0O00O0O [1 ]#line:3807
        O000O00OO0O0O000O .__O0O00OOOOO00OOO00 =OO0O0OO00O0O00O0O [2 ]#line:3808
        O000O00OO0O0O000O .__OOO0OO00O00000OO0 =OO0O0OO00O0O00O0O [3 ]#line:3809
        O000O00OO0O0O000O .__O0OOO00O00OOO00OO =main ().get_path (OO0O0OO00O0O00O0O [4 ])#line:3811
        try :#line:3812
            OOO0O00OO00O0OOOO =BceClientConfiguration (credentials =BceCredentials (O000O00OO0O0O000O .__OOO000000OO0000O0 ,O000O00OO0O0O000O .__OOO0O000000OOOOOO ),endpoint =O000O00OO0O0O000O .__OOO0OO00O00000OO0 )#line:3815
            O000O00OO0O0O000O .__OO0OOOO00000OOO00 =BosClient (OOO0O00OO00O0OOOO )#line:3816
        except Exception as O0O00OOO0000O0O00 :#line:3817
            pass #line:3818
    def get_config (O0O00000OO0O000O0 ,get =None ):#line:3822
        ""#line:3825
        O0000O0OO0OO0O0OO =main ()._config_path +'/bos.conf'#line:3826
        if not os .path .isfile (O0000O0OO0OO0O0OO ):#line:3828
            O0OOOOO00000OO00O =''#line:3829
            if os .path .isfile (main ()._plugin_path +'/bos/config.conf'):#line:3830
                O0OOOOO00000OO00O =main ()._plugin_path +'/bos/config.conf'#line:3831
            elif os .path .isfile (main ()._setup_path +'/data/bosAS.conf'):#line:3832
                O0OOOOO00000OO00O =main ()._setup_path +'/data/bosAS.conf'#line:3833
            if O0OOOOO00000OO00O :#line:3834
                OOO0000O0OO0OO00O =json .loads (public .readFile (O0OOOOO00000OO00O ))#line:3835
                O0OO0O00O00O0O00O =OOO0000O0OO0OO00O ['access_key']+'|'+OOO0000O0OO0OO00O ['secret_key']+'|'+OOO0000O0OO0OO00O ['bucket_name']+'|'+OOO0000O0OO0OO00O ['bucket_domain']+'|'+OOO0000O0OO0OO00O ['backup_path']#line:3836
                public .writeFile (O0000O0OO0OO0O0OO ,O0OO0O00O00O0O00O )#line:3837
        if not os .path .isfile (O0000O0OO0OO0O0OO ):return ['','','','','/']#line:3838
        OO000OO0O0O0OO000 =public .readFile (O0000O0OO0OO0O0OO )#line:3839
        if not OO000OO0O0O0OO000 :return ['','','','','/']#line:3840
        OO00O0OOO0OO000OO =OO000OO0O0O0OO000 .split ('|')#line:3841
        if len (OO00O0OOO0OO000OO )<5 :OO00O0OOO0OO000OO .append ('/')#line:3842
        return OO00O0OOO0OO000OO #line:3843
    def check_config (OO000O000OOO00O0O ):#line:3845
        ""#line:3848
        if not OO000O000OOO00O0O .__OO0OOOO00000OOO00 :return False #line:3849
        try :#line:3850
            OO000O0000OO0OOO0 ='/'#line:3851
            O0000OOOOOO000O0O =OO000O000OOO00O0O .__OO0OOOO00000OOO00 .list_objects (OO000O000OOO00O0O .__O0O00OOOOO00OOO00 ,prefix =OO000O0000OO0OOO0 ,delimiter ="/")#line:3853
            return True #line:3854
        except :#line:3855
            return False #line:3856
    def resumable_upload (O00O00O00OO00OO00 ,OO0O000000OOO0O00 ,object_name =None ,progress_callback =None ,progress_file_name =None ,retries =5 ,):#line:3864
            ""#line:3871
            try :#line:3873
                if object_name [:1 ]=="/":#line:3874
                    object_name =object_name [1 :]#line:3875
                print ("|-正在上传{}到百度云存储".format (object_name ),end ='')#line:3876
                import multiprocessing #line:3877
                O0O00OO0O000O0000 =OO0O000000OOO0O00 #line:3878
                O0000O0O0000OOO00 =object_name #line:3879
                OOOO0O00OO0O00000 =O00O00O00OO00OO00 .__O0O00OOOOO00OOO00 #line:3880
                OOO0000O00OO0O0OO =O00O00O00OO00OO00 .__OO0OOOO00000OOO00 .put_super_obejct_from_file (OOOO0O00OO0O00000 ,O0000O0O0000OOO00 ,O0O00OO0O000O0000 ,chunk_size =5 ,thread_num =multiprocessing .cpu_count ()-1 )#line:3885
                if OOO0000O00OO0O0OO :#line:3886
                    print (' ==> 成功')#line:3887
                    return True #line:3888
            except Exception as O00OO0000O000O0O0 :#line:3889
                print ("文件上传出现错误：")#line:3890
                print (O00OO0000O000O0O0 )#line:3891
            if retries >0 :#line:3894
                print ("重试上传文件....")#line:3895
                return O00O00O00OO00OO00 .resumable_upload (OO0O000000OOO0O00 ,object_name =object_name ,progress_callback =progress_callback ,progress_file_name =progress_file_name ,retries =retries -1 ,)#line:3902
            return False #line:3903
    def upload_file_by_path (OO0O00000000O0OOO ,O0OO00O00O00O000O ,O000OO0000OO0OO0O ):#line:3905
        ""#line:3908
        return OO0O00000000O0OOO .resumable_upload (O0OO00O00O00O000O ,O000OO0000OO0OO0O )#line:3909
    def get_list (OOO0O0OOO0OOOO0OO ,get =None ):#line:3911
        OOOO0000OOOOOOOOO =[]#line:3912
        O000O0OO0OOO000OO =[]#line:3913
        O0OO0O00OO0O0O0O0 =main ().get_path (get .path )#line:3914
        try :#line:3915
            O0O00O0O0O00OO0OO =OOO0O0OOO0OOOO0OO .__OO0OOOO00000OOO00 .list_objects (OOO0O0OOO0OOOO0OO .__O0O00OOOOO00OOO00 ,prefix =O0OO0O00OO0O0O0O0 ,delimiter ="/")#line:3917
            for OO00OOO0OOO0OOO00 in O0O00O0O0O00OO0OO .contents :#line:3918
                if not OO00OOO0OOO0OOO00 .key :continue #line:3919
                O0OOO00OO00O0O00O ={}#line:3920
                OO00OOOOO0OOO0O0O =OO00OOO0OOO0OOO00 .key #line:3921
                OO00OOOOO0OOO0O0O =OO00OOOOO0OOO0O0O [OO00OOOOO0OOO0O0O .find (O0OO0O00OO0O0O0O0 )+len (O0OO0O00OO0O0O0O0 ):]#line:3922
                if not OO00OOOOO0OOO0O0O :continue #line:3923
                O0OOO00OO00O0O00O ["name"]=OO00OOOOO0OOO0O0O #line:3924
                O0OOO00OO00O0O00O ['size']=OO00OOO0OOO0OOO00 .size #line:3925
                O0OOO00OO00O0O00O ["type"]=True #line:3926
                O0OOO00OO00O0O00O ['download']=OOO0O0OOO0OOOO0OO .download_file (O0OO0O00OO0O0O0O0 +"/"+OO00OOOOO0OOO0O0O )#line:3927
                O0OO00OO0OO00OO00 =OO00OOO0OOO0OOO00 .last_modified #line:3928
                O0O0OOO0OO0000000 =datetime .datetime .strptime (O0OO00OO0OO00OO00 ,"%Y-%m-%dT%H:%M:%SZ")#line:3929
                O0O0OOO0OO0000000 +=datetime .timedelta (hours =8 )#line:3930
                OOOOO0O0O00OO00O0 =int ((time .mktime (O0O0OOO0OO0000000 .timetuple ())+O0O0OOO0OO0000000 .microsecond /1000000.0 ))#line:3931
                O0OOO00OO00O0O00O ['time']=OOOOO0O0O00OO00O0 #line:3932
                OOOO0000OOOOOOOOO .append (O0OOO00OO00O0O00O )#line:3933
            for O0OO0OOOOO0O0O0OO in O0O00O0O0O00OO0OO .common_prefixes :#line:3934
                if not O0OO0OOOOO0O0O0OO .prefix :continue #line:3935
                if O0OO0OOOOO0O0O0OO .prefix [0 :-1 ]==O0OO0O00OO0O0O0O0 :continue #line:3936
                O0OOO00OO00O0O00O ={}#line:3937
                O0OO0OOOOO0O0O0OO .prefix =O0OO0OOOOO0O0O0OO .prefix .replace (O0OO0O00OO0O0O0O0 ,'')#line:3938
                O0OOO00OO00O0O00O ["name"]=O0OO0OOOOO0O0O0OO .prefix #line:3939
                O0OOO00OO00O0O00O ["type"]=None #line:3940
                O0OOO00OO00O0O00O ['size']=O0OO0OOOOO0O0O0OO .size #line:3941
                OOOO0000OOOOOOOOO .append (O0OOO00OO00O0O00O )#line:3942
            OO0000OOO00O00000 ={'path':O0OO0O00OO0O0O0O0 ,'list':OOOO0000OOOOOOOOO }#line:3943
            return OO0000OOO00O00000 #line:3944
        except :#line:3945
            OO0000OOO00O00000 ={}#line:3946
            if OOO0O0OOO0OOOO0OO .__OO0OOOO00000OOO00 :#line:3947
                OO0000OOO00O00000 ['status']=True #line:3948
            else :#line:3949
                OO0000OOO00O00000 ['status']=False #line:3950
            OO0000OOO00O00000 ['path']=get .path #line:3951
            OO0000OOO00O00000 ['list']=OOOO0000OOOOOOOOO #line:3952
            OO0000OOO00O00000 ['dir']=O000O0OO0OOO000OO #line:3953
            return OO0000OOO00O00000 #line:3954
    def download_file (OO00O000O000O0OO0 ,O0OOO000OOO000000 ):#line:3956
        ""#line:3959
        OO00O000O000O0OO0 .__O00O00OO000O0O0OO ()#line:3961
        if not OO00O000O000O0OO0 .__OO0OOOO00000OOO00 :#line:3962
            return None #line:3963
        try :#line:3965
            OO00O00O0OOO0OOO0 =OO00O000O000O0OO0 .__OO0OOOO00000OOO00 .generate_pre_signed_url (OO00O000O000O0OO0 .__O0O00OOOOO00OOO00 ,O0OOO000OOO000000 )#line:3966
            _O0OO00O00OOOOO0O0 =sys .version_info #line:3967
            O00000000O00OO00O =(_O0OO00O00OOOOO0O0 [0 ]==2 )#line:3969
            O00OOOOOO0000O0O0 =(_O0OO00O00OOOOO0O0 [0 ]==3 )#line:3972
            if O00OOOOOO0000O0O0 :#line:3973
                OO00O00O0OOO0OOO0 =str (OO00O00O0OOO0OOO0 ,encoding ="utf-8")#line:3974
            else :#line:3975
                OO00O00O0OOO0OOO0 =OO00O00O0OOO0OOO0 #line:3976
            return OO00O00O0OOO0OOO0 #line:3977
        except :#line:3978
            print (OO00O000O000O0OO0 .__O0O0OOOOO0OO0OOO0 )#line:3979
            return None #line:3980
    def delete_file (OO000OOO0OOOO0OOO ,O0O00O000O0000O0O ):#line:3982
        ""#line:3986
        OO000OOO0OOOO0OOO .__O00O00OO000O0O0OO ()#line:3988
        if not OO000OOO0OOOO0OOO .__OO0OOOO00000OOO00 :#line:3989
            return False #line:3990
        try :#line:3992
            O000O0O00O0O00O00 =OO000OOO0OOOO0OOO .__OO0OOOO00000OOO00 .delete_object (OO000OOO0OOOO0OOO .__O0O00OOOOO00OOO00 ,O0O00O000O0000O0O )#line:3993
            return O000O0O00O0O00O00 #line:3994
        except Exception as O0OOOO00O000O0O0O :#line:3995
            OO000OOO0OOOO0OOO .__OOO00O0000OO0OO00 +=1 #line:3996
            if OO000OOO0OOOO0OOO .__OOO00O0000OO0OO00 <2 :#line:3997
                OO000OOO0OOOO0OOO .delete_file (O0O00O000O0000O0O )#line:3999
            print (OO000OOO0OOOO0OOO .__O0O0OOOOO0OO0OOO0 )#line:4000
            return None #line:4001
    def remove_file (OOOO00OO0O0OO00O0 ,O0OO00O000O0OO00O ):#line:4004
        O0OO0OOOO0OO0O0O0 =main ().get_path (O0OO00O000O0OO00O .path )#line:4005
        OOO0OO0OOO0O0OOOO =O0OO0OOOO0OO0O0O0 +O0OO00O000O0OO00O .filename #line:4006
        OOOO00OO0O0OO00O0 .delete_file (OOO0OO0OOO0O0OOOO )#line:4007
        return public .returnMsg (True ,'删除文件成功!')#line:4008
class gcloud_storage_main :#line:4011
    pass #line:4012
class gdrive_main :#line:4014
    pass #line:4015
class msonedrive_main :#line:4017
    pass #line:4018
if __name__ =='__main__':#line:4022
    import argparse #line:4023
    args_obj =argparse .ArgumentParser (usage ="必要的参数：--db_name 数据库名称!")#line:4024
    args_obj .add_argument ("--db_name",help ="数据库名称!")#line:4025
    args_obj .add_argument ("--binlog_id",help ="任务id")#line:4026
    args =args_obj .parse_args ()#line:4027
    if not args .db_name :#line:4028
        args_obj .print_help ()#line:4029
    p =main ()#line:4030
    p ._db_name =args .db_name #line:4031
    if args .binlog_id :p ._binlog_id =args .binlog_id #line:4032
    if p ._binlog_id :#line:4034
        p .execute_by_comandline ()#line:4035
