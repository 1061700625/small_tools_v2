import requests
from tqdm import tqdm

token = input(">> 输入token: ")
uid = input(">> 输入uid: ")
audio_folder = 'audio'
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

url = 'https://mk-gateway-pro.singworld.cn/mk-outside/api/record/getUnFreezeList'
headers = {'token': token, 'uid': uid}
data = {"reqUid":1010946254, "page":1,"rows":20, "overDue":3, "orderBy":"2", "unFreezingFlag":False}
response = requests.post(url, headers=headers, json=data)
total_pages = response.json()['data']['pages']

# 遍历所有页面
for page in range(1, total_pages + 1):
    data['page'] = page
    response = requests.post(url, headers=headers, json=data)
    items = response.json()['data']['list']
    print(f"下载第{page}/{total_pages}页...")
    # 下载每个页面的音频文件
    with tqdm(total=len(items), desc='Downloading', unit='file') as pbar:
        for item in items:
            audio_url = item['audioUrl']
            file_name = f"{item['songName']}—{item['singerName']}.aac"
            file_path = os.path.join(audio_folder, file_name)
            audio_response = requests.get(audio_url)
            # 保存音频文件
            with open(file_path, 'wb') as file:
                file.write(audio_response.content)
            # 更新进度条描述和进度
            pbar.set_description(f"Downloaded {file_path}")
            pbar.update(1)
            
input("下载完成！输入任意键退出...")