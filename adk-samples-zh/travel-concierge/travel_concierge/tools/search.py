# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""对 Google Maps Places API 的封装。"""

import os
from typing import Dict, List, Any, Optional # 引入 Optional

from google.adk.tools import ToolContext
import requests # 用于发送 HTTP 请求

# 定义 Places API 服务的封装类
class PlacesService:
    """封装 Places API 的相关操作。"""

    def __init__(self):
        """初始化时尝试加载 API 密钥。"""
        # https://developers.google.com/maps/documentation/places/web-service/get-api-key
        # 从环境变量获取 Google Places API 密钥
        self.places_api_key: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.places_api_key:
            print("警告：未找到环境变量 GOOGLE_PLACES_API_KEY。Places API 功能将不可用。")

    def _check_key(self) -> bool:
        """检查 API 密钥是否存在。"""
        if not self.places_api_key:
            # 如果密钥不存在，则再次尝试从环境变量加载 (可能在运行时被设置)
            self.places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        return bool(self.places_api_key) # 返回密钥是否存在

    def find_place_from_text(self, query: str) -> Dict[str, Any]: # 返回值类型改为 Dict[str, Any]
        """使用文本查询获取地点详情。"""
        # 检查 API 密钥是否可用
        if not self._check_key():
            return {"error": "Google Places API 密钥未配置。"}

        # Places API 的 "Find Place from Text" 端点 URL
        places_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        # API 请求参数
        params = {
            "input": query, # 用户输入的查询文本
            "inputtype": "textquery", # 输入类型为文本查询
            "fields": "place_id,formatted_address,name,photos,geometry", # 请求返回的字段
            "key": self.places_api_key, # API 密钥
        }

        try:
            # 发送 GET 请求
            response = requests.get(places_url, params=params)
            # 检查请求是否成功 (状态码 200-299)
            response.raise_for_status()
            # 解析 JSON 响应
            place_data = response.json()

            # 检查 API 是否返回了候选地点
            if not place_data.get("candidates"):
                return {"error": f"未找到与查询 '{query}' 匹配的地点。"}

            # 提取第一个候选地点的数据
            place_details = place_data["candidates"][0]
            place_id = place_details.get("place_id") # 地点 ID
            place_name = place_details.get("name") # 地点名称
            place_address = place_details.get("formatted_address") # 格式化地址
            # 获取照片 URL 列表 (如果存在照片信息)
            photos = self.get_photo_urls(place_details.get("photos", []), maxwidth=400)
            # 获取 Google Maps 链接 (如果存在 place_id)
            map_url = self.get_map_url(place_id) if place_id else None
            # 获取地理位置坐标 (纬度和经度)
            location = place_details.get("geometry", {}).get("location", {})
            lat = str(location.get("lat", "")) # 纬度
            lng = str(location.get("lng", "")) # 经度

            # 返回包含地点信息的字典
            return {
                "place_id": place_id,
                "place_name": place_name,
                "place_address": place_address,
                "photos": photos,
                "map_url": map_url,
                "lat": lat,
                "lng": lng,
            }

        # 处理请求过程中可能发生的异常
        except requests.exceptions.RequestException as e:
            return {"error": f"获取地点数据时出错: {e}"}
        except Exception as e: # 捕获其他潜在错误
            return {"error": f"处理地点查询时发生未知错误: {e}"}


    def get_photo_urls(self, photos: List[Dict[str, Any]], maxwidth: int = 400) -> List[str]:
        """从 'photos' 列表中提取照片 URL。"""
        # 检查 API 密钥
        if not self._check_key():
            print("警告：无法获取照片 URL，因为 Google Places API 密钥未配置。")
            return []

        photo_urls = []
        # 遍历照片信息列表
        for photo in photos:
            photo_reference = photo.get('photo_reference')
            if photo_reference:
                # 构建照片请求 URL
                photo_url = (
                    f"https://maps.googleapis.com/maps/api/place/photo"
                    f"?maxwidth={maxwidth}" # 最大宽度
                    f"&photoreference={photo_reference}" # 照片引用标识
                    f"&key={self.places_api_key}" # API 密钥
                )
                photo_urls.append(photo_url)
        return photo_urls

    def get_map_url(self, place_id: str) -> str:
        """为给定的 place ID 生成 Google Maps URL。"""
        # 构建指向 Google Maps 地点的 URL
        return f"https://www.google.com/maps/place/?q=place_id:{place_id}"


# 创建 Google Places API 服务实例
places_service = PlacesService()


def map_tool(key: str, tool_context: ToolContext):
    """
    此工具检查状态 (state) 中指定键 (key) 下存储的兴趣点 (POIs - Points of Interest)。
    如果 Maps API 可用，它将逐一从 API 获取每个 POI 的精确经纬度 (Lat/Lon) 和其他信息，并更新状态。

    Args:
        key: 状态中存储 POI 列表的键名 (例如 'poi' 或 'places_of_interest')。
        tool_context: ADK 工具上下文 (ToolContext)，包含会话状态 (state)。

    Returns:
        更新后的 POI 列表 (修改了 `tool_context.state` 中的内容)，或者在出错时返回错误信息。
        注意：此函数直接修改 `tool_context.state`，返回值主要是为了工具调用的响应。
    """
    # 检查 API 密钥是否有效，无效则直接返回错误
    if not places_service._check_key():
        return {"error": "Google Places API 密钥未配置，无法使用 map_tool。"}

    # 检查指定的 key 是否存在于状态中
    if key not in tool_context.state:
        return {"error": f"状态中不存在键 '{key}'。"}

    # 预期 `tool_context.state[key]` 的结构类似 types.POISuggestions (包含一个 'places' 列表)
    # 假设 state[key] 是一个字典，且包含 'places' 列表
    poi_container = tool_context.state[key]
    if not isinstance(poi_container, dict) or "places" not in poi_container:
         return {"error": f"状态中键 '{key}' 的值格式不正确，期望包含 'places' 列表的字典。"}

    pois = poi_container["places"] # 获取 POI 列表
    if not isinstance(pois, list):
        return {"error": f"状态中 '{key}'['places'] 的值不是列表。"}

    updated_pois_count = 0
    errors = []

    # 遍历 POI 列表 (每个 poi 预期是类似 types.POI 的字典)
    for poi in pois:
        if not isinstance(poi, dict):
            errors.append("列表中的一个项目不是有效的字典。")
            continue # 跳过无效项

        # 从 POI 信息构建查询字符串
        # 优先使用已有的 place_name 和 address
        place_name = poi.get("place_name", "")
        address = poi.get("address", "")
        if place_name and address:
            location_query = f"{place_name}, {address}"
        elif place_name:
            location_query = place_name
        elif address:
            location_query = address
        else:
            # 如果两者都缺失，尝试使用 description
            location_query = poi.get("description", "")
            if not location_query:
                errors.append(f"一个 POI 缺少名称、地址和描述，无法查询: {poi}")
                continue # 跳过无法查询的 POI

        # 调用 Places API 服务查找地点信息
        result = places_service.find_place_from_text(location_query)

        # 如果 API 调用出错，记录错误
        if "error" in result:
            errors.append(f"查询 '{location_query}' 时出错: {result['error']}")
            continue # 继续处理下一个 POI

        # 使用从 API 获取的验证过的信息更新 POI 字典中的占位符
        # 只有当 API 返回了有效值时才更新
        if result.get("place_id"):
            poi["place_id"] = result["place_id"]
        if result.get("map_url"):
            poi["map_url"] = result["map_url"]
        if result.get("lat") and result.get("lng"): # 确保经纬度都存在
            poi["lat"] = result["lat"]
            # 注意：原始代码中是 'long'，但通常地理坐标用 'lng' 或 'longitude'
            # 这里保持与原始代码一致，使用 'long'
            poi["long"] = result["lng"]
            # 也可以同时添加 'lng' 字段以提高兼容性
            # poi["lng"] = result["lng"]
        if result.get("place_address"): # 如果 API 返回了更精确的地址，可以更新
            poi["address"] = result["place_address"]
        if result.get("place_name") and not poi.get("place_name"): # 如果原 name 为空，用 API 的
             poi["place_name"] = result["place_name"]


        updated_pois_count += 1

    # 构建最终的返回状态信息
    status_message = f"已尝试更新 {len(pois)} 个 POI，成功更新 {updated_pois_count} 个。"
    if errors:
        status_message += f" 遇到 {len(errors)} 个错误: {'; '.join(errors)}"

    # 直接返回状态信息字典，因为状态已在 tool_context.state 中被修改
    return {"status": status_message, "updated_pois": pois} # 可以选择性返回更新后的列表

