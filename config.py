import os

# 从操作系统的环境变量中获取一些关键的运行环境参数
# 如果没有获取到，就使用预设的默认值
class Config(object):
	SECRET_KEY = os.environ.get('APP_SECRET_KEY') or 'you-will-never-guess'
	NEO4J_DB_URI = os.environ.get('NEO4J_DB_URI') or 'bolt://localhost:7687'
	NEO4J_DB_USR = os.environ.get('NEO4J_DB_USR') or 'neo4j'
	NEO4J_DB_KEY = os.environ.get('NEO4J_DB_KEY') or 'neo4j'