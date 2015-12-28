daimaduan.com
=============
[![Build Status](https://travis-ci.org/DoubleCiti/daimaduan.com.svg?branch=master)](https://travis-ci.org/DoubleCiti/daimaduan.com)

source code of daimaduan.com

## 项目依赖

* Python 2.7
* MongoDB 3.0+
* NodeJS v4.0.0+

## 如何开始?

### 使用virtualenv管理依赖

1. `pip install virtualenv`
2. `virtualenv .venv`
3. `source .venv/bin/activate`

**注意: 以下步骤都假定你已经成功安装并运行`virtualenv`**

### 编译本地静态资源

1. `node install`
2. `fab assets`

### 本地运行开发服务器

1. 启动MongoDB
2. `cp daimaduan/config.cfg.example daimaduan/config.cfg`
3. 根据你的环境修改`daimaduan/config.cfg`
4. `fab run_server`
