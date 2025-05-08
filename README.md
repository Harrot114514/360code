# 360code
A debug mode password generator tool for "360 kids watch".<p>
一个“360儿童手表”的调试模式密码生成工具<p>
20# 一定看完简介
B站主页:[不会起名的萝卜君](https://space.bilibili.com/1732976071?spm_id_from=333.1007.0.0)
## 使用方法
### 直接运行
对应自己的系统，直接下载编译好的发行文件，运行即可;
### 从源代码运行
#### 一.Windows
1.下载源码
2.确保自己的系统装有Python,打开cmd,输入下面代码检查
~~~
python -V
~~~
部分系统需使用一下代码
~~~
python3 -V
~~~
3.安装依赖
~~~
pip install webbrowser
~~~
4.双击使用即可
## 页面介绍&数据获取方法
### 页面介绍
### 各数据获取方式
#### 一.IMEI
最简单的
在手表设置内的关于界面即可找到(如下图)
![步骤一](https://github.com/Harrot114514/360code/blob/main/photos/IMG_20250508_222149.jpg "步骤一")
![步骤二](https://github.com/Harrot114514/360code/blob/main/photos/IMG_20250508_222233.jpg "步骤二")
![步骤三](https://github.com/Harrot114514/360code/blob/main/photos/IMG_20250508_222311.jpg "步骤三")
#### 二.QRCode
解码手表绑定码即可获得  
可通过下网站解码
[草料二维码解码器](https://cli.im/deqr)  
解码示范  'http://baby.360.cn/wap/index.html?qr=xxxxxxxxxxxxxxxx&c=xxxxxxxxxxxxxxxx&t=W920P'  
其中"qr=xxxxxxxxxxxxxxxx"即是(应该，我再找不到二维码了，并且解码内容固定)