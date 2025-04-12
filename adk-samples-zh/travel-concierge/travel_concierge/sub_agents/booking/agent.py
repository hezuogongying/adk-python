
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

"""travel-concierge Agent 的通用数据模式和类型。"""

from typing import Optional, Union # 导入类型提示

from google.genai import types # 导入 Gemini 类型
from pydantic import BaseModel, Field # 导入 Pydantic 用于数据验证和模式定义


# 用于控制生成 JSON 响应的便捷声明。
json_response_config = types.GenerateContentConfig(
    response_mime_type="application/json" # 要求模型生成 JSON 格式的响应
)


class Room(BaseModel):
    """一个可供选择的房间。"""
    is_available: bool = Field(
        description="该房型是否可供选择。"
    )
    price_in_usd: int = Field(description="所选房间的价格。")
    room_type: str = Field(
        description="房间类型，例如：带阳台双床房、海景大床房……等。"
    )


class RoomsSelection(BaseModel):
    """可供选择的房间列表。"""
    rooms: list[Room]


class Hotel(BaseModel):
    """搜索结果中的一家酒店。"""
    name: str = Field(description="酒店名称")
    address: str = Field(description="酒店的完整地址")
    check_in_time: str = Field(description="入住时间，HH:MM 格式，例如 16:00")
    check_out_time: str = Field(description="退房时间，HH:MM 格式，例如 15:30")
    thumbnail: str = Field(description="酒店 Logo 图片位置") # 通常是相对路径或 URL
    price: int = Field(description="每晚房费")


class HotelsSelection(BaseModel):
    """搜索结果中的酒店列表。"""
    hotels: list[Hotel]


class Seat(BaseModel):
    """搜索结果中的一个座位。"""
    is_available: bool = Field(
        description="该座位是否可供选择。"
    )
    price_in_usd: int = Field(description="所选座位的价格。")
    seat_number: str = Field(description="座位号，例如 22A, 34F... 等。")


class SeatsSelection(BaseModel):
    """搜索结果中的座位列表（通常是二维数组表示座位图）。"""
    seats: list[list[Seat]] # 二维列表，外层列表代表行，内层列表代表该行的座位


class AirportEvent(BaseModel):
    """一个机场事件（出发或到达）。"""
    city_name: str = Field(description="出发或到达城市的名称")
    airport_code: str = Field(description="出发或到达机场的 IATA 代码")
    timestamp: str = Field(description="ISO 8601 格式的出发或到达日期和时间")


class Flight(BaseModel):
    """一个航班搜索结果。"""
    flight_number: str = Field(
        description="航班的唯一标识符，如 BA123, AA31 等。"
    )
    departure: AirportEvent # 出发信息
    arrival: AirportEvent # 到达信息
    airlines: list[str] = Field(
        description="航空公司名称列表，例如：美国航空、阿联酋航空"
    )
    airline_logo: str = Field(description="航空公司 Logo 图片位置") # 通常是相对路径或 URL
    price_in_usd: int = Field(description="航班价格（美元）")
    number_of_stops: int = Field(description="飞行途中的经停次数")


class FlightsSelection(BaseModel):
    """搜索结果中的航班列表。"""
    flights: list[Flight]


class Destination(BaseModel):
    """一个目的地推荐。"""
    name: str = Field(description="目的地名称")
    country: str = Field(description="目的地所在国家名称")
    image: str = Field(description="经验证的目的地图片 URL")
    highlights: str = Field(description="突出关键特色的简短描述")
    rating: str = Field(description="数字评分（例如：4.5）")


class DesintationIdeas(BaseModel):
    """目的地推荐列表。"""
    places: list[Destination] # 修正：类名应为 DestinationIdeas


class POI(BaseModel):
    """Agent 建议的一个兴趣点 (Point Of Interest)。"""
    place_name: str = Field(description="景点的名称")
    address: str = Field(
        description="地址或足以进行地理编码以获取经纬度的信息"
    )
    lat: str = Field(
        description="地点纬度的数字表示（例如：20.6843）"
    )
    long: str = Field( # 修正：字段名通常是 longitude 或 lng
        description="地点经度的数字表示（例如：-88.5678）"
    )
    review_ratings: str = Field( # 修正：字段名建议为 rating
        description="评分的数字表示（例如 4.8、3.0、1.0 等）"
    )
    highlights: str = Field(description="突出关键特色的简短描述")
    image_url: str = Field(description="经验证的目的地图片 URL")
    map_url: Optional[str] = Field(description="经验证的 Google 地图 URL") # 可选
    place_id: Optional[str] = Field(description="Google 地图 place_id") # 可选


class POISuggestions(BaseModel):
    """兴趣点推荐列表。"""
    places: list[POI]


class AttractionEvent(BaseModel):
    """一个景点活动。"""
    event_type: str = Field(default="visit", description="事件类型，默认为参观")
    description: str = Field(
        description="活动或景点参观的标题或描述"
    )
    address: str = Field(description="景点的完整地址")
    start_time: str = Field(description="开始时间，HH:MM 格式，例如 16:00")
    end_time: str = Field(description="结束时间，HH:MM 格式，例如 16:00")
    booking_required: bool = Field(default=False, description="是否需要预订")
    price: Optional[str] = Field(description="某些事件可能需要费用") # 可选


class FlightEvent(BaseModel):
    """行程中的一个航班段。"""
    event_type: str = Field(default="flight", description="事件类型，默认为航班")
    description: str = Field(description="航班的标题或描述")
    booking_required: bool = Field(default=True, description="是否需要预订")
    departure_airport: str = Field(description="机场代码，例如 SEA")
    arrival_airport: str = Field(description="机场代码，例如 SAN")
    flight_number: str = Field(description="航班号，例如 UA5678")
    boarding_time: str = Field(description="登机时间，HH:MM 格式，例如 15:30")
    seat_number: str = Field(description="座位行号和位置，例如 32A")
    departure_time: str = Field(description="出发时间，HH:MM 格式，例如 16:00")
    arrival_time: str = Field(description="到达时间，HH:MM 格式，例如 20:00")
    price: Optional[str] = Field(description="总机票费用") # 可选
    booking_id: Optional[str] = Field(
        description="预订参考 ID，例如 LMN-012-STU"
    ) # 可选


class HotelEvent(BaseModel):
    """行程中的一个酒店预订。"""
    event_type: str = Field(default="hotel", description="事件类型，默认为酒店")
    description: str = Field(description="酒店的名称、标题或描述")
    address: str = Field(description="景点的完整地址") # 修正：应该是酒店的完整地址
    check_in_time: str = Field(description="入住时间，HH:MM 格式，例如 16:00")
    check_out_time: str = Field(description="退房时间，HH:MM 格式，例如 15:30")
    room_selection: str = Field(description="选择的房型")
    booking_required: bool = Field(default=True, description="是否需要预订")
    price: Optional[str] = Field(description="包含所有晚数的总酒店价格") # 可选
    booking_id: Optional[str] = Field(
        description="预订参考 ID，例如 ABCD12345678"
    ) # 可选


class ItineraryDay(BaseModel):
    """行程中单日的事件。"""
    day_number: int = Field(
        description="标识这是行程的第几天，例如 1, 2, 3... 等。"
    )
    date: str = Field(description="这一天的日期，YYYY-MM-DD 格式")
    events: list[Union[FlightEvent, HotelEvent, AttractionEvent]] = Field(
        default=[], description="当天的事件列表" # 使用 Union 来允许多种事件类型
    )


class Itinerary(BaseModel):
    """一个多日行程。"""
    trip_name: str = Field(
        description="描述行程的简单单行文字。例如 '圣地亚哥到西雅图逍遥游'"
    )
    start_date: str = Field(description="行程开始日期，YYYY-MM-DD 格式")
    end_date: str = Field(description="行程结束日期，YYYY-MM-DD 格式")
    origin: str = Field(description="行程起点，例如圣地亚哥")
    destination: str = (Field(description="行程目的地，例如西雅图"),) # 修正：这里多了一个逗号和括号
    days: list[ItineraryDay] = Field(
        default_factory=list, description="多日行程列表" # 默认为空列表
    )


class UserProfile(BaseModel):
    """一个示例用户个人资料。"""
    allergies: list[str] = Field(
        default=[], description="需要避免的食物过敏源列表"
    )
    diet_preference: list[str] = Field( # 修正：原始代码变量名可能是 food_preference
        default=[], description="饮食偏好，例如素食、纯素... 等。"
    )
    passport_nationality: str = Field(
        description="旅行者国籍，例如美国公民"
    )
    home_address: str = Field(description="旅行者的家庭住址") # 修正：原始代码可能是 home.address
    home_transit_preference: str = Field( # 修正：原始代码可能是 home.local_prefer_mode
        description="在家附近的首选交通方式，例如驾车"
    )
    # 可以添加 seat_preference, likes, dislikes, price_sensitivity 等其他字段


class PackingList(BaseModel):
    """行程的打包物品清单。"""
    items: list[str]


