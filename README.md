# 先进FPS游戏AI自瞄系统 / Advanced FPS Game AI Auto-Aim System

## 项目简介 / Project Introduction
本项目开发了一款高级的FPS游戏AI自瞄系统，旨在通过集成先进的图像识别、目标跟踪、运动预测和控制算法，打造最好的自然仿生自瞄体验。本系统使用YoloV5作为图像识别框架，结合卡尔曼滤波进行目标跟踪和运动预测，以及改进的PID算法来控制瞄准过程。
This project developed an advanced AI auto-aim system for FPS games, designed to create the best natural biomimetic auto-aiming experience by integrating advanced image recognition, target tracking, motion prediction, and control algorithms. The system utilizes YoloV5 as the image recognition framework, combined with Kalman filtering for target tracking and motion prediction, and an improved PID algorithm for aiming control.

## 核心功能 / Core Features

### 高精度目标识别 / High-Precision Target Recognition
- **敌人识别：** 采用高质量的训练素材，在低分辨率、较高的掩体遮挡和远距离对枪环境下，仍然能够准确识别敌人，保证瞄准的精确性。
- **Enemy Recognition:** Utilizing high-quality training materials, the system accurately identifies enemies even in low-resolution, high-cover, and long-range combat scenarios, ensuring precise aiming.
- **队友排除：** 完全排除对队友的误识别，确保团队作战的和谐。
- **Teammate Exclusion:** Completely eliminates misidentification of teammates, ensuring team harmony.
- **鲁棒性：** 集成先进的异常检测算法，对误识别具有高度的抵抗力，能够在复杂环境下稳定运行。
- **Robustness:** Integrates advanced anomaly detection algorithms, highly resistant to misidentification, and stable in complex environments.

### 动态跟踪与预测 / Dynamic Tracking and Prediction
- **卡尔曼滤波：** 利用卡尔曼滤波算法跟踪目标运动，预测其未来位置，为动态瞄准提供数据支持。
- **Kalman Filtering:** Uses Kalman filtering to track target movement and predict future positions, providing data support for dynamic aiming.
- **运动预测：** 结合改进的PID算法调整瞄准，以适应目标的动态移动。
- **Motion Prediction:** Combines an improved PID algorithm to adjust aiming to adapt to the dynamic movement of targets.

### 仿生学瞄准 / Biomimetic Aiming
- **PID算法：** 利用改进的PID算法和独立线程控制实现平滑瞄准，在鼠标信号的层面做到和人类操作无法分辨。
- **PID Algorithm:** Uses an improved PID algorithm and independent thread control to achieve smooth aiming that is indistinguishable from human operation at the level of mouse signals.
- **运动预测：** 在平滑瞄准的基础上适应目标的动态移动，确保对目标的锁定精准而快速。
- **Motion Prediction:** Adapts to the dynamic movement of targets based on smooth aiming, ensuring fast and precise target locking.

### 性能优化 / Performance Optimization
- **多线程并行处理：** 系统使用三线程并行处理，包括运动预测、鼠标信号平滑等功能，以提高处理速度和响应时间。
- **Multi-threading:** The system uses three parallel threads for processes including motion prediction and mouse signal smoothing, enhancing processing speed and response time.
- **高FPS支持：** 在笔记本CS帧数仅140fps的设备上，空载时FPS可达300，与游戏一起运行时可保持100fps以上，更好的电脑可以做到和游戏刷新率的完全同步。
- **High FPS Support:** On devices with a native CS frame rate of only 140fps, the system can reach 300 FPS when unloaded and maintain over 100 FPS when running with the game, with better computers achieving full synchronization with the game refresh rate.

### 反作弊技术 / Anti-Cheat Technology
- **驱动级控制：** 对截图和鼠标操作均采用驱动级别的控制，最大程度地规避反作弊系统的检测。
- **Driver-level Control:** Uses driver-level control over screenshots and mouse operations to maximally evade detection by anti-cheat systems.
- **独立线程处理鼠标信号：** 确保程序的鼠标信号刷新频率与物理鼠标一致，绕过多种平台的初步检测。
- **Independent Thread for Mouse Signals:** Ensures that the program's mouse signal refresh rate matches that of the physical mouse, circumventing preliminary checks across multiple platforms.
- **仿生学瞄准：** 通过调整瞄准算法，在鼠标信号的层面做到和人类操作无法分辨。
- **Biomimetic Aiming:** Adjusts the aiming algorithm to make it indistinguishable from human operation at the level of mouse signals.

### 功能丰富 体验独特 / Rich Features for a Unique Experience
- **自动压枪 / Automatic Recoil Control**
- **自动急停检测 / Automatic Sudden Stop Detection**
- **集成多种开火模式 / Integrated Multiple Firing Modes**
- **识别武器 / Weapon Recognition**

## 使用与配置 / Usage and Configuration
本系统支持完全的可调性，用户可以根据自己的需要调整以下参数：
This system offers full adjustability, allowing users to customize the following parameters according to their needs:
- 反应时间 / Reaction Time
- 锁定速度 (默认值最贴近人类习惯) / Locking Speed (default settings closest to human habits)
- 运动预测提前量 (默认值最贴近人类习惯) / Motion Prediction Lead Time (default settings closest to human habits)
- 运动平滑强度 (默认值最贴近人类习惯) / Motion Smoothing Intensity (default settings closest to human habits)
- 自定义开火模式 / Custom Firing Modes

## 成就 / Achievements
- **实战表现：** 在2024S18赛季单挑榜中达到第9名，胜率达到90%。
- **Combat Performance:** Achieved 9th place in the solo challenge leaderboard for the 2024 S18 season, with a win rate of 90%.

## 安装与运行 / Installation and Running
请按照以下步骤安装和运行AI自瞄系统：
Please follow the steps below to install and run the AI auto-aim system:
1. 克隆仓库到本地：`git clone [repository link]`
2. 安装必要的依赖：`pip install -r requirements.txt`
3. 运行系统：`python aim_assist.py`

## 许可证 / License
暂不提供

## 联络方式 / Contact Information
如有任何问题或需要技术支持，请通过以下方式联系我们：
If you have any questions or need technical support, please contact us via:
- 邮箱 / Email: [35********73@qq.com]

感谢您对我们项目的兴趣！
Thank you for your interest in our project!
