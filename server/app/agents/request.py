import aiohttp
from langchain_core.tools import tool
from pydantic import SecretStr, BaseModel, Field

import requests
class AddInputArgs(BaseModel):
    location: str = Field(description="地点, 例如 上海市, 北京市, 杭州, 邯郸, 长春")


@tool(
    description="根据城市地点, 获取目标地区的天气",
    args_schema=AddInputArgs,
    return_direct=False  # 改为False以获得更完整的响应处理
)
async def get_current_weather(location: str):
    """  使用天气工具, 获得数据后, 要告诉用户 数据来源心知天气"""
    try:
        url = f"https://api.seniverse.com/v3/weather/daily.json?key={location}&location={location}&days=3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                weather_data = await response.json()
                return {   "weather_data": weather_data["results"], "source": "数据来源于心知天气"}
    except Exception as e:
        print(f"Error fetching weather: {str(e)}")
        return {"error": f"Failed to fetch weather data: {str(e)}"}
