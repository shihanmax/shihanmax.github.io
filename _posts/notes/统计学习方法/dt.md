# 正则的灵活应用：

## 例1：以神经科学中 C1 大脑皮层神经元为例：

<crop>(0.35, 0.18, 0.65, 0.38)</crop>

- **大脑**
- **region_i**
- **neurons of region_k**

两个假设：
1. 某一区域（域）内，仅有少量神经元被激活。
2. 在空间上，相近的神经元作用类似。

上述结构中，各个神经元参数：
$$
W = 
\begin{cases}
w_{11}, \ldots, w_{1T_1} \\
w_{21}, \ldots, w_{2T_2} \\
\vdots \\
w_{P1}, \ldots, w_{PT_P}
\end{cases}
\quad T_p: \# \text{ of neurons in region } p
$$

假设原始的目标函数为 $ f(w) $，如何通过正则化的形式将上述两个假设考虑进来？

- **Old obj**: minimize $ f(w) $
- **New obj**: minimize $ f(w) + \sum_{i=1}^p \lambda_i \| w_{i,\cdot} \|_1 + \sum_{i=1}^p \sum_{j>i} \lambda_2 \| w_{ij} - w_{ij+1} \|^2 $

> 第 i 个 region  
> → 稀疏化  
> → 相邻神经元工作用不要有太大差别

---

## 例2：Time-Aware Recommendation

### Matrix Factorization:

Given User-Rating matrix:

$$
\text{user}_i \to \left[ \begin{array}{c|c} & r_{ij} \\ \hline & \end{array} \right] = \text{user}_i \to \left[ \begin{array}{c} \\ \hline \end{array} \right] \times K \left[ \begin{array}{c} \\ \hline \end{array} \right], \quad R_{ij} \approx U_i^T \cdot V_j
$$

$$
\uparrow \quad \text{Item}_j
$$