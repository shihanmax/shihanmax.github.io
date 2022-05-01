---
title:  "PyTorch源码阅读"
layout: post
date: 2022-05-01 23:02:34
tags:  ["Deep Learning", "PyTorch", "源码阅读"]
syntaxHighlighter: yes
mathjax: true
---

我阅读的代码版本是，仓库太大，先参考repo里的[codebase-structure](https://github.com/pytorch/pytorch/blob/master/CONTRIBUTING.md#codebase-structure)了解一下整体的结构：

* [c10](c10) - 适用于桌面端和移动端的核心库，后续[ATen/core]中的部分也会逐渐迁移过来，主要用于一些基本功能的实现
* [aten](aten) - C++张量库（不支持自动微分）
  * [src](aten/src) - [README](aten/src/README.md)
    * [ATen](aten/src/ATen)
      * [core](aten/src/ATen/core) - ATen的核心功能库，后续会逐渐迁移至顶层的c10下
      * [native](aten/src/ATen/native) - 算子（Operator）的时间，如果我们想实现一个新的算子，也需要放在这里。大部分CPU上的算子定义在这个目录下的顶层，除了一些需要编译的；
        * [cpu](aten/src/ATen/native/cpu) - 这里并非CPU算子实现，而是对于一些需要通过特定处理器指令集来编译的算子的实现，如AVX，参考[README](aten/src/ATen/native/cpu/README.md) for more details
        * [cuda](aten/src/ATen/native/cuda) - CUDA算子实现；
        * [sparse](aten/src/ATen/native/sparse) - COO稀疏张量运算的CPU和CUDA实现
        * [mkl](aten/src/ATen/native/mkl) [mkldnn](aten/src/ATen/native/mkldnn)
          [miopen](aten/src/ATen/native/miopen) [cudnn](aten/src/ATen/native/cudnn)
          - 仅需简单绑定后端库（backend library）的一些算子的实现
        * [quantized](aten/src/ATen/native/quantized/) - 量子张量实现 [README](aten/src/ATen/native/quantized/README.md)介绍了如何实现一个量子张量
* [torch](torch) - PyTorch库，除了[csrc](torch/csrc)外，都是Python实现
  * [csrc](torch/csrc) - PyTorch库中的C++部分，包括一些Python胶水代码和一些C++实现，有关Python绑定代码的规范，可以参考`setup.py`
    * [README](torch/csrc/README.md)
    * [jit](torch/csrc/jit) - TorchScript JTP的编译器和前端，参考[README](torch/csrc/jit/README.md)
    * [autograd](torch/csrc/autograd) - 反向自动微分的实现，参考[README](torch/csrc/autograd/README.md)
    * [api](torch/csrc/api) - PyTorch的C++前端
    * [distributed](torch/csrc/distributed) - 分布式训练支持
* [tools](tools) - 代码生成脚本，参考[README](tools/README.md)
* [test](test) - PyTorch Python前端单元测试
  * [test_torch.py](test/test_torch.py) - 基础功能测试
  * [test_autograd.py](test/test_autograd.py) - non-NN自动微分测试
  * [test_nn.py](test/test_nn.py) - NN及自动微分测试
  * [test_jit.py](test/test_jit.py) - JIT相关测试
  * ...
  * [cpp](test/cpp) - C++前端的单元测试
    * [api](test/cpp/api) - [README](test/cpp/api/README.md)
    * [jit](test/cpp/jit) - [README](test/cpp/jit/README.md)
    * [tensorexpr](test/cpp/tensorexpr) - [README](test/cpp/tensorexpr/README.md)
  * [onnx](test/onnx) - ONNX测试（PyTorch和Caffe2）
* [caffe2](caffe2) - Caffe2的库.
  * [core](caffe2/core) - Caffe2核心文件,如tensor, workspace, blobs, 等
  * [operators](caffe2/operators) - Caffe2算子.
  * [python](caffe2/python) - Caffe2 Python 绑定.
  * ...
* [.circleci](.circleci) - 持续集成CI相关 [README](.circleci/README.md)



我先挑“软柿子”[torch](torch)开始看。

