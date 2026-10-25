---
title: "Post by @yaogangqiang on X"
author: "@yaogangqiang"
site: "X (Twitter)"
published: 2026-08-11
source: "https://x.com/yaogangqiang/status/2087108405337153953"
domain: "x.com"
language: "en"
description: "Pi 正在把进程内的 Agent Loop，升级为可跨进程恢复的 Durable Runtime。 在 Pi 的定义中，Harness 与普通 Agent Loop 的核心区别是：Loop 的执行依赖当前进程；Harness 将已接受的 Prompt 变成可跨进程恢复的持久化 "
word_count: 334
---

Pi 正在把进程内的 Agent Loop，升级为可跨进程恢复的 Durable Runtime。

在 Pi 的定义中，Harness 与普通 Agent Loop 的核心区别是：Loop 的执行依赖当前进程；Harness 将已接受的 Prompt 变成可跨进程恢复的持久化 Operation。

问题是：模型或工具执行期间进程死亡，重启后如何确定做到哪一步，既不丢失已提交工作，也不盲目重跑副作用？

Harness v2 采用类似 Event Sourcing 的 journal-and-reduce：持续追加编排记录，再根据记录的顺序、存在与缺失，replay/reduce 出当前状态。

当前规范则类似于每次状态转换都打一个小快照：写入完整、以 ID 为主的 OperationState，再用 slot 指向最新版。恢复直接读取最新状态及其引用，不再 replay 编排历史。

与传统 ES 的阶段性快照不同，这里的快照不是用于缩短 event replay 的派生缓存，而是恢复的权威状态。

它仍不能保证外部效果 exactly-once；intent → effect → settlement 只是将不确定窗口显式化，再按 replay 策略处理。代价是重复写入完整状态，换来显式、可枚举、可测试的崩溃状态。  
[https://t.co/mpZboJIBCr](https://t.co/mpZboJIBCr)
