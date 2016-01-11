daimaduan.com
=============
[![Build Status](https://travis-ci.org/DoubleCiti/daimaduan.com.svg?branch=master)](https://travis-ci.org/DoubleCiti/daimaduan.com)

source code of daimaduan.com

## 项目依赖

* Python 2.7
* MongoDB 3.0+

## 本地运行开发服务器

1. 启动MongoDB
2. `cp daimaduan/config.cfg.example daimaduan/config.cfg`
3. `python setup.py develop`
4. `python manage.py runserver`

## Assets

Flask Assets 提供了下面几个命令

    python manage.py assets watch
    python manage.py assets build
    python manage.py assets clean

开发时，可以使用 watch 来自动编译脚本变更。

在部署到生产环境时，确保配置项
    
    # daimaduan/default_settings.py
    ASSETS_DEBUG = True
