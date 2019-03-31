# -*- coding: utf-8 -*-
import os
import sys

# 从操作系统的环境变量中获取一些关键的运行环境参数
# 如果没有获取到，就使用预设的默认值
class Config(object):
	local_tb_dir = os.environ.get('LOCAL_TB_DIR') or './'
	tb_db_name = os.environ.get('TB_DB_NAME') or 'Brain.db'
	hn_tmp_dir = os.environ.get('HN_TMP_DIR') or './'
	hn_db_name = os.environ.get('HN_DB_NAME') or 'tmpBrain.db'
	tb_pub_basedir = os.environ.get('TB_PUB_BASEDIR') or './pub'
	oss_epoint = os.environ.get('OSS_EPOINT') or 'None'
	oss_bucket = os.environ.get('OSS_BUCKET') or 'None'
	oss_acckey = os.environ.get('OSS_ACCKEY') or 'None'
	oss_accsec = os.environ.get('OSS_ACCSEC') or 'None'

# 主程序入口处
if(__name__ == '__main__'):
	# 修复 cmd.exe 中文打印问题
	sys.stdout = open(sys.stdout.fileno(), 
		mode='w', encoding='utf8', buffering=1)
	attrs = vars(Config)
	print("运行时环境变量定义如下: ")
	print('\n'.join("%s\t[ %s ]" % 
		item for item in attrs.items() if not item[0].startswith('__')))
