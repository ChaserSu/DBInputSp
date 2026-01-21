import requests
import sys
import os

def check_update(current_version, github_repo="ChaserSu/DBInputSp"):
    """
    检查GitHub仓库的最新版本
    :param current_version: 当前版本号（如 "0.0.19"）
    :param github_repo: GitHub仓库地址（格式：用户名/仓库名）
    :return: 更新信息字符串，或空字符串表示已是最新版本
    """
    update_info = ""
    try:
        # 调用 GitHub API 获取最新发布版本
        response = requests.get(
            f"https://api.github.com/repos/{github_repo}/releases/latest",
            timeout=3,
            headers={"User-Agent": "DBInputSp-Client"}
        )
        if response.status_code == 200:
            latest_data = response.json()
            latest_version = latest_data.get("tag_name", "").lstrip('v')  # 去除版本号前缀的 'v'
            
            # 版本号对比（简单数字对比，适用于 x.y.z 格式）
            def version_to_tuple(version_str):
                return tuple(map(int, version_str.split('.')))
            
            current_tuple = version_to_tuple(current_version)
            latest_tuple = version_to_tuple(latest_version)
            
            if latest_tuple > current_tuple:
                update_info = f"🎉 发现新版本！当前版本 v{current_version} → 最新版本 v{latest_version}\n"
                update_info += f"📥 下载地址：{latest_data.get('html_url', f'https://github.com/{github_repo}/releases')}\n"
                update_info += f"📝 更新日志：{latest_data.get('body', '请前往 GitHub 查看详细更新日志')[:200]}...\n"
                update_info += f"💡 提示：输入“~”回车可直接下载最新版本到当前目录\n"
            else:
                update_info = f"✅ 当前已是最新版本 v{current_version}！\n"
        else:
            update_info = f"⚠️  更新检查失败：无法获取最新版本信息\n"
    except requests.exceptions.RequestException as e:
        # 网络错误/超时，返回错误信息
        update_info = f"⚠️  更新检查失败：{str(e)}（忽略，继续运行）\n"
    
    return update_info

def download_latest_version(github_repo="ChaserSu/DBInputSp", save_dir="."):
    """
    下载GitHub仓库的最新版本发布资产
    :param github_repo: GitHub仓库地址（格式：用户名/仓库名）
    :param save_dir: 保存文件的目录，默认当前目录
    :return: 下载结果字符串
    """
    result = ""
    try:
        # 获取最新release信息
        response = requests.get(
            f"https://api.github.com/repos/{github_repo}/releases/latest",
            timeout=5,
            headers={"User-Agent": "DBInputSp-Client"}
        )
        
        if response.status_code == 200:
            latest_data = response.json()
            assets = latest_data.get("assets", [])
            
            if assets:
                # 选择第一个资产（通常是主要的安装包）
                asset = assets[0]
                download_url = asset.get("browser_download_url")
                file_name = asset.get("name")
                
                if download_url and file_name:
                    # 下载文件
                    result += f"📥 正在下载：{file_name}\n"
                    result += f"📡 下载地址：{download_url}\n"
                    
                    # 发送下载请求
                    download_response = requests.get(download_url, stream=True, timeout=30)
                    
                    if download_response.status_code == 200:
                        # 保存文件到指定目录
                        file_path = os.path.join(save_dir, file_name)
                        total_size = int(download_response.headers.get("content-length", 0))
                        downloaded_size = 0
                        
                        with open(file_path, "wb") as f:
                            for chunk in download_response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)
                                    # 显示下载进度
                                    if total_size > 0:
                                        progress = (downloaded_size / total_size) * 100
                                        print(f"📊 下载进度：{progress:.1f}% {downloaded_size}/{total_size} bytes", end="\r")
                        
                        print()  # 换行
                        result += f"✅ 下载完成！文件已保存到：{file_path}\n"
                    else:
                        result += f"❌ 下载失败：HTTP {download_response.status_code}\n"
                else:
                    result += "❌ 未找到可下载的文件\n"
            else:
                result += "❌ 未找到任何发布资产\n"
        else:
            result += f"❌ 无法获取最新发布信息：HTTP {response.status_code}\n"
    except requests.exceptions.RequestException as e:
        result += f"❌ 网络错误：{str(e)}\n"
    except Exception as e:
        result += f"❌ 下载失败：{str(e)}\n"
    
    return result

if __name__ == '__main__':
    # 示例用法
    current_version = "0.0.19"
    github_repo = "ChaserSu/DBInputSp"
    update_info = check_update(current_version, github_repo)
    print(update_info)
