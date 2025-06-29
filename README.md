# 中国象棋游戏

一个使用Python和Pygame开发的中国象棋游戏。

## 功能特点

- 完整的中国象棋规则实现
- 图形化界面
- 鼠标点击操作
- 回合制游戏流程

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行游戏：
```bash
python xiangqi.py
```

## 游戏操作

- 点击棋子选择
- 点击目标位置移动棋子
- 红方先行，双方轮流下棋

## 棋子移动规则

- **车**：横竖直线移动，不能越子
- **马**：走"日"字，不能被蹩马腿
- **象**：走"田"字，不能过河，不能被塞象眼
- **士**：只能在九宫格内斜走一格
- **将/帅**：只能在九宫格内直走一格
- **炮**：移动如车，吃子需隔一子
- **兵/卒**：过河前只能前进，过河后可左右移动

## 技术实现

- Python 3.x
- Pygame 2.5.2
- 面向对象设计
- 模块化代码结构

我使用的是miniconda python环境 在项目根目录下运行下面命令可以直接运行：
source venv/bin/activate && python xiangqi.py