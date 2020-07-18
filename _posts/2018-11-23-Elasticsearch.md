---
title: "Elasticsearch初探"
layout: post
date: 2018-11-23 00:00:00
categories: "工具"
tags: ["language", "ElasticSearch"]
syntaxHighlighter: yes
---

## Elasticsearch ##

**Elasticsearch**是一个高伸缩的开源全文搜索和分析引擎，它可以快速地、近实时的存储，搜索和分析大规模的数据。一般被用作底层引擎/技术，为具有复杂搜索功能和要求的应用提供强有力的支撑。

<!--more-->

## 使用场景：

- 电商网站，商品的检索
- 日志或交易数据的统计、汇报、总结
- 在百万或十亿条数据中查找特定的问题

## 基本概念：

### 近实时 NRT

ES平台接近实时，从文档索引到可搜索的时间非常短暂。

### 集群 Cluster

集群是一个或多个**节点（Server）**的集合，它们联合起来保存所有的数据，并且可以在任何一个节点上进行索引和搜索操作。集群由唯一的名称标识，默认是elasticsearch。一个节点只能属于一个集群。你也可以有多个集群，每个集群都有一个唯一的名字。

### 节点 Node

一台独立的服务器就是一个节点，是集群的一部分，参与集群的索引与检索。同样地，节点拥有一个唯一的名字，默认是一个随机的UUID，当然也可以定制。节点名称很重要，可以帮助区分集群服务器和节点的对应关系。

节点通过配置集群名称之后，就可以加入指定的集群，默认情况下节点都会加入到默认集群elasticsearch。

### 索引 Index

索引是具有相似特点的文档集合，如客户数据，产品目录等。

索引由名称（只能使用小写字母）来标识，该名称用于对文档的索引、搜索、更新和删除等操作。单个集群中，可以定制任意数量的索引。

### 文档 Document

文档是可以被索引的基本单位，如用一个文档保存客户的数据，或单个商品的数据。文档用JSON表示，在索引中可以存储大量文档。

### 分片和副本 Shards & Replicas

一个索引可能存储海量数据，有可能超过单个节点的硬盘容量，为了解决这个问题，ES提供了分片功能，即索引细分。即创建索引时，可以定义分片数，每个分片具备索引的全部功能，可以存放在集群中的任何一个节点上。

分片很重要，原因如下：

- 允许水平分割/缩放内容量
- 允许并行地分发操作到多个节点的分片上，从而提高性能和吞吐量

分片分发机制，以及在检索中如何汇总到搜索响应的过程完全由ES管理，并且是透明的。

在网络/云环境中，故障可能会发生，此时，分片会非常有用，强烈建议使用故障转移机制，以防止节点脱机。ES允许将索引的分片复制多份，即副本。

副本的重要性：

- 在分片/节点故障时，提高可用性（注意，副本与原始/主分片不能分配在同一个节点上）
- 允许扩展搜索量，可对所有副本执行搜索

每个索引可以分为多个分片。每个索引也可以被复制零次（意味着没有副本）或多次。一旦复制，每个索引将具有主分片（原始分片）和副分片（主分片的副本）。可以在创建索引时根据索引定义分片和副本的数量。创建索引后，您可以随时动态更改副本数，但不能更改分片数。

默认情况下，每个索引都会被分配5个主分片和1一个复制分片，这意味着如果你的集群中有两个节点，你的索引将会有5个主分片和5个复制分片，总共有10个分片。

每个分片是一个Lucene index，一个Lucene index中可以有很多的文档，截至 LUCENE-5843，最多2147483519(= Integer.MAX_VALUE - 128) 个文档。可以使用 _cat/shards api监视分片大小。

[关于全文检索，Lucene和倒排索引](http://www.cnblogs.com/xing901022/p/3933675.html)


## ES初探

### 安装、启动

安装过程参考ES官网，注意ES依赖Java8环境。

启动方法：

    cd elasticsearch-5.4.1
    ./bin/elasticsearch

### REST API

ES提供了非常强大的REST API与集群进行通讯。

API能力：

- 检查集群、节点、索引的运行状态和统计信息
- 管理集群、节点、索引和元数据
- 执行CRUD，针对索引进行搜索
- 执行高级操作，如分页、排序、过滤、脚本、聚合等

#### 查看集群、节点、索引

    GET /_cat/health?v
    	# 查看节点健康
    
    GET /_cat/nodes?v
    	# 查看集群节点列表
    
    GET /_cat/indices?v
    	# 查看所有索引，如果集群中只有一个节点，则此索引的健康值为yellow（副本未分配）

#### 索引的创建和删除

	PUT /bank?pretty
		# 创建名为testindex的索引
	
	DELETE /bank?pretty
		# 删除testindex索引

#### 文档的创建、修改和删除

	PUT /bank/account/1?pretty
	{
		"name": "John Doe"
	}
		# 索引一篇文档，类型为sometype，ID为1（此ID也可不指定）索引
	
	PUT /bank/account/1?pretty
	{
		"name": "Maxan"
	}
		# 如果对已存在的文档修改内容后，再次执行索引，ES会使用一个新文档取代旧文档（重建索引）
	
	POST /bank/account?pretty
	{
		"name": "Tom"
	}
		# 没有指定ID，使用POST方法取代PUT
	
	POST /bank/account/1/_update?pretty
	{
		"doc": { "name": "Maxan", "age": 24}
	}
		# 对id为1的文档执行更新，ES会删除旧文档，索引新文档
	
	DELETE /bank/account/1?pretty
		# 删除ID为1的文档

#### 批处理

	POST /bank/account/_bulk?pretty
	{"index": {"_id": "1"}}
	{"name": "Tom hanks"}
	{"index": {"_id": "2"}}
	{"name": "Jack"}
	{"update": {"_id": "1"}}
	{"doc": {"name": "Hello World my name is ES"}}
	{"delete": {"_id": "2"}}
	
		# 上面的请求批量索引了两篇文档，注意：最后要有空行


#### 查询

	GET /_search?q=*&sort=account_number:asc&pretty
		# 在所有索引下查询文档（方式1：通过REST request URI 方式发送查询参数）
	GET /bank/_search?q=*&sort=account_number:asc&pretty
		#在bank下查询文档
	GET /bank/_search
	{
	  "query": { "match_all": {} },
	  "sort": [
			{ "account_number":"asc" }
	  ]
	}
		# 使用方式二查询（通过REST request body）

返回结果解释

- took： 查询时间（ms）
- time_out: 是否超时
- _shards: 查询了多少分片
- hits: 查询结果
- hits.total: 符合我们查询条件的文档总数
- hits.hits: 实际查询结果数组（默认为前10个文档）
- hits.sort: 对结果进行排序的键（如果没提供，则默认使用_score进行排序）
- hits._score:
- max_score:

### 查询语言介绍（Query DSL）

match_all

	GET /bank/_search
	{
	  "query": { "match_all": {} }
	}
		# "query": 指定查询定义
		# "match_all": 查询类型
		# "size": 返回结果数
		# "from": 起始位置
		# "sort": {"age" : { "order": "desc"}}  # 按age降序排序
		# "_source": {"name", "age"}

match

	GET /bank/_search
	{
	  "query": { "match": { "address": "mail Goodson" } }
	}
		# "match": 指针对特定字段或一组字段进行搜索，上例返回address中包含"mail"或"Goodson"的文档

match_phase

	GET /bank/_search
	{
	  "query": { "match_phrase": { "address": "mail Goodson" } }
	}
		# 返回包含"main Goodson"短语的文档

#### bool query

must

	GET /bank/_search
	{
	  "query": {
	    "bool": {
	      "must": [
	        { "match": { "address": "mill" } },
	        { "match": { "address": "lane" } }
	      ]
	    }
	  }
	}
		# 查询address中既包含"mail"又包含"lane"的文档

should

	GET /bank/_search
	{
	  "query": {
	    "bool": {
	      "should": [
	        { "match": { "address": "mill" } },
	        { "match": { "address": "lane" } }
	      ]
	    }
	  }
	}
		# should条件中只要有一条满足就可返回

must_not

	GET /bank/_search
	{
	  "query": {
	    "bool": {
	      "must_not": [
	        { "match": { "address": "mill" } },
	        { "match": { "address": "lane" } }
	      ]
	    }
	  }
	}
		# must_not，所有条件都不应该满足

#### filter

查询结果中_score字段代表查询分数，是一个数值，表示匹配度，越高说明越匹配。

布尔查询支持filter子句，它允许使用查询语句限制其它子句的匹配结果，同时不会计算文档的得分。

	GET /bank/_search
	{
	  "query": {
	    "bool": {
	      "must": { "match_all": {} },
	      "filter": {
	        "range": {
	          "balance": {
	            "gte": 20000,
	            "lte": 30000
	          }
	        }
	      }
	    }
	  }
	}
		# 查询余额balance在20000到30000之间的结果

#### 执行聚合
	GET /bank/_search
	{
	  "size": 0,
	  "aggs": {
	    "group_by_age": {
	      "range": {
	        "field": "age",
	        "ranges": [
	          {
	            "from": 20,
	            "to": 30
	          },
	          {
	            "from": 30,
	            "to": 40
	          },
	          {
	            "from": 40,
	            "to": 50
	          }
	        ]
	      },
	      "aggs": {
	        "group_by_gender": {
	          "terms": {
	            "field": "gender.keyword"
	          },
	          "aggs": {
	            "average_balance": {
	              "avg": {
	                "field": "balance"
	              }
	            }
	          }
	        }
	      }
	    }
	  }
	}
		# 按年龄段分组，按性别分组，最终得到每个年龄段的男女平均账户余额

2018/11/23 16:40:32

参考：[https://github.com/13428282016/elasticsearch-CN/wiki/es-gettting-started]
