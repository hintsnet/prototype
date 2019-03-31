# -*- coding: utf-8 -*-
from config import Config
from shutil import copyfile
import filecmp
import os
import sys

# 从 TB 数据目录同步最新的数据库
def sync_tb_db(conf):
	# 获取环境变量中的路径设置
	# 本地 TB 数据所在目录
	local_tb_dir = conf.local_tb_dir
	# TB 数据库文件名
	tb_db_name = conf.tb_db_name
	# 本地 TB 数据库的完整路径
	tb_db_path = "%s/%s" % (local_tb_dir, tb_db_name)
	# hintsnet 数据临时目录
	hn_tmp_dir = conf.hn_tmp_dir
	# hintsnet 数据库文件名
	hn_db_name = conf.hn_db_name
	# hintsnet 数据库的完整路径
	hn_db_path = "%s/%s" % (hn_tmp_dir, hn_db_name)
	if (os.path.isfile(hn_db_path) and filecmp.cmp(tb_db_path, hn_db_path, shallow=False)):
		print("数据库不需要同步!")
	else:
		res = copyfile(tb_db_path, hn_db_path)
		print("数据库已同步到: %s" % res)

# 主程序入口处
if(__name__ == '__main__'):
	# 修复 cmd.exe 中文打印问题
	sys.stdout = open(sys.stdout.fileno(), 
		mode='w', encoding='utf8', buffering=1)
	sync_tb_db(Config)
