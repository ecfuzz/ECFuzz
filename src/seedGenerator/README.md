# Seed Generator

![](../../doc/pictures/classes_seedGenerator.png)

种子生成器依靠配置分析模块得到的如下信息进行工作，并在运行时使用内存存储：

- 配置项全集

- 基本配置项集合

- 配置项关系集合

种子生成器额外维护一个内存对象：

- 种子池：用于保存测试过程中有价值的种子

种子生成器提供以下接口：

- generateSeed() -> Seed : 生成一个种子

- addSeedToPool(Seed seed) -> void ：添加一个种子