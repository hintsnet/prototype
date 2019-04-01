# -*- coding: utf-8 -*-
from config import Config
from shutil import copyfile
import filecmp
import os
import sqlite3
import sys

# 从 TB 数据目录同步最新的数据库
def sync_tb_db(tb_db_path, hn_db_path):
	if (os.path.isfile(hn_db_path) and filecmp.cmp(tb_db_path, hn_db_path, shallow=False)):
		return "数据库不需要同步!"
	else:
		res = copyfile(tb_db_path, hn_db_path)
		return "数据库已同步到: %s" % res

# 连接 sqlite3 数据库
def connect_sqlite_db(db_file_path):
	conn = sqlite3.connect(db_file_path)
	cursor = conn.cursor()
	return cursor

# 通用的数据查询函数, 用于执行任意 sql 语句
def query_db(db_cursor, sql):
    db_cursor.execute(sql)
    records = db_cursor.fetchall()
    return records

# 获取所有标记为"可发布"的节点的 id, 以列表形式返回
def get_pub_thought_ids(db_cursor):
    # 定义 sql 语句
    sql = """
    select dest.id
    from thoughts as src inner join links inner join thoughts as dest
    where src.id = thoughtIdA and dest.id = thoughtIdB and
    links.meaning = 5 and src.name = "可发布"
    """
    results = query_db(db_cursor, sql)
    thought_ids = [result[0] for result in results]
    return thought_ids

# 给定一组节点 id, 获取相关节点的详细信息
# 目前, 只获取 name 字段的内容
def get_thought_data(db_cursor, thought_ids):
    thought_data = []
    for thought_id in thought_ids:
        sql = 'select name from thoughts where id="%s"' % thought_id
        results = query_db(db_cursor, sql)
        thought_data.append({'id': thought_id,'name': results[0][0]})
    return thought_data

# 主程序入口处
if(__name__ == '__main__'):
	# 修复 cmd.exe 中文打印问题
	sys.stdout = open(sys.stdout.fileno(), 
		mode='w', encoding='utf8', buffering=1)
	
	# 获取环境变量中的路径设置
	# 特别说明: 请事先运行 source prep_env 命令
	# 为安全起见, prep_env 文件不会被加入版本库
	# 本地 TB 数据所在目录
	local_tb_dir = Config.local_tb_dir
	# TB 数据库文件名
	tb_db_name = Config.tb_db_name
	# 本地 TB 数据库的完整路径
	tb_db_path = "%s/%s" % (local_tb_dir, tb_db_name)
	# hintsnet 数据临时目录
	hn_tmp_dir = Config.hn_tmp_dir
	# hintsnet 数据库文件名
	hn_db_name = Config.hn_db_name
	# hintsnet 数据库的完整路径
	hn_db_path = "%s/%s" % (hn_tmp_dir, hn_db_name)
	# 从 TB 工作目录同步最新版数据库
	res = sync_tb_db(tb_db_path, hn_db_path)
	print(res)	
	
	# 连接 sqlite 数据库
	db_cursor = connect_sqlite_db(hn_db_path)
	# 获取所有待发布的节点 id 列表
	pub_thought_ids = get_pub_thought_ids(db_cursor)
	# 获取每个节点的详细信息
	res = get_thought_data(db_cursor, pub_thought_ids)
	print(res)