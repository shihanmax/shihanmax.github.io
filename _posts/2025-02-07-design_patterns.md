---
date: 2025-02-07 21:06:09
display_type: note
layout: post
mathjax: true
syntaxHighlighter: true
tags:
title: 设计模式简述
---


# 第一章 简单工厂模式
面向对象的优点：
- 可维护
- 可复用
- 可扩展
- 灵活性好
通过封装、继承、多态（面向对象三大特性）降低程序的耦合度，使用设计模式使程序更加灵活，容易修改，易于复用。

以计算器为例：
封装 - 将业务逻辑和界面逻辑分开，这样业务逻辑可以复用：
将运算类Operation与客户端代码分开
继承 - 如果需要改动Operation类（如添加一个sqrt操作），怎样避免改动目前正常工作的Operation类呢？
使用继承，将各个运算分离。
示例如下：

```java
public class Operation // 运算类
{
    private double _numberA = 0;
    private double _numberB = 0;
    
    public double NumberA
    {
        get { return _numberA; }
        set { _numberA = value; }
    }
    
    public double NumberB
    {
        get { return _numberB; }
        set { _numberB = value; }
    }
    
    public virtual double GetResult()
    {
        double result = 0;
        return result;
    }
}
    
class OpertionAdd : Operation //加法类
{
    public override double GetResult()
    {
        double result = 0;
        result = NumberA + NumberB;
        return result;
    }
}

class OpertionSub : Operation //减法类
{
    public override double GetResult()
    {
        double result = 0;
        result = NumberA - NumberB;
        return result;
    }
}

class OpertionMul : Operation //乘法类
{
    public override double GetResult()
    {
        double result = 0;
        result = NumberA * NumberB;
        return result;
    }
}

class OpertionDiv : Operation //除法类
{
    public override double GetResult()
    {
        double result = 0;
        if (NumberB == 0)
            throw new Exception("除数不能为0！");
        result = NumberA / NumberB;
        return result;
    }
}


public classOperationFactory //运算工厂类（简单工厂模式）
{
    public static Operation createOperate(string operate)
    {
        Operation oper = null;
        switch (operate)
        {
            case "+":
                oper = new OperationAdd();
                break;
            case "-":
                oper  =new OperationSub();
                break;
            case "*":
                oper = new OperationMul();
                break;
            case "/":
                oper = new OperationDiv();
                break;
        }
        return oper;
    }
}

Operation oper;
oper = OperationFactory.CreateOperate("+");
oper.NumberA = 1;
oper.NumberB = 2;
double result = oper.GetResult();
```

# 第二章 策略模式
商场收银台需要一个收款软件，要求输入各商品的单价和数量，合计总消费。
迭代过程：
增加打折功能
增加满xxx减xx功能
增加积分兑换礼品功能
...

使用简单工厂模式来实现：
```java
abstract class CashSuper // 现金收取超类
{
    public abstract double acceptCash(double money); //现金收取超类的抽象方法
}

class CashNormal : CashSuper //正常收费类
{
    public override double acceptCash(double money)
    {
        return money;
    }
}

class CashRebate : CashSuper //打折类
{
    private double moneyRebate = 1d;
    public CashRebate(string moneyRebate)
    {
        this.moneyRebate = double.Parse(moneyRebate);
    }
    
    public override double aceptCash(double money)
    {
        return money * moneyRebate;
    }
}

class CashReturn : CashSuper//满减类
{
    private double moneyCondition = 0.0d;
    private double moneyReturn = 0.0d;
    public CashReturn(string moneyCondition, string moneyReturn)
    {
        this.moneyCondition = double.Parse(moneyConditon);
        this.moneyReturn = double.Parse(moneyReturn);
    }
    
    public override double acceptCash(double money)
    {
        double result = money;
        if (money >= moneyCondition)
            result = money - Math.Floor(money / moneyCondition) * moneyReturn;
        return result
    }
}

class CashFactory //现金收费工厂类
{
    public static CashSuper createCashAccept(string type)
    {
        CashSuper cs = null;
        switch (type)
        {
            case "正常收费":
                cs = CashNormal();
                break;
            case "满300返100":
                CashReturn cr1 = new CashReturn("300", "100");
                cs = cr1;
                break;
            case "打8折":
                CashRebate cr2 = new CashRebate("0.8");
                cs = cr2;
                break;
        }
        return cs
    }
}

//客户端主要部分
double total = 0.0d;
private void btnOk_Click(object sender, EventArgs e)
{
    CashSuper csuper = CashFactory.createCashAccept(cbxType.SelectedItem.ToString());
    double totalPrices = 0d;
    totalPrices = csuper.acceptCash(Convert.ToDouble(txtPrice.Text) * Convert.ToDouble(txtNum.Text));
    total += totalPrices;
    lbxList.Items.Add("单价： " + txtPrice.Text + "数量： " + txtNum.Text + " " + cbxType.SelectedItem + "合计： " + totalPrices.ToString());
    lblResult.Text = total.ToString();
}
```
工厂模式可以解决这个问题，但这个模式只是解决了对象创建的问题，由于工厂本身包含了所有的收费模式，商场如果经常要修改促销方案，则每次维护都需要修改这个工厂，以至于代码需要重新编译部署，工厂模式不是最好的办法，面对算法的经常变动，应该有更好的解决办法。

策略模式
策略模式（Strategy）定义了算法家族，分别封装起来，让它们之间可以互相替换，此模式避免让算法的变化影响到使用算法的客户。
商场的促销方式多样，其实都是一些算法，用工厂来生成算法对象，这没有错，但算法本身只是一种策略，最重要的是这些算法是随时都可能互相替换得，这就是变化点，而封装变化点是面向对象的一种很重要的思维方式。

使用策略模式实现：
```java
abstract class CashSuper // 现金收取超类
{
    public abstract double acceptCash(double money); //现金收取超类的抽象方法
}

class CashNormal : CashSuper //正常收费类
{
    public override double acceptCash(double money)
    {
        return money;
    }
}

class CashRebate : CashSuper //打折类
{
    private double moneyRebate = 1d;
    public CashRebate(string moneyRebate)
    {
        this.moneyRebate = double.Parse(moneyRebate);
    }
    
    public override double aceptCash(double money)
    {
        return money * moneyRebate;
    }
}

class CashReturn : CashSuper//满减类
{
    private double moneyCondition = 0.0d;
    private double moneyReturn = 0.0d;
    public CashReturn(string moneyCondition, string moneyReturn)
    {
        this.moneyCondition = double.Parse(moneyConditon);
        this.moneyReturn = double.Parse(moneyReturn);
    }
    
    public override double acceptCash(double money)
    {
        double result = money;
        if (money >= moneyCondition)
            result = money - Math.Floor(money / moneyCondition) * moneyReturn;
        return result
    }
}

//以上一个超类和四个具体收费类与工厂模式中的相同

class CashContext // CashContext类，上下文对象
{
    CashSuper cs = null;
    
    public CashContext(string type)
    {
        switch (type)
        {
            case "正常收费":
                CashNormal cs0 = new CashNormal();
                cs = cs0
                break;
            case "满300返100":
                CashReturn cr1 = new CashReturn("300", "100");
                cs = cr1;
                break;
            case "打8折":
                CashRebate cr2 = new CashRebate("0.8");
                cs = cr2;
                break;
        }
    }
    
    public double GetResult(double money)
    {
        return cs.acceptCash(money);
    }
}

//客户端代码
double total = 0.0d;
private void btnOk_Click(object sender, EventArgs e)
{
    CashContext csuper = new CashContext(cbxType.SelectedItem.ToString());
    double totalPrices = 0d;
    totalPrices = csuper.GetResult(Convert.ToDouble(txtPrice.Text) * Convert.ToDouble(txtNum.Text));
    total += totalPrices;
    lbxList.Items.Add("单价： " + txtPrice.Text + "数量： " + txtNum.Text + " " + cbxType.SelectedItem + "合计： " + totalPrices.ToString());
    lblResult.Text = total.ToString();
}

```

简单工厂模式和策略模式的对比

```java
CashSuper csuper = CashFactory.createCashAccept(cbxType.SelectedItem.ToString()); //简单工厂模式
CashContext csuper = new CashContext(cbxType.SelectedItem.ToString()); //策略模式
```

简单工厂模式需要让客户端认识两个类：CashSuper 和 CashFactory，而策略模式与简单工厂模式结合的方法，客户端只需要认识一个类 CashContext 就可以。

策略模式解析
策略模式是一种定义一系列算法的方法，从概念上看，所有这些算法完成的都是相同的工作，只是实现不同，它可以以相同的方式调用所有的方法，减少了各种算法类与使用算法类之间的耦合。

策略模式的优点
- 策略模式的strategy类层次为Context定义了一系列可供重用的算法或行为。继承有助于析取出这些算法的公共功能
- 策略模式简化了单元测试，因为每个算法都有自己的类，可以通过自己的接口单独测试。

策略模式就是用来封装算法的，但在实践中，我们发现可以用它来封装几乎任何类型的规则，只要在分析过程中听到需要在不同时间应用不同的业务规则，就可以考虑使用策略模式处理这种变化的可能性。
在基本的策略模式中，选择所用具体实现的职责由客户端对象承担，并转交给策略模式的Context对象。

# 第三章 单一职责原则
单一职责原则（SRP）：就一个类而言，应该仅有一个引起它变化的原因。
如果一个类承担的职责过多，就等于把这些职责耦合在一起，一个职责的变化可能会削弱或者抑制这个类完成其他职责的能力。这种耦合会导致脆弱的设计，当变化发生时，设计会遭受到意想不到的破坏。
以俄罗斯方块游戏为例，应该将游戏的逻辑层和界面层分例。
软件设计真正要做的许多内容，就是发现职责并把那些指责相互分离，如果你能想到多于一个的动机去改变一个类，这个类就有多余一个的职责，就应该考虑将职责分离。

# 第四章 开放-封闭原则
开放-封闭原则：软件实体（类、模块、函数等）应该可以扩展，但是不可修改。
这个原则有两个特征：
1. 对于扩展是开放的（Open for extension）；
2. 对于更改是封闭的（Closed for modification）

怎样的设计才能面对需求的改变却可以保持相对稳定，从而使系统可以在第一个版本以后不断推出新的版本？

无论模块是多么的封闭，都会存在一些无法对之封闭的变化，既然不可能完全封闭，设计人员必须对与他设计的模块应该对哪种变化封闭做出选择。他必须事先猜测出最有可能发生的变化种类，然后构造抽象来隔离那些变化。
开放-封闭原则是面向对象设计的核心所在。遵循这个原则可以带来面向对象技术所声称的巨大好处，也就是可维护、可扩展、可复用、灵活性好。开发人员应该仅对程序中呈现出频繁变化的那些部分作出抽象，然而，对于应用程序的每一个部分都刻意地进行抽象同样不是一个好主意，拒绝不成熟的抽象和抽象本身一样重要。

# 第五章 依赖倒转原则
依赖倒转原则：
- 高层模块不应该依赖低层模块，两个都应该依赖抽象
- 抽象不应该依赖细节，细节应该依赖抽象

里氏代换原则：
子类型必须能够替换掉它们的父类型正是由于子类型的可替换性才使得使用父类类型的模块在无需修改的情况下就可以扩展。

依赖倒转其实可以说是面向对象设计的标志，用哪种语言来编写程序不重要，如果编写时考虑的都是如何针对抽象编程而不是针对细节编程，即程序中所有的依赖关系都是终止于抽象类或者接口，那就是面向对象的设计，反之，就是过程化的设计。

# 第六章 装饰模式
装饰模式：动态地给一个对象添加一些额外的职责，就增加功能来说，装饰模式比生成子类更为灵活。

附：面向对象的概念
1. 面向对象、类与实例
对象是一个自包含的实体，用一组可识别的特性和行为来标识。
类就是具有相同的属性和功能的对象的抽象的集合。
实例就是一个真实的对象。

2. 构造方法
又叫构造函数，其实就是对类进行初始化。构造方法与类同名，无返回值，也不需要void，在new的时候调用。所有类都有构造方法，如果不编码，系统默认生成空的构造方法。如果自己定义了构造方法，则系统默认的构造方法就会失效。
例：
```java
class Cat
{
    private String name = "";
    public Cat(String name) // 构造函数
    {
        this.name = name;
    }
    
    public String Shout()
    {
        return "My name is" + name;
    }
}

private void button1_click(object sender, EventArgs e)
{
    Cat cat = new Cat("咪咪")；
    MessageBox.Show(cat.Shout())
}
```

3. 方法重载
方法重载提供了创建同名的多个方法的能力，但这些方法需要使用不同的参数类型，方法重载可以在不改变原方法的基础上，新增功能。

4. 属性与修饰符
属性是一个方法或一对方法，但在调用它的 代码看来，他是一个字段，即属性适合于以字段的方式使用方法调用的场合。属性有两个方法：get和set。

```java
private int shoutNum = 3; // 声明一个内部字段，私有
public int ShoutNum // 声明ShoutNum属性，共有
{
    get {return shoutNum;}
    set {shoutNum = value;}
}
```

5. 封装
每个对象都能包含它能进行操作所需要的所有信息，这个特性称为封装，因此对象不必依赖其它对象来完成自己的操作，这样方法和属性包装在类中，通过类的实例来实现。
封装的好处：
    - 良好的封装能够减少耦合
    - 类的内部可以自由的修改
    - 类具有清晰的对外接口

6. 继承
对象的继承代表了一种“is-a”的关系。继承者还可以理解为是被继承者的特殊化，因为它除了具备被继承者的特性之外，还具备自己独有的个性。
如果子类继承于父类：
    - 子类拥有父类非private的属性和功能
    - 子类具有自己的属性和功能（即子类具有可扩展性）
    - 子类还可以以自己的方式实现父类的功能（方法重写）
在C#中，子类从它的父类中继承的成员有方法、域、属性、事件、索引指示器，但对构造方法，有些特殊，它不能被继承，只能被调用
```java
class Animal //父类（基类）
{
    protected string name = "";
    public Animal(string name)
    {
        this.name = name;
    }
}

class Cat : Animal // 子类
{
    public Cat(string name) : base(name)
    {}
}
```

继承使得所有子类的公共部分都放在了父类，使得代码得到共享，这就避免了重复，另外，继承可使得修改或者扩展继承而来的实现都较为容易。
继承是类与类之间的一种强耦合关系。继承的缺点是，父类变，子类也要变。

7. 多态
多态表示不同的对象可以执行相同的动作，但要通过他们自己的实现代码来执行。
注意：
    ○ 子类以父类的身份出现
    ○ 子类在工作时以自己的方式来实现
    ○ 子类以父类的身份出现时，子类特有的属性和方法不可以使用
多态的三个前提：
    a. 存在继承关系
    b. 子类要重写父类方法
    c. 父类数据类型的引用指向子类对象

```java
// JAVA多态示例：
    // 父类Animal
    class Animal {
        int num = 10;
        static int age = 20;
        public void eat() {
            System.out.println("动物吃饭");
        }
        
        public static void sleep(){
            System.out.println("动物睡觉");
        }
        
        public void run(){
            System.out.println("动物在奔跑");
        }
    }
    
    // 子类Cat
    class Cat extends Animal {
        int num = 80;
        static int age = 90;
        String name = "tomCat";
        public void eat(){
            System.out.println("猫吃饭");
        }
        
        public static void sleep() {
            System.out.println("猫在睡觉");
        }
        
        public void catchMouse() {
            System.out.println("猫在抓老鼠");
        }
    } 
    
    // 测试类Demo_Test1
    class Demo_Test1 {
        public static void main(String[] args) {
            Animal am = new Cat();
            am.eat();
            am.sleep();
            am.run();
            //am.catchMouse();
            //System.out.println(am.name); //以上两个报错
            System.out.println(am.num);
            System.out.println(am.age);
        }
    }
```

```bash
输出：
猫吃饭
动物在睡觉
动物在奔跑
10
20
```   
    
多态的理解

花木兰替父亲花弧从军。这时候花木兰是子类，花弧是父类。花弧有自己的成员属性年龄，姓名，性别。花木兰也有这些属性，但是很明显二者的属性完全不一样。花弧有自己的非静态成员方法‘骑马杀敌’，同样花木兰也遗传了父亲一样的方法‘骑马杀敌’。花弧还有一个静态方法‘自我介绍’，每个人都可以问花弧姓甚名谁。同时花木兰还有一个自己特有的非静态成员方法‘涂脂抹粉’。但是，现在花木兰替父从军，女扮男装。这时候相当于父类的引用（花弧这个名字）指向了子类对象（花木兰这个人），这样在其他类（其他的人）中访问子类对象（花木兰这个人）的成员属性（姓名，年龄，性别）时，其实看到的都是花木兰她父亲的名字（花弧）、年龄（60岁）、性别（男）。当访问子类对象（花木兰这个人）的非静态成员方法（骑马打仗）时，其实都是看到花木兰自己运用十八般武艺在骑马打仗。当访问花木兰的静态方法时（自我介绍），花木兰自己都是用她父亲的名字信息在向别人作自我介绍。并且这时候花木兰不能使用自己特有的成员方法‘涂脂抹粉’。 --多态中的向下转型

终于旗开得胜了，花木兰告别了战争生活。有一天，遇到了自己心爱的男人，这时候爱情的力量将父类对象的引用（花弧这个名字）强制转换为子类对象本来的引用（花木兰这个名字），花木兰又从新成为了她自己，这时候她完全是她自己了。名字是花木兰，年龄是28，性别是女，打仗依然那样生猛女汉子，自我介绍则堂堂正正地告诉别人我叫花木兰。OMG！终于，终于可以使用自己特有的成员方法‘涂脂抹粉’了。从此，花木兰完全回到了替父从军前的那个花木兰了。并且和自己心爱的男人幸福的过完了一生。 -- 多态中的向上转型

8. 重构
```java
class Animal
{
    ......
    
    public string Shout()
    {
        string result = "";
        for (int i =0; i < shoutNum; i++)
        {
            result += getShoutSound() + "，";
        }
        return "我的名字叫" + name + " " + result;
    }
    
    protected virtual string getShoutSound()
    {
        return "";
    }
}

class Cat : Animal
{
    public Cat() : base()
    {}
    
    public Cat(string name) : base(name)
    {}
    
    protected override string getShoutSound()
    {
        return "喵"
    }
}

class Dog : Animal
{
    public Dog() : base()
    {}
    
    public Dog(string name) : base(name)
    {}
    
    protected override string getShoutSound()
    {
        return "汪"
    }
}

class Sheep : Animal
{
    public Sheep() : base()
    {}
    
    public Sheep(string name) : base(name)
    {}
    
    protected override string getShoutSound()
    {
        return "咩"
    }
}
```

以上Cat、Dog、Sheep三个子类均继承自父类Animal，如果有需求：将自我介绍的格式修改成“我是...”，仅需要修改父类的Shout方法即可。
上面用到了一个设计模式，叫“模板方法”。

9. 抽象类
上例中的Animal对象在现实中并无实体（没有一个名为Animal的实体），考虑把它改为抽象类，同时将getSound方法改为抽象方法：

```java
abstract class Animal
{
    ......
    
    protect abstract string getSound(); // 抽象方法没有方法体
}
```

抽象类要注意几点：
    - 抽象类不能实例化
    - 抽象方法必须是被子类重写的方法
    - 如果类中包含抽象方法，那么类就必须定义为抽象类，不论其是否还包含其它一般方法。
应该使抽象类拥有尽可能多的共同代码，拥有尽可能少的数据。

10. 接口
接着 8.重构中的例子，如果还有更多小动物，如猴子Monkey，猪Pig，叮当Ding，它们都拥有一项特殊的技能：变化。但是不能给他们的父类Animal添加Change方法，因为并不是所有的动物都有变化的本领。此时，要用到接口。
接口是把隐式公共方法和属性结合起来，以封装特定功能的一个集合。一旦类实现了接口，类就可以支持接口指定的所有属性和成员。声明接口在语法上和声明类完全相同，但不允许提供接口中任何成员的执行方式。
还有，实现接口的类必须要实现接口中的所有方法和属性。

对猴子Monkey，猪Pig，叮当Ding三者所要求的变化技能，可以声明一个接口：
```java
interface IChange
{
    string ChangeTing(string thing);
}

class MachineCat : Animal, IChange // 机器猫继承自猫，并实现了 IChange 接口
{
    public MachineCat() : base()
    public MachineCat(string name) : base(name)
    
    public string ChangeThing(string thing) // 实现接口方法，注意不可用override
    {
        return base.Shout() + "我有万能口袋，我可变出：" + thing
    }
}
```

接口和抽象类的区别：
    1. 类是对对象的抽象；抽象类是对类的抽象；接口是对行为的抽象
    2. 如果行为跨越不同类的对象，可使用接口；对于一些相似的类对象，用继承抽象类
    3. 从设计角度讲，抽象类是从子类中发现了公共的东西，泛化出父类，然后子类继承父类，而接口是根本不知道子类的存在，方法如何实现还不确认，预先定义。
    4. 抽象类是自底向上抽象出来的，而接口则是自顶向下设计出来的
    
11. C#的可变数组ArrayList
ArrayList的优点：
    - 大小动态分配
    - 可随意添加、插入、移除某一范围的元素
ArrayList的缺点：
    - 它的元素可以使任何类型，也就是说，它不是类型安全的
在遍历ArrayList中的元素时，我们使用：
foreach(elementType item in someArrayList)
此时指定了元素的类型，在多种类型元素组成的ArrayList中，这种遍历方式会报错，所以使用ArrayList需要将值类型装箱为Object对象，在使用集合元素时，还要进行拆箱操作，这两步会带来较大的性能损耗。

```java
int i = 123;
object o = (object) i; // boxing

o = 123;
i = (int) 0; //unboxing
```

C#2.0后，使用泛型解决了这一问题。

12. 泛型

```java
using System.Collections.Generic;
public partial class Form1 : Form
{
    List<Animal> arrayAnimal; // 表示此集合只能接受Animal类型的数据。
    arrayAnimal = new List<Animal>();
    ......
}
```

通常情况下，都建议使用泛型集合，因为这样可以获得类型安全的直接优点而不需要从基集合类型派生并实现类型特定的成员。此外，如果集合元素为值类型，泛型集合类型的性能通常优于对应的非泛型集合类型。

13. 委托与事件
委托是对函数的封装，可以当做给方法的特征指定一个名称。而事件则是委托的一种特殊形式，当发生有意义的事情是，事件对象处理通知过程。
例子：
需求：有两只老鼠Jarry和Jack，一只猫Tom，当猫叫一声“喵，我是Tom”时，两只老鼠就说“猫来了，快跑”。
```java
class Cat
{
    private string name;
    public Cat(string name)
    {
        this.name = name;
    }
    
    public delegate void CatShoutEventHandler(object sender, CatShoutEventArgs args); // object sender:传递发送通知的对象
    public event CatShoutEventHandler CatShout;
    
    public void Shout()
    {
        Console.WriteLine("喵，我是{0}", name);
    }
    
    if (CatShout != null)
    {
        CatShoutEventArgs e = new CatShoutEventArgs();
        e.name = this.name
        CatShout(this, e);
    }
}

class Mouse
{
    private string name;
    public Mouse(String name)
    {
        this.name = name;
    }
    
    public void Run(object sender, CatShoutEventArgs args)
    {
        Console.WriteLine("猫{0}来了，{1}"快跑, args.name, name)
    }
}

public class CatShoutEventArgs : EventArgs
{
    private string name;
    public string Name
    {
        get {return name;}
        set {name = value;}
    }
}

static void Main(string[] args)
{
    Cat cat = new Cat("Tom");
    Mouse mouse1 = new Mouse("Jarry");
    Mouse mouse2 = new Mouse("Jack");
    
    Cat.CatShout += new Cat.CatShoutEventHandler(mouse1.Run());
    Cat.CatShout += new Cat.CatShoutEventHandler(mouse2.Run());
    
    cat.Shout();
    Console.Read();
}

```

输出：
```bash
喵，我是Tom
猫Tom来了，Jarry快跑
猫Tom来了，Jack快跑
```
