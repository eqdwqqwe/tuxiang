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
    api_key = "sk-k8H2334c64655f76c985327626e94aff66ac02a11f9m1iRg"  # 替换为你的实际API密钥
    api_url = "https://api.gptsapi.net/v1/chat/completions"  # 替换为实际API端点
    
    # 构建提示词
    prompt = """
    用户上传了一张UI图像，图像中事先做好了标注，标注内容在各种框的左上角有一个数字标签。
    你需要准确地根据数字标签对对应框中的UI内容做理解和识别，并进行报告。
    此外，还可能有一些未被框住和打上数字标签的UI组件，你需要在最后进行汇报，汇报时包含最近的标签与位置信息。
    
    以下是图像中已识别的标签内容：
    """
    
    # 添加标签信息
    for tag_id, tag_info in tags_data.items():
        prompt += f"标签 {tag_id}: 类型={tag_info['type']}, 位置={tag_info['bbox']}, 内容='{tag_info['content']}'\n"
    
    prompt += """
    你的输出应该类似：
    1. 标签0: 这是一个...
    2. 标签1: 这是...
    ...
    [如果发现未标记的UI元素]
    补充1: 位于标签X的[位置描述]，这是一个...
    """
    
    # 构建API请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "claude-3-7-sonnet-20250219",  # 替换为实际模型名称
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
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        # 打印返回内容，便于调试
        print("API返回内容：", response.text)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        # 如果有response对象，打印其内容
        error_msg = f"API调用出错: {str(e)}"
        if 'response' in locals():
            error_msg += f"\nAPI返回内容: {response.text}"
        return error_msg

def main():
    parser = argparse.ArgumentParser(description='解释UI标签')
    parser.add_argument('--folder', type=str, required=True, help='输入文件夹路径，包含SOM处理后的文件')
    parser.add_argument('--output', type=str, default='', help='输出结果的文件路径')
    args = parser.parse_args()
    
    folder_path = args.folder
    output_path = args.output
    
    # 构建文件路径
    folder_name = os.path.basename(folder_path)
    tags_file = os.path.join(folder_path, "tags_order_sorted.txt")
    image_file = os.path.join(folder_path, f"{folder_name}_revised.jpg")
    
    # 检查文件是否存在
    if not os.path.exists(tags_file):
        print(f"错误：标签文件不存在: {tags_file}")
        return
    
    if not os.path.exists(image_file):
        print(f"错误：图像文件不存在: {image_file}")
        return
    
    # 读取标签数据
    tags_data = read_tags_order_sorted(tags_file)
    
    # 编码图像
    image_base64 = encode_image(image_file)
    
    # 调用LLM API
    result = call_llm_api(image_base64, tags_data)
    
    # 输出结果
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