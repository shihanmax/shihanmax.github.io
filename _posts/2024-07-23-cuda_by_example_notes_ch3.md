---
title:  "GPU高性能编程CUDA实战（CUDA By Example）阅读笔记：3"
layout: post
date: 2024-07-23 21:58:58
tags:  ["CUDA", "HPC", "CUDA By Example Notes"]
syntaxHighlighter: yes
mathjax: true
---

更新中，全集：[《CUDA By Example》阅读笔记](http://shihanmax.top/tags/#CUDA%20By%20Example%20Notes)

本文是书籍《CUDA By Example》的阅读笔记（or 不信达雅的翻译），第三章 初识CUDA C。

# Chapter 3: **Introduction to CUDA C**

本章目标：

- 第一行CUDA C 代码
- 区分host代码和device代码
- 从host运行device代码
- device内存的使用方法
- 在CUDA兼容设备上查询系统信息

CUDA C将环境区分为host和device，前者指CPU和其内存，后者指GPU和其对应的显存。一个例子：

```cpp
#include <iostream>

__global__ void kernel(void) {
    // Kernel code goes here.
}

int main(void) {
    // Launch the kernel with a single block and a single thread.
    kernel<<<1, 1>>>();
    
    // Print "Hello, World!" to the console.
    printf("Hello, World!\n");

    return 0;
}
```

`__global__`声明该函数需要被CUDA编译器编译，并运行于device上。在host上调用kernel时，尖括号中包含的内容是调用时需要向device传递的参数，指示CUDA runtime如何启动这段device code。

来看一个示例：

```cpp
#include <iostream>
#include "book.h"

__global__ void add(int a, int b, int *c) {
    *c = a + b;
}

int main(void) {
    int c;
    int *dev_c;
    HANDLE_ERROR(cudaMalloc((void **) &dev_c, sizeof(int)));

    add<<<1, 1>>>(2, 7, dev_c);

    HANDLE_ERROR(cudaMemcpy(&c, dev_c,
                             sizeof(int),
                             cudaMemcpyDeviceToHost));
    printf("2 + 7 = %d\n", c);

    cudaFree(dev_c);
    return 0;
}
```

可知：

- 和普通的C函数一样，可以向kernel传参
- 在device上我们需要申请内存来完成数据存储等操作
    

`cudaMalloc()`表示在device上申请显存，第一个参数是一个指向保存结果的地址指针的指针，第二个参数是申请的空间大小。值得注意的是，CUDA C的简洁和强大部分源于其并没有显式地将host code和device code隔离开。

编程者应当使用合适的方法申请、使用和释放对应设备上的内存空间。以下是几个简单的准则：

- 通过cudaMalloc()申请的指针可以传递给设备上的函数；
- 通过cudaMalloc()申请的指针可以读写设备内存；
- 通过cudaMalloc()申请的指针可以传递给主机上的函数；
- 通过cudaMalloc()申请的指针不能读写主机内存；
    

总体而言，主机指针只能访问主机代码中的内存，而设备指针也只能访问设备代码中的内存。

如何查询设备的详细信息？可以使用`cudaGetDeviceCount()`，这个方法将返回一个`cudaDeviceProp`的结构，保存着设备描述、内存量、寄存器数量、线程束（Warp）中包含的线程数量等。在实际编程过程中，我们可能需要特定的功能，这些特定的功能可能对显卡的有一定的要求，我们可以将这些设备要求构造为一个`cudaDeviceProp`的结构体，并通过`cudaChooseDevice()`来选择满足要求的设备。


## 参考

1. [CUDA By Example](https://developer.nvidia.com/cuda-example)