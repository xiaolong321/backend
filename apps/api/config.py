#!/usr/bin/python
# -*- coding: utf-8 -*-
DEFAULT_CONF = {
	"adKey":"", #广告配置：广告key
	"adWho": "self", #广告配置 ：使用谁的广告,为self是，展示自己的banner广告 
	"adLink": "http://ad.qpy.io/api/adlink", #当adWho为self时，该选项生效，表示点击banner广告时跳转的链接
	"adBanner": "http://ad.qpy.io/api/adbanner", #当adWho为self时，该选项生效，表示底部广告展示的banner 320x50
	"ver": "1", #版本配置 : 最新的版本数，如果该数字大于当前app版本数，则会提示更新
	"verName": "1.0", #最新的版本名
	"verDesc": "This is the newest version", #版本配置，最新的版本描述
	"curVer": "1", #版本配置 : 当前app版本数
	"curMarket": "QPY.IO Play", #当前发布市场
	"type": "link", #升级apk的打开模式
	"link": "http://play.qpy.io", #最新版本下载地址
	"updateQ": "24", #自动检查更新的频率，小时
	"appFeedContent":"Give us your feedback:", #关于内容，给反馈
	"appFeedUrl":"http://qpy.io/", #关于内容，反馈链接
	"appAbout":"This app is exported by QPY.IO", #关于内容，产品描述 
	"appUrl": "http://play.qpy.io", #关于内容，产品链接
	#扩展配置 
	"ext_conf": {
	    "notify_msg": "Powered by QPY.IO", #全局底部文字广告内容
	    "notify_act": "http://qpy.io", #全局底部文字广告link
	    "notify_check": "io.qpy.noadplugin", #底部文字广告不展示的插件名
	    "msg_ver": "0", #启动app后推送的消息版本
	    "msg_msg": "Welcome", #内容
	    "msg_type": "link", #启动app后推送的消息打开方式
	    "msg_param": "",  #启动app推送的消息 参数
	    "msg_link": "http://ad.qpy.io/page/welcome", 
	    "conf_ga_gtid": "", #google 统计ID
	    "conf_feedback_email": "support@qpython.com", #发送反馈接收的信箱
	    "conf_pro_url": "market://details?id=io.qpy.noadplugin", #pro版本URL
	    "conf_rate_url": "http://facebook.com/qpy.io", #评分的URL
	    #用户自定义的配置项
	    "other_conf": {
	    }
	},
	#广告配置
	"ext_ad": {} 
}