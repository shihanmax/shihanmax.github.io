# GANS for text

本文尝试对GAN在文本领域的应用现状作一个粗略的调研。

首先介绍GANs的原理和其在图像生成上的应用，接着讨论直接将GANs推广到文本生成时会遇到的一些问题。针对这些问题，介绍几种将GANs应用于文本的实现方案，如微调GANs结构、将PG（policy gradient）引入GANs，以及一些“类GANs模型”的尝试。最后，从当前领域中热门的研究中选取若干典型的工作，并进行简单地解读。

## 一、GANs：由图像到文本

### 1.1 GANs原理

Generative Adversarial Networks (GANs)

<img src="http://qiniu.shihanmax.top/20210407151134_0kbTbR_1*EtVPM-nMOqlLqk9PuNvyIg.jpeg" alt="Gan architecture" style="zoom:80%;" />

The objective of GANs:

$$\min _{G} \max _{D} V(D, G)=\mathbb{E}_{\boldsymbol{x} \sim p_{\mathrm{data}}(\boldsymbol{x})}[\log D(\boldsymbol{x})]+\mathbb{E}_{\boldsymbol{z} \sim p_{\boldsymbol{z}}(\boldsymbol{z})}[\log (1-D(G(\boldsymbol{z})))]$$

### 1.2 GANs for Image

<img src="http://qiniu.shihanmax.top/20210407152709_gq8XV0_1*CCGA_sDasttikaEaF-K2Nw.jpeg" alt="Image GAN" style="zoom:70%;" />

GAN用于图片生成时，隐变量$z$从分布中采样得到，$x$从真实数据中采样得到，

对于生成器（Generator）：通过$z$生成分布$G(z)$，目标：$\arg\max P( D(G(z)))$；

对于判别器（Discriminator）：输入生成器的输出$G(z)$和真实采样$x$，目标：$\arg\max P(D(x))-P(D(G(z)))$

无论是真实的图片还是真实的图片，都是一个实值张量，因此生成器和判别器之间，梯度都是可以正常传递的。



### 1.3 将GANs思想推广到文本

那么我们把GAN的思想推广到文本生成时会发生什么？

Seq2seq是目前最成熟的文本生成框架，以RNN作为decoder为例，在时间步$t$，RNN通过以下计算获得当前时间步最有可能的词$token^\star$：

$$h^t=RNN(h^{t-1}, w^{t-1})$$

$$Idx_{token^\star}=onehot(Softmax(fc(h^t)))$$

然后通过最小化交叉熵损失函数来调整RNN的参数。

下面我们将基于RNN的decoder与GAN中的Generator关联起来，并尝试分析为什么传统的GAN思想无法直接推广在文本生成领域。

在GAN中，则不是使用交叉熵来调整生成器的参数，而是通过$\arg\max P( D(G(z)))$来实现，这里就会存在一个问题，$G(z)$是通过$\arg\max$操作获得的（这个过程也称为sampling），$\arg\max$操作是一个不可导的过程，会导致梯度断开。针对这个问题，很自然的一个想法，我们是否可以不通过argmax来获取onehot表示，直接将生成器的softmax分布传递给判别器？这种方式也是不可行的，原因是，在这种情况下，判别器遇到的负样本一般情况下都是一个浮点张量，而从真实数据中采样的样本$x$一般是onehot张量，这种正负样本的分布差异，自然会导致判别器“偷懒”，比如，判别器是否可以仅仅通过“数”输入中1的个数来判断是否是真实样本？这样的话，判别器就失效了。

另外也可以从loss的角度来分析：一般情况下GAN使用$JS$散度来衡量真实分布和生成分布的差异，注意到只有在两个分布有交叠时，才能使用$JS$散度来衡量其距离（否则的话，$JSD$为$\log2$），但很明显，如果生成器的结果不经过softmax，其生成出multinomial分布的概率应该是接近0的，这种情况下，自然也不能对生成器进行有效的权重更新。

另外一个角度看，使用与真实label的交叉熵也好，使用判别器的判别结果也好，都是对当前模型参数做的微调，想象某一个时间步$t$时softmax的结果为$[0.03, 0.26, 0.18, 0.05, 0.27, 0.16]$，通过softmax采样得到的token index为4，这里可能存在的一个问题是，微调不一定能够改变softmax结果的最大值的index，也即不一定影响sampling的结果，那么对判别器来讲，其训练过程也会失去方向。



## GANs在文本生成上的应用场景和优势

应用场景：machine translation, dialogue systems, image captioning, text style transfer, 

## GANs如何应用于文本？

目前针对GAN在文本生成领域的应用，主要有以下几种GAN改进思路：

- 微调GAN的结构
  - 使用Wasserstein-divergence进行距离衡量
  - 通过Gumbel-Softmax估计（对softmax的一种连续化的估计）
- 通过强化算法和策略梯度（Policy Gradient）（基于强化学习的）
- 生成器结果在连续空间中传递给判别器（避免在离散空间交互）

以下分别介绍上述三种方案。



### 2.1 微调GAN结构

目前主要有两种主流方案，其一主要针对分布距离衡量做工作，另一个则针对softmax无法进行梯度传递进行改进。

#### 2.1.1 使用Wasserstein-divergence

Wasserstein-GAN，又称WGAN，其在生成对抗领域甚至与原版的GAN平分秋色。

在介绍Wasserstein-divergence在GAN中的应用之前，首先了解一下有关距离衡量的内容。

**散度**

散度(Divergence)或称发散度，是[向量分析](https://zh.wikipedia.org/wiki/向量分析)中的一个[向量](https://zh.wikipedia.org/wiki/向量場)[算子](https://zh.wikipedia.org/wiki/算子)，将[向量空间](https://zh.wikipedia.org/wiki/向量空间)上的一个[向量场](https://zh.wikipedia.org/wiki/向量場)（矢量场）对应到一个[标量场](https://zh.wikipedia.org/wiki/标量场)上。散度描述的是向量场里一个点是汇聚点还是发源点，形象地说，就是这包含这一点的一个微小体元中的向量是“向外”居多还是“向内”居多。散度是向量场的一种[强度性质](https://zh.wikipedia.org/wiki/內含及外延性質)，就如同密度、浓度、温度一样，它对应的广延性质是一个封闭区域表面的通量，所以说**散度是通量的体密度**。



**KL散度（Kullback-Leibler divergence，简称KLD）**

KL散度来源于信息论。KL散度又称为**相对熵**。在信息论中，分布$p$的熵定义为：

$$H=-\sum_\limits{i=1}^Np(x_i)\log p(x_i)$$

对熵稍加改动，即可得到相对熵：

$$D_{KL}(p\Vert q)=-\sum_\limits{i=1}^Np(x_i)\cdot (\log p(x_i)-\log(q(x_i))$$

KL散度是两个概率分布$p$和$q$差别的非对称性的度量。 KL散度是用来度量使用基于$q$的分布来编码服从$p$的分布的样本所需的额外的平均比特数（$\log$以$2$为底时）。典型情况下，$p$表示数据的真实分布，$q$表示数据的理论分布、估计的模型分布、或$p$的近似分布$^6$。

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

#### 2.1.2 使用Gumbel-softmax替换softmax

上面已经提到了由$\arg\max$带来的困境：采样后梯度无法传播；不采样，softmax分布和onehot分布不重叠，无法计算距离；1.1部分讨论了不采样、换度量的方法，接下来讨论如何能在采样的情况下保持梯度。

这篇文章$^9$给出的答案是Gumbel-softmax，它最早提出用于类别的重参数化，应用到GAN的改进目标可以认为是设计一个更“强大”的softmax，使得能够代替原生GAN中的softmax+argmax操作，直接进入分布的距离计算。

原生GAN的生成器输出为$y_{old}=onehot(\arg\max(softmax(h)))$，Gumbel-softmax通过$y_{new}=softmax(\frac{1}{\tau}(h+g))$直接给出近似sampling的输出。参数中，$\tau$称为逆温函数，当$\tau \rightarrow 0$时，上式等同于$onehot(\arg\max(\cdot))$；当$\tau \rightarrow \infty$时，输出接近均匀分布，可以给$\tau$一个较大的初始值，在训练中逐渐向0逼近。

文章$^9$使用融合了Gumbel-softmax的GAN进行了长度为12的CFG（上下文无关文法）文本生成，结果可参考下图。

![Gumble-sfm](http://qiniu.shihanmax.top/20210407205434_B1HL5o_lok2862vqe.jpeg)

可以看出，在少数样例上也得到了比较满意的结果，但总体来看，效果仍不理想。

### 2.2 引入强化学习思想

现在我们暂时先把神经网络的概念放在一边，考虑如何从强化学习的角度考虑文本生成，下面以文本生成为例，讨论强化学习的一些基础概念。



#### 2.2.0 强化学习部分术语整理

**reward**: 环境提供给agent的一个可量化的标量反馈信号，用于评价agent在某个时间步的action的好坏；

**agent**: 中文一般翻译为智能体，是强化学习的核心，其可以感知环境的状态（state），并根据环境提供的强化信号（reward signal），通过学习，选择一个合适的动作（Action），最大化长期的reward值；

**episode**: An episode is one complete play of the agent interacting with the environment in the general RL setting. Episodic tasks in RL means that the game of trying to solve the task ends at a terminal stage or after some amount of time. 一般表示agent从开始执行任务到一次任务执行完毕，或达到某一个阶段性的时间点，如一个游戏回合中，智能体被击毙或击毙对方boss；



#### 2.2.1 Policy

我们定义强化学习中的决策执行者为agent，可以定义agent的：

状态$s$（state）：截止目前为止生成的文本

动作$a$（action）：下一步应该生成哪一个词（即，词表的大小即是选择空间）

当agent最终生成了结尾符$<eos>$时，它会获得一个reword，用于表示agent在当前及前序的状态-决策过程中的质量（或生成的文本序列的质量）。

因此，我们可以把**判别器**看作对agent的一个reward函数。接下来需要讨论的是，agent在特定的状态$s$如何选择合适的动作$a$呢？这里要引出**policy**的概念：

**Policy**是一个函数$\pi(a\mid s,\theta)$，该函数受参数$\theta$控制，基于当前状态$s$，输出所有动作$a$的概率分布，agent通过这个概率分布来进行action采样（而不是直接采用概率最高的，这一定程度上也给了agent一定的探索性）。

截至目前，我们把agent做文本生成的任务归结到policy函数$\pi^\star$的选择上，即确定最优参数$\theta^\star$最大化某一个评价指标$J(\theta)$。

策略梯度法（Policy gradient）是用于寻找最优policy函数$\theta^\star$的一类策略优化方法，它基于评价指标$J(\theta)$对$\theta$的梯度。即为了寻找最优的参数$\theta^\star$，可以对$J$执行梯度上升算法：

$$\theta_{t+1}=\theta_t+    \alpha \widehat{\nabla J\left(\boldsymbol{\theta}_{t}\right)}$$

其中，$\widehat{\nabla J\left(\boldsymbol{\theta}_{t}\right)}$表示梯度的估计，这里的估计由策略梯度定理（Policy gradient theorem）保证：

$$\nabla J(\boldsymbol{\theta}) \propto \sum_\limits{s} \mu(s) \sum_\limits{a} q_{\pi}(s, a) \nabla \pi(a \mid s, \boldsymbol{\theta})$$

其中，$\mu(s)$表示agent进入状态$s$的可能性（归一化的）；$q(s,a)$表示从状态$s$中选择动作$a$的质量（quality）。

评价指标$J(\theta)$的梯度估计是所有状态、所有动作上的累加。但是在实际应用中，我们希望能够仅通过当前的状态$S_t$和动作$A_t$来计算梯度的估计，接下来引入强化算法（Reinforce algorithm）来解决这一问题。




#### 2.2.2 Reinforce Algorithm

回顾梯度的估计：

$$\nabla J(\boldsymbol{\theta}) \propto \sum_\limits{s} \mu(s) \sum_\limits{a} q_{\pi}(s, a) \nabla \pi(a \mid s, \boldsymbol{\theta})$$

$\mu_s$其实可以看做policy$\pi$下的状态$s$出现的概率，所以外层的累加可以看做内层关于$\pi$的期望：

$$\mathbb{E}_{\pi}\left[\sum_{a} q_{\pi}\left(S_{t}, a\right) \nabla \pi\left(a \mid S_{t}, \boldsymbol{\theta}\right)\right]$$

现在考虑内层的累加，内层引入$\pi(a\mid S_t,\boldsymbol{\theta})$，表示基于状态$S_t$的动作概率分布：

$$\mathbb{E}_{\pi}\left[\sum_{a} \pi\left(a \mid S_{t}, \boldsymbol{\theta}\right) q_{\pi}\left(S_{t}, a\right) \frac{\nabla \pi\left(a \mid S_{t}, \boldsymbol{\theta}\right)}{\pi\left(a \mid S_{t}, \boldsymbol{\theta}\right)}\right]$$

$\sum_\limits{a} \pi\left(a \mid S_{t}, \boldsymbol{\theta}\right) q_{\pi}\left(S_{t}, a\right) $是在所有动作$a$上的累加，可以变形为：

$$\sum_{a} \pi\left(a \mid S_{t}, \boldsymbol{\theta}\right) q_{\pi}\left(S_{t}, a\right) =q_\pi(S_t,A_t)$$

则有：

$$\nabla J(\boldsymbol{\theta}) \propto \mathbb{E}_{\pi}\left[q_{\pi}\left(S_{t}, A_{t}\right) \frac{\nabla \pi\left(A_{t} \mid S_{t}, \boldsymbol{\theta_t}\right)}{\pi\left(A_{t} \mid S_{t}, \boldsymbol{\theta_t}\right)}\right] $$

至此，我们可以仅通过一个样本$(S_t,A_t)$来进行梯度估计了！

将$q_\pi(S_t,A_t)$记为$G_t$，可以得到强化算法的更新策略：

$$\boldsymbol{\theta}_{t+1} \doteq \boldsymbol{\theta}_{t} + \alpha G_t \frac{\nabla \pi\left(A_{t} \mid S_{t}, \boldsymbol{\theta}\right)}{\pi\left(A_{t} \mid S_{t}, \boldsymbol{\theta}\right)}$$

$G_t$可以认为是从当前时间$t$到当前回合（episode）结束的累加reward的期望；$\nabla \pi\left(A_{t} \mid S_{t}, \boldsymbol{\theta}\right)$为一个向量，它指示当我们在次进入状态$S_t$时，采取动作$A_t$的概率增加最大的方向。



#### 2.2.3 RL引入text GANs

接下来我们将上文的一些结论引入GANs中。

首先构建一个判别器，它的输入是一段文本，输出为一个值，表示这段文本是真实文本（非机器生成文本）的概率。可以使用任何一个文本分类模型（如RNNs、CNNs等），其输出作为对输入的reward，将在**本回合结束时**传回生成器用于policy参数$\theta$的更新。

接着构造一个生成器，该生成器中需要包含我们在上文中提到的policy函数$\pi(a\mid s,\boldsymbol{\theta})$，$\boldsymbol{\theta}$对应生成器的参数，其将会按照上文中得到的reinforce algorithm进行更新。生成器能够接收一段文本，输出下一个token的概率分布（使用一个RNN就可以）：

$$h_t=RNN(h_{t-1},x_t)$$

$$p(a_t \mid x_1,x_2,...,x_t)=softmax(b+Wh_t)$$

由于我们使用中间反馈（intermediate rewards）$R_k$来计算$G_t$，但判别器的reward仅在每个回合结束时才会向生成器传递，这就意味着，只有生成器生成一个完整的句子后才能得到判别器的反馈，SeqGAN$^{10}$通过引入Monte-Carlo rollouts来解决这个问题：

$$R_{t}=\frac{1}{N} \sum_\limits{n=1}^{N} D_{\phi}\left(Y_{1: T}^{n}\right), Y_{1: T}^{n} \in MonteCarlo \left(Y_{1: t} ; N\right)$$

具体细节将在本文的第三节介绍。

#### 2.2.4 基于RL的GANs可能存在的问题

1. 采样方差

   由于中间策略梯度是由采样获得的，回合之间的方差会很大，导致训练过程十分不稳定，收敛较慢，针对这个问题，SeqGAN$^{10}$在前期使用MLE对生成器和判别器进行了预训练；

2. 局部最优点

   策略梯度方法容易收敛到局部最优解，尤其当状态-动作空间很大时。（比如文本生成时，每个时间步的选择空间为词表大小，接近十万量级）。



### 2.3 其他架构

文章$^{11}$将auto-encoder引入GAN，这里我们简单地介绍auto-encoder是如何引入的，它解决了什么问题。该文章具体的结构将在本文第三节中介绍。

首先简单介绍一下auto-encoder架构，auto-encoder包含两部分：encoder和decoder。encoder负责将输入$x$投影到维度相对更小的空间中的一个潜向量，decoder负责从潜向量中重建输入$x$，得到$x'$。auto-encoder的作用是捕捉输入中更通用的、更本质（essential）的特征，并尽量忽略输入中的噪声。

![auto-encoder](http://qiniu.shihanmax.top/20210409174424_2fyGxX_1*JzNrasJKhwCb2Uv79OBbuQ.jpeg)

那么auto-encoder如何能够引入GAN呢？

回顾我们在1.3中讨论的将GAN由图像领域引入文本领域时面临的本质问题：离散的生成器采样结果。

现在稍微改变一下GAN在文本生成上的思路：将句子的生成任务看作在句子空间中的句向量采样问题（而不是前述的序列的每一个token的采样问题）。也即是说，生成器的输出是一个潜空间的句向量（而不是一个句子）。

那么判别器的任务也发生了改变：判断生成器产生的句向量是不是“真实的”。那么，下一个问题就是，“真实的”句向量从哪里来？这里就可以引入auto-encoder了，首先，在训练GAN之前，可以先在大量语料上训练一个auto-encoder，训练完成后，从真实语料中采样得到的句子经过aoto-encoder编码得到的句向量，作为“真实的”句向量；而生成器生成的句向量则作为负样本，即“虚假的”句向量。

当GAN训练到最优时，我们可以取GAN的生成器生成的句向量（经过训练，对于判别器来说，它已经是“真假难辨”），然后将此向量输入auto-encoder的decoder，得到$x'$作为生成的结果。



## 三、GAN for text经典研究调研

| 时间 | paper                                                        | Source | Leaderboard |
| ---- | ------------------------------------------------------------ | ------ | ----------- |
| 2016 | GANs for Sequences of Discrete Elements with the Gumbel-softmax Distribution | arXiv  |             |
| 2016 | Generating Text via Adversarial Training                     | NLPS   |             |
| 2017 | Adversarial Feature Matching for Text Generation             | ICML   |             |
| 2017 | Adversarial Learning for Neural Dialogue Generation          | ACL    |             |
| 2017 | SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient | AAAI   | yes         |
| 2017 | RankGAN: Adversarial Ranking for Language Generation         | NIPS   | yes         |
| 2018 | MASKGAN: BETTER TEXT GENERATION VIA FILLING IN THE \_\_\_\_\_ | ICLR   |             |
| 2018 | LeakGAN: Long Text Generation via Adversarial Training with Leaked Information | AAAI   | yes         |
| 2018 | STWGAN-GP: Generating Text through Adversarial Training using Skip-Thought Vectors | NAACL  | yes         |
| 2019 | RelGAN: Relational Generative Adversarial Networks for Text Generation | ICLR   | yes         |
| 2020 | PPOGAN: Training language GANs from Scratch                  | NIPS   | yes         |
| 2020 | Improving GAN Training with Probability Ratio Clipping and Sample Reweighting | NIPS   |             |
| 2021 | Refining Deep Generative Models via Discriminator Gradient Flow | ICLR   |             |







## 四、GAN、RL和VAE的概念澄清

### 4.1 GAN和RL的联系

说“GAN是RL的特例”有失偏颇。准确来说和GAN很相似的是Actor-Critic（AC）。更准确来说是以**Deterministic Policy Gradient**（DPG）为代表的对于**连续动作输出**建模的RL算法。



### 4.2 GANs和VAE的联系



## 五、后记

文献$^{1,2,3}$系列十分适合作为GAN for text的入门材料，本文借鉴了大部分内容。

## Refs.

1. [Generative Adversarial Networks for Text Generation — Part 1](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-1-2b886c8cab10)
2. [Generative Adversarial Networks for Text Generation — Part 2: RL](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-2-rl-1bc18a2b8c60)
3. [Generative Adversarial Networks for Text Generation — Part 3: non-RL methods](https://becominghuman.ai/generative-adversarial-networks-for-text-generation-part-3-non-rl-methods-70d1be02350b)
4. [强化学习基础介绍](https://zhuanlan.zhihu.com/p/27860483)
5. [f-GAN: Training Generative Neural Samplers using Variational Divergence Minimization](https://arxiv.org/abs/1606.00709)
6. [wiki-相对熵](https://zh.wikipedia.org/wiki/相对熵)
7. [wiki-散度](https://zh.wikipedia.org/wiki/散度)
8. [Improved Training of Wasserstein GANs]( https://arxiv.org/abs/1704.00028)
9. [Categorical Reparameterization with Gumbel-Softmax](https://arxiv.org/abs/1611.01144)
10. [SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient](https://arxiv.org/pdf/1609.05473.pdf)
11. [Adversarial Text Generation Without Reinforcement Learning](https://arxiv.org/pdf/1810.06640.pdf)
12. 
