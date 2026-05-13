# 小星星桌面宠物 - 动画制作指南

## 当前 spritesheet 结构

`spritesheet.webp` 是一张包含多帧动画的精灵图，按**垂直方向**排列不同动画，每套动画按**水平方向**排列帧。

```
Y 轴方向（垂直）:
  0-200px   : 行走动画 (walk)
  200-400px : 喝水动画 (drink) - 需要补充
  400-600px : 专注敲键盘 (focus) - 需要补充
  600-800px : 吃文件 (eat) - 需要补充
  800-1000px: 待机动画 (idle) - 需要补充

X 轴方向（水平）:
  每帧 200px 宽，按顺序排列
```

## 基础参数

- **单帧尺寸**: 200px × 200px
- **每套动画帧数**: 建议 4-8 帧
- **文件格式**: WebP（支持透明通道）
- **推荐的 spritesheet 尺寸**: 
  - 宽度: 200px × 最大帧数（如 8 帧 = 1600px）
  - 高度: 200px × 动画套数（如 5 套 = 1000px）

## CSS Animation 配置

### 1. 行走动画（已有）

```css
#pet {
  animation: walk 0.8s steps(4) infinite;
}

@keyframes walk {
  0% { background-position: 0px 0px; }
  100% { background-position: -800px 0px; }  /* 4帧 × 200px = -800px */
}
```

### 2. 喝水动画（需要补充）

位置：Y = -200px 处

```css
#pet.drink {
  animation: drink 0.5s steps(4) infinite;
}

@keyframes drink {
  0% { background-position: 0px -200px; }
  100% { background-position: -800px -200px; }
}
```

### 3. 专注敲键盘动画（需要补充）

位置：Y = -400px 处（如果在 pet.html 中使用，需要新增类）

```css
#pet.focus {
  animation: typing 0.3s steps(6) infinite;
}

@keyframes typing {
  0% { background-position: 0px -400px; }
  100% { background-position: -1200px -400px; }  /* 6帧 × 200px = -1200px */
}
```

### 4. 吃文件动画（需要补充）

位置：Y = -600px 处

```css
#pet.eat {
  animation: eat 0.6s steps(5) infinite;
}

@keyframes eat {
  0% { background-position: 0px -600px; }
  100% { background-position: -1000px -600px; }  /* 5帧 × 200px = -1000px */
}
```

### 5. 待机动画（需要补充）

位置：Y = -800px 处

```css
#pet.idle {
  animation: idle 2s steps(8) infinite;
}

@keyframes idle {
  0% { background-position: 0px -800px; }
  100% { background-position: -1600px -800px; }  /* 8帧 × 200px = -1600px */
}
```

## 动画帧坐标计算器

```
// 起始 X 坐标: 0
// 结束 X 坐标: -(帧数 × 200)
// Y 坐标: -(动画索引 × 200)
// 
// 动画索引: 
//   0: 行走
//   1: 喝水
//   2: 专注
//   3: 吃文件
//   4: 待机
```

## 制作步骤（以 Photoshop 为例）

### 步骤 1：准备画布

1. 打开 Photoshop
2. 新建文件：
   - 宽度: 1600px（8帧 × 200px）
   - 高度: 1000px（5套动画 × 200px）
   - 分辨率: 72 PPI
   - 颜色模式: RGB
   - 背景: 透明

### 步骤 2：绘制第一套动画（行走）

1. 在顶部的 200×200px 区域绘制第 1 帧
2. 向右移动 200px，绘制第 2 帧
3. 继续向右，绘制第 3、4 帧
4. 建议动作：左右脚交替、尾巴摆动

### 步骤 3：绘制第二套动画（喝水）

1. 向下移动 200px，在新区域绘制
2. 帧序列建议：
   - 帧 1: 拿起杯子
   - 帧 2: 杯子靠近嘴
   - 帧 3: 喝水动作
   - 帧 4: 放下杯子

### 步骤 4：绘制第三套动画（专注敲键盘）

1. 继续向下 200px
2. 帧序列建议：
   - 帧 1: 手在键盘上方
   - 帧 2: 按下按键
   - 帧 3: 抬起手
   - 帧 4-6: 重复敲击动作（可加不同按键）

### 步骤 5：绘制第四套动画（吃文件）

1. 继续向下 200px
2. 帧序列建议：
   - 帧 1: 张嘴
   - 帧 2: 文件靠近嘴
   - 帧 3: 咬住文件
   - 帧 4: 咀嚼
   - 帧 5: 吞咽/满足表情

### 步骤 6：绘制第五套动画（待机）

1. 继续向下 200px
2. 帧序列建议（循环播放）：
   - 帧 1-2: 正常站立
   - 帧 3-4: 眨眼
   - 帧 5-6: 左右看
   - 帧 7-8: 打哈欠或伸懒腰

### 步骤 7：导出 WebP

1. 选择 `文件 > 导出 > 导出为`
2. 格式选择 `WebP`
3. 勾选 `透明度`
4. 质量建议: 80-90%
5. 保存为 `spritesheet.webp`
6. 替换 `desktop-pet/assets/spritesheet.webp`

## GIMP 替代方案（免费）

如果不想用 Photoshop，可以使用 GIMP：

1. 下载 GIMP（免费）: https://www.gimp.org/
2. 新建图像：1600×1000px，透明背景
3. 使用 `视图 > 显示网格` 和 `图像 > 配置网格` 设置 200×200px 网格
4. 逐帧绘制
5. 导出时选择 `文件 > 导出为`，选择 WebP 格式

## 关键位置说明（pet.html）

当前宠物嘴巴位置大约在：
- 距离左边: 70px
- 距离顶部: 100px
- 大小: 60px × 60px

```css
#mouth-drop {
  position: absolute;
  width: 60px;
  height: 60px;
  top: 100px;
  left: 70px;
  border-radius: 50%;
}
```

**建议**：在设计吃文件动画时，确保嘴巴位置与拖拽区域对齐。

## 调试技巧

1. **查看当前帧**: 在浏览器 DevTools 中检查 `#pet` 元素的 `background-position`
2. **慢速播放**: 将 `animation-duration` 从 `0.8s` 改为 `5s`，观察每帧
3. **显示边框**: 临时给 `#pet` 添加 `border: 1px solid red` 查看边界
4. **单帧测试**: 手动设置 `background-position: -400px -200px` 查看特定帧

## 设计建议

1. **保持一致性**：每帧角色位置尽量保持一致，避免抖动
2. **循环流畅**：最后一帧应自然过渡到第一帧
3. **表情丰富**：小星星可以有不同的表情变化（眨眼、微笑等）
4. **颜色协调**：保持与原有美术风格一致
5. **文件大小**：控制在 2MB 以内，保证加载速度

## 常见问题

**Q: 动画播放不流畅？**
A: 检查帧之间的差异是否过大，建议相邻帧变化幅度小一些。

**Q: 动画位置偏移？**
A: 确保每帧角色的基准点（如脚底）在同一水平线上。

**Q: 背景不透明？**
A: 导出 WebP 时务必勾选透明通道，或在 CSS 中设置 `background: transparent`。

**Q: 动画速度不合适？**
A: 调整 CSS 中的 `animation-duration` 值，单位为秒。

## 动画状态机建议

```
[idle] --有交互--> [walk]
[walk] --30分钟到--> [drink] --5秒后--> [idle]
[idle] --拖拽文件到嘴--> [eat] --完成后--> [idle]
[focus.html 独立窗口] --> [typing] 循环
```

如需添加更多动画状态，按照这个模式扩展 CSS 和 JavaScript 即可。