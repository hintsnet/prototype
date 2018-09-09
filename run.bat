@echo off
REM "设置 flask app 的入口脚本"
set FLASK_APP=hintsnet.py

REM "设置 flask app 的运行环境参数"
REM "请手动设置 APP 密钥，千万不要写入源码文件！"
echo set APP_SECRET_KEY=...
REM "请手动设置 NEO4J 数据库配置信息，千万不要写入源码文件！"
echo set NEO4J_DB_URI=...
echo set NEO4J_DB_USR=...
echo set NEO4J_DB_KEY=...

REM "启动 flask app"
flask run
