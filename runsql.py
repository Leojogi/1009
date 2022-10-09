#!/usr/bin/env python3
# coding:utf-8
import json
import os
import re
import subprocess
import sys
import hashlib
from collections import OrderedDict  #有序字典
import configparser

class Solution:
    def __init__(self, project, database, fr):
        self.project = project
        self.database = database
        self.fr = fr
        self.repo_path = "/repo/"
        self.host = "10.182.220.137"
        self.shell_path = "/root/auto_deploy_sql/"
        self.read_dic = OrderedDict()    #已读字典
        self.installed_dic = OrderedDict()  # 已安装的目录字典
        self.failed_sql = []  # 安装失败的sql脚本列表

    def md5_all(self, dir_path):
        try:
            data = ''
            sql_path = dir_path + "/{}/install/".format(self.database)
            file_lst = os.listdir(sql_path)
            for item1 in file_lst:
                if ".sql" in item1:
                    temp_path = os.path.join(sql_path, item1)
                    if os.path.isfile(temp_path):
                        with open(temp_path, "r") as fp:    #所有sql脚本总的md5
                            data += fp.read()
                        fp.close()
            dir_md5 = hashlib.md5(data.encode(encoding="utf-8")).hexdigest()
            return dir_md5
        except FileNotFoundError as e:
            print(e)
            dir_md5 = ''
            return dir_md5

    def md5_all_ngcv(self, dir_path):
        try:
            data = ''
            sql_path = dir_path + "/{}/{}/install/".format(s.env, self.database)
            file_lst = os.listdir(sql_path)
            for item1 in file_lst:
                if ".sql" in item1:
                    temp_path = os.path.join(sql_path, item1)
                    if os.path.isfile(temp_path):
                        with open(temp_path, "r") as fp:    #所有sql脚本总的md5
                            data += fp.read()
                        fp.close()
            dir_md5 = hashlib.md5(data.encode(encoding="utf-8")).hexdigest()
            return dir_md5
        except FileNotFoundError as e:
            print(e)
            dir_md5 = ''
            return dir_md5

    def get_base_path(self):  # 拿到sql脚本所在位置
        base_path = "{}{}/{}".format(self.repo_path, self.project, self.fr)    #/repo/tip/FR
        return base_path

    def get_dirlist(self, base_path):   #/repo/tip
        dirlst = []
        file_list = os.listdir(base_path)  # 获取文件夹下所有的文件
        for item1 in file_list:
            temp_path = os.path.join(base_path, item1)
            if os.path.isdir(temp_path):
                if item1 != "init":
                    dirlst.insert(0, temp_path)
        return dirlst                 #['/repo/tip/20220829-TIP1.7-BUG317328', '/repo/data/tip/20220828-TIP1.7-BUG317328']

    def get_requirement(self, dir_path):
        basePath = self.get_base_path()     #/repo/tip
        requirementPath = dir_path + "/{}/requirement.txt".format(self.database)         #/repo/data/tip/20220828-TIP1.7-BUG317328/mysql/requirement.txt
        if os.path.exists(requirementPath):  # 如果依赖文件存在
            with open(requirementPath, 'r') as fp:
                requireDir = fp.read()
            fp.close()
            self.read_dic[dir_path] = 1         #读取完目录字典置为1
            if dir_path not in requireLst:        #如果不在总的依赖表里面，则添加到临时表里面
                tmp_lst.append(dir_path)
            if "init" not in requireDir:    #递归被依赖对象
                try:
                    if self.read_dic[os.path.join(basePath, requireDir.split('\n')[0])] == 1 or os.path.join(basePath, requireDir.split('\n')[0]) in s.check_list().keys(): #如果被依赖对象已经读取过或者已经跑过则递归中断
                        return
                except KeyError as e:
                    print(KeyError, ":", e)
                    return
                self.get_requirement(os.path.join(basePath, requireDir.split('\n')[0]))
            return
        else:
            print("依赖文件不存在")
            self.read_dic[dir_path] = 1  # 读取完目录字典置为1

    def get_requirement_ngcv(self, dir_path):
        basePath = self.get_base_path()     #/repo/tip
        requirementPath = dir_path + "/{}/{}/requirements.txt".format(s.env, self.database)         #/repo/tip/20220828-TIP1.7-BUG317328/aliyun/mysql/requirement.txt
        if os.path.exists(requirementPath):             #如果目录文件存在
            with open(requirementPath, 'r') as fp:
                requireDir = fp.read()
            fp.close()
            self.read_dic[dir_path] = 1         #读取完目录字典置为1
            if dir_path not in requireLst:        #如果不在总的依赖表里面，则添加到临时表里面
                tmp_lst.append(dir_path)
            if "init" not in requireDir:    #递归被依赖对象
                try:
                    if self.read_dic[os.path.join(basePath, requireDir.split('\n')[0])] == 1 or os.path.join(basePath, requireDir.split('\n')[0]) in s.check_list().keys(): #如果被依赖对象已经读取过或者已经跑过则递归中断
                        return
                except KeyError as e:
                    print(KeyError, ":", e)
                    return
                self.get_requirement_ngcv(os.path.join(basePath, requireDir.split('\n')[0]))
            return
        else:                                      #如果目录文件不存在
            self.read_dic[dir_path] = 1  # 读取完目录字典置为1


    def exec_sql(self, dir_path):
        sql_path = dir_path + "/{}/install".format(self.database)
        # bash /root/auto_deploy_sql/sql_record.sh /repo/tip/20220829-TIP1.7-BUG317328/mysql/install/ 10.182.220.137
        cmd = "bash {}sql_record.sh {} {}".format(self.shell_path, sql_path, self.host)
        print("cmd\n", cmd)
        output = subprocess.getoutput(cmd)
        print("output\n", output)
        return output

    def exec_sql_ngcv(self, dir_path):
        sql_path = dir_path + "/{}/{}/install".format(s.env, self.database)
        # bash /root/auto_deploy_sql/sql_record.sh /repo/tip/20220829-TIP1.7-BUG317328/mysql/install/ 10.182.220.137
        cmd = "bash {}sql_record.sh {} {}".format(self.shell_path, sql_path, self.host)
        print("cmd\n", cmd)
        output = subprocess.getoutput(cmd)
        print("output\n", output)
        return output

    def get_failed_sql(self, dir_path):
        last_failed_path = dir_path + "/{}/install/record/last.error".format(self.database)     #拿到sql运行脚本的结果
        if os.path.isfile(last_failed_path):
            with open(last_failed_path, 'r', encoding="utf-8") as fp:  # 读取sql脚本安装的运行结果
                temp_lst = fp.readlines()
            fp.close()
            for item2 in temp_lst:
                self.failed_sql.append(dir_path + "/{}/install/{}".format(self.database, item2.split('\n')[0]))
        return

    def get_failed_sql_ngcv(self, dir_path):
        last_failed_path = dir_path + "/{}/{}/install/record/last.error".format(s.env, self.database)     #拿到sql运行脚本的结果
        if os.path.isfile(last_failed_path):
            with open(last_failed_path, 'r', encoding="utf-8") as fp:  # 读取sql脚本安装的运行结果
                temp_lst = fp.readlines()
            fp.close()
            for item2 in temp_lst:
                self.failed_sql.append(dir_path + "/{}/{}/install/{}".format(s.env, self.database, item2.split('\n')[0]))
        return

    def record_success_dir(self):   #持久化记录已经成功跑过的目录
        try:
            with open("{}runned_dir.txt".format(self.shell_path), "r", encoding="utf-8") as fp:  # 追加到文件中去，原文件内容保持不动，a+在尾部追加
                dic = json.loads(fp.read())
        except Exception as e:
            print(Exception, ":", e)
            dic = {}

        with open("{}runned_dir.txt".format(self.shell_path), "w", encoding="utf-8") as fp:  # 去重追加到本地文件中去
            for key, value in self.installed_dic.items():
                if value == "successed":
                    dic[key] = self.md5_all(key)              #得到已跑过的目录的md5
            fp.write(json.dumps(dic))
        fp.close()
        return

    def record_success_dir_ngcv(self):   #持久化记录已经成功跑过的目录
        try:
            with open("{}runned_dir.txt".format(self.shell_path), "r", encoding="utf-8") as fp:  # 追加到文件中去，原文件内容保持不动，a+在尾部追加
                dic = json.loads(fp.read())
        except Exception as e:
            print(Exception, ":", e)
            dic = {}

        with open("{}runned_dir.txt".format(self.shell_path), "w", encoding="utf-8") as fp:  # 去重追加到本地文件中去
            for key, value in self.installed_dic.items():
                if value == "successed":
                    dic[key] = self.md5_all_ngcv(key)              #得到已跑过的目录的md5
            fp.write(json.dumps(dic))
        fp.close()
        return

    def check_list(self):
        try:
            with open("{}runned_dir.txt".format(self.shell_path), "r", encoding="utf-8") as fp:  #读取已经跑过的目录
                dic = json.loads(fp.read())
            fp.close()
            return dic
        except Exception as e:
            print(Exception, ':', e)
            dic = {}
            return dic

if __name__ == "__main__":
    config = configparser.ConfigParser()  # 实例化ConfigParser
    config.read("config.ini")     # 读取config.ini
    project = config.get("arg", "project")  # 读取 [DATABASE] 分组下的 project 的值
    db = config.get("arg", "db")  # 读取 [DATABASE] 分组下的 project 的值
    fr = config.get("arg", "fr")  # 读取 [DATABASE] 分组下的 project 的值
    env = config.get("arg", "env")  # 读取 [DATABASE] 分组下的 project 的值
    s = Solution(project, db, fr)
    dirlist = s.get_dirlist(s.get_base_path())    #得到所有的目录
    print("dirlist========", dirlist)

    if s.project == "ngcv":
        s.env = env
        requireLst = []                  #依赖关系记录
        runned = s.check_list()
        for item in dirlist:             #去除没有相应路径的
            tp = os.path.join(item, "/{}/{}".format(s.env, s.database))
            if not os.path.exists(tp):
                print("{}没有需执行路径".format(item))
                dirlist.remove(item)
        for item in dirlist:             #字典记录目录读取状态
            md5 = s.md5_all_ngcv(item)
            try:
                if item in runned.keys():
                    if md5 != runned[item]:       #判断没有跑过的目录
                        s.read_dic[item] = 0     #待安装的目录，置0表示尚未找过依赖关系
                else:
                    s.read_dic[item] = 0
            except KeyError as e:
                print(KeyError, ":", e)
                s.read_dic[item] = 0
        print("read_dic========", s.read_dic)
        for key, value in s.read_dic.items():    #读取值为0的目录找依赖关系
            if value == 0:
                tmp_lst = []
                s.get_requirement_ngcv(key)          #迭代文件夹之间的依赖关系
                for i in range(len(tmp_lst)):
                    n = tmp_lst.pop()
                    requireLst.insert(0, n)
        print("requireLst=========", requireLst)

        requireLst.reverse()
        for item in requireLst:
            output = s.exec_sql_ngcv(item)
            if "ERROR" in output:   #如果在执行过程中报错，终止执行接下里的脚本,并记录报错的目录
                s.installed_dic[item] = "failed"
                s.get_failed_sql_ngcv(item)      #记录出错的具体脚本
                break
            s.installed_dic[item] = "successed"  #记录已成功执行的目录

        print("s.failed_sql=========", s.failed_sql)
        print("s.installed_dic======", s.installed_dic)
        s.record_success_dir_ngcv()       #持久化记录已经跑过的目录
    else:
        requireLst = []                  #依赖关系记录
        runned = s.check_list()
        for item in dirlist:             #去除没有相应路径的
            tp = os.path.join(item, "/{}".format(s.database))
            if not os.path.exists(tp):
                print("{}没有需执行路径".format(item))
                dirlist.remove(item)
        for item in dirlist:             #字典记录目录读取状态
            md5 = s.md5_all(item)
            try:
                if item in runned.keys():
                    if md5 != runned[item]:       #判断没有跑过的目录
                        s.read_dic[item] = 0     #待安装的目录，置0表示尚未找过依赖关系
                else:
                    s.read_dic[item] = 0
            except KeyError as e:
                print(KeyError, ":", e)
                s.read_dic[item] = 0
        print("read_dic========", s.read_dic)
        for key, value in s.read_dic.items():    #读取值为0的目录找依赖关系
            if value == 0:
                tmp_lst = []
                s.get_requirement(key)          #迭代文件夹之间的依赖关系
                for i in range(len(tmp_lst)):
                    n = tmp_lst.pop()
                    requireLst.insert(0, n)
        print("requireLst=========", requireLst)

        requireLst.reverse()
        for item in requireLst:
            output = s.exec_sql(item)
            if "ERROR" in output:   #如果在执行过程中报错，终止执行接下里的脚本,并记录报错的目录
                s.installed_dic[item] = "failed"
                s.get_failed_sql(item)      #记录出错的具体脚本
                break
            s.installed_dic[item] = "successed"  #记录已成功执行的目录

        print("s.failed_sql=========", s.failed_sql)
        print("s.installed_dic======", s.installed_dic)
        s.record_success_dir()       #持久化记录已经跑过的目录









