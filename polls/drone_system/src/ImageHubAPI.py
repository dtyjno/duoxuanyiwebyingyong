import requests
from datetime import timedelta
import base64
import mimetypes
import json

class ImageHubUploader:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.headers = {
            "X-API-Key": api_key,
            "Accept": "application/json"
        }

    def _send_request(self, files=None, data=None):
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
            
            # 无论状态码如何先尝试解析JSON
            try:
                result = response.json()
                if response.status_code == 200:
                    return result
                else:
                    return {"error": result}
            except json.JSONDecodeError:
                return {"error": response.text}

        except requests.exceptions.RequestException as e:
            error_info = {"exception": str(e)}
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_info.update({"response": e.response.json()})
                except:
                    error_info.update({"response": e.response.text})
            return {"error": error_info}

    def upload_file(self, file_path: str, **kwargs):
        """上传文件并返回解析后的结果"""
        mime_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, 'rb') as f:
            files = {'source': (file_path, f, mime_type)}
            data = {k: v for k, v in kwargs.items() if v is not None}
            
            response = self._send_request(files=files, data=data)
            
            # if 'error' in response:
            #     print(f"上传失败: {response['error']}")
            #     return None
            
            # 提取关键信息
            result = {
                "status": response.get('status_txt'),
                "url": response.get('image', {}).get('url'),
                "url_short": response.get('image', {}).get('url_short'),
                "delete_url": response.get('image', {}).get('delete_url'),
                "raw": response
            }
            
            print(f"上传成功！删除链接: {result['delete_url']}")
            return result
        
    # 方式2：通过URL上传
    def upload_from_url(self, file_url: str, **kwargs):
        data = {'source': file_url}
        data.update(kwargs)
        response = self._send_request(data=data)
        if 'error' not in response:
            return response
        else:
            print("上传失败，未能获取有效响应")
            return None

    # 方式3：上传Base64数据
    def upload_base64(self, base64_data: str, file_name: str, **kwargs):
        data = {
            'source': f"data:{mimetypes.guess_type(file_name)[0]};base64,{base64_data}",
            'title': file_name
        }
        data.update(kwargs)
        response = self._send_request(data=data)
        if 'error' not in response:
            return response
        else:
            print("上传失败，未能获取有效响应")
            return None

# 使用示例
if __name__ == "__main__":
    # 初始化配置
    UPLOAD_API = "https://www.imagehub.cc/api/1/upload"
    API_KEY = "chv_ctza_a7f99e53587ab2b6bf6f63255e57bf09965d9b82ac42dda888a90c1ccfcaa10e898122f9439a46e3d1c4f4d904f9a061f19ded67d36eb869bc1cf6a3c02d46bb"
    uploader = ImageHubUploader(UPLOAD_API, API_KEY)

    # 示例1：上传本地文件
    result = uploader.upload_file(
        "photo.jpg",
        title="假期照片",
        description="2024年夏季旅行拍摄",
        tags="旅行,自然",
        album_id="12345",
        expiration="P3D",  # 3天后过期
        nsfw=0,
        format="json"
    )
    print("上传结果:", result)

    # 示例2：通过URL上传
    url_result = uploader.upload_from_url(
        "https://example.com/remote-image.jpg",
        category_id="2",
        width=800,
        use_file_date=1
    )
    print("URL上传结果:", url_result)

    # 示例3：上传Base64数据
    with open("document.pdf", "rb") as f:
        base64_str = base64.b64encode(f.read()).decode()
    
    base64_result = uploader.upload_base64(
        base64_str,
        "document.pdf",
        description="重要合同文件",
        tags="文档,合同",
        expiration="PT1H"  # 1小时后过期
    )
    print("Base64上传结果:", base64_result)