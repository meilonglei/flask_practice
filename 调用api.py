import requests

# 服务器的实际 IP 地址
server_ip = '192.168.1.105'

# API 地址
url = f"http://{server_ip}:5000/api/detect"
api_key = "your-secret-api-key-12345"
# 要上传的图片
file_path = r"D:\Desktop\ultralytics-main\ultralytics\assets\bus.jpg"  # 替换为你的图片路径

# 发送 POST 请求
with open(file_path, 'rb') as f:
    response = requests.post(
        url,
        files={'file': f},
        headers={
            'Authorization': f'Bearer {api_key}'
        }
    )

# 打印结果
if response.status_code == 200:
    result = response.json()
    print("✅ 检测成功！")
    print("检测到的物体：")
    for obj in result['detections']:
        print(f"  {obj['class']} ({obj['confidence']:.2f})")

    print(server_ip)
    print(result['image_url'])

    print(f"结果图片: http://{server_ip}:5000{result['image_url']}")
    
else:
    print(f"❌ 错误: {response.status_code}, {response.text}")