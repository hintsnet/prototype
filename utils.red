;; 常用工具函数汇总
Red [needs: 'view]

; 生成从 1 到 num 的整数序列
range: function [num [integer!]] [
	collect [
		repeat i num [keep i]
	]
]

; 把字符串列表扁平化, 然后再做操作, 比如打印
flatten_and_proc: function [a_function a_list] [
	a_function [rejoin a_list]
]

; 弹出提示信息, 并在规定时间内关闭
msgbox: function [;-- based on work by Nodrygo
	"显示一条提示消息, 超过给定时间后自动消失"
	msg			[string!]	"希望显示的消息"
	seconds	[time!]		"停留的秒数"
] [
	view/flags [
		title "提示"
		msg-text: text msg center return	; 在文本组件中居中显示提示消息
		OK-btn: button "好的" [unview]			; 点击按钮可关闭窗口
		rate seconds on-time [unview]			; 2 秒后自动关闭按钮
		do [															; 居中显示 OK 按钮
			OK-btn/offset/x: 
			  msg-text/offset/x			+
			  (msg-text/size/x / 2)	-
				(OK-btn/size/x / 2)]
	] [modal popup]
]
