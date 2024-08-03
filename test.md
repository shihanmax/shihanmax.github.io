NLP
 数据结构与算法
  回溯
   框架
   例题
    N皇后
    所有的排列
 机器学习模型
  k-近邻法
  朴素贝叶斯
  决策树
  逻辑回归
  最大熵模型
  支持向量机SVM
  提升方法
  EM算法
  条件随机场CRF
  隐马尔可夫模型HMM
 深度学习模型
  词向量模型
   Glove
   FastText
   Word2vec
    skip-gram
    CBOW
  CNN
  RNN
   LSTM
    LSTM+CRF
   GRU
  Transformer
  mamba
 NLP下游任务（旧的待废弃）
  文本表示
   onehot表示（词袋模型，bag of words）
   tf-idf（词频-逆文档频率）
   word2vec词向量
   bert预训练模型
  文本分类
   任务
    给定一段文本，得到该文本的表示向量，对该向量做分类
   举例
    垃圾邮件/正常邮件分类
    正面情绪/负面情绪分类
   模型
    机器学习
     朴素贝叶斯
     逻辑回归
     svm
    深度学习
     text CNN
     LSTM
  聚类
  序列标注
   任务
    对一段文本进行标注，即对每一个词都给出一个类别
   举例
    分词
    命名实体识别
    词性标注
    关系抽取
   模型
    条件随机场CRF
    隐马尔可夫模型HMM
    Bi-LSTM+CRF
     模型的结构？
     为什么使用这个结构？
   其他
    序列标注的标签一般使用BOI标签
  文本生成
   给定文本或者图片，生成一段文字
   模型
    多使用seq2seq模型
   文本摘要
    任务
     给定长文本text，使用模型得到该段文本的一个简短的总结
    模型
     机器学习
      使用tfidf可以得到该段文本中的关键字
     深度学习
      可以训练seq2seq模型，首先编码器由原始文本生成一段表示向量，进入解码器得到输出
  对话系统
   分类
    chit-chat闲聊
     多使用seq2seq模型，能回答简单的问题，不涉及查数据库，没有任务完成能力，主要为娱乐作用
    QA bot单轮会话
     我们有问答库K，存放着收集到的问题和答案对（Q，A），对给定的问题q，去库中检索最相近的问题Qi，然后将对应的答案返回
    task bot多轮会话
     NLU模块（natural language understanding，自然语言理解）
      基本方法
       分词
       词性标注
       命名实体识别
      包括
       domain 识别（对话领域识别）
       意图intent识别
       slot抽取
        槽信息抽取
     DM模块（dialogue manager，对话管理）
      dialogue state tracking
       对话状态追踪
      policy
       对话策略管理
     NLG模块（natural language generate，自然语言生成）
      自然语言生成
 LLM
  预处理
   数据准备
   分词技术
    工作流程
     文本归一化
      删除多余的换行符、空格等；大小写归一化、音调移除
      实现：https://huggingface.co/docs/tokenizers/api/normalizers
     预切分（pre-tokenization）
      通过空格或标点，将句子且氛围更小的单元
      实现：https://huggingface.co/docs/tokenizers/api/pre-tokenizers
      示例
       BERT tokenizer：基于空格和标点进行切分
       GPT2：基于空格和标签，但空格会保留成特殊字符“Ġ” 
       T5：仅基于空格进行切分，标点不会切分。并且空格会保留成特殊字符"▁"，并且句子开头也会添加特殊字符"▁"
     基于分词模型的切分
      实现：https://huggingface.co/docs/tokenizers/api/models
     后处理
      如添加special token等
      实现：https://huggingface.co/docs/tokenizers/api/post-processors
    分词粒度
     基于字
      特点
       token信息量少
       解码效率低
     基于子词（subword）
      特点
       词表规模适中
       可以捕捉同源词之间的关系
       无UNK
      方法
       BPE （Byte-Pair Encoding）
        训练流程
         1. 将原始文本数据分段
         2. 对每段文本，进行预切分
         3. 对所有预切分得到的词，进行wordlevel切分，生成原始词表
         4. 在达到退出条件前，循环执行以下步骤
          4.1 统计相邻子词pair的出现次数
          4.2 选择次数最多的一组pair，将其加入词表，同时记录一条合并规则
          4.3 将上述pair的合并更新到每个词的wordlevel切分结果
        推理流程
         1. 原始文本预切分
         2. 将每个词切分为最小单元
         3. 遍历每个merge rule，对每个词，将最小单元进行合并，得到最终结果
       BBPE（Byte-level BPE）
        与BPE的区别是：切分与合并的粒度是utf-8编码，即对原文本，先使用utf8进行编码
       WordPiece
       Unigram
       参考文档：https://zhuanlan.zhihu.com/p/651430181
     基于词
      特点
       词表庞大
       相近词之间的关系无法捕捉（如单复数）
       存在UNK
    分词工具
     SentencePiece
      支持BPE、Unigram、Char-level等分词方法
   预训练数据预处理
    处理pipeline
     1. 数据长度过滤（小于某一长度的，针对书籍类别需要增加）
     2. 文本内容归一化（简繁体转化、汉字归一化）
     3. 特殊字符过滤（正则过滤）
     4. 分词&敏感词过滤
     5. 特殊内容过滤（过滤作者、文章来源、头部导航信息、尾部导航信息 、url链接等）
     6. 敏感信息打码
     7. 文章内句子去重&文章相似度去重
  模型结构
   Transformers
    Position Embedding
     Sinsuoid
     RoPE
      [[cos m \theta, -sin m \theta], [sin m \theta, cos m \theta]]
      外推方法
       推理时加入
        PI线性内插
         按照目标长度，缩放旋转弧度
        NTK-aware
         增大RoPE的base（原来是10000），高频分量（向量低维度部分）旋转速度降幅低，低频分量旋转速度降幅高
        NTK-by-parts
         不改变高频部分，仅缩小低频分量的旋转弧度
        Dynamic NTK
         推理长度小于等于训练长度时，不进行插值，推理长度大于训练长度时，每一步都通过NTK-aware插值动态放大base
        YaRN
         NTK-by-parts与注意力分布修正策略的结合，通过温度系数修正注意力分布
        ReRoPE？
         待阅读：https://github.com/bojone/rerope/blob/main/rerope_patch.py
       训练时加入
        KERPLE
        XPOS
        HWFA
     Alibi
      https://arxiv.org/pdf/2108.12409.pdf
      softmax(q_i K^T + m * (-(i-1), ..., -2, -1, 0); m=2^(-8/n) for attention head i..n
      外推方法
       内插
       NTK Alibi
       参考：https://github.com/keezen/ntk_alibi
     cubox://card?id=7147218958729349367
     长度外推
      外推目的
       在训练时使用较短的序列，而在推理时使模型能够处理比训练时更长的序列，同时保持或接近训练时的性能。
      外推面临的问题
       外推部分位置编码训练中没有见过，泛化性能差（即使无参数，也会影响上层学习）
       预测时序列更长，注意力更分散，熵更高
      认知误区
       单单优化位置编码的设计，未必能够解决长度外推问题；
       外推的基本前提是函数的光滑性，而RoPE、Sinusoidal等位置编码是正余弦函数的组合，在某些位置是高频振荡的；
       而不震荡的位置编码函数，往往又缺乏足够的容量来编码位置信息
      外推测试基准
       CHE基准：Google《Neural Networks and the Chomsky Hierarchy》提出的长度泛化基准
        这里的CHE基准就是测试模型是否具有解析正则语言、上下文无关语言、以及上下文有关语言语义的能力吧，也就是看神经模型能不能模拟有限状态机、下推自动机以及线性有界自动机。对这三种语言的解析transformer相比rnn是有天然劣势的，其原因就是注意力机制的无序性以及作为补偿的位置编码的次优性，用这三种语言比较rnn和transformer的话后者确实吃亏的。自然语言跟这三种语言明显不一样，众多实践已经证明transformer的自然语言语义解析能力远大于rnn的。这就带来一个问题：用che基准衡量transformer长度外推能力所得到的优劣结论，可以作为其对自然语言长度外推能力的有效参考吗？
    Self Attention
     KVCache
     优化
      QKV计算
       MHA -> MQA、GQA
        MQA、GQA主要通过降低KV Cache来提升吞吐量（+30%～40%）
      硬件&计算逻辑优化
       FlashAttention
       显存架构分析
      attention机制优化
       Sliding Window Attention
       Shift Short Attention (LongLoRA)
       Attention Sink (Streaming LLM)
    FeedFoward Neural Network（FFN）
    LayerNorm
     相关面试题
      LN的作用
      可学习参数量分析
      LN和BN的区别，为什么不用BN
      PostNorm和PreNorm有什么不同？（收敛速度、效果）、为什么最近的模型开始使用prenorm了
   模型参数量与计算分析
    参数量计算
     以llama2-7b为例V*h + L * (12.04h^2 + 12.36h)
      词向量
       V*h
      transformer layer * L
       self attention (4h^2 + 4h)
        W_Q、W_K、W_V矩阵: h^2 * 3 + 3h
        W_O矩阵：h^2 + h
       MLP (8.04h^2 + 6.36h)
        上投影矩阵W1: h * intermediate_size (2.68h) + 2.68h
        上投影矩阵W_gate：h * intermediate_size (2.68h) + 2.68h
        下投影矩阵W2：intermediate_size (2.68h) * h + h
       LayerNorm (RMSNorm) * 2
        self attention层和MLP层后各有一个RMSNorm层：h * 2
    训练时显存分析
     以llama2-7b为例（20 bytes; 20*7B=140G）
      模型状态
       fp16参数 = 2bytes
       fp16梯度 = 2bytes
      优化器状态
       fp32参数=4bytes
       fp32梯度=4bytes
       fp32 momentum = 4bytes
       fp32 variance = 4bytes
    推理时显存分析
     以llama2-7b为例（2 bytes; 2*7B=14G）
      fp16参数 = 2bytes
    计算量
    训练时间估计
    KV Cache分析
    cubox://card?id=7159099260032519387
   MOE混合专家模型
    原理：将传统transformer模型中的FFN替换为MoE层（多个专家层），并通过门控网络，控制token级别的分发
    优缺点
     优势
      与稠密模型相比，训练速度更快
      同参数量模型，推理更快
     劣势
      需要显存资源多
      微调存在泛化能力不足的问题
  训练
   强化学习
    chatgpt训练流程
     pretrain
     SFT
     RLHF
      RM
      PPO
    强化学习算法
     DPO
      与RLHF对比
   高效参数训练
    工程实现
     PEFT
    方法
     LoRA
      lora微调target选择
       1. 理论上transformer中的所有linear层均可配置为lora target
       2. 部分target的lora微调，能够和所有linear层微调效果持平：https://arxiv.org/pdf/2106.09685
      lora显存&参数&训练时间分析
     LoRA+
      原理
      参考
       https://arxiv.org/pdf/2402.12354.pdf
       https://kexue.fm/archives/10001
     DoRA
      https://arxiv.org/pdf/2402.09353.pdf
     QLoRA
     Ptuning
     Prefix tuning
     Prompt tuning
   并行训练
    并行基础知识
     分布式通信原语
      ref: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/collectives.html
      Reduce
       one rank receives the reduction of input values across ranks
      AllReduce
       each rank receives the reduction of input values across ranks
      Broadcast/Scatter
       all ranks receive data from a “root” rank
      AllGather
       each rank receives the aggregation of data from all ranks in the order of the ranks
      ReduceScatter
       input values are reduced across ranks, with each rank receiving a subpart of the result
    并行方法
     数据并行 DP
      通信量分析
      两种实现
       RingAllReduce（pytorch中的DDP的原理）
       Parameter Server
     流水线并行PP
      实现
       GPipe
       PipeDream
     张量并行TP
    框架
     Megatron
     Deepspeed
      ZeRO系列
       ZERO DP
        减小模型的显存占用
       ZERO R
        减小剩余内存消耗
       ZERO Offload
        让CPU和内存参与训练
       ZERO Infinity
        NVMe（待补充）
     Accerate
   数据精度
    浮点数表示形式
     组成：符号位（sign）、指数位（exponent）、尾数位（fraction）
     二进制转十进制：(-1)^sign * 2^(exponent - 偏置) * 1.fraction(二进制)
    混合精度训练
     fp32
      1/8/23
     fp16
      1/5/10
     bf16
      1/8/7
   Scaling Law
    结论
     1. 对于Decoder-only的模型，计算量C(Flops), 模型参数量N，数据大小D(token数)，三者满足：C～=6ND
     2. 模型性能与C、N、D有关，与模型具体结构无关
     3. 固定N、C、D任意两个，剩下的与模型性能呈幂律关系
     4. 提升模型性能，模型参数量N和数据D需要同步放大
     5. Scaling Law同时适用于语言模型、其他模态及多模态任务
   训练trick
    packing sft
     1. fast-packing：将整个数据合并后打包为最大长度（包括inputs_id和attention mask）
     2. bin-packing：NPhard问题（无最优解），将数据排序后，使用两个指针进行装箱。
    dynamic batching
     Motivation: 多domain任务中，对于同一目标loss，不同domain的loss下降程度不一致情况，因此在同一个batch中可以设计动态loss（softmax方式）
    noise neptune
     noisy embeddings Finetune（https://arxiv.org/pdf/2310.05914.pdf）：在input embed上增加随机噪声
   多机多卡
    1. 通讯中断
     高容错程序自动自愈方案：EasyDL
    2. 存储问题同步
     重新启动进程自动同步已保存的ckpt
    3. zero3
    4. 卡损坏（无解）
    5. 训练突刺
     在训练代码中出现突刺自动加载最新的ckpt
  推理
   推理框架
    vllm
     https://zhuanlan.zhihu.com/p/661360117
      设计了一种针对KVCache的显存管理策略，的通过地址不连续的分块显存来保存KVCache，减少显存碎片，提高显存的有效利用率。（显存碎片产生的原因是，为了避免生成长度过长导致KVCache越界，因此会预分配最大长度的KVCache，但是实际上大部分请求的长度远小于最大长度，所以实际上很多显存被KVCache浪费了）
    TensorRT-LLM
    StreamingLLM
   推理优化
    显存
     KVCache
     PagedAttention
    计算
     算子融合
     高性能算子
    服务
     Continuous Batching
     Dynamic Batching
     Async Serving
    分布式
     张量并行
     流水线并行
     NCCL通信优化
    低比特量化
     INT4/INT8 weight only (W4A16 & W8A16)
     Weight + Activation同时量化
     KVCache量化
     Hopper架构下的FP8
   解码方法
    贪心解码
    beam search
    基于采样的解码
     带温度的随机采样
     top-k采样
     top-p采样
  模型族
   GPT
   Llama
   ChatGLM
   Qwen
   Baichuan
   https://zhuanlan.zhihu.com/p/651747035