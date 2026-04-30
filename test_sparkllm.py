"""使用_SparkLLMClient正确方式"""
from sparkai.v2.llm.llm import _SparkLLMClient

# 创建客户端
client = _SparkLLMClient(
    app_id='b3105b92',
    api_key='09ed8f5ee8ab99d26e36841fc8872606',
    api_secret='ZTAzMjMzMmYxNTRhZjA3NGYxYWU1ZTg3',
    api_url='wss://spark-api.xf-yun.com/v3.5/chat',
    spark_domain='x2',
)

# 发送消息
try:
    response = client.generate([{"role": "user", "content": "你好"}])
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()