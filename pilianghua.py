import requests
import json
import os
import base64
from PIL import Image
import io
import argparse

def read_tags_order_sorted(file_path):
    """读取SOM处理后的tags_order_sorted.txt文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.read().strip().split('\n')
    
    tags = {}
    for line in lines:
        if not line.strip():
            continue
        
        parts = line.split(': ', 1)
        if len(parts) != 2:
            continue
            
        tag_id = parts[0].split(' ')[1]
        tag_data = eval(parts[1])  # 解析字典字符串
        tags[tag_id] = tag_data
    
    return tags

def encode_image(image_path):
    """将图像编码为base64格式"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_llm_api(image_base64, tags_data):
    """
    调用大型语言模型API分析UI图像和标签
    注意：这是一个示例函数，需要替换为实际的API调用代码
    """
    # 这里需要替换为实际API调用代码和API密钥
    api_key = "sk-k8H2334c64655f76c985327626e94aff66ac02a11f9m1iRg"  
    api_url = "https://api.gptsapi.net/v1/chat/completions"  
    
    # 构建提示词
    prompt = """

    作为UI分析助手，请对上传的UI界面图像进行详细分析。图像中包含了已标注的UI元素，每个标注都有一个数字标签位于框的左上角。

    分析要求：
    1. 详细解释每个已标注区域的UI元素，包括元素的外形、位置、大小、颜色、文字内容等。
    2. 说明每个UI元素的功能和用途，判断UI元素是否可交互
    3. 分析UI元素之间的关系和布局逻辑
    4. 识别未标注的重要UI元素

    标签信息格式说明：
    - 类型(type)：表示UI元素的类型（如按钮、文本框等）
    - 位置(bbox)：表示UI元素在界面中的坐标位置
    - 内容(content)：表示UI元素包含的文本或信息

    已识别的标签内容如下：
    """
    
    # 添加标签信息
    for tag_id, tag_info in tags_data.items():
        prompt += f"标签 {tag_id}: 类型={tag_info['type']}, 位置={tag_info['bbox']}, 内容='{tag_info['content']}'\n"
    
    prompt += """
    你需要结合标签信息和图像识别结果，判断标签信息中的识别是否准确，如果存在错误，请进行修正。
    此外，你需要判断图像中是否存在未标注及标注错误的UI元素，如果有，请进行补充说明。

    你需要确保对所有的标签都有详细的分析和描述，UI元素功能的分析结果需要尽可能详细，如果可能，说明UI元素的交互方式和当前状态。
    
    对于不能完全确定功能的UI元素，请说明所有可能的功能。
    请不要遗漏任何UI元素，不要遗漏任何可能的功能。
    
    请按以下格式输出分析结果：
    

    1. 已标注UI元素分析：
       标签 [编号]: [元素类型] [详细说明该UI元素的描述]
         功能：[详细说明该UI元素的功能与可能的功能]
    
    例如：
    标签 1: 按钮 这是一个按钮，位于界面左上角，按钮上显示"返回"字样。
    功能：点击按钮可以返回上一级界面。
    
    注意：编号不能被组合，请不要出现类似"1-2"的编号。

    2. 未标注UI元素补充：
       补充元素1：[位置描述]
         类型：[推测的元素类型]
         功能：[推测的功能]
         参考位置：[相对于最近标签的位置]
   
    除了按格式输出的分析结果不要输出其他内容。
    请确保分析准确、专业且易于理解。
    """
    
    # 构建API请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o",  # 替换为实际模型名称
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的UI分析助手，擅长理解和解释UI界面的各个元素。"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 10000
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API调用出错: {str(e)}"

def find_all_data_folders(root_dir):
    """
    递归查找所有包含tags_order_sorted.txt和*_revised.jpg的子文件夹
    返回这些文件夹的绝对路径列表
    """
    data_folders = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'tags_order_sorted.txt' in filenames:
            # 查找是否有*_revised.jpg
            revised_jpgs = [f for f in filenames if f.endswith('_revised.jpg')]
            if revised_jpgs:
                data_folders.append(dirpath)
    return data_folders

def main():
    parser = argparse.ArgumentParser(description='解释UI标签')
    parser.add_argument('--folder', type=str, help='输入文件夹路径，包含SOM处理后的文件')
    parser.add_argument('--output', type=str, default='', help='输出结果的文件路径')
    parser.add_argument('--batch_folder', type=str, help='批量处理的总目录，递归查找所有数据文件夹')
    args = parser.parse_args()
    
    if args.batch_folder:
        # 批量模式
        batch_root = args.batch_folder
        data_folders = find_all_data_folders(batch_root)
        if not data_folders:
            print(f"未找到任何有效数据文件夹于: {batch_root}")
            return
        print(f"共找到{len(data_folders)}个数据文件夹，开始批量处理...")
        for folder_path in data_folders:
            folder_name = os.path.basename(folder_path)
            tags_file = os.path.join(folder_path, "tags_order_sorted.txt")
            # 查找*_revised.jpg
            revised_jpgs = [f for f in os.listdir(folder_path) if f.endswith('_revised.jpg')]
            if not revised_jpgs:
                print(f"跳过: {folder_path}，未找到*_revised.jpg")
                continue
            image_file = os.path.join(folder_path, revised_jpgs[0])
            # 读取标签数据
            tags_data = read_tags_order_sorted(tags_file)
            # 编码图像
            image_base64 = encode_image(image_file)
            # 调用LLM API
            result = call_llm_api(image_base64, tags_data)
            # 输出到该文件夹下
            output_path = os.path.join(folder_path, 'ui_analysis_result.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"已处理: {folder_path}，结果保存至: {output_path}")
        print("批量处理完成！")
        return
    # 单文件夹模式（保留原有逻辑）
    folder_path = args.folder
    output_path = args.output
    if not folder_path:
        print("请指定--folder 或 --batch_folder 参数")
        return
    folder_name = os.path.basename(folder_path)
    tags_file = os.path.join(folder_path, "tags_order_sorted.txt")
    image_file = os.path.join(folder_path, f"{folder_name}_revised.jpg")
    if not os.path.exists(tags_file):
        print(f"错误：标签文件不存在: {tags_file}")
        return
    if not os.path.exists(image_file):
        print(f"错误：图像文件不存在: {image_file}")
        return
    tags_data = read_tags_order_sorted(tags_file)
    image_base64 = encode_image(image_file)
    result = call_llm_api(image_base64, tags_data)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"结果已保存至: {output_path}")
    else:
        print("\n分析结果:")
        print("="*50)
        print(result)
        print("="*50)

if __name__ == "__main__":
    main() 