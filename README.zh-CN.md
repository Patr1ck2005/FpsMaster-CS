# FpsMaster-CS

**历史计算机视觉与输入控制原型。** 保留 YOLOv5 检测、跟踪／滤波、控制逻辑和 Windows 桌面界面的实验。

[English](README.md) · [文档历史](docs/README-history.md)

## 源码索引

| 路径 | 内容 |
|---|---|
| `models/`、`utils/` | 检测模型支持与上游衍生工具 |
| [cs_master/detector.py](cs_master/detector.py) | 检测集成 |
| [cs_master/kfilter.py](cs_master/kfilter.py) | 跟踪／滤波 |
| `cs_master/controller.py`、`cs_master/main_loop.py` | 输入／控制流程 |
| `cs_master/gui.py`、`main.py` | PyQt 桌面入口 |
| `*.engine`、`*.pyd` | 历史平台二进制 |

## 状态与研究边界

这是历史源码档案，不是持续维护的竞技游戏产品或经过验证的性能基准。旧说明中关于完美识别、输入不可区分、排行榜成绩和反作弊兼容性的表述，没有本仓库可复现评估支持，不应视为已经验证的事实。

打开桌面应用可能初始化输入监听与控制逻辑，因此本页提供**源码阅读入口**，不提供针对其他玩家使用的快速操作教程。适合继续研究的范围是离线录像、自建模拟器或明确授权测试环境，分别测量检测误差、跟踪稳定性和延迟。

原环境混合 Windows 原生模块、序列化引擎和 Python 依赖，当前可移植性与二进制来源没有重新验收。本次没有启动驱动、GUI、控制器或模型，原源码和贡献历史保留。

## 许可与来源

此快照未声明仓库整体许可证。模型代码和工具可能有各自上游条款，复用前需检查文件头与说明；包含二进制不代表已获使用授权或已具备可复现性。[旧公开 README](docs/README-history.md) 可从 Git 历史追溯。
