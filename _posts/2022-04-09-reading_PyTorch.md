---
title:  "PyTorch源码阅读"
layout: post
date: 2022-04-09 23:05:29
tags:  ["Deep Learning", "PyTorch", "源码阅读"]
syntaxHighlighter: yes
mathjax: true
---

工作后一直在用PyTorch编写模型，对于经常用到的一些API和类，结合搜索引擎基本上能够满足需求，但在这个过程中其实也存在一个认知较浅的问题，所谓“知其然却不知其所以然”，在日常使用中，我经常会产生一些疑问，比如：

- Tensor是PyTorch的核心，它的底层是怎么实现的？
- PyTorch的自动微分是怎么实现的？我如果要自定义一个算子，我该怎么处理它的forward和backward？
- PyTorch内部的优化器是怎么实现的？
- PyTorch数据相关的Dataset、DataLoader等是怎么做加速的？
- CUDA相关的内容，是如何和显卡配合工作的？如何设计模型以提高显卡利用率？
- ...

类似这种问题还有很多，细想了一下，其实有些内容可以通过阅读PyTorch文档和社区各位大佬的笔记来理解，但有些牵涉到底层实现的部分，最好还是需要自己亲自来阅读一下源码才能更深入的理解。

从PyTorch的github仓库可以看到，PyTorch源代码大概有53%是用CPP编写的，有35%左右是通过Python实现的，剩余还有一些CUDA、C、和OC的代码。对我个人，语言方面，Python还好说，但CPP/C平常用的很少，底子偏弱；代码量方面，目前整个仓库预估大概有40万行左右的代码，并且以每天约30个commits的速度缓慢增加，整体阅读显然是不太可能的，只能挑重要的，自己感兴趣的部分深入阅读，可以预想后面阅读过程一定不会太轻松。

<img src="http://qiniu.shihanmax.top/20220409224505_fGtDIf_%E6%88%AA%E5%B1%8F2022-04-09%20%E4%B8%8B%E5%8D%8810.45.01.jpeg" alt="sc_of_torch" style="zoom:50%;" />

<center>PyTorch源码语言分布</center>

之前除了看过一点点Python的源码之外，就几乎很少阅读过源码了，这块的经验也比较匮乏，目前也还没有整理好阅读节奏，后面初步计划，先从Python层的代码开始读起，等进入状态了之后再慢慢地深入到C实现。

这个页面就用来跟踪 & 记录进度吧。

阅读过程主要参考一下资料：

1. [OpenMMLab-PyTorch 源码解读系列](https://zhuanlan.zhihu.com/p/328674159)
2. [知乎-罗秀哲-PyTorch源码浅析](https://zhuanlan.zhihu.com/p/34629243)
