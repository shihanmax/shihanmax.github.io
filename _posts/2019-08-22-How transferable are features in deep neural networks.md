---
title: How transferable are features in deep neural networks
layout: post
categories: 'NLP'
tags:
  - 'transfer learning'
mathjax: true
syntaxHighlighter: 'yes'
date: 2019-08-22 19:38:33
---

Jason Yosinski, Jeff Clune, Yoshua Bengio, and Hod Lipson

本文通过实验考察从网络第一层的强泛化能力的特征到最后一层的任务相关的特征之间的转变过程。对神经元的泛化能力（generality）以及特异性（specificity）进行量化分析。

迁移能力 受两个因素影响：

-   后层的神经元更专注于特定的任务
-   优化自适应（co-adapted）神经元的困难

<!--more-->

我们在 ImageNet 上的实验表明，以上两个因素均有占主导的时候，取决于特征的转移过程发生在网络的前、中、后层；另外发现，两个任务的差异性越大，泛化能力就越差，但仍然超过随机特征的效果。最后的发现是，无论初始化时使用了多少层与训练权重，在 finetune 到特定数据集之后，仍然保持泛化能力。

我们称第一层的特征为general特征，最后一层的特征为specific特征。那么在两层中间一定存在着从 genral到specific之间的转变，那么问题来了：

-   我们可以量化某一层的general或者specific的度吗？
-   转变发生在某一层，还是分布在几层之间？
-   转变发生在网络的前部、中部、还是后部？

我们关心这些问题的原因是，如果我们能够掌握上述转变发生的位置，我们就能够更有效地利用迁移学习，其有效性已经得到广泛认可。在迁移学习中，我们可以冻结transferred feature，仅训练后层随机初始化的网络，或者将它们随后层任务一起微调（finetune），这取决于新领域的数据集规模。

#### Experiment results

![The results from this paper’s main experiment.](http://shihanmax.top/截屏2019-08-22下午7.35.42.png)

![Performance degradation vs. layer.](http://shihanmax.top/截屏2019-08-22下午7.36.29.png)



#### 本文贡献：

1.  定义一种量化各层泛化能力的方法
2.  发现以下两种会破坏性能的点：
    -   特征自身的专一性
    -   optimization difficulties due to splitting the base network between co-adapted neurons on neighboring layers
3.  量化研究了随着任务差异性的提升，泛化能力如何下降
4.  对比了浅层随机初始化和迁移学习的效果，后者更好
5.  我们发现前层权重在新的数据集上微调后，在旧的数据集上的效果依然保持

















