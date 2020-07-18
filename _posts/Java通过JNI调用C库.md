---
title:  "Java通过JNI调用C库"
date:   2018-10-15 00:00:00
categories: Java
tags:  JNI
syntaxHighlighter: yes
---

### 什么是库
库是写好的现有的，成熟的，可以复用的代码。现实中每个程序都要依赖很多基础的底层库，不可能每个人的代码都从零开始，因此库的存在意义非同寻常。本质上来说库是一种可执行代码的二进制形式，可以被操作系统载入内存执行。库有两种：静态库（.a、.lib）和动态库（.so、.dll）。
所谓静态、动态是指链接。

<!--more-->

### 静态库
之所以成为【静态库】，是因为在链接阶段，会将汇编生成的目标文件.o与引用到的库一起链接打包到可执行文件中。因此对应的链接方式称为静态链接。
试想一下，静态库与汇编生成的目标文件一起链接为可执行文件，那么静态库必定跟.o文件格式相似。其实一个静态库可以简单看成是一组目标文件（.o/.obj文件）的集合，即很多目标文件经过压缩打包后形成的一个文件。静态库特点总结：
- 静态库对函数库的链接是放在编译时期完成的。
- 程序在运行时与函数库再无瓜葛，移植方便。
- 浪费空间和资源，因为所有相关的目标文件与牵涉到的函数库被链接合成一个可执行文件。

### 动态库
通过上面的介绍发现静态库，容易使用和理解，也达到了代码复用的目的，那为什么还需要动态库呢？
为什么还需要动态库？
为什么需要动态库，其实也是静态库的特点导致。
- 空间浪费是静态库的一个问题。
- 另一个问题是静态库对程序的更新、部署和发布页会带来麻烦。如果静态库liba.lib更新了，所以使用它的应用程序都需要重新编译、发布给用户（对于玩家来说，可能是一个很小的改动，却导致整个程序重新下载，全量更新）。
动态库在程序编译时并不会被连接到目标代码中，而是在程序运行是才被载入。不同的应用程序如果调用相同的库，那么在内存里只需要有一份该共享库的实例，规避了空间浪费问题。动态库在程序运行是才被载入，也解决了静态库对程序的更新、部署和发布页会带来麻烦。用户只需要更新动态库即可，增量更新。

### 动态库特点总结：
- 动态库把对一些库函数的链接载入推迟到程序运行的时期。
- 可以实现进程之间的资源共享。（因此动态库也称为共享库）
- 将一些程序升级变得简单。
- 甚至可以真正做到链接载入完全由程序员在程序代码中控制（显示调用）。

### 实验(linux上编译动态链接库lib*.so的过程)：
```c++
1. //新建Demo.java
    public class Hello {
        static {
            try {
                System.loadLibrary("hello");
            } catch(UnsatisfiedLinkError e) {
                System.err.println("cannot load library" + e.toString());
            }
        }

        public Hello(){
        }

        public native void sayHello(String name);

        public static void main(String[] args) {
            Hello hello = new Hello();
            hello.sayHello("jack!");
        }
    }

2. //生成Demo.h
	i. javac Demo.java
	ii. javah Demo
	iii. //此时目录下生成Demo.h，包含对函数sayHello()的声明

3. //新建Demo.cpp，按照Demo.h中的声明格式，实现函数sayHello()
	#include "Hello.h"
	#include <stdio.h>
		 // 与 Hello.h 中函数声明相同
	JNIEXPORT void JNICALL Java_Hello_sayHello  (JNIEnv * env, jobject arg, jstring instring)
	{
    // 从 instring 字符串取得指向字符串 UTF 编码的指针
    const jbyte *str = (const jbyte *)env->GetStringUTFChars( instring, JNI_FALSE );
    printf("Hello,%s\n",str);
    // 通知虚拟机本地代码不再需要通过 str 访问 Java 字符串。
    env->ReleaseStringUTFChars( instring, (const char *)str );
    return;
	}

4. //编译Demo.cpp
	i. g++ -I/usr/lib/jvm/java-8-oracle/include -I/usr/lib/jvm/java-8-oracle/include/linux -fPIC -c Hello.cpp
	ii. g++ -shared Hello.o -o libhello.so

5. //将动态库libhello.so 放入usr/lib中，或者将其路径添加到动态库搜索路径

6. //通过Demo.java测试动态库的调用
	i. javac Demo.java
	ii. java Demo
	Hello,jack!
```



References

https://www.cnblogs.com/i80386/p/4442330.html
https://blog.csdn.net/chlaws/article/details/7650378/
