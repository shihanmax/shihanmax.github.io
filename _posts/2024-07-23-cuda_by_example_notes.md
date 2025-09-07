---
title:  "《GPU高性能编程CUDA实战（CUDA By Example）》阅读笔记 合集"
layout: post
date: 2024-07-31 23:18:18
tags:  ["CUDA", "HPC"]
syntaxHighlighter: yes
mathjax: true
---

* 导航
{:toc #markdown-toc}

⌛️  更新中..（last update: 2024-07-31）


> Changelog:
> - 2024-07-31: 更新第四章：Parallel Programming in CUDA C
> - 2024-07-23: 更新第三章：Introduction to CUDA C
> - 2024-07-18: 更新第二章：Getting Started
> - 2024-07-04: 更新第一章：Why CUDA? Why Now?

<hr/>
<br/>


本文是书籍《CUDA By Example》的阅读笔记（or 不“信达雅”的翻译）。

## 第一章：为什么要用 CUDA C (Why CUDA? Why Now?)

### 并行计算时代

并行计算（parallel computing）之前并不被太多关注，但近几年局面发生了一些变化。

本章目标：

- 认识并行计算的重要性
    
- GPU计算、CUDA简史
    
- 了解几个成功的CUDA C应用
    

2010年左右，消费级计算机基本上都开始配备多核中央处理器，并行计算技术也逐渐开始引入消费电子如手机、音乐播放器等。这一领域发展迅速，这要求软件开发者熟悉多种并行训练平台&技术。

30年来，提升消费级计算机性能的一大手段是提升中央处理器的时钟频率（1MHz->4GHz），但受集成电路的限制，时钟频率不能无限制增加， 这要求硬件制造商考虑替代的性能提升方案。

超级计算机也采用增加处理器数量的方式来提升性能，个人计算机后来也逐渐受到启发，在提升单核时钟频率的同时，逐渐开始采用多核心CPU。

### GPU运算的兴起

通过GPU进行通用计算也是个比较新颖的概念，但用图像处理器做运算也有一定的历史。

在1980s-1990s间，诸如Windows之类的图形界面操作系统的发展也促使图形处理器市场开始形成和发展。早在1990s就有个人电脑用户购买2D显示加速器。这种加速器可以辅助进行硬件级别的位图运算，提升显示性能。

与此同时，一家做专业计算的名为Silicon Graphics的公司逐渐将3D图形应用到政府、科学、国防等领域。1992年，这家公司通过OpenGL来提供编程接口，OpenGL被设计为一个标准化的、平台无关的3D图形开发套件。

1990s中期，消费软件对3D图形处理的要求开始急剧增加，这其中有两点比较典型：1. Doom、Duke Nukem 3D、Quake等第一人称游戏的发布对更真实的3D环境模拟提出了更高的要求，尤其是第一人称射击游戏显著地加速了3D图形领域的发展。2. NVIDIA，ATI Technologies，3dfx Interactive等公司开始发布平价的视觉加速器。

NVIDIA发布的 GeForce 256将消费级显示硬件的性能推到了新的高度，首次支持直接在GPU上运行变换和光照计算。此后这种方式开始成为主流。

从并行计算的视角来看，2001年NVIDIA发布了GeForce 3系列，被认为是GPU技术发展的最重要的突破性时刻。它是首款支持微软DirectX 8的显卡，可以带来更高级的渲染效果，包括像素和顶点着色器。

早期的一些研究者可以通过OpenGL和DirectX提供的API来进行编程，这二者也是与GPU交互的必经之路，自然地，在GPU上进行任意计算也会受到API的限制，因此研究者们开始机遇图形API探索一些通用的计算方式。在2000s左右，GPU的主要用途是使用被称为pixel shaders的可编程数学单元来为屏幕上的每个像素点着色。一个pixel shader包含(x, y)的位置信息和其他附加信息，如颜色、材质或其他属性，由于颜色和材质信息是由编程人员控制的，所以，研究人员发现他们可以GPU来处理其他任何数据。也就是说，GPU被“欺骗”来做一些和颜色渲染无关的运算工作。但事实上，研究者面临比较多的约束，比如程序仅接收有限的颜色和材质信息，没有地方保存结果GPU运算完成后的结果。另外，GPU处理浮点数的行为几乎没办法预测，当程序出错、挂起时，也没有很好的debug途径。

上面还不够，要使用GPU，开发者要学会OpenGL或者DirectX（唯一与GPU交互的媒介），这意味着，要把数据存在图形纹理中，然后调用OpenGL或者DirectX的API完成计算，另外，还要使用专门的图形编程语言来编写计算。这要求开发者既要应对资源和编程上的挑战，又要学习计算机图形学和着色语言，这些是比较难以让人接受的障碍。

### CUDA架构

在GeForce 3系列GPU发布的5年后（2006年），英伟达发布了第一代支持DirectX 10的GPU，即GeForce 8800 GTX，它也是第一款支持NVIDIA CUDA架构的GPU，使得通用计算成为可能。

与前几代将计算资源划分为定点和像素着色器不同，CUDA架构包含一个统一的着色器管道，允许芯片上的每个算术逻辑单元（ALU）被程序编组以执行通用计算。由于NVIDIA计划将这一代图形处理器用于通用计算，ALU符合IEEE对单精度浮点数运算的要求，并且为进行通用计算量身定制了指令集。另外，CUDA支持任意内存读写，支持缓存访问（ 被称为共享内存），这些功能无一不是为了提升GPU的运算能力。

为了使CUDA能够被最大多数的开发者所接受，NVIDIA基于标准C语言，增加了少量的关键字来支持CUDA架构新增特性，在GeForce 8800GTX发布的几个月后，NVIDIA开源了基于CUDA C语言的编译器，CUDA C是第一个由GPU公司设计并用于GPU通用计算的语言。借助它，开发者无需再掌握OpenGL或者DirectX，也能进行GPU编程，也无需再费力将程序伪装为一个计算视觉任务了。

自2007年CUDA C首次亮相，很多领域如医疗影像、计算流体动力学、环境科学领域等都基于它得到了迅速发展。


## 第二章：准备工作 (Getting Started)

本章目标：

- 下载本书涉及的所有软件
    
- 搭建CUDA C编程环境
    

### 开发环境

要使用CUDA C编程，需要准备以下工具：

- 支持CUDA的图形处理器（GPU）
    
- NVIDIA设备驱动
    
- CUDA开发工具包
    
- 标准C编译器
    

自2006年GeForce 8800 GTX发布以来，基本上所有的NVIDIA都支持CUDA。因此找到一个支持CUDA的GPU并不难（显存大于256MB）。

我们需要安装NVIDIA显卡驱动软件，以提供软件和CUDA设备之间通讯的桥梁。一般安装最新版本即可。

有了GPU和驱动，我们便可以编译、运行CUDA C了，由于我们编写的程序需要运行在两个不同的处理器上（CPU、GPU），显然我们需要两个编译器，分别用于GPU和CPU程序的编译。


## 第三章 CUDA C 初探 (Introduction to CUDA C)

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


## 第四章 CUDA C并行编程 (Parallel Programming in CUDA C)

### 本章目标：

- CUDA实现并行的重要方式
- 使用CUDA C编写一段并行代码

考虑一段在CPU上运行的计算矢量和的代码：

```c
void add(int *a, int *b, int *c) {
    int tid = 0; // 第0个CPU
    while (tid < N) {
        c[tid] = a[tid] + b[tid];
        tid += 1;
    }
}
```

这里使用`while`循环，是考虑到，如果有多个CPU或者多个CPU核，我们可以将`tid`修改为CPU核心个数的倍数，来实现并行。比如有两个核心，则两个核心的`tid`分别设置为0和1，并将步长设置为2。

我们可以基于GPU实现相同的运算，代码如下：

```c
#include "common/book.h"

#define N 10

int main(void) {
    int a[N], b[N], c[N];
    int *dev_a, *dev_b, **dev_c;

    // 在GPU上分配内存
    HANDLE_ERROR(cudaMalloc((void **) &dev_a, N * sizeof(int)));
    HANDLE_ERROR(cudaMalloc((void **) &dev_b, N * sizeof(int)));
    HANDLE_ERROR(cudaMalloc((void **) &dev_c, N * sizeof(int)));

    // 在CPU上为数组a和b赋值
    for (int i = 0; i < N; i++) {
        a[i] = -i;
        b[i] = i * i;
    }

    // 将a和b复制到GPU
    HANDLE_ERROR(cudaMemcpy(dev_a, a, N * sizeof(int), cudaMemcpyHostToDevice));
    HANDLE_ERROR(cudaMemcpy(dev_b, b, N * sizeof(int), cudaMemcpyHostToDevice));

    add<<<N, 1>>>(dev_a, dev_b, dev_c);

    // 将数组c从GPU赋值到cpu
    HANDLE_ERROR(cudaMemcpy(c, dev_c, N * sizeof(int), cudaMemcpyDeviceToHost));

    // 结果
    for (int i = 0; i < N; i++) {
        printf("%d + %d = %d\n", a[i], b[i], c[i]);
    }

    // 释放在GPU上分配的内存
    cudaFree(dev_a);
    cudaFree(dev_b);
    cudaFree(dev_c);

    return 0;
}

__global__ void add(int *a, int **b, int *c) {
    int tid = blockIdx.x; // 计算此索引位置的数据
    if (tid < N)
        c[tid] = a[tid] + b[tid];
}
```

上述代码中，`add<<<N, 1>>>`中的`N`表示执行该核函数时使用的并行线程块的数量，实际执行中，GPU会运算该核函数的`N`个副本。由于CUDA支持二维线程块数组，`add()`函数中的代码`int tid = blockIdx.x;`通过`blockIdx.x`来获取线程的位置。还有一点，我们增加了判断`if (tid < N)`是为了避免`tid`越界（通常情况下条件是满足的）。

上述例子展示了使用CUDA计算两个N维矢量和是如此的简单，如果我们想扩大`N`，比如计算两个20000维的矢量的和，我们只需要将`N`设置为20000即可，这样代码运行时就可以一次性启动20000个线程，并行地完成计算。目前，CUDA限制`N`最大为65535。

上面计算矢量和的例子可能有些无聊，接下来我们看一个有趣一些的例子：绘制 Julia 集的曲线🐶。

### Julia集定义

满足某个复数计算函数的所有的点构成的边界。算法如下：通过一个等式对复平面中的点求值，如果迭代过程中值发散了，这个点不属于Julia集。迭代等式为：$Z_{n+1} = Z_n^2 + C$

首先看一下基于CPU的实现：

```c
int main(void) {
    CPUBitmap bitmap(DIM, DIM); // 实例化位图
    unsigned char *ptr = bitmap.get_ptr(); // 指向位图的指针
    kernel(ptr); // 传递给核函数
    bitmap.display_and_exit();
}


void kernel(unsigned char *ptr) {
    for (int y = 0; y < DIM; y++) {
        for (int x = 0; x < DIM; x++) {
            int offset = x + y * DIM;
            int juliaValue = julia(x, y); // 判断(x, y)对应的点是否属于 Julia 集
            ptr[offset * 4 + 0] = 255 * juliaValue;
            ptr[offset * 4 + 1] = 0;
            ptr[offset * 4 + 2] = 0;
            ptr[offset * 4 + 3] = 255;
        }
    }
}

// julia实现
int julia(int x, int y) {
    const float scale = 1.5;  // 图形的缩放函数

    // 以下将复平面原点移动到图像中心
    float jx = scale \* (float)(DIM / 2 - x) / (DIM / 2);
    float jy = scale \* (float)(DIM / 2 - y) / (DIM / 2);

    cuComplex c(-0.8, 0.156);  // 任意选择一个复数常量 C
    cuComplex a(jx, jy);

    int i = 0;
    for (i=0; i<200; i++){
        a = a \* a + c;
        if (a.magnitude2() > 1000)
            return 0;
    }

    return 1;
}


// 保存复数值的结构体：
struct cuComplex {
    float r;
    float i;
    cuComplex(float a, float b) : r(a), i(b) {}

    float magnitude2(void) { return r * r + i * i; }
    cuComplex operator*(const cuComplex& a) {
        return cuComplex(r * a.r - i * a.i, i * a.r + r * a.i);
    }

    cuComplex operator+(const cuComplex& a) {
        return cuComplex(r + a.r, i + a.i);
    }
};
```

接下来我们基于CUDA来实现Julia集合：

```c
#include "common/book.h"
#include "common/cpu_bitmap.h"

#define DIM 1000

int main(void) {
    CPUBitmap bitmap(DIM, DIM);
    unsigned char *dev_bitmap; // 申请设备指针

    HANDLE_ERROR(cudaMalloc((void **) &dev_bitmap, bitmap.image_size())); // 分配设备内存
    
    dim3 grid(DIM, DIM); // 初始化grid和block，dim3类型来自 CUDA 头文件，表示一个三位数组，当我们使用两个参数来初始化时，CUDA runtime 会自动把第三位设置为1
    kernel<<<grid, 1>>>(dev_bitmap);

    HANDLE_ERROR(cudaMemcpy(bitmap.get_ptr(), dev_bitmap, bitmap.image_size(), cudaMemcpyDeviceToHost)); // 设备内存复制到主机

    bitmap.display_and_exit();

    cudaFree(dev_bitmap);
}

// CUDA 版本的 kernel 实现：
__global__ void kernel(unsigned char *ptr) {
    int x = blockIdx.x;
    int y = blockIdx.y;
    int offset = x + y * gridDim.x; // 线性偏移
    int juliaValue = julia(x, y); // 判断(x, y)对应的点是否属于 Julia 集

    ptr[offset * 4 + 0] = 255 * juliaValue;
    ptr[offset * 4 + 1] = 0;
    ptr[offset * 4 + 2] = 0;
    ptr[offset * 4 + 3] = 255;
}


// julia实现，除了__device__之外，其余与 CPU 版本相同
__device__ int julia(int x, int y) {
    const float scale = 1.5;  // 图形的缩放函数

    // 以下将复平面原点移动到图像中心
    float jx = scale \* (float)(DIM / 2 - x) / (DIM / 2);
    float jy = scale \* (float)(DIM / 2 - y) / (DIM / 2);

    cuComplex c(-0.8, 0.156);  // 任意选择一个复数常量 C
    cuComplex a(jx, jy);

    int i = 0;
    for (i=0; i<200; i++){
        a = a \* a + c;
        if (a.magnitude2() > 1000)
            return 0;
    }

    return 1;

}


// cuComplex 结构体，也仅仅在__device__修饰符上有差别：
struct cuComplex {
    float r;
    float i;
    cuComplex(float a, float b) : r(a), i(b) {}

    __device__ float magnitude2(void) { return r * r + i * i; }
    __device__ cuComplex operator*(const cuComplex& a) {
        return cuComplex(r * a.r - i * a.i, i * a.r + r * a.i);
    }

    __device__ cuComplex operator+(const cuComplex& a) {
        return cuComplex(r + a.r, i + a.i);
    }
};
```

以上便是CUDA版本的实现。

至此，我们已经可以使用CUDA处理一些有一定规模的并行计算任务了。


## 参考

1. [CUDA By Example](https://developer.nvidia.com/cuda-example)