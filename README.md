# UI标签解释器

这个Python脚本用于解释SOM处理后的UI图像标签数据。它读取SOM处理的文本和图像文件，通过大型语言模型API来分析和解释UI元素。

## 功能

- 读取SOM处理后的`tags_order_sorted.txt`文件
- 处理带有数字标签的UI图像
- 调用大型语言模型API解释每个标签对应的UI元素
- 输出标签的详细解释
- 识别图像中未标记的UI组件

## 安装

1. 确保已安装Python 3.6或更高版本
2. 安装所需依赖:

```bash
pip install requests pillow
```

## 使用方法

通过命令行运行脚本，指定包含SOM处理后文件的文件夹:

```bash
python ui_label_interpreter.py --folder /path/to/folder --output /path/to/output.txt
```

参数说明:
- `--folder`: 必需，包含SOM处理后文件的文件夹路径
- `--output`: 可选，输出结果的文件路径；如不指定，结果将输出到控制台

## 文件要求

文件夹中应包含以下文件:
- `tags_order_sorted.txt`: SOM处理后的标签数据
- `[folder_name]_revised.jpg`: SOM处理后的标注图像

## API配置

在使用之前，请在脚本中配置你的API密钥和终端点:

```python
api_key = "YOUR_API_KEY"  # 替换为你的实际API密钥  
api_url = "YOUR_API_ENDPOINT"  # 替换为实际API端点
model = "YOUR_MODEL_NAME"  # 替换为你要使用的模型名称
```

## 输出示例

```
分析结果:
==================================================
1. 标签0: 这是一个显示时间的状态栏图标，显示"16:25"。
2. 标签1: 这是一个用户头像或个人资料图标。
...
补充1: 位于标签7的下方，这是一个可滚动的内容区域。
==================================================
```

## 注意事项

- 需要有可用的大型语言模型API访问权限
- 图像必须是SOM处理后的带有标签的图像
- 标签必须已经在图像中标记 