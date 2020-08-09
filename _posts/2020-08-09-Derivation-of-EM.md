---
title:  "Derivation of EM"
layout: post
date: 2020-08-09 17:16:03
categories: NLP
tags:  EM
syntaxHighlighter: yes
Mathjax: true
---

设$\theta$为模型参数；$x$为observed variable；$z$为latent variable

$L(\theta)= \ln p(x\mid \theta)$，$objective: \arg \max L(\theta)=\arg \max \ln p(x\mid\theta)$

EM算法通过迭代获取当前轮次下的$\theta$和$z$的最优解，记经过$n$轮迭代后的参数为$\theta_n$，目标函数也可以写成如下的形式，即，在第$n$次迭代的基础上，最大化当前的目标函数和第$n$轮目标函数的差值：

$$\begin{aligned} \arg \max _{\theta} L(\theta)-L\left(\theta_{n}\right) &=\ln p(x \mid \theta) -\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x, z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x \mid z, \theta) \cdot p(z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(x \mid z, \theta\right) \cdot p(z \mid \theta) \cdot \frac{p\left(z \mid x, \theta_{n}\right)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(z \mid x, \theta_{n}\right) \cdot \frac{p(x \mid z, \theta) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \end{aligned}$$

$\log\sum$项在求梯度过程中不方便计算，这里引入Jensen不等式：$\ln\sum_\limits{i=1}^{n}\lambda_i x_i \geqslant \sum_\limits{i=1}^{n}\lambda_i\ln x_i \quad s.t. \sum_\limits{i=1}^{n}=1$

由于$\sum_\limits{z} p(z\mid x,\theta_n)=1$，可将该项视为Jensen不等式中的$\lambda$，因此有：

$\arg\max L(\theta)-L(\theta_n) \geqslant \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p\left(x \mid z, \theta\right) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right)$

至此，得到：

$$\begin{aligned} L(\theta)-L(\theta_n) & \geqslant \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p\left(x \mid z, \theta\right) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ &=\sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p(x\mid z,\theta) \cdot p(z\mid \theta)}{p(x\mid x,\theta_n) \cdot p(x\mid \theta_n)} \\&=\Delta(\theta\mid\theta_n) \end{aligned} $$

即：$L(\theta)\geqslant L(\theta_n) +\Delta(\theta\mid\theta_n)$

