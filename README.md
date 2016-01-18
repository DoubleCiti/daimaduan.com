daimaduan.com
=============
[![Build Status](https://travis-ci.org/DoubleCiti/daimaduan.com.svg?branch=master)](https://travis-ci.org/DoubleCiti/daimaduan.com)

source code of daimaduan.com

## 项目依赖

* Python 2.7
* MongoDB 3.0+

## 本地运行开发服务器

1. 启动MongoDB
2. `cp daimaduan/default_settings.py daimaduan/config.cfg`
3. `python setup.py develop`
4. `CONFIG=config.cfg fab run`

## Assets

Flask Assets 提供了下面几个命令

```bash
python manage.py assets watch
python manage.py assets build
python manage.py assets clean
```

开发时，可以使用 watch 来自动编译脚本变更。

在部署到生产环境时，确保配置项

```ini
# daimaduan/default_settings.py
ASSETS_DEBUG = True
```

## message bus系统

daimaduan使用`Celery`来管理异步的任务, 启动`woker`的命令为:

```
celery -A daimaduan.bootstrap:celery worker -l info
```
