## SQL2Excel 工具

一款基于 Python 的 SQL 查询结果导出为 Excel 的小工具，操作简单，界面简洁。

目前，只实现了以 MySQL 数据库作为数据源的导出，可继续扩展。

### AI 提示词

此工具使用 AI 工具辅助完成，提示词如下：

```text
你是一名 python 专家，擅长 GUI 应用开发，并且能设计出优美好看的界面，请使用 pyside6 开发下面内容。


## 需求

我想开发一个根据输入的 SQL 语句，导出 Excel 文件的桌面应用：

- 界面使用左右布局，左右大小比例为 1:3;
- 左边区域分为上下两部分，上部分有两个按钮，第一个是[新增数据源]按钮，用于添加数据源信息；第二个是[新增脚本]按钮，用于添加导出数据的字段信息和对应SQL信息；下半部分有一个 tabs标签页，有两个tab标签分别是：数据源和脚本；当点击数据源标签时，可以显示添加的数据源名称列表，当点击脚本标签时，可以显示添加的脚本名称列表；
- 在左边区域点击[新增数据源] 按钮时，右边区域需要显示数据源名称、数据源类型、host、port 输入框，并且右下方有一个保存按钮；
- 在左边区域点击[新增脚本] 按钮时，右边区域需要显示脚本名称、字段名称、SQL脚本输入框，并且右下方有一个[保存]按钮；
- 在左边区域数据源tab标签页内容中，点击对应的数据源名称，在右边区域显示对应的详情，并且在右下方有[保存]按钮和[删除]按钮；
- 在左边区域脚本tab标签页内容中，点击对应的脚本名称，在右边区域显示对应详情，并且在右下方有[保存]按钮、[执行]按钮和[删除]按钮，点击[执行]按钮可以进行数据导出，并以 Excel 文件形式输出，在执行导出时有进度条显示；
- 数据源与脚本信息以 json 形式保存到文件中；
- 点击对应的[保存]按钮可以保存数据，点击对应的[删除]按钮可以删除数据

## 参考资料

请参考下面5个资料：

### [参考资料 1] PySide6 简介

- 粘贴 https://blog.alexsun.top/posts/python/packages/pyside6/chapter01/ 里的内容。

### [参考资料 2] PySide6 快速入门

- 粘贴 https://blog.alexsun.top/posts/python/packages/pyside6/chapter02/ 里的内容。

### [参考资料 3] PySide6 控件

- 粘贴 https://blog.alexsun.top/posts/python/packages/pyside6/chapter04/ 里的内容。

### [参考资料 4] PySide6 信号与槽

- 粘贴 https://www.perfcode.com/python/pyside6/signals-and-slots 里的内容。

### [参考资料 5] PySide6 样式和动画

- 粘贴 https://blog.alexsun.top/posts/python/packages/pyside6/chapter07/ 里的内容。


## 要求

- 代码需要符合 Python 开发规范，参数、方法等命名必须清晰明了；
- 界面设计符合用户使用习惯，界面设计参考 github desktop 的风格和样式；
- 将代码进行工程化，不要在一个文件里面；

```

### 效果图

**添加数据源**

![添加数据源](./resources/imgs/add-datasource.png)

**查看数据源**

![查看数据源](./resources/imgs/datasource.png)

**添加SQL脚本**

![添加SQL脚本](./resources/imgs/add-script.png)

**查看SQL脚本**

![查看SQL脚本](./resources/imgs/script.png)





