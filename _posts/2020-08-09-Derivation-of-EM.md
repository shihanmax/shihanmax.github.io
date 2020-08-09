---
title:  "Derivation of EM"
layout: post
date: 2020-08-09 17:16:03
categories: NLP
tags:  EM
syntaxHighlighter: yes
Mathjax: true
---

隐变量模型（Latent Variable Models）指模型中包含不可观测的隐含变量$z$，隐变量模型的求解根据$z$的已知与否分为两类：

- complete case
- incomplete case

complete case是指求解过程中，$(x,z)$均已知，此类模型求解可以使用MLE等方法进行求解；incomplete case中，隐变量$z$是未知的，求解该类模型需要使用EM算法。

下文对EM算法进行简单的推导，假设因变量模型相关的参数和变量分别为：

- $\theta$：model parameters
- $x$：observed variable
- $z$：latent variable

Objective: $L(\theta)= \ln p(x\mid \theta)$，优化目标为：$\arg \max L(\theta)=\arg \max \ln p(x\mid\theta)$

记EM算法经过$n$轮迭代后的参数为$\theta_n$，目标函数也可以写成如下的形式，即在第$n$次迭代的基础上，最大化当前的目标函数和第$n$轮目标函数的差值：

$$\begin{aligned} \arg \max _{\theta} L(\theta)-L\left(\theta_{n}\right) &=\ln p(x \mid \theta) -\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x, z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p(x \mid z, \theta) \cdot p(z \mid \theta)-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(x \mid z, \theta\right) \cdot p(z \mid \theta) \cdot \frac{p\left(z \mid x, \theta_{n}\right)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ &=\ln \sum_{z} p\left(z \mid x, \theta_{n}\right) \cdot \frac{p(x \mid z, \theta) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \end{aligned}$$

$\log\sum$项在求梯度过程中不方便计算，这里引入Jensen不等式：$\ln\sum_\limits{i=1}^{n}\lambda_i x_i \geqslant \sum_\limits{i=1}^{n}\lambda_i\ln x_i \quad s.t. \sum_\limits{i=1}^{n}\lambda_i=1$

由于$\sum_\limits{z} p(z\mid x,\theta_n)=1$，可将该项视为Jensen不等式中的$\lambda$，因此有：

$\arg\max L(\theta)-L(\theta_n) \geqslant \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p\left(x \mid z, \theta\right) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right)$

至此，得到：

$$\begin{aligned} L(\theta)-L(\theta_n) & \geqslant \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p\left(x \mid z, \theta\right) \cdot p(z \mid \theta)}{p\left(z \mid x, \theta_{n}\right)}-\ln p\left(x \mid \theta_{n}\right) \\ &=\sum_{z} p\left(z \mid x, \theta_{n}\right) \ln \frac{p(x\mid z,\theta) \cdot p(z\mid \theta)}{p(x\mid x,\theta_n) \cdot p(x\mid \theta_n)} \\&=\Delta(\theta\mid\theta_n) \end{aligned} $$

即：$L(\theta)\geqslant L(\theta_n) +\Delta(\theta\mid\theta_n)$，此时最大化$L(\theta)$等价于最大化$L(\theta)$的下界，因此，下一轮迭代的最优$\theta_{n+1}$可以表示为：

$$\begin{aligned} \theta_{n+1} &=a r g \max _{\theta} L\left(\theta_{n}\right)+\Delta\left(\theta \mid \theta_{n}\right) \\ &=\arg \max _{\theta} \Delta\left(\theta \mid \theta_{n}\right) \\ &=\arg \max _{\theta} \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln p(x \mid z, \theta) \cdot p(z \mid \theta) \\ &=\arg \max _{\theta} \sum_{z} p\left(z \mid x, \theta_{n}\right) \ln p(x, z \mid \theta) \\ &=\arg \max _{\theta} E_{z \mid x, \theta_{n}} p(x, z \mid \theta)\end{aligned}$$

其中，$E_{z \mid x, \theta_{n}} p(x, z \mid \theta)$为$(z|x,\theta,n)$的期望，由于该项中包含了两个未知变量$\theta,z$，最大化过程分为两步进行：

- E-step：根据当前的$\theta$计算出$z$的期望（在包含两个待求解变量时，E-step固定其中的$\theta$来独立求解$z$，因此EM算法中的E-step可以看作是coordinate decent的一种特例。）
- M-step：$maximize \ln p(x,z\mid \theta)$（可以认为此时的$z$是已知的，这种comlelte-case可以直接使用MLE等优化方法直接求解。）

迭代执行上述两步，直至收敛，便可以得到最终需要求解的参数$\theta$。