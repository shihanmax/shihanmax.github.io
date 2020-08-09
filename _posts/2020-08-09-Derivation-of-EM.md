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

EM算法通过迭代获取当前轮次下的$\theta$和$z$的最优解，记经过$n$轮迭代后的参数为$\theta_n$。



$$\begin{aligned} \arg \max _{\theta} L(\theta)-L\left(\theta_{n}\right) &=\ln p(x \mid \theta) -\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x, z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x \mid z, \theta) \cdot p(z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(x \mid z, \theta\right) \cdot p(z \mid \theta) \cdot \frac{p\left(z \mid x, \theta_{n}\right)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(z \mid x, \theta_{n}\right) \cdot \frac{p(x \mid z, \theta) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ & \geqslant \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p\left(x \mid z \theta\right) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \end{aligned}$$