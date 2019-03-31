Red[]

card_reactor: make reactor! [
  title: "新标题"
	cont: "新内容"
	html: is [rejoin [{
	  <html>
		  <head>
		    <meta http-equiv=Content-Type content="text/html; charset=utf-8" />
				<title>} title {</title>
			</head>
			<body>
			  <p>} cont {</p>
			</body>
		</html>
	}]]
]

cmd: ""
okay: "[OK]"
err: "[!]"

while [(cmd <> "quit") and (cmd <> "exit")] [
  cmd: ask "接下来做什么？"
  switch/default cmd [
    "new"    [ print [okay "创建新笔记" ] ]
		"view"   [ print [okay "查看 N 号笔记" ] ]
		"search" [ print [okay "搜索含有 X 的笔记"] ]
	  "edit"   [ print [okay "编辑 N 号笔记" ] ]
	  "del"    [ print [okay "删除 N 号笔记" ] ]
	] [ print [err "暂不支持该命令:" cmd] ]
]

quit