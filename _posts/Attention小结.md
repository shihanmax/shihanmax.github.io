#### 

attention最早在machine translation中被提出，用于seq2seq的解码过程中与encoder作注意力计算。

在seq2seq模型中，输入通过encoder计算得到一个中间向量，decoder接受中间向量后解码得到输出。这里就带来了一个问题：中间向量的容量未必能够保留输入的所有信息。针对这个现象，[Bahdanau et al., 2015](https://arxiv.org/pdf/1409.0473.pdf)提出了attention机制。

以一般的seq2seq模型为例，定义如下：

输入：$\mathrm{x}=[x_1, x_2, ...,x_n]$

输出：$\mathrm{y}=[y_1, y_2,...,y_m]$

encoder RNN在第$i$时刻的隐状态：$\mathrm{h}_i=[\overrightarrow{h_i}^T;\overleftarrow{h_i}^T]^T, i=1,2,...,n$

decoder RNN在第t个时间步的隐状态：$\rm{s}_t=f(\rm{s}_{t-1},y_{t-1},\rm{c}_t)$



常见的attention

- Content-base
- Location-base

- Bahdanau Attention
- Luong Attention
  - Dot
  - General
  - Concat（Additive）
- Scaled Dot-product 





