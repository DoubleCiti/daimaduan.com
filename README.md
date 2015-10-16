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
4. `cd daimaduan && python runserver.py`
