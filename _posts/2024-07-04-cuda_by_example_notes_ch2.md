---
title:  "GPU高性能编程CUDA实战（CUDA By Example）阅读笔记：2"
layout: post
date: 2024-07-18 00:55:16
tags:  ["CUDA", "HPC", "CUDA By Example Notes"]
syntaxHighlighter: yes
mathjax: true
---

更新中，全集：[《CUDA By Example》阅读笔记](http://shihanmax.top/tags/#CUDA%20By%20Example%20Notes)

本文是书籍《CUDA By Example》的阅读笔记（or 不信达雅的翻译），第二章 环境准备。

# Chapter 2: Getting Started

本章目标：

- 下载本书涉及的所有软件
    
- 搭建CUDA C编程环境
    

## 开发环境

要使用CUDA C编程，需要准备以下工具：

- 支持CUDA的图形处理器（GPU）
    
- NVIDIA设备驱动
    
- CUDA开发工具包
    
- 标准C编译器
    

自2006年GeForce 8800 GTX发布以来，基本上所有的NVIDIA都支持CUDA。因此找到一个支持CUDA的GPU并不难（显存大于256MB）。

我们需要安装NVIDIA显卡驱动软件，以提供软件和CUDA设备之间通讯的桥梁。一般安装最新版本即可。

有了GPU和驱动，我们便可以编译、运行CUDA C了，由于我们编写的程序需要运行在两个不同的处理器上（CPU、GPU），显然我们需要两个编译器，分别用于GPU和CPU程序的编译。


## 参考

1. [CUDA By Example](https://developer.nvidia.com/cuda-example)