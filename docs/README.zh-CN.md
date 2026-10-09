# Bird in the City · 城市中的鸟

**一个用双手手势控制、以城市生态为主题的像素风游戏原型。**

[English](../README.md) · [观看演示](https://www.youtube.com/watch?v=oaUomb2fTL8) · [代码结构](ARCHITECTURE.md)

![游戏标题与稻田场景](images/title.png)

## 这是什么项目？

玩家扮演一只失去栖息地、穿行于香港城市景观中的黄胸鹀。右手控制飞行，左手捏合射击，在玻璃、烟雾和高楼构成的障碍中生存，并收集恢复生命、护盾和射击强化道具。

这个项目尝试把城市环境对鸟类的压力转化成可以感知的游戏反馈：生命值下降时，小鸟的形态和城市背景一起变化。它是环境主题的交互原型；目前没有用户研究或教育效果数据来证明其实际影响。

![城市背景的三个状态](images/city-states.png)

| 生命值 | 视觉反馈 |
| :--- | :--- |
| 75–100 | 明亮的城市、健康的小鸟 |
| 25–74 | 色彩变暗的城市、受伤的小鸟 |
| 低于 25 | 灰色城市、重伤的小鸟 |

这些状态由当前生命值决定，回血后也会恢复，并非真实环境模拟。

## 怎么玩？

| 操作 | 方式 |
| :--- | :--- |
| 开始 / 查看故事 / 退出 | 鼠标点击菜单 PLAY / INTRO / QUIT |
| 移动 | 移动右手食指尖，小鸟活动范围限制在画面左侧三分之一 |
| 射击 | 左手拇指与食指捏合；保持捏合会按冷却间隔连续射击 |
| 游戏结束后重试 | 聚焦游戏窗口，按 R |
| 游戏结束后退出 | 聚焦游戏窗口，按 Q |
| 游戏中退出 | 关闭游戏窗口 |

摄像头需要能看清双手，建议保持充分照明。额外打开的 Hand Tracking 窗口显示摄像头画面及手部关键点。当前代码在本机处理画面。

![健康状态游戏画面](images/gameplay-healthy.png)

*截图来自项目已有的作品集素材，由游戏代码配合模拟手势输入渲染，分数和等级为展示用数值，不是实时试玩记录。详见[素材说明](images/README.md)。*

## 本地运行

准备 Python 3.11、摄像头，以及能正常使用图形界面和音频设备的电脑。

```bash
git clone https://github.com/092135/bird-in-the-city.git
cd bird-in-the-city
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Windows 创建虚拟环境时使用 `py -3.11 -m venv .venv`，在 PowerShell 中用 `.venv\Scripts\Activate.ps1` 激活，然后运行相同的安装和启动命令。

新增的 `run.py` 会进入正确的资源目录再启动原程序，解决从项目根目录启动时字体、音效相对路径不正确的问题。原有的 `cd main` → `python test.py` 方式仍可使用。

依赖文件提供旧版 MediaPipe Hands 接口的兼容性基线；本次文档整理没有完成真实摄像头全流程试玩，也不代表所有操作系统均已验证。

## 当前限制

- 需要摄像头。源代码虽然打印了“回退到键盘控制”的提示，但没有实现键盘移动和射击。
- 使用 `mp.solutions.hands` 旧接口，请在独立环境中安装指定依赖。
- 摄像头失败处理、音频设备异常处理仍需完善。
- `main/test.py` 是游戏主体，不是自动化测试文件；配置、菜单、交互、渲染目前集中在一个文件中。

## 仓库导航

- [`../run.py`](../run.py)：从根目录启动游戏。
- [`../requirements.txt`](../requirements.txt)：依赖版本。
- [`../main/test.py`](../main/test.py)：原始游戏实现。
- `main/Animation/`、`main/font/`、`main/sfx/`：游戏美术、字体和声音。
- [`ARCHITECTURE.md`](ARCHITECTURE.md)：技术流程、主要类与后续拆分建议。
- [`images/`](images/)：README 展示素材。
