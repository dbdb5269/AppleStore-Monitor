# 概述

本项目应用主要用来监测Apple Store线下直营店货源情况，主要使用Python实现。

本项目fork自[AppleStore-Monitor](https://github.com/LennonChin/AppleStore-Monitor)

本项目在原有功能的基础上修改为pushdeer推送和支持iPhone 15系列

# 最近更新

- [x] 23.9.18 修改为pushdeer推送以及支持iPhone15 pro 系列

# 安装

```bash
# 拉取代码 
git clone https://github.com/LennonChin/AppleStore-Monitor.git

# 进入目录
cd AppleStore-Monitor

# 安装依赖
pip install -r requirements.txt
```

# 使用Pushdeer推送通知

【强烈建议配置】如不配置则没有通知功能。

本监控提供了pushdeer监控的功能，可以在监控到有货源时将消息通过Pushdeer进行推送。如要启用该功能，首先需要注册安装pushdeer，详细可参考文档：

[pushdeer接入](https://www.pushdeer.com/)

配置完毕后，记下相关的Access Key，后面配置时需要用到。


# 开始配置

使用`python monitor.py config`命令进行配置，可以配置多个监控商品：

```bash
$> python monitor.py config
--------------------
[0] Apple Watch
[1] AirPods
[2] iPhone 13
选择要监控的产品：1
--------------------
[0] AirPods
[1] AirPods Max
选择要监控的产品子类：1
--------------------
[0] AirPods Max - 银色
选择要监控的产品型号：0
--------------------
是否添加更多产品[Enter继续添加，非Enter键退出]：
--------------------
[0] Apple Watch
[1] AirPods
[2] iPhone 13
选择要监控的产品：2
--------------------
[0] iPhone 13 Mini
[1] iPhone 13
[2] iPhone 13 Pro
[3] iPhone 13 Pro Max
选择要监控的产品子类：3
--------------------
...
[11] 512GB 远峰蓝色
...
选择要监控的产品型号：11
--------------------
是否添加更多产品[Enter继续添加，非Enter键退出]：n
选择计划预约的地址：
请稍后...1/3
--------------------
[0] 北京
[1] 上海
...
请选择地区序号：1
请稍后...2/3
请稍后...3/3
--------------------
[0] 黄浦区
...
请选择地区序号：0
正在加载网络资源...
--------------------
选择的计划预约的地址是：上海 上海 黄浦区，加载预约地址周围的直营店...
[0] 香港广场，地址：上海市黄浦区淮海中路 282 号
[1] 南京东路，地址：上海市黄浦区南京东路 300 号
[2] 上海环贸 iapm ，地址：上海市徐汇区淮海中路 999 号
[3] 浦东，地址：上海市浦东新区陆家嘴世纪大道 8 号
[4] 环球港，地址：上海市普陀区中山北路 3300 号
[5] 五角场，地址：上海市杨浦区翔殷路 1099 号
[6] 七宝，地址：上海市闵行区漕宝路 3366 号 
[7] 苏州，地址：苏州市苏州工业园区
[8] 无锡恒隆广场，地址：无锡市梁溪区
[9] 天一广场，地址：宁波市海曙区碶闸街 155 号
[10] 杭州万象城，地址：杭州市江干区富春路 701 号
[11] 西湖，地址：杭州市上城区平海路 100 号
排除无需监测的直营店，输入序号[直接回车代表全部监测，多个店的序号以空格分隔]：7 8 9 10 11
已选择的无需监测的直营店：苏州，无锡恒隆广场，天一广场，杭州万象城，西湖
--------------------
输入pushdeer Access Key[如不配置直接回车即可]：
--------------------
输入扫描间隔时间[以秒为单位，默认为30秒，如不配置直接回车即可]：
--------------------
是否在程序异常时发送通知[Y/n，默认为n]：
--------------------
扫描配置已生成，并已写入到apple_store_monitor_configs.json文件中
请使用 python monitor.py start 命令启动监控
```

配置完成后，会在当前目录下生成一个[apple_store_monitor_configs.json](https://github.com/LennonChin/AppleStore-Monitor/blob/main/apple_store_monitor_configs.json)文件：

```json
{
  "selected_products": {
    "MU2W3CH/A": [
      "iPhone 15 Pro Max",
      "512GB 蓝色"
    ]
  },
  "selected_area": "天津 天津 河西区",
  "exclude_stores": [
    "R648",
    "R609",
    "R478",
    "R557"
  ],
  "notification_configs": {
    "pushdeer": {
      "access_key": ""
    }
  },
  "scan_interval": 10,
  "alert_exception": true
}
```

如果你明白每项的意思，也可以手动填写该JSON文件，不过一定要按照上面例子中的层级，尤其是`selected_products`部分。


# 启动监控

接下来只需要用下面的命令启动监控即可：

比如前台启动：

```bash
python monitor.py start
```

或者后台启动：

```bash
nohup python -u monitor.py start > monitor.log 2>&1 &
```

# 通知效果

4种情况会通知：

1. 启动时通知，以确认相关信息是否正确，启动是否成功。
2. 扫描到有货源时会通知。
3. 每天6:00 ~ 23:00整点报时，以确保程序还正常运行。
4. 程序异常时会通知，如不是致命异常，不用理会。
