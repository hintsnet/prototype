# -*- coding: utf-8 -*-
from config import Config
from shutil import copyfile
import filecmp
import os
import oss2
import re
import sqlite3
import sys

# 定义文件同步方法
def sync_file(src_file_path, dest_file_path):
	# 目标文件是否已存在?
	# 源文件与目标文件是否无差别?
	if os.path.isfile(src_file_path) and \
		filecmp.cmp(src_file_path, dest_file_path, shallow=False):
		return "文件不需要同步!"
	else:
		# 把源数据库文件复制为目标文件
		res = copyfile(src_file_path, dest_file_path)
		return "文件已经同步到: %s" % res

# 定义 sqlite3 数据库游标获取方法
def connect_sqlite_db(db_file_path):
	# 连接给定的 sqlite3 数据库
	conn = sqlite3.connect(db_file_path)
	# 获得数据库游标
	cursor = conn.cursor()
	return cursor

# 通用 sqlite3 数据查询方法, 用于执行各种 sql 查询
def query_db(db_cursor, sql):
	# 执行给定的 sql 语句
	db_cursor.execute(sql)
	# 获取 sql 查询成功后获得的记录
	records = db_cursor.fetchall()
	return records

# 获取所有标记为"可发布"的节点的 id, 以列表形式返回
def get_pub_thought_ids(db_cursor):
	# 定义 sql 语句, 查询所有可以发布的节点 id
	sql = """
	select dest.id
	from thoughts as src inner join links inner join thoughts as dest
	where src.id = thoughtIdA and dest.id = thoughtIdB and
	links.meaning = 5 and src.name = "可发布"
	"""
	results = query_db(db_cursor, sql)
	thought_ids = [result[0] for result in results]
	return thought_ids

# 定义一个方法, 给定一个节点 id, 获取各种与之相关的数据
def get_thought_data(db_cursor, thought_id):
	# 定义 sql 语句, 对每个节点进行相关数据的查询
	sql = """
	select name from thoughts where id="%s"
	""" % thought_id
	results = query_db(db_cursor, sql)
	# 把查询结果转化为 python dict
	thought_data = { \
		'id': thought_id, \
		'name': results[0][0] \
	}
	return thought_data

# 定义一个方法, 以 html list 格式生成待发布节点列表
def gen_thought_index(db_cursor, thought_ids):
	thought_items = ""
	for thought_id in thought_ids:
		thought_data = get_thought_data(db_cursor, thought_id)
		thought_items += '<li><a href="%s.html">%s</a></li>\n' % (thought_data['id'], thought_data['name'])
	index_body = "<ul>\n%s</ul>" % thought_items
	return index_body

# 获取节点的附件(多媒体文件)列表
def get_media_file_list(thought_id, local_dir):
	media_list = os.listdir("%s/%s/Notes" % (local_dir, thought_id))
	media_list.remove('notes.html')
	return media_list

# 定义一个方法, 把本地文件上传到 OSS 平台 (目前为 aliyun-oss)
def sync_file_to_oss(bucket_handle, oss_dir, local_file, to_pub_file):
	if os.path.isfile(to_pub_file) and \
		filecmp.cmp(local_file, to_pub_file, shallow=False):
		return "本地文件 %s 不需要同步!" % local_file.split('/')[-1]
	else:
		copyfile(local_file, to_pub_file)
		ret = bucket_handle.put_object_from_file('%s/%s' % (oss_dir, to_pub_file), local_file)
		return "本地文件 %s 同步状态: %s" % (local_file, ret)

# 批量替换文件中满足条件的字符串
def file_replace_with(file, match_str, subst_str):
	new_content = ""
	with open(file, "rt", encoding="utf-8") as fh:
		new_content = fh.read().replace(match_str, subst_str)
	with open(file, "w", encoding="utf-8") as fh:
		fh.write(new_content)
	return True

# 定义一个方法, 检查本地待发布文件的同步状态
def sync_media_files(bucket_handle, thought_id, local_dir, to_pub_dir):
	rets = ""
	media_file_list = get_media_file_list(thought_id, local_dir)
	for media_file in media_file_list:
		local_media_file = '%s/%s/Notes/%s' % (local_dir, thought_id, media_file)
		to_pub_media_file = "%s/media/%s" % (to_pub_dir, media_file)
		pub_note_file = '%s/%s.html' % (to_pub_dir, thought_id)
		ret = sync_file_to_oss(bucket_handle, "hintsnet/tb/media", local_media_file, to_pub_media_file)
		file_replace_with(pub_note_file, to_pub_media_file, to_pub_media_file + "/eq_width")
		rets += ret + "\n"
	return rets

# 定义一个方法, 读取文件内容(utf8 编码)
def get_file_content(file):
	content = False
	with open(file, "r", encoding="utf-8") as fh:
		content = fh.read()
	return content

# 定义一个方法, 把本地笔记内容转换为适合公网发布的笔记内容
def make_local_note_public(local_note_content):
	pub_note = \
		local_note_content.replace('<!--BrainNotesBase-->', \
		'https://pimfans.oss-cn-beijing.aliyuncs.com/hintsnet/tb/media')
	return pub_note

# 获取节点的笔记文件
# 如果没有找到笔记文件, 则返回 False
def get_thought_note_file(local_dir, thought_id):
	thought_note_file = '%s/%s/Notes/notes.html' % (local_dir, thought_id)
	if os.path.isfile(thought_note_file):
		return thought_note_file
	else:
		return False

# 把内存的内容写为文件(utf8 编码)
def write_content_to_file(content, file):
	with open(file, "w+", encoding="utf-8") as fh:
		ret = fh.write(content)
	return ret

# 给定 title 和 body, 包装为 html 页面
def gen_full_html(title, body):
	full_html = """
<html>
  <head>
	<title>%s</title>
	<meta name="viewport" content="width=device-width, initial-scale=1 user-scalable=no">
	<meta http-equiv=Content-Type content="text/html; charset=utf-8">
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

def gen_site_index_file(db_cursor, thought_ids, to_pub_dir):
	# 生成待发布节点(网页链接入口)的索引
	thought_idx = gen_thought_index(db_cursor, thought_ids)
	# 为节点索引生成完整的 html 页面内容
	index_full_html = gen_full_html("引思卡片索引", thought_idx)
	# 把节点索引 html 内容发布为 index.html 页面
	ret = write_content_to_file(index_full_html, "%s/index.html" % to_pub_dir)
	return ret

# 定义一个方法, 针对每个待发布的节点 id, 逐一生成相关的笔记节点
def gen_site_note_files(db_cursor, bucket_h, thought_ids, local_dir, to_pub_dir):
	rets = ""
	for thought_id in thought_ids:
		# 获取当前节点 id 对应的各项信息
		thought_data = get_thought_data(db_cursor, thought_id)
		# 定义当前节点对应的待发布节点文件路径
		pub_note_file = "%s/%s.html" % (to_pub_dir, thought_id)
		# 获取当前节点对应的本地笔记文件路径(有可能为 False)
		local_note_file = get_thought_note_file(local_tb_dir, thought_id)
		# 定义变量, 保存待发布的笔记内容
		to_pub_note_content = ""
		# 尝试获取本地笔记文件的内容(如果笔记不存在, 则使用默认内容)
		if local_note_file != False:
			# 定义本地笔记文件名
			local_note_content = get_file_content(local_note_file)
			# 本地笔记内容公开化(生成基于 oss 的图片链接)
			to_pub_note_content = make_local_note_public(local_note_content)
			# 把本地图片上传到网络
			ret = sync_media_files(bucket_h, thought_id, local_dir, to_pub_dir)
			rets += ret + "\n"
		else:
			to_pub_note_content = "<h4>此节点暂无笔记</h4>"
		# 基于待发布笔记内容, 生成 html 内容
		to_pub_note_html = gen_full_html(thought_data['name'], to_pub_note_content)
		# html 文件内容存为文件, 以便上传到服务器
		write_content_to_file(to_pub_note_html, pub_note_file)
	# 去除返回信息中多于的换行符
	rets = re.sub("\n+", "\n", rets)
	return rets

# 主程序入口处
if __name__ == '__main__':
	# ---- 修复 cmd.exe 中文打印问题 ----
	sys.stdout = open(sys.stdout.fileno(), \
		mode='w', encoding='utf8', buffering=1)
	
	# ---- 获取环境变量中的路径设置 ----
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
	
	# ---- 从 TB 工作目录同步最新版数据库 ----
	sync_status = sync_file(tb_db_path, hn_db_path)
	# 打印数据库同步结果
	print("数据库同步状态: [ %s ]" % sync_status)
	
	# ---- 启动数据库/图床等工具的访问接口 ----
	# 获取 sqlite 数据库游标对象
	db_cursor = connect_sqlite_db(hn_db_path)
	# 获取 aliyun oss 的 bucket 操作对象
	auth = oss2.Auth(Config.oss_acckey, Config.oss_accsec)
	bucket_h = oss2.Bucket(auth, Config.oss_epoint, Config.oss_bucket)

	# ---- 收集待发布内容 ----
	# utteranc.es 提供的评论插件代码
	sns_comment_github = '''
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
	# 获取所有待发布的节点 id 列表
	pub_thought_ids = get_pub_thought_ids(db_cursor)
	# 生成网站的索引页面
	ret = gen_site_index_file(db_cursor, pub_thought_ids, tb_pub_basedir)
	print("索引文件写入状态: [ %s ]" % os.path.isfile(tb_pub_basedir + "/index.html"))
	# 生成单个笔记页面
	ret = gen_site_note_files(db_cursor, bucket_h, pub_thought_ids, local_tb_dir, tb_pub_basedir)
	print("笔记文件写入状态: [\n%s]" % ret)
