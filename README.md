daimaduan.com
=============
[![Build Status](https://travis-ci.org/DoubleCiti/daimaduan.com.svg?branch=master)](https://travis-ci.org/DoubleCiti/daimaduan.com)

source code of daimaduan.com

## 项目依赖

* Python 2.7
* MongoDB 3.0+
* node.js

## 开发环境配置

在运行服务器程序之前, 需要先准备好本地的开发坏境

```
gem install sass
npm install -g bower scss uglifyjs bower
bower install
```

## 本地运行开发服务器

1. 启动MongoDB
2. `cp daimaduan/default_settings.py daimaduan/custom_settings.py`
3. `python setup.py develop`
4. `fab run`

## message bus系统

daimaduan使用`Celery`来管理异步的任务, 启动`woker`的命令为:

```
celery -A daimaduan.bootstrap:celery worker -l info
```
