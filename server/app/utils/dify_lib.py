import os

import requests
import time
from typing import Dict, List, Optional


DIFY_URL = os.getenv("DIFY_URL")
DIFY_API_KEY = os.getenv("DIFY_LIBRARY_API_KEY")

class DifyKnowledgeBaseClient:
    def __init__(self, api_key: str = DIFY_API_KEY, base_url: str = DIFY_URL):
        """
        初始化Dify客户端

        Args:
            api_key: Dify API密钥
            base_url: Dify API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {os.getenv("DIFY_LIBRARY_API_KEY")}',
            'Content-Type': 'application/json'
        }

    def create_by_text_to_document(self, dataset_id: str, name: str = None, text: str = None) -> Dict:
        """
        使用text文档
        """
        url = f"{self.base_url}/v1/datasets/{dataset_id}/document/create-by-text"
        print(url)
        payload = {
                  "name": name,
                  "text": text,
                  "indexing_technique": "high_quality",
                  "process_rule": {
                    "mode": "automatic"
              }
        }
        print(self.headers)
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"创建文档失败: {response.status_code}, {response.text}")

        return response.json()



    def create_document(self, dataset_id: str, text_content: str, document_name: str = None) -> Dict:
        """
        创建文档并插入到知识库

        Args:
            dataset_id: 知识库ID
            text_content: 要插入的文本内容
            document_name: 文档名称

        Returns:
            包含文档ID和其他信息的响应
        """
        if not document_name:
            document_name = f"document_{int(time.time())}"

        url = f"{self.base_url}/ai/datasets/{dataset_id}/document/create-by-text"

        payload = {
                  "name": "bbb",
                  "text": "bbb",
                  "indexing_technique": "high_quality",
                  "process_rule": {
                    "mode": "automatic"
              }
        }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"创建文档失败: {response.status_code}, {response.text}")

        return response.json()

    def get_document_status(self, dataset_id: str, document_id: str) -> Dict:
        """
        获取文档的嵌入状态

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID

        Returns:
            包含文档状态的信息
        """
        url = f"{self.base_url}/datasets/{dataset_id}/documents/{document_id}"

        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"获取文档状态失败: {response.status_code}, {response.text}")

        return response.json()

    def wait_for_embedding_complete(self, dataset_id: str, document_id: str, timeout: int = 300) -> Dict:
        """
        等待文档嵌入完成

        Args:
            dataset_id: 知识库ID
            document_id: 文档ID
            timeout: 超时时间（秒）

        Returns:
            最终的文档状态信息
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status_info = self.get_document_status(dataset_id, document_id)

            # 检查嵌入状态
            current_status = status_info.get('data', {}).get('status', 'unknown')

            if current_status == 'completed':
                return status_info
            elif current_status in ['error', 'archived']:
                raise Exception(f"文档处理失败: {current_status}, 详情: {status_info}")

            print(f"等待嵌入完成... 当前状态: {current_status}")
            time.sleep(5)  # 等待5秒后重试

        raise Exception("等待文档嵌入超时")

    def insert_text_to_knowledge_base(self, dataset_id: str, text_content: str,
                                      document_name: str = None, wait_for_completion: bool = True) -> Dict:
        """
        插入文本到知识库并获取最终状态

        Args:
            dataset_id: 知识库ID
            text_content: 要插入的文本内容
            document_name: 文档名称
            wait_for_completion: 是否等待嵌入完成

        Returns:
            包含文档ID和最终状态的信息
        """
        # 创建文档
        create_result = self.create_document(dataset_id, text_content, document_name)

        document_id = create_result.get('data', {}).get('id')
        if not document_id:
            raise Exception(f"无法从创建响应中获取文档ID: {create_result}")

        result = {
            'document_id': document_id,
            'creation_result': create_result
        }

        if wait_for_completion:
            # 等待嵌入完成并获取最终状态
            final_status = self.wait_for_embedding_complete(dataset_id, document_id)
            result['final_status'] = final_status
            result['embedding_completed'] = True
        else:
            # 立即返回状态，不等待嵌入完成
            current_status = self.get_document_status(dataset_id, document_id)
            result['current_status'] = current_status
            result['embedding_completed'] = False

        return result


# 便捷函数
def insert_text_to_dify_knowledge_base(api_key: str, dataset_id: str, text_content: str,
                                       document_name: str = None, base_url: str = DIFY_URL) -> Dict:
    """
    便捷函数：插入文本到Dify知识库并等待嵌入完成

    Args:
        api_key: Dify API密钥
        dataset_id: 知识库ID
        text_content: 要插入的文本内容
        document_name: 文档名称
        base_url: Dify API基础URL

    Returns:
        包含文档ID和最终状态的信息
    """
    client = DifyKnowledgeBaseClient(api_key, base_url)
    return client.insert_text_to_knowledge_base(dataset_id, text_content, document_name)


def check_embedding_status(api_key: str, dataset_id: str, document_id: str,
                           base_url: str = DIFY_URL) -> Dict:
    """
    便捷函数：检查文档嵌入状态

    Args:
        api_key: Dify API密钥
        dataset_id: 知识库ID
        document_id: 文档ID
        base_url: Dify API基础URL

    Returns:
        包含文档状态的信息
    """
    client = DifyKnowledgeBaseClient(api_key, base_url)
    return client.get_document_status(dataset_id, document_id)
