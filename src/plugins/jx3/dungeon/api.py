import re

from tabulate import tabulate

from src.tools.dep import *
from src.tools.generate import generate, get_uuid
from src.plugins.help import css

ASSETS = TOOLS[:-5] + "assets"
VIEWS = TOOLS[:-5] + "views"

try:
    from src.tools.dep.jx3.tuilan import gen_ts, gen_xsk, format_body, dungeon_sign # 收到热心网友举报，我们已对推栏的算法进行了隐藏。
except:
    pass

async def zone(server, id):
    server = server_mapping(server)
    final_url = f"{Config.jx3api_link}/view/role/teamCdList?token={token}&server={server}&name={id}&ticket={ticket}&robot={bot}&scale=1"
    data = await get_api(final_url)
    if data["code"] == 404:
        return ["玩家不存在或尚未在世界频道发言哦~"]
    return data["data"]["url"]

async def get_cd(server: str, sep: str):
    url = f"https://pull.j3cx.com/api/serendipity?server={server}&serendipity={sep}&pageSize=1"
    data = await get_api(url)
    data = data.get("data").get("data")
    if not data:
        return "没有记录哦~"
    data = data[0]
    time = data["date_str"]
    msg = f"「{server}」服务器上一次记录「{sep}」：\n{time}\n数据来源：@茗伊插件集"
    return msg

async def post_url(url, proxy: dict = None, headers: str = None, timeout: int = 300, data: dict = None):
    async with httpx.AsyncClient(proxies=proxy, follow_redirects=True) as client:
        resp = await client.post(url, timeout=timeout, headers=headers, data=data)
        result = resp.text
        return result

device_id = ticket.split("::")[1]

async def get_map(name, mode):
    param = {
        "mode": 2,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/list", data=param, headers=headers)
    data = json.loads(data)
    for i in data["data"]:
        for x in i["dungeon_infos"]:
            if x["name"] == name:
                for y in x["maps"]:
                    if y["mode"] == mode:
                        return y["map_id"]


async def get_boss(map, mode, boss):
    map_id = await get_map(map, mode)
    param = {
        "map_id": map_id,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/info", data=param, headers=headers)
    data = json.loads(data)
    for i in data["data"]["info"]["boss_infos"]:
        if i["name"] == boss:
            return i["index"]


async def get_drops(map, mode, boss):
    boss_id = await get_boss(map, mode, boss)
    param = {
        "boss_id": boss_id,
        "ts": gen_ts()
    }
    param = format_body(param)
    xsk = gen_xsk(param)
    headers = {
        "Host" : "m.pvp.xoyo.com",
        "Accept" : "application/json",
        "Accept-Language" : "zh-cn",
        "Connection" : "keep-alive",
        "Content-Type" : "application/json",
        "cache-control" : "no-cache",
        "fromsys" : "APP",
        "clientkey" : "1",
        "apiversion" : "3",
        "gamename" : "jx3",
        "platform" : "ios",
        "sign" : "true",
        "token" : ticket,
        "deviceid" : device_id,
        "User-Agent" : "SeasunGame/193 CFNetwork/1240.0.4 Darwin/20.6.0",
        "x-sk": xsk
    }
    data = await post_url(url="https://m.pvp.xoyo.com/dungeon/boss-drop", data=param, headers=headers)
    return json.loads(data)

# 暂时不打算做5人副本，5人副本与10人副本的请求地址不同。
# 10人/25人：https://m.pvp.xoyo.com/dungeon/list
# 5人：https://m.pvp.xoyo.com/dungeon/list-all
# 暂时未知数据是否相同，后续考虑是否添加。

def mode_mapping(mode):
    if mode in ["25yx", "yx", "YX", "Yx", "yX", "25人YX", "25人英雄", "英雄", "25Yx", "25人yX", "25人yx", "25英雄"]:
        return "25人英雄"
    elif mode in ["25pt", "PT", "pt", "pT", "25人PT", "25人Pt", "25人pt", "25普通", "普通", "25人普通", "25pt", "铂"]:
        return "25人普通"
    elif mode in ["10人", "10", "10人普通", "10PT", "10pt"]:
        return "10人普通"
    elif mode in ["10人yx", "10人英雄", "10YX", "10yx"]:
        return "10人英雄"
    elif mode in ["10人tz", "10tz", "10TZ", "10Tz", "10人挑战", "10挑战"]:
        return "10人挑战"
    elif mode in ["25人tz", "tz", "TZ", "Tz", "25挑战", "25人挑战", "25TZ", "25tz"]:
        return "25人挑战"
    else:
        return False

star = """
<svg width="20" height="20">
    <polygon points="10,0 13,7 20,7 14,12 16,19 10,15 4,19 6,12 0,7 7,7" style="fill:gold; stroke:gold; stroke-width:1px;" />
</svg>
"""

template = """
<tr>
    <td class="short-column">
        <img src="$icon"></img>
    </td>
    <td class="short-column">$name</td>
    <td class="short-column">
        <div class="attrs">$attrs</div></td>
    <td class="short-column">$type</td>
    <td class="short-column">
        $stars
    </td>
    <td class="short-column">$quailty</td>
    <td class="short-column">$score</td>
    <td class="short-column"><div class="attrs">$fivestone</div></td>
</tr>
"""

equip_types = ["帽子","上衣","腰带","护臂","裤子","鞋","项链","腰坠","戒指","投掷囊"]

filter_words = ["根骨","力道","元气","身法","体质"]

async def genderater(map, mode, boss):
    mode = mode_mapping(mode)
    if mode == False:
        return ["唔……难度似乎音卡不能理解哦~"]
    zone = zone_mapping(map)
    if zone == False:
        return ["唔……副本名称似乎音卡不能理解哦~"]
    try:
        data = await get_drops(map, mode, boss)
    except KeyError:
        return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
    data = data["data"]
    armors = data["armors"]
    others = data["others"]
    weapons = data["weapons"]
    if len(armors) == 0 and len(others) == 0 and len(weapons) == 0:
        return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    else:
        tablecontent = []
        for i in armors:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            if i["Icon"]["SubKind"] in equip_types and i["Type"] != "Act_运营及版本道具":
                type_ = "装备"
                attrs_data = i["ModifyType"]
                attrs_list = []
                for x in attrs_data:
                    string = x["Attrib"]["GeneratedMagic"]
                    flag = False
                    for y in filter_words:
                        if string.find(y) != -1:
                            flag = True
                    if flag:
                        continue
                    attrs_list.append(string)
                attrs = "<br>".join(attrs_list)
                if i["type"] != "戒指":
                    diamon_data = i["DiamonAttribute"]
                    diamon_list = []
                    for x in diamon_data:
                        string = re.sub(r"\b+", "", x["Attrib"]["GeneratedMagic"]) + "?"
                        diamon_list.append(string)
                    fivestone = "<br>".join(diamon_list)
                else:
                    fivestone = "不适用"
                max = i["MaxStrengthLevel"]
                stars = []
                for x in range(int(max)):
                    stars.append(star)
                stars = "\n".join(stars)
                quailty = i["Quality"]
                equip_type = i["Icon"]["SubKind"]
                if equip_type == "帽子":
                    score = str(int(quailty)*1.62)
                elif equip_type in ["上衣","裤子"]:
                    score = str(int(quailty)*1.8)
                elif equip_type in ["腰带","护臂","鞋"]:
                    score = str(int(quailty)*1.26)
                elif equip_type in ["项链","腰坠","戒指"]:
                    score = str(int(quailty)*0.9)
                elif equip_type in ["投掷囊"]:
                    score = str(int(quailty)*1.08)
            else:
                if i["Type"] == "Act_运营及版本道具":
                    type_ = "外观"
                else:
                    type_ = re.sub(r"\d+", "", i["Icon"]["SubKind"])
                attrs = "不适用"
                fivestone = "不适用"
                max = "不适用"
                quailty = "不适用"
                score = "不适用"
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        for i in weapons:
            name = i["Name"]
            icon = i["Icon"]["FileName"]
            type_ = i["Icon"]["SubKind"] if i["Icon"]["SubKind"] != "投掷囊" else "暗器"
            attrs_data = i["ModifyType"]
            attrs_list = []
            for x in attrs_data:
                string = x["Attrib"]["GeneratedMagic"]
                flag = False
                for y in filter_words:
                    if string.find(y) != -1:
                        flag = True
                if flag:
                    continue
                attrs_list.append(string)
            attrs = "<br>".join(attrs_list)
            diamon_data = i["DiamonAttribute"]
            diamon_list = []
            for x in diamon_data:
                string = re.sub(r"\b+", "", x["Attrib"]["GeneratedMagic"]) + "?"
                diamon_list.append(string)
            fivestone = "<br>".join(diamon_list)
            max = i["MaxStrengthLevel"]
            stars = []
            for x in range(int(max)):
                stars.append(star)
            stars = "\n".join(stars)
            quailty = i["Quality"]
            score = str(int(quailty)*2.16)
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        for i in others:
            type_ = "不适用"
            icon = i["Icon"]["FileName"]
            name = i["Name"]
            attrs = "不适用"
            stars = "不适用"
            score = "不适用"
            quailty = "不适用"
            fivestone = "不适用"
            tablecontent.append(template.replace("$icon", icon).replace("$name", name).replace("$attrs", attrs).replace("$type", type_).replace("$stars", stars).replace("$quailty", quailty).replace("$score", score).replace("$fivestone", fivestone))
        final_table = "\n".join(tablecontent)
        html = read(VIEWS + "/jx3/drop/drop.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", final_table).replace("$randomsaohua", saohua).replace("$appinfo", f" · 掉落列表 · {mode}{map} · {boss}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()
def zone_mapping(zone):
    if zone in ["风起稻香","团队副本","战宝迦兰","战宝"]:
        return "战宝迦兰"
    elif zone in ["荻花宫后山","荻花后山","后山"]:
        return "荻花宫后山"
    elif zone in ["宫中神武遗迹","宫中神武","宫中"]:
        return "宫中神武遗迹"
    elif zone in ["持国天王殿","持国"]:
        return "持国天王殿"
    elif zone in ["荻花圣殿","荻花","dh"]:
        return "荻花圣殿"
    elif zone in ["持国天王回忆录","持国回忆录"]:
        return "持国天王回忆录"
    elif zone in ["荻花洞窟","洞窟"]:
        return "荻花洞窟"
    elif zone in ["烛龙殿","烛龙","zld","猪笼"]:
        return "烛龙殿"
    elif zone in ["会战唐门","会战南诏皇宫","皇宫"]:
        return "会战唐门"
    elif zone in ["龙渊泽","lyz"]:
        return "龙渊泽"
    elif zone in ["太原之战·逐虎驱狼","逐虎","逐虎驱狼"]:
        return "太原之战·逐虎驱狼"
    elif zone in ["太原之战·夜守孤城","野兽","夜守孤城","夜守"]:
        return "太原之战·夜守孤城"
    elif zone in ["秦皇陵","盗墓","qhl"]:
        return "秦皇陵"
    elif zone in ["风雪稻香村","稻香村"]:
        return "风雪稻香村"
    elif zone in ["血战天策","血战"]:
        return "血战天策"
    elif zone in ["大明宫","dmg"]:
        return "大明宫"
    elif zone in ["战宝军械库","军械库"]:
        return "战宝军械库"
    elif zone in ["永王行宫·花月别院","花月别院","花月"]:
        return "永王行宫·花月别院"
    elif zone in ["永王行宫·仙侣庭院","仙侣庭院","仙侣","仙女"]:
        return "永王行宫·仙侣庭院"
    elif zone in ["上阳宫·双曜亭","双曜","双曜亭","双耀"]:
        return "上阳宫·双曜亭"
    elif zone in ["上阳宫·观风殿","观风","观风殿","gfd"]:
        return "上阳宫·观风殿"
    elif zone in ["风雷刀谷·锻刀厅","锻刀厅","ddt"]:
        return "风雷刀谷·锻刀厅"
    elif zone in ["风雷刀谷·千雷殿","千雷","千雷殿"]:
        return "风雷刀谷·千雷殿"
    elif zone in ["狼牙堡·战兽山","战兽山","战兽"]:
        return "狼牙堡·战兽山"
    elif zone in ["狼牙堡·燕然峰","燕然","嫣然","燕然峰"]:
        return "狼牙堡·燕然峰"
    elif zone in ["狼牙堡·辉天堑","辉天","辉天堑","htq"]:
        return "狼牙堡·辉天堑"
    elif zone in ["狼牙堡·狼神殿","狼神","lsd","狼神殿"]:
        return "狼牙堡·狼神殿"
    elif zone in ["冰火岛·荒血路","hxl","荒血路"]:
        return "冰火岛·荒血路"
    elif zone in ["冰火岛·青莲狱","青莲狱","qly"]:
        return "冰火岛·青莲狱"
    elif zone in ["尘归海·巨冥湾","jmw","巨冥湾","追须"]:
        return "尘归海·巨冥湾"
    elif zone in ["尘归海·饕餮洞","饕餮洞","饕餮","ttd"]:
        return "尘归海·饕餮洞"
    elif zone in ["敖龙岛","奥比岛","ald"]:
        return "敖龙岛"
    elif zone in ["范阳夜变","夜店","范阳夜店","范阳书店"]:
        return "范阳夜变"
    elif zone in ["达摩洞","dmd","达","达摩"]:
        return "达摩洞"
    elif zone in ["白帝江关","白帝","白帝江棺","白"]:
        return "白帝江关"
    elif zone in ["雷域大泽","雷域","雷狱","瘤子","大泽","雷"]:
        return "雷域大泽"
    elif zone in ["河阳之战","河阳","河"]:
        return "河阳之战"
    elif zone in ["西津渡","码头","西西西","xjd"]:
        return "西津渡"
    elif zone in ["武狱黑牢","黑牢","武狱","牢","武牢"]:
        return "武狱黑牢"
    else:
        return False

# async def generater(map, mode, boss):
#     mode = mode_mapping(mode)
#     if mode == False:
#         return ["唔……难度似乎音卡不能理解哦~"]
#     zone = zone_mapping(map)
#     if zone == False:
#         return ["唔……副本似乎音卡不能理解哦~"]
#     try:
#         data = await get_drops(zone, mode, boss)
#     except KeyError:
#         return ["唔……没有找到该掉落列表，请检查副本名称、BOSS名称或难度~"]
#     data = data["data"]
#     armors = data["armors"]
#     others = data["others"]
#     weapons = data["weapons"]
#     if len(armors) == 0 and len(others) == 0 and len(weapons) == 0:
#         return ["唔……没有找到该boss的掉落哦~\n您确定" + f"{boss}住在{mode}{map}吗？"]
    
# Working

template = """
<tr>
    <td class="short-column">$zonename</td>
    <td class="short-column">$zonemode</td>
    <td>
    $images
    </td>
</tr>
"""

unable_ = """
<img src="$imagepath", height="20",width="20"></img>
"""

available_ = """
<img src="$imagepath", height="20",width="20"></img>
"""

async def zone_v2(server, id):
    server = server_mapping(server)
    details_request = f"{Config.jx3api_link}/data/role/detailed?token={token}&server={server}&name={id}"
    details_data = await get_api(details_request)
    if details_data["code"] != 200:
        guid = ""
        return ["唔……获取玩家信息失败。"]
    else:
        guid = details_data["data"]["globalRoleId"]
    ts = gen_ts()
    param = {
        "globalRoleId": guid,
        "sign": dungeon_sign(f"globalRoleId={guid}&ts={ts}"),
        "ts": ts
    }
    param = format_body(param)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "m.pvp.xoyo.com",
        "Origin": "https://w.pvp.xoyo.com:31727",
        "User-Agent": "SeasunGame/178 CFNetwork/1240.0.2 Darwin/20.5.0",
        "token": ticket,
        "X-Sk": gen_xsk(param)
    }
    data = await post_url("https://m.pvp.xoyo.com/h5/parser/cd-process/get-by-role", headers=headers, data=param)
    unable = unable_.replace("$imagepath", ASSETS + "/image/grey.png")
    available = available_.replace("$imagepath", ASSETS + "/image/gold.png")
    data = json.loads(data)
    if data["data"] == []:
        return ["该玩家目前尚未打过任何副本哦~\n注意：10人普通副本会在周五刷新一次。"]
    else:
        contents = []
        for i in data["data"]:
            images = []
            map_name = i["mapName"]
            map_type = i["mapType"]
            for x in i["bossProgress"]:
                if x["finished"] == True:
                    images.append(unable)
                else:
                    images.append(available)
            image_content = "\n".join(images)
            temp = template.replace("$zonename", map_name).replace("$zonemode", map_type).replace("$images", image_content)
            contents.append(temp)
        content = "\n".join(contents)
        html = read(VIEWS + "/jx3/teamcd/teamcd.html")
        font = ASSETS + "/font/custom.ttf"
        saohua = await get_api(f"https://www.jx3api.com/data/saohua/random?token={token}")
        saohua = saohua["data"]["text"]
        html = html.replace("$customfont", font).replace("$tablecontent", content).replace("$randomsaohua", saohua).replace("$appinfo", f" · 副本记录 · {server} · {id}")
        final_html = CACHE + "/" + get_uuid() + ".html"
        write(final_html, html)
        final_path = await generate(final_html, False, "table", False)
        return Path(final_path).as_uri()