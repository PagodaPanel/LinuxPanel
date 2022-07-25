import os #line:14
import sys #line:15
import time #line:16
import psutil #line:17
os .chdir ("/www/server/panel")#line:19
sys .path .insert (0 ,"/www/server/panel")#line:20
sys .path .insert (0 ,"class/")#line:21
import public #line:23
from system import system #line:24
from panelPlugin import panelPlugin #line:25
from BTPanel import auth ,cache #line:26
class panelDaily :#line:28
    def check_databases (O000O0000000000OO ):#line:30
        ""#line:31
        O0O000000OO0OO0O0 =["app_usage","server_status","backup_status","daily"]#line:32
        import sqlite3 #line:33
        O00OOO0O0O0OO0OOO =sqlite3 .connect ("/www/server/panel/data/system.db")#line:34
        OO000OO0O0O00OO00 =O00OOO0O0O0OO0OOO .cursor ()#line:35
        O000OO0OO00OOOO00 =",".join (["'"+OO0O0O0OOOOOO000O +"'"for OO0O0O0OOOOOO000O in O0O000000OO0OO0O0 ])#line:36
        O00OOOOOOO0O00O00 =OO000OO0O0O00OO00 .execute ("SELECT name FROM sqlite_master WHERE type='table' and name in ({})".format (O000OO0OO00OOOO00 ))#line:37
        OOOO00OO000000OO0 =O00OOOOOOO0O00O00 .fetchall ()#line:38
        O0O0OOO0OO0O000O0 =False #line:41
        OO0O0000O000000OO =[]#line:42
        if OOOO00OO000000OO0 :#line:43
            OO0O0000O000000OO =[OOO0O0O0O0O0OO000 [0 ]for OOO0O0O0O0O0OO000 in OOOO00OO000000OO0 ]#line:44
        if "app_usage"not in OO0O0000O000000OO :#line:46
            OOOO00O0000OO00O0 ='''CREATE TABLE IF NOT EXISTS `app_usage` (
                    `time_key` INTEGER PRIMARY KEY,
                    `app` TEXT,
                    `disks` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:52
            OO000OO0O0O00OO00 .execute (OOOO00O0000OO00O0 )#line:53
            O0O0OOO0OO0O000O0 =True #line:54
        if "server_status"not in OO0O0000O000000OO :#line:56
            print ("创建server_status表:")#line:57
            OOOO00O0000OO00O0 ='''CREATE TABLE IF NOT EXISTS `server_status` (
                    `status` TEXT,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:61
            OO000OO0O0O00OO00 .execute (OOOO00O0000OO00O0 )#line:62
            O0O0OOO0OO0O000O0 =True #line:63
        if "backup_status"not in OO0O0000O000000OO :#line:65
            print ("创建备份状态表:")#line:66
            OOOO00O0000OO00O0 ='''CREATE TABLE IF NOT EXISTS `backup_status` (
                    `id` INTEGER,
                    `target` TEXT,
                    `status` INTEGER,
                    `msg` TEXT DEFAULT "",
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:73
            OO000OO0O0O00OO00 .execute (OOOO00O0000OO00O0 )#line:74
            O0O0OOO0OO0O000O0 =True #line:75
        if "daily"not in OO0O0000O000000OO :#line:77
            OOOO00O0000OO00O0 ='''CREATE TABLE IF NOT EXISTS `daily` (
                    `time_key` INTEGER,
                    `evaluate` INTEGER,
                    `addtime` DATETIME DEFAULT CURRENT_TIMESTAMP
                )'''#line:82
            OO000OO0O0O00OO00 .execute (OOOO00O0000OO00O0 )#line:83
            O0O0OOO0OO0O000O0 =True #line:84
        if O0O0OOO0OO0O000O0 :#line:86
            O00OOO0O0O0OO0OOO .commit ()#line:87
        OO000OO0O0O00OO00 .close ()#line:88
        O00OOO0O0O0OO0OOO .close ()#line:89
        return True #line:90
    def get_time_key (OO0OO0OO0OO00OOOO ,date =None ):#line:92
        if date is None :#line:93
            date =time .localtime ()#line:94
        O000O000OOO0OO00O =0 #line:95
        OOOO000O0O0OO0O00 ="%Y%m%d"#line:96
        if type (date )==time .struct_time :#line:97
            O000O000OOO0OO00O =int (time .strftime (OOOO000O0O0OO0O00 ,date ))#line:98
        if type (date )==str :#line:99
            O000O000OOO0OO00O =int (time .strptime (date ,OOOO000O0O0OO0O00 ))#line:100
        return O000O000OOO0OO00O #line:101
    def store_app_usage (OOO0O0O00OO000OOO ,time_key =None ):#line:103
        ""#line:111
        OOO0O0O00OO000OOO .check_databases ()#line:113
        if time_key is None :#line:115
            time_key =OOO0O0O00OO000OOO .get_time_key ()#line:116
        O00OOO0OOO000O0OO =public .M ("system").dbfile ("system").table ("app_usage")#line:118
        O000OOO0OOOOOO0OO =O00OOO0OOO000O0OO .field ("time_key").where ("time_key=?",(time_key )).find ()#line:119
        if O000OOO0OOOOOO0OO and "time_key"in O000OOO0OOOOOO0OO :#line:120
            if O000OOO0OOOOOO0OO ["time_key"]==time_key :#line:121
                return True #line:123
        O0OO00000OO00OO0O =public .M ('sites').field ('path').select ()#line:125
        O0000O0O00O0O0OOO =0 #line:126
        for OOO00O00OO0OO0OO0 in O0OO00000OO00OO0O :#line:127
            OO0O0OO000O00OO00 =OOO00O00OO0OO0OO0 ["path"]#line:128
            if OO0O0OO000O00OO00 :#line:129
                O0000O0O00O0O0OOO +=public .get_path_size (OO0O0OO000O00OO00 )#line:130
        OOO0OO00O0OO0O000 =public .get_path_size ("/www/server/data")#line:132
        O00OO00O00O000O0O =public .M ("ftps").field ("path").select ()#line:134
        OO0O000O000OO00OO =0 #line:135
        for OOO00O00OO0OO0OO0 in O00OO00O00O000O0O :#line:136
            O0OOO00OOO0O0OO00 =OOO00O00OO0OO0OO0 ["path"]#line:137
            if O0OOO00OOO0O0OO00 :#line:138
                OO0O000O000OO00OO +=public .get_path_size (O0OOO00OOO0O0OO00 )#line:139
        O0O0OO0OO0OO00O0O =public .get_path_size ("/www/server/panel/plugin")#line:141
        O0OO00O0O00O00O00 =["/www/server/total","/www/server/btwaf","/www/server/coll","/www/server/nginx","/www/server/apache","/www/server/redis"]#line:149
        for O0OO000OO0OOOO000 in O0OO00O0O00O00O00 :#line:150
            O0O0OO0OO0OO00O0O +=public .get_path_size (O0OO000OO0OOOO000 )#line:151
        O000OO00O0OOO0000 =system ().GetDiskInfo2 (human =False )#line:153
        O0O0OOOO0O0O0000O =""#line:154
        O0O000O00OO00OOO0 =0 #line:155
        OO0O000O00OOOO000 =0 #line:156
        for O00O0OOO0000000OO in O000OO00O0OOO0000 :#line:157
            OO000000O000OO00O =O00O0OOO0000000OO ["path"].replace ("-","_")#line:158
            if O0O0OOOO0O0O0000O :#line:159
                O0O0OOOO0O0O0000O +="-"#line:160
            O0O00OO00O0O000O0 ,O0O000O0OOO000000 ,O00O0O00OOOOOOO0O ,O000OO0000O000O00 =O00O0OOO0000000OO ["size"]#line:161
            O0000OO0000000O0O ,O0O0O00OO0OOOO000 ,_OO0O000O0O00O0OOO ,_OO0OOO0OO00OO00OO =O00O0OOO0000000OO ["inodes"]#line:162
            O0O0OOOO0O0O0000O ="{},{},{},{},{}".format (OO000000O000OO00O ,O0O000O0OOO000000 ,O0O00OO00O0O000O0 ,O0O0O00OO0OOOO000 ,O0000OO0000000O0O )#line:163
            if OO000000O000OO00O =="/":#line:164
                O0O000O00OO00OOO0 =O0O00OO00O0O000O0 #line:165
                OO0O000O00OOOO000 =O0O000O0OOO000000 #line:166
        OOOOOO0000O000O00 ="{},{},{},{},{},{}".format (O0O000O00OO00OOO0 ,OO0O000O00OOOO000 ,O0000O0O00O0O0OOO ,OOO0OO00O0OO0O000 ,OO0O000O000OO00OO ,O0O0OO0OO0OO00O0O )#line:171
        OO00O00OOOO0O0OO0 =public .M ("system").dbfile ("system").table ("app_usage").add ("time_key,app,disks",(time_key ,OOOOOO0000O000O00 ,O0O0OOOO0O0O0000O ))#line:173
        if OO00O00OOOO0O0OO0 ==time_key :#line:174
            return True #line:175
        return False #line:178
    def parse_char_unit (OOOOO00OO0O0OOO00 ,O0OO0OO00O0O0O00O ):#line:180
        OO00OOO00OOO0OO00 =0 #line:181
        try :#line:182
            OO00OOO00OOO0OO00 =float (O0OO0OO00O0O0O00O )#line:183
        except :#line:184
            OO000OOOOO00OO00O =O0OO0OO00O0O0O00O #line:185
            if OO000OOOOO00OO00O .find ("G")!=-1 :#line:186
                OO000OOOOO00OO00O =OO000OOOOO00OO00O .replace ("G","")#line:187
                OO00OOO00OOO0OO00 =float (OO000OOOOO00OO00O )*1024 *1024 *1024 #line:188
            elif OO000OOOOO00OO00O .find ("M")!=-1 :#line:189
                OO000OOOOO00OO00O =OO000OOOOO00OO00O .replace ("M","")#line:190
                OO00OOO00OOO0OO00 =float (OO000OOOOO00OO00O )*1024 *1024 #line:191
            else :#line:192
                OO00OOO00OOO0OO00 =float (OO000OOOOO00OO00O )#line:193
        return OO00OOO00OOO0OO00 #line:194
    def parse_app_usage_info (O00OO0OOOOO0OOOO0 ,OOO0O000OO00O0000 ):#line:196
        ""#line:197
        if not OOO0O000OO00O0000 :#line:198
            return {}#line:199
        print (OOO0O000OO00O0000 )#line:200
        OOOOOO0O0O0O0O0OO ,OO00O000OO0O000O0 ,OOOOO0OO000000O0O ,OOO000OOO0O0000OO ,O0O0OO00OOO000OO0 ,O0OOOO0O000O000O0 =OOO0O000OO00O0000 ["app"].split (",")#line:201
        OO000O00OO0OOO00O =OOO0O000OO00O0000 ["disks"].split ("-")#line:202
        O0O00000OOOO0OO0O ={}#line:203
        print ("disk tmp:")#line:204
        print (OO000O00OO0OOO00O )#line:205
        for O0O0OO0000OOO0000 in OO000O00OO0OOO00O :#line:206
            print (O0O0OO0000OOO0000 )#line:207
            OO0O0O0OO0OOOOO00 ,O0OO0OOOO00O00O00 ,OO0O00OO0O0O0000O ,O0OOO0OOOO00000O0 ,O00O00O00O0OOOO00 =O0O0OO0000OOO0000 .split (",")#line:208
            O00O0O0O0O00000O0 ={}#line:209
            O00O0O0O0O00000O0 ["usage"]=O00OO0OOOOO0OOOO0 .parse_char_unit (O0OO0OOOO00O00O00 )#line:210
            O00O0O0O0O00000O0 ["total"]=O00OO0OOOOO0OOOO0 .parse_char_unit (OO0O00OO0O0O0000O )#line:211
            O00O0O0O0O00000O0 ["iusage"]=O0OOO0OOOO00000O0 #line:212
            O00O0O0O0O00000O0 ["itotal"]=O00O00O00O0OOOO00 #line:213
            O0O00000OOOO0OO0O [OO0O0O0OO0OOOOO00 ]=O00O0O0O0O00000O0 #line:214
        return {"apps":{"disk_total":OOOOOO0O0O0O0O0OO ,"disk_usage":OO00O000OO0O000O0 ,"sites":OOOOO0OO000000O0O ,"databases":OOO000OOO0O0000OO ,"ftps":O0O0OO00OOO000OO0 ,"plugins":O0OOOO0O000O000O0 },"disks":O0O00000OOOO0OO0O }#line:225
    def get_app_usage (O00O0O000O00O0OO0 ,OOOOO0O0O0000OO0O ):#line:227
        O0O0000OOO00OO0OO =time .localtime ()#line:229
        O000OO0OO00O00O00 =O00O0O000O00O0OO0 .get_time_key ()#line:230
        O0OOO00O0O000000O =time .localtime (time .mktime ((O0O0000OOO00OO0OO .tm_year ,O0O0000OOO00OO0OO .tm_mon ,O0O0000OOO00OO0OO .tm_mday -1 ,0 ,0 ,0 ,0 ,0 ,0 )))#line:233
        O0O0O000O00O0000O =O00O0O000O00O0OO0 .get_time_key (O0OOO00O0O000000O )#line:234
        OO00OO0OO0O0OO0O0 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key =? or time_key=?",(O000OO0OO00O00O00 ,O0O0O000O00O0000O ))#line:236
        O0O0OO0O0OO00OO0O =OO00OO0OO0O0OO0O0 .select ()#line:237
        if type (O0O0OO0O0OO00OO0O )==str or not O0O0OO0O0OO00OO0O :#line:240
            return {}#line:241
        O00OOO00OOO0O0O00 ={}#line:242
        O0O0OOOOO0O0OOO0O ={}#line:243
        for OO0OOO000OOOO00OO in O0O0OO0O0OO00OO0O :#line:244
            if OO0OOO000OOOO00OO ["time_key"]==O000OO0OO00O00O00 :#line:245
                O00OOO00OOO0O0O00 =O00O0O000O00O0OO0 .parse_app_usage_info (OO0OOO000OOOO00OO )#line:246
            if OO0OOO000OOOO00OO ["time_key"]==O0O0O000O00O0000O :#line:247
                O0O0OOOOO0O0OOO0O =O00O0O000O00O0OO0 .parse_app_usage_info (OO0OOO000OOOO00OO )#line:248
        if not O00OOO00OOO0O0O00 :#line:250
            return {}#line:251
        for O0O0O00O00O000000 ,OO0OOOO00O0O0O00O in O00OOO00OOO0O0O00 ["disks"].items ():#line:254
            OOOO00OOOOOO00O00 =int (OO0OOOO00O0O0O00O ["total"])#line:255
            OOOOO0OOO0000O00O =int (OO0OOOO00O0O0O00O ["usage"])#line:256
            O0O0O000OOO000O00 =int (OO0OOOO00O0O0O00O ["itotal"])#line:258
            O00OO00OO0O00000O =int (OO0OOOO00O0O0O00O ["iusage"])#line:259
            if O0O0OOOOO0O0OOO0O and O0O0O00O00O000000 in O0O0OOOOO0O0OOO0O ["disks"].keys ():#line:261
                OO0OO0O00O00OOO00 =O0O0OOOOO0O0OOO0O ["disks"]#line:262
                O0O0O00000O00O0O0 =OO0OO0O00O00OOO00 [O0O0O00O00O000000 ]#line:263
                O000O0OOOO00000O0 =int (O0O0O00000O00O0O0 ["total"])#line:264
                if O000O0OOOO00000O0 ==OOOO00OOOOOO00O00 :#line:265
                    OOO0OOO0OOOOO0000 =int (O0O0O00000O00O0O0 ["usage"])#line:266
                    O000000O0OOO00OOO =0 #line:267
                    O00OO000OOO00OO00 =OOOOO0OOO0000O00O -OOO0OOO0OOOOO0000 #line:268
                    if O00OO000OOO00OO00 >0 :#line:269
                        O000000O0OOO00OOO =round (O00OO000OOO00OO00 /OOOO00OOOOOO00O00 ,2 )#line:270
                    OO0OOOO00O0O0O00O ["incr"]=O000000O0OOO00OOO #line:271
                OOOO0OOO00O000O0O =int (O0O0O00000O00O0O0 ["itotal"])#line:274
                if True :#line:275
                    OOO0OOOO000O0OO0O =int (O0O0O00000O00O0O0 ["iusage"])#line:276
                    O0O000O0OOO00OO0O =0 #line:277
                    O00OO000OOO00OO00 =O00OO00OO0O00000O -OOO0OOOO000O0OO0O #line:278
                    if O00OO000OOO00OO00 >0 :#line:279
                        O0O000O0OOO00OO0O =round (O00OO000OOO00OO00 /O0O0O000OOO000O00 ,2 )#line:280
                    OO0OOOO00O0O0O00O ["iincr"]=O0O000O0OOO00OO0O #line:281
        O00000O000O0OOO0O =O00OOO00OOO0O0O00 ["apps"]#line:285
        O0000OO0O0O00O0OO =int (O00000O000O0OOO0O ["disk_total"])#line:286
        if O0O0OOOOO0O0OOO0O and O0O0OOOOO0O0OOO0O ["apps"]["disk_total"]==O00000O000O0OOO0O ["disk_total"]:#line:287
            O0OO00O0OO00OO0O0 =O0O0OOOOO0O0OOO0O ["apps"]#line:288
            for O0OO00000O0O0OO00 ,O0OOO000O0O00OO00 in O00000O000O0OOO0O .items ():#line:289
                if O0OO00000O0O0OO00 =="disks":continue #line:290
                if O0OO00000O0O0OO00 =="disk_total":continue #line:291
                if O0OO00000O0O0OO00 =="disk_usage":continue #line:292
                OOO0OOOOO0000O0OO =0 #line:293
                OOOOO0OO0000O000O =int (O0OOO000O0O00OO00 )-int (O0OO00O0OO00OO0O0 [O0OO00000O0O0OO00 ])#line:294
                if OOOOO0OO0000O000O >0 :#line:295
                    OOO0OOOOO0000O0OO =round (OOOOO0OO0000O000O /O0000OO0O0O00O0OO ,2 )#line:296
                O00000O000O0OOO0O [O0OO00000O0O0OO00 ]={"val":O0OOO000O0O00OO00 ,"incr":OOO0OOOOO0000O0OO }#line:301
        return O00OOO00OOO0O0O00 #line:302
    def get_timestamp_interval (O000OOO0O0O0O0O0O ,OO00OO0OO00OOOOOO ):#line:304
        O0O0OO00O0OOOO0O0 =None #line:305
        O0O0OO0O00O0O0O00 =None #line:306
        O0O0OO00O0OOOO0O0 =time .mktime ((OO00OO0OO00OOOOOO .tm_year ,OO00OO0OO00OOOOOO .tm_mon ,OO00OO0OO00OOOOOO .tm_mday ,0 ,0 ,0 ,0 ,0 ,0 ))#line:308
        O0O0OO0O00O0O0O00 =time .mktime ((OO00OO0OO00OOOOOO .tm_year ,OO00OO0OO00OOOOOO .tm_mon ,OO00OO0OO00OOOOOO .tm_mday ,23 ,59 ,59 ,0 ,0 ,0 ))#line:310
        return O0O0OO00O0OOOO0O0 ,O0O0OO0O00O0O0O00 #line:311
    def check_server (O00OOOOOOO0OO0OOO ):#line:314
        try :#line:315
            O00OOO0OO00OOOOO0 =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:318
            OOO000O00O0OOO0OO =panelPlugin ()#line:319
            O00O000O0O00O0000 =public .dict_obj ()#line:320
            O0000O000O0O0O0OO =""#line:321
            for OO0O000OO0O00OOOO in O00OOO0OO00OOOOO0 :#line:322
                O0000O00OOOO00O0O =False #line:323
                O0000000OOO00OO00 =False #line:324
                O00O000O0O00O0000 .name =OO0O000OO0O00OOOO #line:325
                O0000000OO00O000O =OOO000O00O0OOO0OO .getPluginInfo (O00O000O0O00O0000 )#line:326
                if not O0000000OO00O000O :#line:327
                    continue #line:328
                OO00O0O00O0O0O00O =O0000000OO00O000O ["versions"]#line:329
                for OO0OOO0OO00O0O0OO in OO00O0O00O0O0O00O :#line:331
                    if OO0OOO0OO00O0O0OO ["status"]:#line:334
                        O0000000OOO00OO00 =True #line:335
                    if "run"in OO0OOO0OO00O0O0OO .keys ()and OO0OOO0OO00O0O0OO ["run"]:#line:336
                        O0000000OOO00OO00 =True #line:338
                        O0000O00OOOO00O0O =True #line:339
                        break #line:340
                O0O0O00OO00OO00O0 =0 #line:341
                if O0000000OOO00OO00 :#line:342
                    O0O0O00OO00OO00O0 =1 #line:343
                    if not O0000O00OOOO00O0O :#line:345
                        O0O0O00OO00OO00O0 =2 #line:346
                O0000O000O0O0O0OO +=str (O0O0O00OO00OO00O0 )#line:347
            if '2'in O0000O000O0O0O0OO :#line:351
                public .M ("system").dbfile ("server_status").add ("status, addtime",(O0000O000O0O0O0OO ,time .time ()))#line:353
        except Exception as O000O0O0000OO0O0O :#line:354
            return True #line:356
    def get_daily_data (OO0000O0OOO0OO000 ,O00OOOO00O0O0O0OO ):#line:358
        ""#line:359
        O00O0OO0OOO0O0OO0 ="IS_PRO_OR_LTD_FOR_PANEL_DAILY"#line:361
        OO000OO0OO00O0O0O =cache .get (O00O0OO0OOO0O0OO0 )#line:362
        if not OO000OO0OO00O0O0O :#line:363
            try :#line:364
                OOO0O00OO00O0OO0O =panelPlugin ()#line:365
                OOOO0OO000O000O00 =OOO0O00OO00O0OO0O .get_soft_list (O00OOOO00O0O0O0OO )#line:366
                if OOOO0OO000O000O00 ["pro"]<0 and OOOO0OO000O000O00 ["ltd"]<0 :#line:367
                    if os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:368
                        os .remove ("/www/server/panel/data/start_daily.pl")#line:369
                    return {"status":False ,"msg":"No authorization.","data":[],"date":O00OOOO00O0O0O0OO .date }#line:375
                cache .set (O00O0OO0OOO0O0OO0 ,True ,86400 )#line:376
            except :#line:377
                return {"status":False ,"msg":"获取不到授权信息，请检查网络是否正常","data":[],"date":O00OOOO00O0O0O0OO .date }#line:383
        if not os .path .exists ("/www/server/panel/data/start_daily.pl"):#line:386
            public .writeFile ("/www/server/panel/data/start_daily.pl",O00OOOO00O0O0O0OO .date )#line:387
        return OO0000O0OOO0OO000 .get_daily_data_local (O00OOOO00O0O0O0OO .date )#line:388
    def get_daily_data_local (OOO0OOO0OO000OOO0 ,OO0O0O00O000O0O0O ):#line:390
        O0O0OO0O000OO0000 =time .strptime (OO0O0O00O000O0O0O ,"%Y%m%d")#line:391
        OOOOOO0OO000OO0OO =OOO0OOO0OO000OOO0 .get_time_key (O0O0OO0O000OO0000 )#line:392
        OOO0OOO0OO000OOO0 .check_databases ()#line:394
        OO000OOOO0OO00OO0 =time .strftime ("%Y-%m-%d",O0O0OO0O000OO0000 )#line:396
        OOOOO00O0O0OOOOO0 =0 #line:397
        O0O00O0OOOOOOO0OO ,OOOO000O0OOOOO0OO =OOO0OOO0OO000OOO0 .get_timestamp_interval (O0O0OO0O000OO0000 )#line:398
        O0O00OOOO0OOO0O0O =public .M ("system").dbfile ("system")#line:399
        OO00000O0O0O00OO0 =O0O00OOOO0OOO0O0O .table ("process_high_percent")#line:400
        O00OOOOO0O0OOO0OO =OO00000O0O0O00OO0 .where ("addtime>=? and addtime<=?",(O0O00O0OOOOOOO0OO ,OOOO000O0OOOOO0OO )).order ("addtime").select ()#line:401
        O0O0O00OOO0OO00OO =[]#line:405
        if len (O00OOOOO0O0OOO0OO )>0 :#line:406
            for OOO00OOO0O0O000OO in O00OOOOO0O0OOO0OO :#line:408
                O00000O00000OO0OO =int (OOO00OOO0O0O000OO ["cpu_percent"])#line:410
                if O00000O00000OO0OO >=80 :#line:411
                    O0O0O00OOO0OO00OO .append ({"time":OOO00OOO0O0O000OO ["addtime"],"name":OOO00OOO0O0O000OO ["name"],"pid":OOO00OOO0O0O000OO ["pid"],"percent":O00000O00000OO0OO })#line:419
        O00OOO0O00000OO0O =len (O0O0O00OOO0OO00OO )#line:421
        O0OOO00000OO0OO0O =0 #line:422
        OOO0OO00O00OO0000 =""#line:423
        if O00OOO0O00000OO0O ==0 :#line:424
            O0OOO00000OO0OO0O =20 #line:425
        else :#line:426
            OOO0OO00O00OO0000 ="CPU出现过载情况"#line:427
        O0O00OOO00O0OO00O ={"ex":O00OOO0O00000OO0O ,"detail":O0O0O00OOO0OO00OO }#line:431
        OOOOO00O00O00OOO0 =[]#line:434
        if len (O00OOOOO0O0OOO0OO )>0 :#line:435
            for OOO00OOO0O0O000OO in O00OOOOO0O0OOO0OO :#line:437
                OO0000O000O00O0O0 =float (OOO00OOO0O0O000OO ["memory"])#line:439
                O0OO0OO0O00O00000 =psutil .virtual_memory ().total #line:440
                O00O00000O0O00OO0 =round (100 *OO0000O000O00O0O0 /O0OO0OO0O00O00000 ,2 )#line:441
                if O00O00000O0O00OO0 >=80 :#line:442
                    OOOOO00O00O00OOO0 .append ({"time":OOO00OOO0O0O000OO ["addtime"],"name":OOO00OOO0O0O000OO ["name"],"pid":OOO00OOO0O0O000OO ["pid"],"percent":O00O00000O0O00OO0 })#line:450
        OO00O00000OOOOOO0 =len (OOOOO00O00O00OOO0 )#line:451
        O00OO00O00O0000OO =""#line:452
        O0OOO00O0O0O0OOO0 =0 #line:453
        if OO00O00000OOOOOO0 ==0 :#line:454
            O0OOO00O0O0O0OOO0 =20 #line:455
        else :#line:456
            if OO00O00000OOOOOO0 >1 :#line:457
                O00OO00O00O0000OO ="内存在多个时间点出现占用80%"#line:458
            else :#line:459
                O00OO00O00O0000OO ="内存出现占用超过80%"#line:460
        OO0O0O0OOOO0OOOOO ={"ex":OO00O00000OOOOOO0 ,"detail":OOOOO00O00O00OOO0 }#line:464
        OOOOOO0O0OO0O00O0 =public .M ("system").dbfile ("system").table ("app_usage").where ("time_key=?",(OOOOOO0OO000OO0OO ,))#line:468
        OO0OO0000O0OO0000 =OOOOOO0O0OO0O00O0 .select ()#line:469
        OO0OOO0O0O0000O0O ={}#line:470
        if OO0OO0000O0OO0000 and type (OO0OO0000O0OO0000 )!=str :#line:471
            OO0OOO0O0O0000O0O =OOO0OOO0OO000OOO0 .parse_app_usage_info (OO0OO0000O0OO0000 [0 ])#line:472
        OO00O00O000OOOOO0 =[]#line:473
        if OO0OOO0O0O0000O0O :#line:474
            O0O0000O0O000O0OO =OO0OOO0O0O0000O0O ["disks"]#line:475
            for OO0000OO00O000OO0 ,OO0OOOO0O0O0O0O00 in O0O0000O0O000O0OO .items ():#line:476
                OOOOOO00O00000O0O =int (OO0OOOO0O0O0O0O00 ["usage"])#line:477
                O0OO0OO0O00O00000 =int (OO0OOOO0O0O0O0O00 ["total"])#line:478
                OOOOOO0O0OOO0OOOO =round (OOOOOO00O00000O0O /O0OO0OO0O00O00000 ,2 )#line:479
                O00O00O000O0O0O0O =int (OO0OOOO0O0O0O0O00 ["iusage"])#line:480
                OOOO0OO0O000OOO00 =int (OO0OOOO0O0O0O0O00 ["itotal"])#line:481
                if OOOO0OO0O000OOO00 >0 :#line:482
                    O0OO0O00OO0000O00 =round (O00O00O000O0O0O0O /OOOO0OO0O000OOO00 ,2 )#line:483
                else :#line:484
                    O0OO0O00OO0000O00 =0 #line:485
                if OOOOOO0O0OOO0OOOO >=0.8 :#line:489
                    OO00O00O000OOOOO0 .append ({"name":OO0000OO00O000OO0 ,"percent":OOOOOO0O0OOO0OOOO *100 ,"ipercent":O0OO0O00OO0000O00 *100 ,"usage":OOOOOO00O00000O0O ,"total":O0OO0OO0O00O00000 ,"iusage":O00O00O000O0O0O0O ,"itotal":OOOO0OO0O000OOO00 })#line:498
        O0OOOO0OO0000O0O0 =len (OO00O00O000OOOOO0 )#line:500
        OOO000O0000O0OO00 =""#line:501
        OO00OOO00OOO0O0O0 =0 #line:502
        if O0OOOO0OO0000O0O0 ==0 :#line:503
            OO00OOO00OOO0O0O0 =20 #line:504
        else :#line:505
            OOO000O0000O0OO00 ="有磁盘空间占用已经超过80%"#line:506
        O0000O0OOO0OO000O ={"ex":O0OOOO0OO0000O0O0 ,"detail":OO00O00O000OOOOO0 }#line:511
        O0OOO00O0O0O00000 =public .M ("system").dbfile ("system").table ("server_status").where ("addtime>=? and addtime<=?",(O0O00O0OOOOOOO0OO ,OOOO000O0OOOOO0OO ,)).order ("addtime desc").select ()#line:515
        O00OO00OO00OOOOOO =["php","nginx","apache","mysql","tomcat","pure-ftpd","redis","memcached"]#line:520
        OO0O000OOO0OO00OO ={}#line:522
        OOO0O0O0OOO00OO00 =0 #line:523
        O0OOO000O00OO00OO =""#line:524
        for OOO00O0OO0OOO0O0O ,O0O000000OOO00O00 in enumerate (O00OO00OO00OOOOOO ):#line:525
            if O0O000000OOO00O00 =="pure-ftpd":#line:526
                O0O000000OOO00O00 ="ftpd"#line:527
            O0OO00OO0O000000O =0 #line:528
            O0000OOO0OOOOO00O =[]#line:529
            for O0O0OOO00000OOO0O in O0OOO00O0O0O00000 :#line:530
                _OOOOOOO00OOO0OOOO =O0O0OOO00000OOO0O ["status"]#line:533
                if OOO00O0OO0OOO0O0O <len (_OOOOOOO00OOO0OOOO ):#line:534
                    if _OOOOOOO00OOO0OOOO [OOO00O0OO0OOO0O0O ]=="2":#line:535
                        O0000OOO0OOOOO00O .append ({"time":O0O0OOO00000OOO0O ["addtime"],"desc":"退出"})#line:536
                        O0OO00OO0O000000O +=1 #line:537
                        OOO0O0O0OOO00OO00 +=1 #line:538
            OO0O000OOO0OO00OO [O0O000000OOO00O00 ]={"ex":O0OO00OO0O000000O ,"detail":O0000OOO0OOOOO00O }#line:543
        OO00000OOO0000000 =0 #line:545
        if OOO0O0O0OOO00OO00 ==0 :#line:546
            OO00000OOO0000000 =20 #line:547
        else :#line:548
            O0OOO000O00OO00OO ="系统级服务有出现异常退出情况"#line:549
        OOOOOOOOOO0O00000 =public .M ("crontab").field ("name,sName,sType").where ("sType in (?, ?, ?)",("database","enterpriseBackup","site",)).select ()#line:553
        OOOOO00O0OO00OO0O =set ()#line:556
        for OO0O0O00O00O00000 in OOOOOOOOOO0O00000 :#line:557
            if OO0O0O00O00O00000 ["sType"]=="database":#line:558
                OOOOO00O0OO00OO0O .add (OO0O0O00O00O00000 ["sName"])#line:559
            elif OO0O0O00O00O00000 ["sType"]=="enterpriseBackup":#line:560
                OO0O00OO00O0O00OO =OO0O0O00O00O00000 ["name"]#line:561
                O0O000O0000OOO000 =OO0O00OO00O0O00OO [OO0O00OO00O0O00OO .rfind ("[")+1 :OO0O00OO00O0O00OO .rfind ("]")]#line:562
                OOOOO00O0OO00OO0O .add (O0O000O0000OOO000 )#line:563
        O00000OO00OOO0O00 ="ALL"in OOOOO00O0OO00OO0O #line:567
        O0OO000OOO00OO0OO =set (OOO0OOO00O0O0OO0O ["sName"]for OOO0OOO00O0O0OO0O in OOOOOOOOOO0O00000 if OOO0OOO00O0O0OO0O ["sType"]=="site")#line:568
        OOOOOOOOOOOO000OO ="ALL"in O0OO000OOO00OO0OO #line:569
        OOOO0O0O0OOO0O000 =[]#line:570
        O0O00OO0000OOO0O0 =[]#line:571
        if not O00000OO00OOO0O00 :#line:572
            O0000O0OO0O00OOOO =public .M ("databases").field ("name").select ()#line:573
            for O000O000OOO00000O in O0000O0OO0O00OOOO :#line:574
                OO00O00O0OO0OO000 =O000O000OOO00000O ["name"]#line:575
                if OO00O00O0OO0OO000 not in OOOOO00O0OO00OO0O :#line:576
                    OOOO0O0O0OOO0O000 .append ({"name":OO00O00O0OO0OO000 })#line:577
        if not OOOOOOOOOOOO000OO :#line:579
            O0O00O000OO0O0O00 =public .M ("sites").field ("name").select ()#line:580
            for O00OO0OO0OO00O0OO in O0O00O000OO0O0O00 :#line:581
                OOOO0O0O0O00OOOOO =O00OO0OO0OO00O0OO ["name"]#line:582
                if OOOO0O0O0O00OOOOO not in O0OO000OOO00OO0OO :#line:583
                    O0O00OO0000OOO0O0 .append ({"name":OOOO0O0O0O00OOOOO })#line:584
        OOO0O0OO00O0O0O0O =public .M ("system").dbfile ("system").table ("backup_status").where ("addtime>=? and addtime<=?",(O0O00O0OOOOOOO0OO ,OOOO000O0OOOOO0OO )).select ()#line:587
        O000000OOOO000OOO ={"database":{"no_backup":OOOO0O0O0OOO0O000 ,"backup":[]},"site":{"no_backup":O0O00OO0000OOO0O0 ,"backup":[]},"path":{"no_backup":[],"backup":[]}}#line:602
        OOOO0000OO0O00O00 =0 #line:603
        for O00O0000O0O000O00 in OOO0O0OO00O0O0O0O :#line:604
            OO0OO000O0O00OOO0 =O00O0000O0O000O00 ["status"]#line:605
            if OO0OO000O0O00OOO0 :#line:606
                continue #line:607
            OOOO0000OO0O00O00 +=1 #line:609
            O0O00O00O0O0000OO =O00O0000O0O000O00 ["id"]#line:610
            O000OOO0OOOOOO0O0 =public .M ("crontab").where ("id=?",(O0O00O00O0O0000OO )).find ()#line:611
            if not O000OOO0OOOOOO0O0 :#line:612
                continue #line:613
            O0O0OOOOOOOO0OO00 =O000OOO0OOOOOO0O0 ["sType"]#line:614
            if not O0O0OOOOOOOO0OO00 :#line:615
                continue #line:616
            O0O000O0000OOO000 =O000OOO0OOOOOO0O0 ["name"]#line:617
            O0OO000000000OOOO =O00O0000O0O000O00 ["addtime"]#line:618
            O00OO00O0O0OOOOO0 =O00O0000O0O000O00 ["target"]#line:619
            if O0O0OOOOOOOO0OO00 not in O000000OOOO000OOO .keys ():#line:620
                O000000OOOO000OOO [O0O0OOOOOOOO0OO00 ]={}#line:621
                O000000OOOO000OOO [O0O0OOOOOOOO0OO00 ]["backup"]=[]#line:622
                O000000OOOO000OOO [O0O0OOOOOOOO0OO00 ]["no_backup"]=[]#line:623
            O000000OOOO000OOO [O0O0OOOOOOOO0OO00 ]["backup"].append ({"name":O0O000O0000OOO000 ,"target":O00OO00O0O0OOOOO0 ,"status":OO0OO000O0O00OOO0 ,"target":O00OO00O0O0OOOOO0 ,"time":O0OO000000000OOOO })#line:630
        OOOO0O0000OO000O0 =""#line:632
        O0O0000OOOO0OOO0O =0 #line:633
        if OOOO0000OO0O00O00 ==0 :#line:634
            O0O0000OOOO0OOO0O =20 #line:635
        else :#line:636
            OOOO0O0000OO000O0 ="有计划任务备份失败"#line:637
        if len (OOOO0O0O0OOO0O000 )==0 :#line:639
            O0O0000OOOO0OOO0O +=10 #line:640
        else :#line:641
            if OOOO0O0000OO000O0 :#line:642
                OOOO0O0000OO000O0 +=";"#line:643
            OOOO0O0000OO000O0 +="有数据库未及时备份"#line:644
        if len (O0O00OO0000OOO0O0 )==0 :#line:646
            O0O0000OOOO0OOO0O +=10 #line:647
        else :#line:648
            if OOOO0O0000OO000O0 :#line:649
                OOOO0O0000OO000O0 +=";"#line:650
            OOOO0O0000OO000O0 +="有网站未备份"#line:651
        OO0O00O0000O00000 =0 #line:654
        O00OOO0O00O000OOO =public .M ('logs').where ('addtime like ? and type=?',(str (OO000OOOO0OO00OO0 )+"%",'用户登录',)).select ()#line:655
        O0O0000OOOO0O0000 =[]#line:656
        if O00OOO0O00O000OOO and type (O00OOO0O00O000OOO )==list :#line:657
            for O0O00000000000O00 in O00OOO0O00O000OOO :#line:658
                O0OO000O0OOOOOO00 =O0O00000000000O00 ["log"]#line:659
                if O0OO000O0OOOOOO00 .find ("失败")>=0 or O0OO000O0OOOOOO00 .find ("错误")>=0 :#line:660
                    OO0O00O0000O00000 +=1 #line:661
                    O0O0000OOOO0O0000 .append ({"time":time .mktime (time .strptime (O0O00000000000O00 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0O00000000000O00 ["log"],"username":O0O00000000000O00 ["username"],})#line:666
            O0O0000OOOO0O0000 .sort (key =lambda OO0OOOOOOOO00O0OO :OO0OOOOOOOO00O0OO ["time"])#line:667
        OO00OOOOO0OOOO00O =public .M ('logs').where ('type=?',('SSH安全',)).where ("addtime like ?",(str (OO000OOOO0OO00OO0 )+"%",)).select ()#line:669
        O0OO0O0OO0O0OO000 =[]#line:671
        O000O00O0OO000O0O =0 #line:672
        if OO00OOOOO0OOOO00O :#line:673
            for O0O00000000000O00 in OO00OOOOO0OOOO00O :#line:674
                O0OO000O0OOOOOO00 =O0O00000000000O00 ["log"]#line:675
                if O0OO000O0OOOOOO00 .find ("存在异常")>=0 :#line:676
                    O000O00O0OO000O0O +=1 #line:677
                    O0OO0O0OO0O0OO000 .append ({"time":time .mktime (time .strptime (O0O00000000000O00 ["addtime"],"%Y-%m-%d %H:%M:%S")),"desc":O0O00000000000O00 ["log"],"username":O0O00000000000O00 ["username"]})#line:682
            O0OO0O0OO0O0OO000 .sort (key =lambda OO00OO0O0OO0OOO00 :OO00OO0O0OO0OOO00 ["time"])#line:683
        OOO0O00O0000OOO00 =""#line:685
        OOO0O00OO0O0O0000 =0 #line:686
        if O000O00O0OO000O0O ==0 :#line:687
            OOO0O00OO0O0O0000 =10 #line:688
        else :#line:689
            OOO0O00O0000OOO00 ="SSH有异常登录"#line:690
        if OO0O00O0000O00000 ==0 :#line:692
            OOO0O00OO0O0O0000 +=10 #line:693
        else :#line:694
            if OO0O00O0000O00000 >10 :#line:695
                OOO0O00OO0O0O0000 -=10 #line:696
            if OOO0O00O0000OOO00 :#line:697
                OOO0O00O0000OOO00 +=";"#line:698
            OOO0O00O0000OOO00 +="面板登录有错误".format (OO0O00O0000O00000 )#line:699
        O0OOO00O0O0O00000 ={"panel":{"ex":OO0O00O0000O00000 ,"detail":O0O0000OOOO0O0000 },"ssh":{"ex":O000O00O0OO000O0O ,"detail":O0OO0O0OO0O0OO000 }}#line:709
        OOOOO00O0O0OOOOO0 =O0OOO00000OO0OO0O +O0OOO00O0O0O0OOO0 +OO00OOO00OOO0O0O0 +OO00000OOO0000000 +O0O0000OOOO0OOO0O +OOO0O00OO0O0O0000 #line:711
        O00O0000O0OO0OO00 =[OOO0OO00O00OO0000 ,O00OO00O00O0000OO ,OOO000O0000O0OO00 ,O0OOO000O00OO00OO ,OOOO0O0000OO000O0 ,OOO0O00O0000OOO00 ]#line:712
        OOOO0OO00OO00OO00 =[]#line:713
        for O00O00O0OO00O00O0 in O00O0000O0OO0OO00 :#line:714
            if O00O00O0OO00O00O0 :#line:715
                if O00O00O0OO00O00O0 .find (";")>=0 :#line:716
                    for OOO0OO0OO00O00OO0 in O00O00O0OO00O00O0 .split (";"):#line:717
                        OOOO0OO00OO00OO00 .append (OOO0OO0OO00O00OO0 )#line:718
                else :#line:719
                    OOOO0OO00OO00OO00 .append (O00O00O0OO00O00O0 )#line:720
        if not OOOO0OO00OO00OO00 :#line:722
            OOOO0OO00OO00OO00 .append ("服务器运行正常，请继续保持！")#line:723
        O0OO00O00OOO0OO00 =OOO0OOO0OO000OOO0 .evaluate (OOOOO00O0O0OOOOO0 )#line:727
        return {"data":{"cpu":O0O00OOO00O0OO00O ,"ram":OO0O0O0OOOO0OOOOO ,"disk":O0000O0OOO0OO000O ,"server":OO0O000OOO0OO00OO ,"backup":O000000OOOO000OOO ,"exception":O0OOO00O0O0O00000 ,},"evaluate":O0OO00O00OOO0OO00 ,"score":OOOOO00O0O0OOOOO0 ,"date":OOOOOO0OO000OO0OO ,"summary":OOOO0OO00OO00OO00 ,"status":True }#line:744
    def evaluate (OOOOO00OOOO0O0O0O ,O0OO0000000000OO0 ):#line:746
        OO0OOO0000OOO0O0O =""#line:747
        if O0OO0000000000OO0 >=100 :#line:748
            OO0OOO0000OOO0O0O ="正常"#line:749
        elif O0OO0000000000OO0 >=80 :#line:750
            OO0OOO0000OOO0O0O ="良好"#line:751
        else :#line:752
            OO0OOO0000OOO0O0O ="一般"#line:753
        return OO0OOO0000OOO0O0O #line:754
    def get_daily_list (OOOOO00O00OOOOO00 ,O0O0O00OOO00000O0 ):#line:756
        O00O0000O00OOO0OO =public .M ("system").dbfile ("system").table ("daily").where ("time_key>?",0 ).select ()#line:757
        O0O00000OO000000O =[]#line:758
        for O0O00O00O00O0000O in O00O0000O00OOO0OO :#line:759
            O0O00O00O00O0000O ["evaluate"]=OOOOO00O00OOOOO00 .evaluate (O0O00O00O00O0000O ["evaluate"])#line:760
            O0O00000OO000000O .append (O0O00O00O00O0000O )#line:761
        return O0O00000OO000000O 