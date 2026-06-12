#!/usr/bin/env python3
"""八字排盘 Web 服务器 — 纯 stdlib，零依赖
启动: python3 server.py
访问: http://localhost:8768
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from datetime import datetime

PORT = 8768
HOST = 'localhost'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============== 八字计算引擎 ==============

TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WU_XING = ["木", "火", "土", "金", "水"]
GAN_WUXING = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
ZHI_WUXING = [4, 0, 0, 1, 2, 1, 2, 3, 3, 2, 4, 4]
GAN_YIN = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
JIAZI = [(i % 10, i % 12) for i in range(60)]
JIAZI_IDX = {(g, z): i for i, (g, z) in enumerate(JIAZI)}

LUNAR_DATA = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x16a95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x05ac0, 0x0ab60, 0x096d5, 0x092e0,
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,
    0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a4d0, 0x0d150, 0x0f252,
    0x0d520,
]

SOLAR_TERM_BASE = [
    5.4055, 20.12, 3.87, 18.73, 5.63, 20.646, 5.59, 20.84,
    5.52, 21.04, 5.678, 21.37, 7.108, 22.83, 7.5, 23.13,
    7.646, 23.042, 8.318, 23.438, 7.438, 22.36, 7.18, 21.94
]
SOLAR_TERM_MONTH = [1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12]
NAYIN = ["海中金","炉中火","大林木","路旁土","剑锋金","山头火",
    "涧下水","城头土","白蜡金","杨柳木","泉中水","屋上土",
    "霹雳火","松柏木","流水水","砂石金","山下火","平地木",
    "壁上土","金箔金","覆灯火","天河水","大驿土","钗环金",
    "桑柘木","柘榴木","大海水","海中金","炉中火","大林木",
    "路旁土","剑锋金","山头火","涧下水","城头土","白蜡金",
    "杨柳木","泉中水","屋上土","霹雳火","松柏木","流水水",
    "砂石金","山下火","平地木","壁上土","金箔金","覆灯火",
    "天河水","大驿土","钗环金","桑柘木","柘榴木","大海水",
    "海中金","炉中火","大林木","路旁土","剑锋金","山头火"]
ZHI_CANG_GAN = {
    0: [9], 1: [5, 9, 7], 2: [0, 2, 4], 3: [1], 4: [4, 1, 9],
    5: [2, 4, 6], 6: [3, 5], 7: [5, 3, 1], 8: [6, 4, 8],
    9: [7], 10: [4, 7, 3], 11: [8, 0],
}

QIONGTONG_RULES = {
    0: {0:{'primary':['火'],'secondary':['木','土'],'desc':'子月甲木天寒木冻，先取火暖局，再用木助，土培根。'},
        1:{'primary':['火'],'secondary':['木','土'],'desc':'丑月甲木寒气未退，仍以火为先，木为助。'},
        2:{'primary':['水'],'secondary':['火'],'desc':'寅月甲木建禄当令，初春尚寒，先用水润，再用火暖。'},
        3:{'primary':['水'],'secondary':['土','金'],'desc':'卯月甲木羊刃当令，春深木旺，用水滋扶，土培金修。'},
        4:{'primary':['水'],'secondary':['金'],'desc':'辰月甲木清明后木气渐退，先水养木，金为配合。'},
        5:{'primary':['水'],'secondary':['金','土'],'desc':'巳月甲木夏初木渴，急需水润，金发水源，土培根。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月甲木盛夏火炎木焚，以水为救，金生水源。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月甲木三伏土燥，以水为先，金发水源。'},
        8:{'primary':['水','土'],'secondary':['火'],'desc':'申月甲木秋初木凋，水润土培，仍需火暖。'},
        9:{'primary':['水'],'secondary':['火','土'],'desc':'酉月甲木秋深金旺克木，水通关为急，再火制金暖局。'},
        10:{'primary':['水'],'secondary':['火'],'desc':'戌月甲木秋末土燥，水润为先，火暖为辅。'},
        11:{'primary':['水'],'secondary':['火'],'desc':'亥月甲木长生之地，尚需水火调候，水润火暖。'}},
    1: {0:{'primary':['火'],'secondary':['土'],'desc':'子月乙木寒冬需火暖局，土培根固。'},
        1:{'primary':['火'],'secondary':['土'],'desc':'丑月乙木寒气仍存，以火暖之，土培其根。'},
        2:{'primary':['水'],'secondary':['火'],'desc':'寅月乙木春初尚寒，水润为先，火暖次之。'},
        3:{'primary':['水'],'secondary':['火'],'desc':'卯月乙木建禄当令，木得时气，水润即可。'},
        4:{'primary':['水'],'secondary':['火','金'],'desc':'辰月乙木清明前后，水润木，火暖局，金修枝。'},
        5:{'primary':['水'],'secondary':['火'],'desc':'巳月乙木夏初木干，急需求水，微火不宜过。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月乙木火炎木焚，水为至尊，金发水源。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月乙木三伏土燥木枯，水为急务，金为水源。'},
        8:{'primary':['水'],'secondary':['火'],'desc':'申月乙木初秋水润，微火暖局。'},
        9:{'primary':['水'],'secondary':['火'],'desc':'酉月乙木秋深金锐，水通关，火制金暖木。'},
        10:{'primary':['水'],'secondary':['火'],'desc':'戌月乙木土燥木枯，水润为急，火暖为助。'},
        11:{'primary':['水'],'secondary':['火'],'desc':'亥月乙木长生之月，水过寒则需火温之。'}},
    2: {0:{'primary':['木'],'secondary':['火'],'desc':'子月丙火绝地，以木生火为急，次用火助。'},
        1:{'primary':['木'],'secondary':['火'],'desc':'丑月丙火寒气未尽，木为生火之源，火为自旺。'},
        2:{'primary':['木'],'secondary':['水'],'desc':'寅月丙火长生当令，木生火势，水润不至过炎。'},
        3:{'primary':['木'],'secondary':['水'],'desc':'卯月丙火春火渐旺，木生火明，水调候。'},
        4:{'primary':['水'],'secondary':['木'],'desc':'辰月丙火清明后火势渐增，水为先防过炎，木为辅。'},
        5:{'primary':['水'],'secondary':['金'],'desc':'巳月丙火建禄当令，火炎土燥，以水制火为急。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月丙火羊刃当令，火极旺，非水不能制。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月丙火三伏火炎土燥，水为第一要义。'},
        8:{'primary':['木'],'secondary':['水'],'desc':'申月丙火秋初火退，木生火续焰，水微调。'},
        9:{'primary':['木'],'secondary':['火'],'desc':'酉月丙火秋深火弱，木为生火之源，火助自旺。'},
        10:{'primary':['木'],'secondary':['火'],'desc':'戌月丙火入库中，木生火出库，火助焰。'},
        11:{'primary':['木'],'secondary':['火'],'desc':'亥月丙火绝地需木通关，水生木→木生火。'}},
    3: {0:{'primary':['木'],'secondary':['火'],'desc':'子月丁火灯烛之光，以木续焰，火助其明。'},
        1:{'primary':['木'],'secondary':['火'],'desc':'丑月丁火寒气未消，木为燃料，火助光明。'},
        2:{'primary':['木'],'secondary':['水'],'desc':'寅月丁火初春尚寒，木为源，水微调。'},
        3:{'primary':['木'],'secondary':['水'],'desc':'卯月丁火春火渐明，木续其光，水调候。'},
        4:{'primary':['水'],'secondary':['木'],'desc':'辰月丁火清明后炎势起，水先调候，木次之。'},
        5:{'primary':['水'],'secondary':['金'],'desc':'巳月丁火夏火炎炎，以水制火为先。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月丁火火旺至极，非水不能调候。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月丁火三伏土燥，水为急需。'},
        8:{'primary':['木'],'secondary':['水'],'desc':'申月丁火秋初渐退，木续焰，水微调。'},
        9:{'primary':['木'],'secondary':['火'],'desc':'酉月丁火秋深火微，以木续焰，火助明。'},
        10:{'primary':['木'],'secondary':['火'],'desc':'戌月丁火入库中，木疏土出火，火助。'},
        11:{'primary':['木'],'secondary':['火'],'desc':'亥月丁火绝处逢生，先取木通关，次火助。'}},
    4: {0:{'primary':['火'],'secondary':['土'],'desc':'子月戊土天寒土冻，先取火暖土，土为助。'},
        1:{'primary':['火'],'secondary':['土'],'desc':'丑月戊土寒气未尽，火暖为先，土实为助。'},
        2:{'primary':['火'],'secondary':['水'],'desc':'寅月戊土初春土寒木克，先火暖土，水润。'},
        3:{'primary':['水'],'secondary':['火'],'desc':'卯月戊土春深木旺克土，水润通关，火暖。'},
        4:{'primary':['水'],'secondary':['火'],'desc':'辰月戊土清明后土湿，水为调剂，火烘土。'},
        5:{'primary':['水'],'secondary':['金'],'desc':'巳月戊土建禄当令，土热水干，以水润土为先。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月戊土盛夏土燥，非水不能润。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月戊土三伏土厚且燥，水润为急务。'},
        8:{'primary':['火'],'secondary':['水'],'desc':'申月戊土秋初土寒，火暖土气，水微润。'},
        9:{'primary':['火'],'secondary':['水'],'desc':'酉月戊土秋深金泄土气，火补土气，水微调。'},
        10:{'primary':['火'],'secondary':['水'],'desc':'戌月戊土秋末土燥，火火互补，水微润。'},
        11:{'primary':['火'],'secondary':['水'],'desc':'亥月戊土冬初土湿寒，火暖为急，水调理。'}},
    5: {0:{'primary':['火'],'secondary':['土'],'desc':'子月己土田园冻结，先火暖之，土实助之。'},
        1:{'primary':['火'],'secondary':['土'],'desc':'丑月己土寒气仍在，火暖土，土助实。'},
        2:{'primary':['火'],'secondary':['水'],'desc':'寅月己土木旺土虚，火生土实之，水润。'},
        3:{'primary':['火'],'secondary':['水'],'desc':'卯月己土木盛土虚，火生土，水调候。'},
        4:{'primary':['水'],'secondary':['火'],'desc':'辰月己土清明湿土，水理之，火烘之。'},
        5:{'primary':['水'],'secondary':['金'],'desc':'巳月己土夏土焦裂，水润为先。'},
        6:{'primary':['水'],'secondary':['金'],'desc':'午月己土盛夏土焦，水为至尊。'},
        7:{'primary':['水'],'secondary':['金'],'desc':'未月己土三伏土厚焦，水润为急。'},
        8:{'primary':['火'],'secondary':['水'],'desc':'申月己土秋初土寒，火暖土，水微润。'},
        9:{'primary':['火'],'secondary':['水'],'desc':'酉月己土秋深金泄土，火补土，水微润。'},
        10:{'primary':['火'],'secondary':['水'],'desc':'戌月己土秋末土燥，火暖土，水微调。'},
        11:{'primary':['火'],'secondary':['水'],'desc':'亥月己土冬初土湿，火暖土为急。'}},
    6: {0:{'primary':['火'],'secondary':['木'],'desc':'子月庚金金寒水冷，以火暖金为先，木生火。'},
        1:{'primary':['火'],'secondary':['木'],'desc':'丑月庚金寒气未退，火暖金，木为火源。'},
        2:{'primary':['火'],'secondary':['水','木'],'desc':'寅月庚金绝处逢生，火暖金，水润，木生火。'},
        3:{'primary':['火'],'secondary':['水'],'desc':'卯月庚金胎地，火暖金，水调候。'},
        4:{'primary':['火'],'secondary':['水'],'desc':'辰月庚金养地，火炼金，水调候。'},
        5:{'primary':['水'],'secondary':['火'],'desc':'巳月庚金长生当令，火过旺则水制之。'},
        6:{'primary':['水'],'secondary':['火'],'desc':'午月庚金火旺熔金，水制火护金为先。'},
        7:{'primary':['水'],'secondary':['火'],'desc':'未月庚金三伏火土燥，水润土护金。'},
        8:{'primary':['火'],'secondary':['木'],'desc':'申月庚金建禄当令，金锐气足，火炼成器。'},
        9:{'primary':['火'],'secondary':['水'],'desc':'酉月庚金羊刃当令，金锋最利，火煅之。'},
        10:{'primary':['火'],'secondary':['木'],'desc':'戌月庚金秋末金锐，火煅成器，木为火源。'},
        11:{'primary':['火'],'secondary':['木'],'desc':'亥月庚金金寒水冷，火暖金，木为火源。'}},
    7: {0:{'primary':['火'],'secondary':['木'],'desc':'子月辛金珠玉金寒，火暖为先，木生火。'},
        1:{'primary':['火'],'secondary':['木'],'desc':'丑月辛金寒气尚存，火暖金，木为火源。'},
        2:{'primary':['火'],'secondary':['水'],'desc':'寅月辛金绝处胎养，火暖金，水微润。'},
        3:{'primary':['火'],'secondary':['水'],'desc':'卯月辛金胎地金嫩，火暖之，水润之。'},
        4:{'primary':['火'],'secondary':['水'],'desc':'辰月辛金养地，火煅金，水调候。'},
        5:{'primary':['水'],'secondary':['火'],'desc':'巳月辛金长生当令，火旺则水制之。'},
        6:{'primary':['水'],'secondary':['火'],'desc':'午月辛金火旺金熔，水制火为急。'},
        7:{'primary':['水'],'secondary':['火'],'desc':'未月辛金三伏土燥埋金，水润土出金。'},
        8:{'primary':['火'],'secondary':['木'],'desc':'申月辛金帝旺之地，珠玉已成，火煅成器。'},
        9:{'primary':['火'],'secondary':['水'],'desc':'酉月辛金建禄当令，金纯气足，火煅之。'},
        10:{'primary':['火'],'secondary':['木'],'desc':'戌月辛金秋末金气，火煅成器，木生火。'},
        11:{'primary':['火'],'secondary':['木'],'desc':'亥月辛金金寒水冷，火暖金，木生火。'}},
    8: {0:{'primary':['土'],'secondary':['火'],'desc':'子月壬水羊刃当令，水势滔天，以土制水为先。'},
        1:{'primary':['土'],'secondary':['火'],'desc':'丑月壬水寒气尚在，土制水，火暖局。'},
        2:{'primary':['火'],'secondary':['土','木'],'desc':'寅月壬水初春尚寒，火暖水，土制，木泄。'},
        3:{'primary':['土'],'secondary':['火'],'desc':'卯月壬水春水渐涨，土制水，火暖。'},
        4:{'primary':['土'],'secondary':['火'],'desc':'辰月壬水水库之地，土制水库，火暖。'},
        5:{'primary':['金'],'secondary':['水'],'desc':'巳月壬水绝地水源枯，金生水为先。'},
        6:{'primary':['金'],'secondary':['水'],'desc':'午月壬水胎地，火旺水干，金为水源。'},
        7:{'primary':['金'],'secondary':['水'],'desc':'未月壬水三伏土燥水干，金生水为急。'},
        8:{'primary':['木'],'secondary':['土'],'desc':'申月壬水长生当令，水源充沛，木泄之，土制。'},
        9:{'primary':['木'],'secondary':['土'],'desc':'酉月壬水秋金旺生水，木泄水气，土制。'},
        10:{'primary':['土'],'secondary':['火'],'desc':'戌月壬水秋末水退，土制水库，火暖。'},
        11:{'primary':['木'],'secondary':['火'],'desc':'亥月壬水建禄当令，水势浩大，木泄为先。'}},
    9: {0:{'primary':['土'],'secondary':['火'],'desc':'子月癸水建禄当令，雨露寒水，土制水，火暖。'},
        1:{'primary':['土'],'secondary':['火'],'desc':'丑月癸水寒气深重，土制水，火暖局。'},
        2:{'primary':['火'],'secondary':['土'],'desc':'寅月癸水初春水寒，火暖水为先，土次制。'},
        3:{'primary':['火'],'secondary':['土'],'desc':'卯月癸水春水渐温，火暖之即可。'},
        4:{'primary':['火'],'secondary':['土'],'desc':'辰月癸水水库之地，火暖为先，土制水。'},
        5:{'primary':['金'],'secondary':['水'],'desc':'巳月癸水绝处，金为水源，水助。'},
        6:{'primary':['金'],'secondary':['水'],'desc':'午月癸水火旺水干，金生水为至尊。'},
        7:{'primary':['金'],'secondary':['水'],'desc':'未月癸水三伏土燥水竭，金为源泉。'},
        8:{'primary':['木'],'secondary':['土'],'desc':'申月癸水长生当令，木泄水秀，土制。'},
        9:{'primary':['木'],'secondary':['土'],'desc':'酉月癸水秋金生水旺，木泄水气，土制。'},
        10:{'primary':['土'],'secondary':['火'],'desc':'戌月癸水秋末水退，土制水，火暖。'},
        11:{'primary':['木'],'secondary':['火'],'desc':'亥月癸水羊刃当令，木泄水势，火暖。'}},
}

def _is_leap_solar(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def _days_in_solar_year(y):
    return 366 if _is_leap_solar(y) else 365

def _day_of_year(y, m, d):
    md = [31, 28 + (1 if _is_leap_solar(y) else 0), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return sum(md[:m-1]) + d

def _days_between(y1, m1, d1, y2, m2, d2):
    days = 0
    for y in range(y1, y2):
        days += _days_in_solar_year(y)
    days -= _day_of_year(y1, m1, d1)
    days += _day_of_year(y2, m2, d2)
    return days

def get_solar_term_dates(year):
    terms = []
    for i in range(24):
        d = SOLAR_TERM_BASE[i] + 0.2422 * (year - 1900) - int((year - 1900) / 4)
        if year >= 2000:
            d += 0.03 if i in (0,1,2,3,4,5) else 0
        day = int(d)
        hour = int((d - day) * 24)
        terms.append((SOLAR_TERM_MONTH[i], day, hour))
    return terms

def get_year_ganzhi(year, month, day):
    terms = get_solar_term_dates(year)
    lichun_m, lichun_d, _ = terms[2]
    if month < lichun_m or (month == lichun_m and day < lichun_d):
        year -= 1
    return (year - 4) % 60

def get_month_ganzhi(year, month, day):
    year_gz = get_year_ganzhi(year, month, day)
    year_gan_idx = year_gz % 10
    terms = get_solar_term_dates(year)
    date_val = year * 10000 + month * 100 + day
    jie_zhi = [(0, 1), (2, 2), (4, 3), (6, 4), (8, 5), (10, 6),
               (12, 7), (14, 8), (16, 9), (18, 10), (20, 11), (22, 0)]
    mzhi = None
    for jie_idx, zhi in reversed(jie_zhi):
        jm, jd, _ = terms[jie_idx]
        jv = year * 10000 + jm * 100 + jd
        if date_val >= jv:
            mzhi = zhi
            break
    if mzhi is None:
        mzhi = 1
    yue_start_gan = {0:2, 1:2, 2:4, 3:4, 4:6, 5:6, 6:8, 7:8, 8:0, 9:0}
    base_gan = yue_start_gan[year_gan_idx % 10]
    gan = (base_gan + (mzhi - 2)) % 10
    if gan < 0: gan += 10
    return JIAZI_IDX[(gan, mzhi)]

def get_day_ganzhi(year, month, day):
    days = _days_between(1900, 1, 1, year, month, day)
    return (10 + days) % 60

def get_hour_ganzhi(day_gz_idx, hour):
    day_gan = day_gz_idx % 10
    zhi = ((hour + 1) // 2) % 12
    zi_gan = {0:0, 1:0, 2:2, 3:2, 4:4, 5:4, 6:6, 7:6, 8:8, 9:8}
    gan = (zi_gan[day_gan] + zhi) % 10
    return JIAZI_IDX[(gan, zhi)]

def get_shishen(day_gan_idx, other_gan_idx):
    g, o = day_gan_idx, other_gan_idx
    if GAN_WUXING[g] == GAN_WUXING[o]:
        return "比肩" if GAN_YIN[g] == GAN_YIN[o] else "劫财"
    if (GAN_WUXING[g] + 1) % 5 == GAN_WUXING[o]:
        return "食神" if GAN_YIN[g] == GAN_YIN[o] else "伤官"
    if (GAN_WUXING[g] + 2) % 5 == GAN_WUXING[o]:
        return "偏财" if GAN_YIN[g] == GAN_YIN[o] else "正财"
    if (GAN_WUXING[g] + 3) % 5 == GAN_WUXING[o]:
        return "七杀" if GAN_YIN[g] == GAN_YIN[o] else "正官"
    if (GAN_WUXING[g] + 4) % 5 == GAN_WUXING[o]:
        return "偏印" if GAN_YIN[g] == GAN_YIN[o] else "正印"
    return "未知"

def get_tianyi(gan_idx, zhi_idx):
    rules = {0:[1,7],4:[1,7],6:[1,7],1:[0,8],5:[0,8],2:[11,9],3:[11,9],8:[3,5],9:[3,5],7:[6,2]}
    return zhi_idx in rules.get(gan_idx,[])

def get_taohua(zhi):
    rules = {2:3,6:3,10:3, 8:9,0:9,4:9, 5:6,9:6,1:6, 11:0,3:0,7:0}
    return rules.get(zhi)

def get_yima(zhi):
    rules = {2:8,6:8,10:8, 8:2,0:2,4:2, 5:11,9:11,1:11, 11:5,3:5,7:5}
    return rules.get(zhi)

def get_yangren(gan, zhi):
    if GAN_YIN[gan]==0: return False
    return zhi=={0:3,2:6,4:6,6:9,8:0}.get(gan,-1)

def get_huagai(zhi):
    rules = {2:10,6:10,10:10, 8:4,0:4,4:4, 5:1,9:1,1:1, 11:7,3:7,7:7}
    return rules.get(zhi)

def get_jiangxing(zhi):
    rules = {2:6,6:6,10:6, 8:0,0:0,4:0, 5:9,9:9,1:9, 11:3,3:3,7:3}
    return rules.get(zhi)

def get_wenchang(gan_idx, zhi_idx):
    rules = {0:[5],1:[6],2:[8],4:[8],3:[9],5:[9],6:[11],7:[0],8:[2],9:[3]}
    return zhi_idx in rules.get(gan_idx,[])

def get_kongwang(dgz_idx):
    kong = [(10,11),(8,9),(6,7),(4,5),(2,3),(0,1)]
    return kong[dgz_idx//10]

def get_shi_chen_name(hour):
    zhi_names = ["子时","丑时","寅时","卯时","辰时","巳时","午时","未时","申时","酉时","戌时","亥时"]
    time_ranges = ["23:00-01:00","01:00-03:00","03:00-05:00","05:00-07:00",
                   "07:00-09:00","09:00-11:00","11:00-13:00","13:00-15:00",
                   "15:00-17:00","17:00-19:00","19:00-21:00","21:00-23:00"]
    zhi = ((hour + 1) // 2) % 12
    return zhi_names[zhi], time_ranges[zhi]

def full_bazi(year, month, day, hour, gender='男'):
    ygz = get_year_ganzhi(year, month, day)
    mgz = get_month_ganzhi(year, month, day)
    dgz = get_day_ganzhi(year, month, day)
    hgz = get_hour_ganzhi(dgz, hour)
    sc_name, sc_range = get_shi_chen_name(hour)

    gans = [ygz%10, mgz%10, dgz%10, hgz%10]
    zhis = [ygz%12, mgz%12, dgz%12, hgz%12]
    gz_idxs = [ygz, mgz, dgz, hgz]
    day_gan = dgz % 10
    day_zhi = dgz % 12
    pnames = ['年','月','日','时']

    # 四柱详情
    pillars = []
    for i, (pn, g, z, gz_idx) in enumerate(zip(pnames, gans, zhis, gz_idxs)):
        ss = "日主" if i == 2 else get_shishen(day_gan, g)
        cang = ZHI_CANG_GAN[z]
        cang_detail = []
        for ci, c in enumerate(cang):
            cang_detail.append({
                'gan': TIAN_GAN[c],
                'shishen': get_shishen(day_gan, c),
                'strength': ['本气','中气','余气'][ci] if ci < 3 else '',
                'wuxing': WU_XING[GAN_WUXING[c]],
            })
        pillars.append({
            'name': pn,
            'gan': TIAN_GAN[g], 'zhi': DI_ZHI[z],
            'gan_idx': g, 'zhi_idx': z, 'gz_idx': gz_idx,
            'shishen': ss,
            'gan_wuxing': WU_XING[GAN_WUXING[g]],
            'zhi_wuxing': WU_XING[ZHI_WUXING[z]],
            'nayin': NAYIN[gz_idx % 60],
            'cang_gan': cang_detail,
        })

    # 五行统计
    wuxing_count = {"金":0,"木":0,"水":0,"火":0,"土":0}
    for g, z in zip(gans, zhis):
        wuxing_count[WU_XING[GAN_WUXING[g]]] += 1
        wuxing_count[WU_XING[ZHI_WUXING[z]]] += 1
        for idx, c in enumerate(ZHI_CANG_GAN[z]):
            if idx == 0: continue
            wuxing_count[WU_XING[GAN_WUXING[c]]] += 0.5

    # 旺衰
    day_wx = GAN_WUXING[day_gan]
    month_zhi = zhis[1]; month_wx = ZHI_WUXING[month_zhi]
    de_ling = 3 if month_wx==day_wx else (2 if (month_wx+4)%5==day_wx else 0)
    de_di = sum(1 for z in zhis if ZHI_WUXING[z]==day_wx) + sum(0.3 for z in zhis for c in ZHI_CANG_GAN[z] if GAN_WUXING[c]==day_wx)
    sheng_wx = (day_wx+4)%5
    de_sheng = sum(1 for g in gans if GAN_WUXING[g]==sheng_wx) + sum(0.5 for z in zhis for c in ZHI_CANG_GAN[z] if GAN_WUXING[c]==sheng_wx)
    de_zhu = sum(1 for i,g in enumerate(gans) if GAN_WUXING[g]==day_wx and g!=day_gan) + sum(0.5 for z in zhis for c in ZHI_CANG_GAN[z] if GAN_WUXING[c]==day_wx)
    total = de_ling + de_di + de_sheng + de_zhu
    if total >= 6: level = "身旺"
    elif total >= 4: level = "中和偏旺"
    elif total >= 2.5: level = "中和偏弱"
    elif total >= 1: level = "身弱"
    else: level = "极弱"

    # 格局
    cang = ZHI_CANG_GAN[month_zhi]
    geju_candidates = []
    for c in cang:
        if c in gans and c != day_gan:
            geju_candidates.append({'gan': TIAN_GAN[c], 'shishen': get_shishen(day_gan, c)})
    ss_geju = {'正官':'正官格','七杀':'七杀格','正财':'正财格','偏财':'偏财格',
               '正印':'正印格','偏印':'偏印格','食神':'食神格','伤官':'伤官格'}
    geju = ss_geju.get(geju_candidates[0]['shishen'],'杂气格') if geju_candidates else (
        '建禄格' if ZHI_WUXING[month_zhi]==day_wx and month_zhi in [2,5,8,11] else
        ('阳刃格' if month_zhi in [0,3,6,9] and ZHI_WUXING[month_zhi]==day_wx else '杂气格'))

    # 用神
    yongshen = None
    rule = QIONGTONG_RULES.get(day_gan, {}).get(month_zhi, {})
    if rule:
        yongshen = {'primary': rule['primary'], 'secondary': rule['secondary'], 'desc': rule['desc']}

    # 神煞
    year_gan = ygz % 10; year_zhi = ygz % 12
    shensha_by_pillar = []
    for i, (g, z) in enumerate(zip(gans, zhis)):
        p_ss = []
        if get_tianyi(year_gan, z) or get_tianyi(day_gan, z): p_ss.append('天乙贵人')
        if get_wenchang(day_gan, z) or get_wenchang(year_gan, z): p_ss.append('文昌')
        if get_taohua(day_zhi)==z or get_taohua(year_zhi)==z: p_ss.append('桃花')
        if get_yima(day_zhi)==z: p_ss.append('驿马')
        if get_yangren(day_gan, z): p_ss.append('羊刃')
        if get_huagai(day_zhi)==z: p_ss.append('华盖')
        if get_jiangxing(day_zhi)==z: p_ss.append('将星')
        shensha_by_pillar.append(p_ss if p_ss else ['—'])
    kong = get_kongwang(dgz)
    kongwang = [DI_ZHI[kong[0]], DI_ZHI[kong[1]]]

    # 刑冲合害
    pz = zhis
    rels = []
    for i in range(4):
        for j in range(i+1,4):
            for a,b in [(0,6),(1,7),(2,8),(3,9),(4,10),(5,11)]:
                if sorted([pz[i],pz[j]])==sorted([a,b]):
                    rels.append(f"{pnames[i]}{pnames[j]}六冲: {DI_ZHI[pz[i]]}冲{DI_ZHI[pz[j]]}")
    for i in range(4):
        for j in range(i+1,4):
            for a,b,wx in [(0,1,2),(2,11,0),(3,10,1),(4,9,3),(5,8,4),(6,7,2)]:
                if sorted([pz[i],pz[j]])==sorted([a,b]):
                    rels.append(f"{pnames[i]}{pnames[j]}六合: {DI_ZHI[pz[i]]}合{DI_ZHI[pz[j]]}→{WU_XING[wx]}")
    ZHI_XING = {0:[3],3:[0],2:[5,8],5:[2,8],8:[2,5],1:[7,10],7:[1,10],10:[1,7],4:[4],6:[6],9:[9],11:[11]}
    for i in range(4):
        zi = pz[i]
        if zi in ZHI_XING:
            for j in range(4):
                if i!=j and pz[j] in ZHI_XING[zi]:
                    rels.append(f"{pnames[i]}{pnames[j]}相刑: {DI_ZHI[zi]}刑{DI_ZHI[pz[j]]}")
    for triple, wx in [([8,0,4],4),([11,3,7],0),([2,6,10],1),([5,9,1],3)]:
        found = [(i,pnames[i]) for i in range(4) if pz[i] in triple]
        if len(found)>=2:
            names = ''.join(n for _,n in found)
            rels.append(f"{names}{'三合' if len(found)==3 else '半合'}: →{WU_XING[wx]}局")

    # 大运
    yin_yang_year = GAN_YIN[year_gan]
    forward = (yin_yang_year==1 and gender=='男') or (yin_yang_year==0 and gender!='男')
    terms = get_solar_term_dates(year)
    jie_indices = [0,2,4,6,8,10,12,14,16,18,20,22]
    jie_names = ["小寒","立春","惊蛰","清明","立夏","芒种","小暑","立秋","白露","寒露","立冬","大雪"]
    birth_val = year*10000 + month*100 + day
    days_to_jie = 0; jie_name = ""
    if forward:
        for ji in jie_indices:
            jm,jd,_ = terms[ji]
            jv = year*10000 + jm*100 + jd
            if jv >= birth_val:
                days_to_jie = _days_between(year,month,day, year,jm,jd)
                jie_name = jie_names[jie_indices.index(ji)]
                break
    else:
        for ji in reversed(jie_indices):
            jm,jd,_ = terms[ji]
            jv = year*10000 + jm*100 + jd
            if jv <= birth_val:
                days_to_jie = _days_between(year,jm,jd, year,month,day)
                jie_name = jie_names[jie_indices.index(ji)]
                break
    start_age = max(1, round(days_to_jie/3.0))

    dayun_list = []
    for i in range(8):
        age = start_age + i*10
        new_gz = (mgz + 1 + i) % 60 if forward else (mgz - 1 - i) % 60
        ss = get_shishen(day_gan, new_gz%10)
        dayun_list.append({
            'age_start': age, 'age_end': age+9,
            'gan': TIAN_GAN[new_gz%10], 'zhi': DI_ZHI[new_gz%12],
            'shishen': ss, 'gan_wuxing': WU_XING[GAN_WUXING[new_gz%10]],
            'zhi_wuxing': WU_XING[ZHI_WUXING[new_gz%12]],
        })

    # 当前流年
    now = datetime.now()
    current_year = now.year
    liunian_gz = (current_year - 4) % 60
    liunian_ss = get_shishen(day_gan, liunian_gz % 10)

    return {
        'basic': {
            'solar': f"{year}年{month:02d}月{day:02d}日 {hour:02d}时",
            'gender': gender,
            'shichen': sc_name, 'shichen_range': sc_range,
        },
        'pillars': pillars,
        'day_master': {
            'gan': TIAN_GAN[day_gan], 'wuxing': WU_XING[day_wx],
            'yin_yang': '阳' if GAN_YIN[day_gan] else '阴',
            'nayin': NAYIN[dgz % 60],
        },
        'wuxing_count': wuxing_count,
        'wangshuai': {
            'de_ling': de_ling, 'de_di': round(de_di,1),
            'de_sheng': round(de_sheng,1), 'de_zhu': round(de_zhu,1),
            'total': round(total,1), 'level': level,
        },
        'geju': {
            'name': geju,
            'source': f"月支{DI_ZHI[month_zhi]}藏干透出" if geju_candidates else f"月支{DI_ZHI[month_zhi]}",
            'candidates': [f"{c['gan']}({c['shishen']})" for c in geju_candidates],
        },
        'yongshen': yongshen,
        'shensha': {'by_pillar': shensha_by_pillar, 'kongwang': kongwang},
        'relations': rels if rels else ['四柱无明显刑冲合害'],
        'dayun': {
            'direction': '顺排' if forward else '逆排',
            'start_age': start_age,
            'days_to_jie': days_to_jie,
            'jie_name': jie_name,
            'list': dayun_list,
        },
        'liunian': {
            'year': current_year,
            'gan': TIAN_GAN[liunian_gz % 10],
            'zhi': DI_ZHI[liunian_gz % 12],
            'shishen': liunian_ss,
        },
        'current_dayun': None,
    }


# ============== HTTP 服务器 ==============

class BaziHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            html_path = os.path.join(SCRIPT_DIR, 'index.html')
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            else:
                self.send_error(404, 'index.html not found')
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/pai':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(body)

            try:
                year = int(params.get('year', [0])[0])
                month = int(params.get('month', [0])[0])
                day = int(params.get('day', [0])[0])
                hour = int(params.get('hour', [0])[0])
                gender = params.get('gender', ['男'])[0]

                if not (1900 <= year <= 2100):
                    raise ValueError("年份超出范围(1900-2100)")
                if not (1 <= month <= 12):
                    raise ValueError("月份无效")
                if not (1 <= day <= 31):
                    raise ValueError("日期无效")
                if not (0 <= hour <= 23):
                    raise ValueError("小时无效")

                result = full_bazi(year, month, day, hour, gender)
                # 计算当前大运
                now = datetime.now()
                age = now.year - year
                for dy in result['dayun']['list']:
                    if dy['age_start'] <= age <= dy['age_end']:
                        result['current_dayun'] = dy
                        break

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    server = HTTPServer((HOST, PORT), BaziHandler)
    print(f"\n  八字排盘 Web 服务已启动")
    print(f"  地址: http://{HOST}:{PORT}")
    print(f"  按 Ctrl+C 停止\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止")
        server.server_close()


if __name__ == '__main__':
    main()
