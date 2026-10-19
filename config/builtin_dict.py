# -*- coding: utf-8 -*-
"""内置全量字典兜底数据 (自动从 3C机型字典库.xlsx 提取，确保 Vercel 云端 100% 零文件依赖秒加载)"""

BUILTIN_BRANDS = [
  {
    "id": "1",
    "name": "IPHONE"
  },
  {
    "id": "2",
    "name": "SAMSUNG"
  },
  {
    "id": "3",
    "name": "NOKIA"
  },
  {
    "id": "4",
    "name": "HTC"
  },
  {
    "id": "5",
    "name": "XIAOMI"
  },
  {
    "id": "6",
    "name": "LG"
  },
  {
    "id": "8",
    "name": "HUAWEI"
  },
  {
    "id": "9",
    "name": "ZTE"
  },
  {
    "id": "10",
    "name": "LENOVO"
  },
  {
    "id": "11",
    "name": "GIONEE"
  },
  {
    "id": "12",
    "name": "酷比"
  },
  {
    "id": "14",
    "name": "MOTOROLA"
  },
  {
    "id": "15",
    "name": "海尔"
  },
  {
    "id": "17",
    "name": "飞利浦"
  },
  {
    "id": "19",
    "name": "MEIZU"
  },
  {
    "id": "20",
    "name": "COOLPAD"
  },
  {
    "id": "21",
    "name": "天语"
  },
  {
    "id": "22",
    "name": "BlackBerry"
  },
  {
    "id": "26",
    "name": "索爱"
  },
  {
    "id": "27",
    "name": "OPPO"
  },
  {
    "id": "28",
    "name": "爱国者"
  },
  {
    "id": "33",
    "name": "长虹"
  },
  {
    "id": "36",
    "name": "戴尔"
  },
  {
    "id": "37",
    "name": "东芝"
  },
  {
    "id": "38",
    "name": "DOOV"
  },
  {
    "id": "48",
    "name": "宏碁"
  },
  {
    "id": "49",
    "name": "ASUS"
  },
  {
    "id": "51",
    "name": "HISENSE"
  },
  {
    "id": "60",
    "name": "康佳"
  },
  {
    "id": "64",
    "name": "NUBIA"
  },
  {
    "id": "65",
    "name": "纽曼"
  },
  {
    "id": "72",
    "name": "SONY"
  },
  {
    "id": "78",
    "name": "万利达"
  },
  {
    "id": "80",
    "name": "夏普"
  },
  {
    "id": "104",
    "name": "中国移动"
  },
  {
    "id": "125",
    "name": "台电"
  },
  {
    "id": "127",
    "name": "昂达"
  },
  {
    "id": "169",
    "name": "松下"
  },
  {
    "id": "227",
    "name": "SMARTISAN"
  },
  {
    "id": "229",
    "name": "ONEPLUS"
  },
  {
    "id": "230",
    "name": "MEITU"
  },
  {
    "id": "312",
    "name": "LETV"
  },
  {
    "id": "313",
    "name": "VIVO"
  },
  {
    "id": "315",
    "name": "微软"
  },
  {
    "id": "317",
    "name": "糖果"
  },
  {
    "id": "320",
    "name": "格力"
  },
  {
    "id": "321",
    "name": "小辣椒"
  },
  {
    "id": "328",
    "name": "Google"
  },
  {
    "id": "335",
    "name": "亚马逊"
  },
  {
    "id": "417",
    "name": "手机"
  },
  {
    "id": "418",
    "name": "安卓"
  },
  {
    "id": "420",
    "name": "奇酷"
  },
  {
    "id": "421",
    "name": "ivvi"
  },
  {
    "id": "459",
    "name": "360"
  },
  {
    "id": "468",
    "name": "先锋"
  },
  {
    "id": "473",
    "name": "蓝魔"
  },
  {
    "id": "507",
    "name": "8848"
  },
  {
    "id": "554",
    "name": "保千里"
  },
  {
    "id": "555",
    "name": "其他品牌"
  },
  {
    "id": "564",
    "name": "AGM"
  },
  {
    "id": "565",
    "name": "REALME"
  },
  {
    "id": "802",
    "name": "HONOR"
  },
  {
    "id": "803",
    "name": "中国电信"
  },
  {
    "id": "804",
    "name": "中国联通"
  },
  {
    "id": "805",
    "name": "FFALCON"
  },
  {
    "id": "806",
    "name": "APPLE"
  },
  {
    "id": "807",
    "name": "Hi nova"
  },
  {
    "id": "808",
    "name": "鼎桥"
  },
  {
    "id": "810",
    "name": "Nothing"
  },
  {
    "id": "811",
    "name": "步步高"
  },
  {
    "id": "812",
    "name": "读书郎"
  },
  {
    "id": "813",
    "name": "E人E本"
  },
  {
    "id": "814",
    "name": "好记星"
  },
  {
    "id": "815",
    "name": "惠普"
  },
  {
    "id": "816",
    "name": "酷比魔方"
  },
  {
    "id": "817",
    "name": "快易典"
  },
  {
    "id": "818",
    "name": "科大讯飞"
  },
  {
    "id": "819",
    "name": "诺亚舟"
  },
  {
    "id": "820",
    "name": "索立信"
  },
  {
    "id": "821",
    "name": "VOYO"
  },
  {
    "id": "822",
    "name": "五元素"
  },
  {
    "id": "823",
    "name": "小天才"
  },
  {
    "id": "824",
    "name": "小霸王"
  },
  {
    "id": "825",
    "name": "中柏"
  },
  {
    "id": "826",
    "name": "京东"
  },
  {
    "id": "827",
    "name": "Verizon Ellipsis"
  },
  {
    "id": "828",
    "name": "爱奇艺"
  },
  {
    "id": "829",
    "name": "巴诺书店"
  },
  {
    "id": "830",
    "name": "格斐斯"
  },
  {
    "id": "831",
    "name": "好状元"
  },
  {
    "id": "832",
    "name": "虹PAD"
  },
  {
    "id": "833",
    "name": "Jide"
  },
  {
    "id": "834",
    "name": "京东方"
  },
  {
    "id": "835",
    "name": "纽麦"
  },
  {
    "id": "836",
    "name": "小度"
  },
  {
    "id": "837",
    "name": "优学派"
  },
  {
    "id": "838",
    "name": "AMAZFIT"
  },
  {
    "id": "839",
    "name": "佳明"
  },
  {
    "id": "840",
    "name": "机械革命"
  },
  {
    "id": "841",
    "name": "Alienware"
  },
  {
    "id": "842",
    "name": "WIKO"
  },
  {
    "id": "844",
    "name": "VETAS"
  },
  {
    "id": "845",
    "name": "Ticwatch"
  },
  {
    "id": "846",
    "name": "COROS"
  },
  {
    "id": "847",
    "name": "SUUNTO"
  },
  {
    "id": "848",
    "name": "读书才子"
  },
  {
    "id": "849",
    "name": "小导师"
  },
  {
    "id": "850",
    "name": "维摩"
  },
  {
    "id": "851",
    "name": "Vido"
  },
  {
    "id": "852",
    "name": "知学士"
  },
  {
    "id": "853",
    "name": "普耐尔"
  },
  {
    "id": "854",
    "name": "先科"
  },
  {
    "id": "855",
    "name": "kreta"
  },
  {
    "id": "856",
    "name": "BOOX"
  },
  {
    "id": "857",
    "name": "网易有道"
  },
  {
    "id": "858",
    "name": "ViewSonic"
  },
  {
    "id": "859",
    "name": "Micro-Star"
  },
  {
    "id": "860",
    "name": "TECNO"
  },
  {
    "id": "861",
    "name": "ABARDEEN"
  },
  {
    "id": "862",
    "name": "DIDO"
  },
  {
    "id": "863",
    "name": "Fitbit"
  },
  {
    "id": "864",
    "name": "GOIIOG"
  },
  {
    "id": "865",
    "name": "Healbe"
  },
  {
    "id": "866",
    "name": "HPANPAN"
  },
  {
    "id": "867",
    "name": "Hwatch"
  },
  {
    "id": "868",
    "name": "JEEP"
  },
  {
    "id": "869",
    "name": "KUMI"
  },
  {
    "id": "870",
    "name": "RichEast"
  },
  {
    "id": "871",
    "name": "RPAP"
  },
  {
    "id": "872",
    "name": "iwown"
  },
  {
    "id": "873",
    "name": "爱百分"
  },
  {
    "id": "874",
    "name": "宝护光"
  },
  {
    "id": "875",
    "name": "北斗"
  },
  {
    "id": "876",
    "name": "POLAR"
  },
  {
    "id": "877",
    "name": "BUTCH"
  },
  {
    "id": "878",
    "name": "TRANGU"
  },
  {
    "id": "879",
    "name": "Diesel"
  },
  {
    "id": "880",
    "name": "FERACE"
  },
  {
    "id": "881",
    "name": "GAINES"
  },
  {
    "id": "882",
    "name": "codoon"
  },
  {
    "id": "883",
    "name": "航光测控"
  },
  {
    "id": "884",
    "name": "Haylou"
  },
  {
    "id": "885",
    "name": "京东京造"
  },
  {
    "id": "886",
    "name": "Carkira"
  },
  {
    "id": "887",
    "name": "LOKMAT"
  },
  {
    "id": "888",
    "name": "luoneng"
  },
  {
    "id": "889",
    "name": "MAISHUO"
  },
  {
    "id": "890",
    "name": "鸣动"
  },
  {
    "id": "891",
    "name": "VOSSTR"
  },
  {
    "id": "892",
    "name": "狮奥利兴"
  },
  {
    "id": "893",
    "name": "Schreiter"
  },
  {
    "id": "894",
    "name": "糖猫"
  },
  {
    "id": "895",
    "name": "WeLoop"
  },
  {
    "id": "896",
    "name": "WEIDISUO"
  },
  {
    "id": "897",
    "name": "文吉星"
  },
  {
    "id": "898",
    "name": "希比希"
  },
  {
    "id": "899",
    "name": "星空侠"
  },
  {
    "id": "900",
    "name": "仪卡"
  },
  {
    "id": "901",
    "name": "EZON"
  },
  {
    "id": "902",
    "name": "ZARKS"
  },
  {
    "id": "903",
    "name": "宙边"
  },
  {
    "id": "904",
    "name": "欧坦"
  },
  {
    "id": "905",
    "name": "ROYOLE"
  },
  {
    "id": "906",
    "name": "HASEE"
  },
  {
    "id": "907",
    "name": "雷神"
  },
  {
    "id": "909",
    "name": "ThinkPad"
  },
  {
    "id": "910",
    "name": "ThinkBook"
  }
]

BUILTIN_MOBILE = {
  "RAM": [
    "1G",
    "2G",
    "3G",
    "4G",
    "6G",
    "8G",
    "10G",
    "12G",
    "16G",
    "18G",
    "24G",
    "32G",
    "64G",
    "96G",
    "128G",
    "512MB",
    "1.5GB",
    "2.5GB",
    "3GB",
    "4GB",
    "6GB",
    "8GB",
    "12GB",
    "16GB",
    "20GB",
    "32GB",
    "48GB",
    "无内存"
  ],
  "ROM": [
    "8G",
    "16G",
    "32G",
    "64G",
    "128G",
    "256G",
    "512G",
    "640G",
    "1TB",
    "2TB",
    "4TB",
    "512M",
    "1024G"
  ],
  "机型颜色": [
    "玻璃白",
    "金色",
    "黑色",
    "银色",
    "白色",
    "玫瑰金色",
    "亮黑色",
    "深空灰色",
    "红色",
    "蓝色",
    "黄色",
    "紫色",
    "粉色",
    "灰色",
    "橙色",
    "绿色",
    "珊瑚色",
    "极光色",
    "珠光贝母",
    "黑金色",
    "天空之境",
    "其他颜色",
    "暗夜绿色",
    "石墨色",
    "海蓝色",
    "釉白色",
    "夏日胡杨",
    "秋日胡杨",
    "冰霜银",
    "零度白",
    "深海蓝",
    "超闪蓝",
    "超闪黑",
    "超闪白",
    "霓虹",
    "简单黑",
    "氧气紫",
    "星海蓝",
    "月光银",
    "莫奈漫彩",
    "爵士黑",
    "月光白",
    "黑镜",
    "银月",
    "幻砂星海",
    "浮光",
    "星河银",
    "太空蓝",
    "幻彩流星",
    "静默星空",
    "碧海星辰",
    "湖光秋色",
    "云墨灰",
    "锖色",
    "粉橙色",
    "羽砂黑",
    "白沙银",
    "雅川青",
    "冰原蓝",
    "钛金属灰",
    "原色钛金属",
    "沙漠色钛金属"
  ],
  "网络制式": [
    "全网通",
    "双网通",
    "移动版",
    "联通版",
    "电信版",
    "移动版全网通",
    "运营商版全网通",
    "5G",
    "4G",
    "WIFI",
    "WIFI+5G",
    "WIFI+4G",
    "WIFI+3G",
    "其他"
  ],
  "购买渠道": [
    "国行",
    "其他版本",
    "大陆国行",
    "国行官换机",
    "国行资源机",
    "国行权益机",
    "国行官翻机",
    "港版",
    "美版有锁",
    "美版无锁",
    "水货有锁",
    "水货无锁",
    "非大陆国行",
    "展示机",
    "其他渠道"
  ]
}

BUILTIN_LAPTOP = {
  "固态硬盘": [
    "512G",
    "1TB",
    "2TB",
    "4TB",
    "256G",
    "128G",
    "120G",
    "240G",
    "480G",
    "960G",
    "1TB及以上",
    "不含固态硬盘",
    "无"
  ],
  "机械硬盘": [
    "无",
    "不含机械硬盘",
    "500G",
    "1TB",
    "2TB",
    "3TB",
    "4TB",
    "机械硬盘500GB-1TB",
    "机械硬盘1TB",
    "机械硬盘2TB",
    "机械硬盘3TB",
    "机械硬盘1.5TB及以上",
    "机械硬盘512GB",
    "机械硬盘256GB及以下",
    "机械硬盘128GB",
    "机械硬盘64GB",
    "机械硬盘320GB",
    "机械硬盘750GB"
  ],
  "处理器": [
    "CPU-Test-Thread-49",
    "CPU-Test-Thread-48",
    "CPU-Test-Thread-47",
    "CPU-Test-Thread-46",
    "CPU-Test-Thread-45",
    "CPU-Test-Thread-44",
    "CPU-Test-Thread-43",
    "CPU-Test-Thread-42",
    "CPU-Test-Thread-41",
    "CPU-Test-Thread-40",
    "CPU-Test-Thread-39",
    "CPU-Test-Thread-38",
    "CPU-Test-Thread-37",
    "CPU-Test-Thread-36",
    "CPU-Test-Thread-35",
    "CPU-Test-Thread-34",
    "CPU-Test-Thread-33",
    "CPU-Test-Thread-32",
    "CPU-Test-Thread-31",
    "CPU-Test-Thread-30",
    "CPU-Test-Thread-29",
    "CPU-Test-Thread-28",
    "CPU-Test-Thread-27",
    "CPU-Test-Thread-26",
    "CPU-Test-Thread-25",
    "CPU-Test-Thread-24",
    "CPU-Test-Thread-23",
    "CPU-Test-Thread-22",
    "CPU-Test-Thread-21",
    "CPU-Test-Thread-20",
    "CPU-Test-Thread-19",
    "CPU-Test-Thread-18",
    "CPU-Test-Thread-17",
    "CPU-Test-Thread-16",
    "CPU-Test-Thread-15",
    "CPU-Test-Thread-14",
    "CPU-Test-Thread-13",
    "CPU-Test-Thread-12",
    "CPU-Test-Thread-11",
    "CPU-Test-Thread-10",
    "CPU-Test-Thread-9",
    "CPU-Test-Thread-8",
    "CPU-Test-Thread-7",
    "CPU-Test-Thread-6",
    "CPU-Test-Thread-5",
    "CPU-Test-Thread-4",
    "CPU-Test-Thread-3",
    "CPU-Test-Thread-2",
    "CPU-Test-Thread-1",
    "CPU-Test-Thread-0",
    "i9-9999HX-Special",
    "i5-2234",
    "i3 1.1G",
    "i5 1.1G",
    "Core M 1.1G",
    "m3 1.1G",
    "1.2 GHz Intel Core i5",
    "i7 1.2G",
    "Core M 1.2G",
    "m3 1.2G",
    "m5 1.2G",
    "i5 1.3G",
    "1.3 GHz Intel Core i7",
    "Core M 1.3G",
    "m7 1.3G",
    "2 Duo 1.4G",
    "i5 1.4G",
    "i7 1.4G",
    "2 Duo 1.6G",
    "i5 1.6G",
    "1.6 GHz Intel Core m3",
    "i5 1.7G",
    "i7 1.7G",
    "1.8 GHz Intel Core 2 Duo",
    "i5 1.8G",
    "i7 1.8G",
    "2 Duo 2.0G",
    "i5 2.0G",
    "i7 2.0G",
    "2 Duo 2.13G",
    "2.16 GHz Intel Core 2 Duo",
    "2.2 GHz Intel Core 2 Duo",
    "2.2 GHz Intel Core i5",
    "i7 2.2G",
    "2 Duo 2.26G",
    "i5 2.3G",
    "i7 2.3G",
    "i9 2.3G",
    "2 Duo 2.4G",
    "i5 2.4G",
    "i7 2.4G",
    "i9 2.4G",
    "2 Duo 2.5G",
    "i5 2.5G",
    "i7 2.5G",
    "i5 2.53G",
    "2 Duo 2.6G",
    "i5 2.6G",
    "i7 2.6G",
    "i7 2.66G",
    "i5 2.7G",
    "i7 2.7G",
    "2 Duo 2.8G",
    "i5 2.8G",
    "i7 2.8G",
    "i5 2.9G",
    "i7 2.9G",
    "i9 2.9G",
    "3.0 GHz Intel Core 2 Duo",
    "i7 3.0G",
    "i5 3.1G",
    "i7 3.1G",
    "i5 3.3G",
    "i7 3.3G",
    "i7 3.5G",
    "Core M 1.8G",
    "Intel Core Ultra 9 285H",
    "Intel Core Ultra 7 255HX",
    "Intel Core Ultra 7 155H",
    "Intel Core Ultra 5 125H",
    "Intel Core Ultra 9 185H",
    "Intel Core Ultra 7 268V",
    "Intel Core Ultra 7 258V",
    "Intel Core Ultra 5 228V",
    "Intel Core Ultra 5 226V",
    "Intel Core Ultra 5 238V",
    "Intel Core i9-14900HX",
    "Intel Core i7-14700HX",
    "Intel Core i7-14650HX",
    "Intel Core i5-14500HX",
    "Intel Core i9-13980HX",
    "Intel Core i9-13900HX",
    "Intel Core i7-13700HX",
    "Intel Core i7-13650HX",
    "Intel Core i5-13500HX",
    "Intel Core i5-13420H",
    "Intel Core i5-12500H",
    "Intel Core i7-12700H",
    "Intel Core i9-12900H",
    "Intel Core i3",
    "Intel Core i5",
    "Intel Core i7",
    "Intel Core i9",
    "Intel Core i3 10代",
    "Intel Core i3 11代",
    "Intel Core i3 12代",
    "Intel Core i3 13代",
    "Intel Core i5 10代",
    "Intel Core i5 11代",
    "Intel Core i5 12代",
    "Intel Core i5 13代",
    "Intel Core i5 14代",
    "Intel Core i7 10代",
    "Intel Core i7 11代",
    "Intel Core i7 12代",
    "Intel Core i7 13代",
    "Intel Core i7 14代",
    "Intel Core i9 10代",
    "Intel Core i9 11代",
    "Intel Core i9 12代",
    "Intel Core i9 13代",
    "Intel Core i9 14代",
    "AMD Ryzen AI 9 HX 370",
    "AMD Ryzen AI 9 365",
    "AMD Ryzen AI 7 350",
    "AMD Ryzen 9 9955HX",
    "AMD Ryzen 9 8945HX",
    "AMD Ryzen 9 7945HX",
    "AMD Ryzen 9 7940HX",
    "AMD Ryzen 7 8845H",
    "AMD Ryzen 7 7840H",
    "AMD Ryzen 7 7735H",
    "AMD Ryzen 7 7735HS",
    "AMD Ryzen 5 8645H",
    "AMD Ryzen 5 7640H",
    "AMD Ryzen 5 7535H",
    "AMD Ryzen 3",
    "AMD Ryzen 5",
    "AMD Ryzen 7",
    "AMD Ryzen 9",
    "Apple M1",
    "Apple M1 Pro",
    "Apple M1 Max",
    "Apple M2",
    "Apple M2 Pro",
    "Apple M2 Max",
    "Apple M3",
    "Apple M3 Pro",
    "Apple M3 Max",
    "Apple M4",
    "Apple M4 Pro",
    "Apple M4 Max",
    "高通骁龙 X Elite",
    "高通骁龙 X Plus",
    "麒麟 9006C",
    "麒麟X90"
  ],
  "显卡": [
    "GPU-Test-Thread-49",
    "GPU-Test-Thread-48",
    "GPU-Test-Thread-47",
    "GPU-Test-Thread-46",
    "GPU-Test-Thread-45",
    "GPU-Test-Thread-44",
    "GPU-Test-Thread-43",
    "GPU-Test-Thread-42",
    "GPU-Test-Thread-41",
    "GPU-Test-Thread-40",
    "GPU-Test-Thread-39",
    "GPU-Test-Thread-38",
    "GPU-Test-Thread-37",
    "GPU-Test-Thread-36",
    "GPU-Test-Thread-35",
    "GPU-Test-Thread-34",
    "GPU-Test-Thread-33",
    "GPU-Test-Thread-32",
    "GPU-Test-Thread-31",
    "GPU-Test-Thread-30",
    "GPU-Test-Thread-29",
    "GPU-Test-Thread-28",
    "GPU-Test-Thread-27",
    "GPU-Test-Thread-26",
    "GPU-Test-Thread-25",
    "GPU-Test-Thread-24",
    "GPU-Test-Thread-23",
    "GPU-Test-Thread-22",
    "GPU-Test-Thread-21",
    "GPU-Test-Thread-20",
    "GPU-Test-Thread-19",
    "GPU-Test-Thread-18",
    "GPU-Test-Thread-17",
    "GPU-Test-Thread-16",
    "GPU-Test-Thread-15",
    "GPU-Test-Thread-14",
    "GPU-Test-Thread-13",
    "GPU-Test-Thread-12",
    "GPU-Test-Thread-11",
    "GPU-Test-Thread-10",
    "GPU-Test-Thread-9",
    "GPU-Test-Thread-8",
    "GPU-Test-Thread-7",
    "GPU-Test-Thread-6",
    "GPU-Test-Thread-5",
    "GPU-Test-Thread-4",
    "GPU-Test-Thread-3",
    "GPU-Test-Thread-2",
    "GPU-Test-Thread-1",
    "GPU-Test-Thread-0",
    "RTX 5090 Super",
    "NVIDIA GeForce RTX 5090",
    "NVIDIA GeForce RTX 5080",
    "NVIDIA GeForce RTX 5070 Ti",
    "NVIDIA GeForce RTX 5070",
    "NVIDIA GeForce RTX 5060",
    "NVIDIA GeForce RTX 5050",
    "NVIDIA GeForce RTX 4090",
    "NVIDIA GeForce RTX 4080",
    "NVIDIA GeForce RTX 4070",
    "NVIDIA GeForce RTX 4060",
    "NVIDIA GeForce RTX 4050",
    "NVIDIA GeForce RTX 3080 Ti",
    "NVIDIA GeForce RTX 3080",
    "NVIDIA GeForce RTX 3070 Ti",
    "NVIDIA GeForce RTX 3070",
    "NVIDIA GeForce RTX 3060",
    "NVIDIA GeForce RTX 3050 Ti",
    "NVIDIA GeForce RTX 3050",
    "NVIDIA GeForce RTX 2080 Super",
    "NVIDIA GeForce RTX 2080",
    "NVIDIA GeForce RTX 2070 Super",
    "NVIDIA GeForce RTX 2070",
    "NVIDIA GeForce RTX 2060 Super",
    "NVIDIA GeForce RTX 2060",
    "NVIDIA GeForce RTX 2050",
    "NVIDIA GeForce GTX 1660 Ti",
    "NVIDIA GeForce GTX 1650 Ti",
    "NVIDIA GeForce GTX 1650",
    "NVIDIA GeForce GTX 1060",
    "NVIDIA GeForce GTX 1050 Ti",
    "NVIDIA GeForce GTX 1050",
    "NVIDIA GeForce MX570",
    "NVIDIA GeForce MX550",
    "NVIDIA GeForce MX450",
    "NVIDIA GeForce MX350",
    "NVIDIA GeForce MX330",
    "NVIDIA GeForce MX250",
    "NVIDIA GeForce MX150",
    "AMD Radeon RX 7900M",
    "AMD Radeon RX 7600M XT",
    "AMD Radeon RX 7600S",
    "AMD Radeon RX 6850M XT",
    "AMD Radeon RX 6800M",
    "AMD Radeon RX 6700M",
    "AMD Radeon RX 6600M",
    "AMD Radeon 780M",
    "AMD Radeon 680M",
    "Intel Arc A770M",
    "Intel Arc A730M",
    "Intel Arc A550M",
    "Intel Arc A370M",
    "Intel Arc Graphics",
    "Intel Iris Xe Graphics",
    "Intel UHD Graphics",
    "核芯/集成显卡",
    "其它显卡",
    "独显8G",
    "独显6G",
    "独显4G",
    "独显2G"
  ]
}

BUILTIN_WATCH = {
  "表壳材质": [
    "铝金属表壳",
    "不锈钢表壳",
    "钛金属表壳",
    "精密陶瓷",
    "纤维高强度聚合物",
    "高分子材料",
    "陶瓷表壳",
    "黑色镶金非晶表壳",
    "纳米微晶陶瓷",
    "精钢表壳",
    "陶瓷+塑胶",
    "316L不锈钢材质",
    "钛金属+陶瓷",
    "不锈钢+陶瓷",
    "钛金属+蓝宝石玻璃",
    "聚合纤维",
    "聚合纤维+铝金属",
    "金属+塑胶",
    "碳纤维",
    "不锈钢+塑胶",
    "不锈钢+高分子纤维复合材料",
    "非晶锆合金材质",
    "玻璃",
    "塑胶",
    "316L低碳精钢",
    "玻璃纤维增强聚酰胺",
    "尼龙增强聚酰胺",
    "钢化玻璃",
    "硅胶",
    "钛合金+纤维增强聚合物"
  ],
  "表壳尺寸": [
    "41毫米",
    "45毫米",
    "40毫米",
    "44毫米",
    "38毫米",
    "42毫米",
    "46毫米",
    "49毫米",
    "43毫米",
    "51毫米",
    "47毫米",
    "1.85寸",
    "1.85英寸",
    "1.43英寸",
    "1.91英寸",
    "2.07英寸",
    "1.5英寸",
    "1.3英寸",
    "1.78英寸",
    "1.4英寸",
    "1.69英寸",
    "1.28英寸",
    "1.2英寸",
    "1.32英寸",
    "1.39英寸",
    "1.6英寸",
    "0.9英寸",
    "48毫米",
    "1.64英寸",
    "1.74英寸",
    "1.1英寸",
    "1.47英寸",
    "1.75英寸",
    "1英寸",
    "1.23英寸",
    "55毫米",
    "53毫米",
    "50毫米",
    "52毫米",
    "57毫米",
    "34毫米"
  ],
  "连接": [
    "GPS",
    "GPS+蜂窝网络",
    "蓝牙",
    "WIFI",
    "eSIM独立通话"
  ],
  "网络制式": [
    "全网通",
    "双网通",
    "移动版",
    "联通版",
    "电信版",
    "移动版全网通",
    "运营商版全网通",
    "WIFI",
    "WIFI+5G",
    "WIFI+4G",
    "WIFI+3G",
    "其他"
  ]
}
