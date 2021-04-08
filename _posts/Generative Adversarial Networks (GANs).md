## GANS for text

## 一、GAN和RL的联系

GAN和RL的联系

但是说GAN是RL的特例，这个还是有失偏颇。准确来说和GAN很相似的是**Actor-Critic（**AC**）**。更准确来说是以**Deterministic Policy Gradient**（DPG）为代表的对于**连续动作输出**建模的RL算法。



## 二、GAN由图像到文本的推广

Generative Adversarial Networks (GANs)

<img src="http://qiniu.shihanmax.top/20210407151134_0kbTbR_1*EtVPM-nMOqlLqk9PuNvyIg.jpeg" alt="Gan architecture" style="zoom:80%;" />

The objective of GANs:
$$
\min _{G} \max _{D} V(D, G)=\mathbb{E}_{\boldsymbol{x} \sim p_{\mathrm{data}}(\boldsymbol{x})}[\log D(\boldsymbol{x})]+\mathbb{E}_{\boldsymbol{z} \sim p_{\boldsymbol{z}}(\boldsymbol{z})}[\log (1-D(G(\boldsymbol{z})))]
$$


review GANs for Images

<img src="http://qiniu.shihanmax.top/20210407152709_gq8XV0_1*CCGA_sDasttikaEaF-K2Nw.jpeg" alt="Image GAN" style="zoom:70%;" />

GAN用于图片生成时，隐变量$z$从分布中采样得到，$x$从真实数据中采样得到，

对于生成器：通过$z$生成分布$G(z)$，目标：$\arg\max P( D(G(z)))$；

对于判别器：输入生成器的输出$G(z)$和真实采样$x$，目标：$\arg\max P(D(x))-P(D(G(z)))$

无论是真实的图片还是真实的图片，都是一个实值张量，因此生成器和判别器之间，梯度都是可以正常传递的。



那么我们把GAN的思想推广到文本生成时会发生什么？

Seq2seq是目前最成熟的文本生成框架，以RNN作为decoder为例，在时间步$t$，RNN通过以下计算获得当前时间步最有可能的词$token^\star$：

$$h^t=RNN(h^{t-1}, w^{t-1})$$

$$Idx_{token^\star}=onehot(Softmax(fc(h^t)))$$

然后通过最小化交叉熵损失函数来调整RNN的参数。

下面我们将基于RNN的decoder与GAN中的Generator关联起来，并尝试分析为什么传统的GAN思想无法直接推广在文本生成领域。

在GAN中，则不是使用交叉熵来调整生成器的参数，而是通过$\arg\max P( D(G(z)))$来实现，这里就会存在一个问题，$G(z)$是通过$\arg\max$操作获得的（这个过程也称为sampling），$\arg\max$操作是一个不可导的过程，会导致梯度断开。针对这个问题，很自然的一个想法，我们是否可以不通过argmax来获取onehot表示，直接将生成器的softmax分布传递给判别器？这种方式也是不可行的，原因是，在这种情况下，判别器遇到的负样本一般情况下都是一个浮点张量，而从真实数据中采样的样本$x$一般是onehot张量，这种正负样本的分布差异，自然会导致判别器“偷懒”，比如，判别器是否可以仅仅通过“数”输入中1的个数来判断是否是真实样本？这样的话，判别器就失效了。

另外也可以从loss的角度来分析：一般情况下GAN使用$JS$散度来衡量真实分布和生成分布的差异，注意到只有在两个分布有交叠时，才能使用$JS$散度来衡量其距离（否则的话，$JSD$为$\log2$），但很明显，如果生成器的结果不经过softmax，其生成出multinomial分布的概率应该是接近0的，这种情况下，自然也不能对生成器进行有效的权重更新。

另外一个角度看，使用与真实label的交叉熵也好，使用判别器的判别结果也好，都是对当前模型参数做的微调，想象某一个时间步$t$时softmax的结果为$[0.03, 0.26, 0.18, 0.05, 0.27, 0.16]$，通过softmax采样得到的token index为4，这里可能存在的一个问题是，微调不一定能够改变softmax结果的最大值的index，也即不一定影响sampling的结果，那么对判别器来讲，其训练过程也会失去方向。

## 三、文本GAN的

想要解决上述问题，核心还是要保证从生成器到判别器的梯度是连接的。目前针对GAN在文本生成领域的应用，主要有以下几种GAN改进思路：

- 微调GAN的结构
  - 使用Wasserstein-divergence进行距离衡量
  - 通过Gumbel-Softmax估计（对softmax的一种连续化的估计）
- 通过强化算法和策略梯度（基于强化学习的）
- 生成器结果在连续空间中传递给判别器（避免在离散空间交互）

以下分别介绍上述三种方案。

## 1. 微调GAN结构

目前主要有两种主流方案，其一主要针对分布距离衡量做工作，另一个则针对softmax无法进行梯度传递进行改进。

### 1.1 使用Wasserstein-divergence

Wasserstein-GAN，又称WGAN，其在生成对抗领域甚至与原版的GAN平分秋色。

在介绍Wasserstein-divergence在GAN中的应用之前，首先了解一下有关距离衡量的内容。

**散度**

散度(Divergence)或称发散度，是[向量分析](https://zh.wikipedia.org/wiki/向量分析)中的一个[向量](https://zh.wikipedia.org/wiki/向量場)[算子](https://zh.wikipedia.org/wiki/算子)，将[向量空间](https://zh.wikipedia.org/wiki/向量空间)上的一个[向量场](https://zh.wikipedia.org/wiki/向量場)（矢量场）对应到一个[标量场](https://zh.wikipedia.org/wiki/标量场)上。散度描述的是向量场里一个点是汇聚点还是发源点，形象地说，就是这包含这一点的一个微小体元中的向量是“向外”居多还是“向内”居多。散度是向量场的一种[强度性质](https://zh.wikipedia.org/wiki/內含及外延性質)，就如同密度、浓度、温度一样，它对应的广延性质是一个封闭区域表面的通量，所以说**散度是通量的体密度**。



**KL散度（Kullback-Leibler divergence，简称KLD）**

KL散度来源于信息论。KL散度又称为相对熵。在信息论中，一个分布的熵定义为：

$$H=-\sum_\limits{i=1}^Np(x_i)\log p(x_i)$$

对熵稍加改动，即可得到相对熵：

$$D_{KL}(p\Vert q)=-\sum_\limits{i=1}^Np(x_i)\cdot (\log p(x_i)-\log(q(x_i))$$

KL散度是两个概率分布$p$和$q$差别的非对称性的度量。 KL散度是用来度量使用基于$q$的分布来编码服从$p$的分布的样本所需的额外的平均比特数（$\log$以$2$为底时）。典型情况下，$p$表示数据的真实分布，$q$表示数据的理论分布、估计的模型分布、或$p$的近似分布。

在生成对抗网络中，多使用KLD对两个分布的距离进行度量。



**JS散度**

JS散度也用于度量两个概率分布的相似度，它是KL散度的变体，解决了KL散度的非对称问题。JSD的取值在$0 \sim 1$之间，其定义如下：

$$JS(p_1\Vert p2)=\frac{1}{2}KL(p_1 \Vert \frac{p_1+p_2}{2})   +   \frac{1}{2}KL(p_2 \Vert \frac{p_1+p_2}{2})$$



**Wasserstein散度（Wasserstein-divergence）**

文章$^5$使用芬切尔共轭（Fenchel Conjugate）的性质证明了，任何$f-divergence$都可以作为KLD（或JSD）的替代方案，$f-divergence$的定义如下：

$$D_f(p \Vert q) = \int_xq(x)f(\frac{p(x)}{q(x)})dx$$

其中，$f(\cdot)$称为$f$函数，它必须满足两个条件：

- $f$是凸函数（convex function）
- $f(1)=0$

可以看出，KL-divergence是f-divergence的一种。而Wasserstein-divergence也是对KL-divergence的一种改进。中文译为“推土机距离”，可以形象地理解为，将两个分布看作两个土堆，Wasserstein-divergence就是计算将两个土堆堆成一样的形状所需要的泥土搬运总距离。

![Wasserstein-divergence](http://qiniu.shihanmax.top/20210407201450_6D8pRH_z8u94r9mbi.jpeg)



相比原版的GAN，Wasserstein-divergence更能体现出分布循序渐进的过程，在GAN的训练过程中，无论是KL散度还是JS散度，在开始训练后的很长一段时间内，散度值都为$\log2$，而Wasserstein-divergence的值则是平滑变化的。

由于Wasserstein-divergence克服了JS散度的“两个分布必须包含重叠部分”的缺点，我们也就自然地可以计算生成器的softmax分布和真实onehot分布的距离了。

值得注意的是，Wasserstein-divergence提出并不针对GAN在文本生成上面临的问题，事实上，其对于GAN的发展带来的意义更重要。文章$^8$使用GAN在文本生成上做了实验，结果表明，加入Wasserstein-divergence的GAN至少处于可以训练的状态了（虽然生成效果距离MLE结果还有一段距离）。

![Wdtest](http://qiniu.shihanmax.top/20210407203303_iDjaAX_ba0nwqbdn6.jpeg)

### 1.2 使用Gumbel-softmax替换softmax

上面已经提到了由$\arg\max$带来的困境：采样，梯度无法传播；不采样，softmax分布和onehot分布不重叠，无法计算距离；1.1部分讨论了不采样、换度量的方法，接下来讨论如何能在采样的情况下保持梯度。

这篇文章$^9$给出的答案是Gumbel-softmax，它最早提出用于类别的重参数化，应用到GAN的改进目标可以认为是设计一个更“强大”的softmax，使得能够代替原生GAN中的softmax+argmax操作，直接进入分布的距离计算。

原生GAN的生成器输出为$y_{old}=onehot(\arg\max(softmax(h)))$，Gumbel-softmax通过$y_{new}=softmax(\frac{1}{\tau}(h+g))$直接给出近似sampling的输出。参数中，$\tau$称为逆温函数，当$\tau \rightarrow 0$时，上式等同于$onehot(\arg\max(\cdot))$；当$\tau \rightarrow \infty$时，输出接近均匀分布，可以给$\tau$一个较大的初始值，在训练中逐渐向0逼近。

文章$^9$使用融合了Gumbel-softmax的GAN进行了长度为12的CFG（上下文无关文法）文本生成，结果可参考下图。

![Gumble-sfm](http://qiniu.shihanmax.top/20210407205434_B1HL5o_lok2862vqe.jpeg)

可以看出，在少数样例上也得到了比较满意的结果，但总体来看，效果仍不理想。

## 2. 引入强化学习思想

## 3. 其他架构

Refs.

1. [Generative Adversarial Networks for Text Generation — Part 1](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-1-2b886c8cab10)
2. [Generative Adversarial Networks for Text Generation — Part 2: RL](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-2-rl-1bc18a2b8c60)
3. [Generative Adversarial Networks for Text Generation — Part 3: non-RL methods](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-3-non-rl-methods-70d1be02350b)
4. ss
5. [f-GAN: Training Generative Neural Samplers using Variational Divergence Minimization](https://arxiv.org/abs/1606.00709)
6. [wiki-相对熵](https://zh.wikipedia.org/wiki/相对熵)
7. [wiki-散度](https://zh.wikipedia.org/wiki/散度)
8. [Improved Training of Wasserstein GANs]( https://arxiv.org/abs/1704.00028)
9. [Categorical Reparameterization with Gumbel-Softmax](https://arxiv.org/abs/1611.01144)
