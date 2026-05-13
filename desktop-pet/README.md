# 小星星桌面宠物

一个独立的 Electron 桌面宠物应用，基于原有的 Codex 宠物资源开发。

## 功能特性

### 1. 喝水提醒
- 每 30 分钟自动提醒喝水
- 宠物会播放喝水动画（需要补充对应动画帧）
- 可通过系统托盘菜单调整提醒间隔

### 2. 文件回收站
- 将文件拖拽到宠物嘴巴区域即可删除
- 文件会被移入系统回收站，可恢复
- 删除成功/失败会有通知提示

### 3. 专注模式
- 右键菜单或托盘菜单开启
- 显示敲键盘动画（需要补充对应动画帧）
- 实时计时器显示专注时长
- 独立窗口，可移动位置

### 4. 聊天同步
- 双击宠物或通过菜单打开聊天窗口
- 与小程序后端实时同步
- 显示对方在线状态
- 每 3 秒自动刷新消息
- 支持表情和文字消息

## 安装与运行

### 前置要求

1. Node.js 16+ 
2. Python 3.8+（后端运行需要）
3. MySQL 数据库

### 安装步骤

```bash
# 1. 进入桌面宠物目录
cd desktop-pet

# 2. 安装依赖
npm install

# 3. 配置后端数据库
# 编辑 server/config.py，修改数据库连接信息
# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://用户名:密码@localhost/数据库名'

# 4. 初始化后端数据库
cd ../server
pip install -r requirements.txt
python migrate.py  # 如果需要添加 token 字段
python app.py       # 启动后端服务

# 5. 运行桌面宠物（新终端窗口）
cd ../desktop-pet
npm start
```

### 打包应用

```bash
npm run build
```

打包后的安装包在 `dist/` 目录下。

## 默认用户账号

后端预置了两个测试用户：

| 用户名 | 密码 | 昵称 |
|--------|------|------|
| user1 | 951106 | 星星住进太阳里 |
| user2 | 950812 | 太阳怀里有星星 |

## 项目结构

```
-pet/
├── desktop-pet/          # Electron 桌面宠物应用
│   ├── main.js          # 主进程
│   ├── pet.html         # 宠物主窗口
│   ├── focus.html       # 专注模式窗口
│   ├── chat.html        # 聊天窗口
│   ├── assets/          # 资源文件
│   │   └── spritesheet.webp
│   └── package.json
│
├── server/              # Flask 后端服务
│   ├── app.py           # Flask 应用入口
│   ├── models.py        # 数据模型
│   ├── config.py        # 配置文件
│   ├── migrate.py       # 数据库迁移脚本
│   └── requirements.txt
│
└── starlet/             # 原 Codex 宠物资源
    ├── pet.json
    └── spritesheet.webp
```

## 操作说明

| 操作 | 功能 |
|------|------|
| 拖拽宠物 | 移动位置 |
| 双击宠物 | 打开聊天窗口 |
| 右键宠物 | 显示菜单 |
| 拖拽文件到嘴巴 | 删除文件 |
| 系统托盘双击 | 显示宠物 |
| 系统托盘右键 | 显示菜单 |

## 动画资源补充

当前使用的 `spritesheet.webp` 包含基本的行走动画。建议补充以下动画帧：

1. **喝水动画**：宠物喝水的帧序列
2. **专注/敲键盘动画**：宠物敲键盘的帧序列
3. **吃文件动画**：宠物"吃掉"文件的帧序列
4. **待机动画**：宠物休息/晃动的帧序列

每套动画建议 4-8 帧，垂直排列在 spritesheet 中。修改对应 HTML 文件的 CSS `background-position` 和 `steps()` 即可。

## 技术栈

- **前端**：Electron + HTML/CSS/JavaScript
- **后端**：Flask + Flask-SQLAlchemy + MySQL
- **通信**：RESTful API + 轮询

## 注意事项

1. 确保后端服务 (`python app.py`) 在 `http://localhost:5000` 运行
2. 首次运行前需要初始化 MySQL 数据库
3. 聊天功能需要先登录才能使用
4. 文件删除操作使用系统回收站，不会永久删除

## 许可证

MIT