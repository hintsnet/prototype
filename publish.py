# -*- coding: utf-8 -*-
from config import Config
from shutil import copyfile
import filecmp
import os
import oss2
import sqlite3
import sys

# 从 TB 数据目录同步最新的数据库
def sync_tb_db(tb_db_path, hn_db_path):
	if os.path.isfile(hn_db_path) and filecmp.cmp(tb_db_path, hn_db_path, shallow=False):
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

# 生成待发布节点列表的 html list
def gen_thought_index(thought_data):
	thought_items = ""
	for thought in thought_data:
		thought_items += '<li><a href="%s.html">%s</a></li>\n' % (thought['id'], thought['name'])
	index_body = "<ul>\n%s</ul>" % thought_items
	return index_body

# 获取节点的附件(多媒体文件)列表
def get_media_list(thought_id, local_dir):
	media_list = os.listdir("%s/%s/Notes" % (local_dir, thought_id))
	media_list.remove('notes.html')
	return media_list

def check_media_files(thought_id, local_dir, pub_dir, bucket_handle):
	media_list = get_media_list(thought_id, local_dir)
	for media in media_list:
		local_media = '%s/%s/Notes/%s' % (local_dir, thought_id, media)
		pub_media = "%s/media/%s" % (pub_dir, media)
		pub_note = '%s/%s.html' % (pub_dir, thought_id)
		if os.path.isfile(local_media):
			if os.path.isfile(pub_media) and filecmp.cmp(local_media, pub_media, shallow=False):
				print("媒体文件 %s 不需要同步!" % media)
			else:
				copyfile(local_media, pub_media)
				res = bucket_handle.put_object_from_file('hintsnet/tb/media/%s' % pub_media, local_media)
				file_replace_with(pub_note, media, media + "/eq_width")
				print("媒体文件 %s 同步状态: %s" % (media, res))
		else:
			pass
	return True

# 获取节点的笔记内容(如果有的话)
def get_thought_detail(thought_data, local_dir, pub_dir):
	for thought in thought_data:
		local_note = '%s/%s/Notes/notes.html' % (local_dir, thought['id'])
		pub_note = '%s/%s.html' % (pub_dir, thought['id'])
		if os.path.isfile(local_note):
			if os.path.isfile(pub_note) and filecmp.cmp(local_note, pub_note, shallow=False):
				pass
			else:
				copyfile(local_note, pub_note)
				file_replace_with(pub_note, '<!--BrainNotesBase-->', 'https://pimfans.oss-cn-beijing.aliyuncs.com/hintsnet/tb/media')
				with open(pub_note, "r", encoding="utf-8") as note_fh:
					note_content = note_fh.read()
				with open(pub_note, "w", encoding="utf-8") as note_fh:
					note_full_html = gen_html_page(thought['name'], note_content + sns_comment + '\n\n<META http-equiv=Content-Type content="text/html; charset=utf-8">')
					note_fh.write(note_full_html)
				media_list = get_media_list(thought['id'], local_dir)
				check_media_files(thought['id'], local_dir, pub_dir, bucket_h)
		else:
			with open(pub_note, "w", encoding="utf-8") as note_fh:
				note_full_html = '<p>暂无笔记</p>\n\n<META http-equiv=Content-Type content="text/html; charset=utf-8">'
				note_fh.write(note_full_html)
	return True

# 批量替换文件中满足条件的字符串
def file_replace_with(file, match_str, subst_str):
	new_content = ""
	with open(file, "rt", encoding="utf-8") as fh:
		new_content = fh.read().replace(match_str, subst_str)
	with open(file, "w", encoding="utf-8") as fh:
		fh.write(new_content)
	return True

# 把 html 内容写为文件
def write_content_to_file(content, pub_dir, filename):
	with open("%s/%s" % (pub_dir, filename), "w+", encoding="utf-8") as fh:
		fh.write(content)
	return True

# 给定 title 和 body, 包装为 html 页面
def gen_html_page(title, body):
	full_html = """
<html>
  <head>
	<title>%s</title>
	<meta name="viewport" content="width=device-width, initial-scale=1 user-scalable=no">
	<meta charset="utf-8">
	<style>
		img { width:95%%; }
	</style>
  </head>
  <body>
%s
  </body>
</html>
""" % (title, body)
	return full_html

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
	# 待发布文件所在目录
	tb_pub_basedir = Config.tb_pub_basedir
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
	thought_data = get_thought_data(db_cursor, pub_thought_ids)
	thought_idx = gen_thought_index(thought_data)
	
	sns_comment = '''
<h2>使用 GitHub 账号发表评论</h2>
<script src="https://utteranc.es/client.js"
	repo="hintsnet/discussions"
	issue-term="title"
	label="utterances"
	theme="github-light"
	crossorigin="anonymous"
	async>
</script>
	'''
	auth = oss2.Auth(Config.oss_acckey, Config.oss_accsec)
	bucket_h = oss2.Bucket(auth, Config.oss_epoint, Config.oss_bucket)
	
	html_body = gen_html_page(u"引思卡片索引", thought_idx)
	gen_html_page(html_body,"index.html")
	get_thought_detail(thought_data, local_tb_dir, tb_pub_basedir)
