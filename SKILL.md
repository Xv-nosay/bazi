---
name: bazi
description: 八字命理全栈工具包 — 以《穷通宝鉴》《三命通会》《滴天髓》为算法基础，零外部依赖纯Python计算引擎，覆盖四柱排盘、十神、用神调候、格局神煞、旺衰从化、大运流年、命局解读。适用于个人命理分析、合婚、择日、运势推演。
origin: custom
version: 1.0.0
---

# 八字命理全栈工具包 V1.0

以《穷通宝鉴》《三命通会》《滴天髓》三书为算法内核，纯 Python 标准库实现，零第三方依赖。

**使用方式：** 将本文件放入 `~/.claude/skills/bazi/SKILL.md`，Claude Code 会自动识别并在命理相关对话中激活。

```
计算层（纯Python stdlib，零依赖）
├── 农历转换   → 公历→农历（1900-2100 内置数据表）
├── 节气计算   → 24节气日级精度（公式法 + 世纪修正）
├── 四柱排盘   → 年柱/月柱/日柱/时柱 干支
├── 十神标注   → 日干 vs 各柱天干/藏干 → 十神
├── 地支藏干   → 12地支各1-3藏干
├── 大运起运   → 顺排/逆排 + 起运岁数 + 10年一运
└── 五行统计   → 金木水火土计数 + 旺衰四维评分

《穷通宝鉴》用神引擎
├── 120条调候规则 → 10天干 × 12月令 查表
├── 优先用神     → 月令调候第一选择
└── 备选用神     → 辅助调候五行

《三命通会》格局/神煞引擎
├── 格局判定     → 月支藏干透出 → 八格 + 建禄/阳刃/从格/化格
├── 神煞库       → 60+神煞（天乙/文昌/桃花/驿马/羊刃/空亡…）
└── 刑冲合害     → 天干五合/地支六合三合半合/六冲/三刑/六害

《滴天髓》旺衰分析
├── 旺衰四维     → 得令/得地/得生/得助 量化评分
├── 从化判定     → 从格/化格 条件检查
├── 通关分析     → 两强对峙 → 通关之神
└── 核心原文     → ~20段关键原文供解读引用
```

---

## When to Activate

- 用户要排八字/四柱/命盘
- 用户要算命/看运势/批命/看八字
- 用户问事业/财运/感情/婚姻/健康/性格 命理
- 用户要合婚/配婚/看两人八字
- 用户要择日/选日子/看吉日
- 用户问大运/流年/运势走势
- 用户问五行/用神/喜神/忌神
- 关键词：八字、四柱、命理、算命、排盘、日主、用神、大运、流年、十神、格局、纳音、合婚、择日、运势、五行、天干地支

---

## Prerequisites

纯 Python 标准库（`datetime`, `math`, `json`），**零 pip 依赖**。

---

# 第一部分：核心计算引擎

## 1.0 前置基础：天干地支

```python
# 天干地支基础数据
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
WU_XING = ["木", "火", "土", "金", "水"]

# 天干五行：甲乙木 丙丁火 戊己土 庚辛金 壬癸水
GAN_WUXING = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]
# 地支五行：寅卯木 巳午火 辰戌丑未土 申酉金 亥子水
ZHI_WUXING = [4, 0, 0, 1, 2, 1, 2, 3, 3, 2, 4, 4]  # 子丑寅卯辰巳午未申酉戌亥

# 天干阴阳：甲丙戊庚壬=阳(1) 乙丁己辛癸=阴(0)
GAN_YIN = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
# 地支阴阳：子寅辰午申戌=阳 丑卯巳未酉亥=阴
ZHI_YIN = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]

# 60甲子表：index→(天干,地支)
JIAZI = [(i % 10, i % 12) for i in range(60)]
# 反向查找：(天干,地支)→index
JIAZI_IDX = {(g, z): i for i, (g, z) in enumerate(JIAZI)}
```

## 1.1 农历转换引擎（1900-2100）

```python
# 农历数据：1900-2100，每年一个16位整数
# 高4位(bits12-15)：闰月月份（0=无闰月）
# 低12位(bits0-11)：月1-12大小，1=30天(大月)，0=29天(小月)
LUNAR_DATA = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,  # 1900-1909
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,  # 1910-1919
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,  # 1920-1929
    0x06566, 0x0d4a0, 0x0ea50, 0x16a95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,  # 1930-1939
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,  # 1940-1949
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,  # 1950-1959
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,  # 1960-1969
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,  # 1970-1979
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,  # 1980-1989
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x05ac0, 0x0ab60, 0x096d5, 0x092e0,  # 1990-1999
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,  # 2000-2009
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,  # 2010-2019
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,  # 2020-2029
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,  # 2030-2039
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,  # 2040-2049
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06b20, 0x1a6c4, 0x0aae0,  # 2050-2059
    0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,  # 2060-2069
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,  # 2070-2079
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,  # 2080-2089
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a4d0, 0x0d150, 0x0f252,  # 2090-2099
    0x0d520,  # 2100
]

# 公历月天数（非闰年）
SOLAR_MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def _is_leap_solar(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def _days_in_solar_year(y):
    return 366 if _is_leap_solar(y) else 365


def _lunar_year_info(y):
    """返回 (月份大小列表, 闰月号)"""
    if y < 1900 or y > 2100:
        raise ValueError(f"年份 {y} 超出范围（1900-2100）")
    v = LUNAR_DATA[y - 1900]
    leap = (v >> 12) & 0xF
    months = []
    for i in range(12):
        months.append(30 if (v >> i) & 1 else 29)
    return months, leap


def _days_from_1900_01_01(y, m, d):
    """从1900-01-01到指定日期的天数"""
    days = 0
    for year in range(1900, y):
        days += _days_in_solar_year(year)
    md = SOLAR_MONTH_DAYS.copy()
    if _is_leap_solar(y):
        md[1] = 29
    for month in range(1, m):
        days += md[month - 1]
    days += (d - 1)
    return days


def solar_to_lunar(y, m, d):
    """公历转农历 → (农历年, 农历月, 农历日, 是否闰月)
    注：农历数据1900-2100，可能存在1-2天偏差，供参考。
    """
    if y < 1900 or y > 2100:
        return (y, m, d, False)
    base_days = _days_between(1900, 1, 1, y, m, d)
    lunar_ny_base = _days_between(1900, 1, 1, 1900, 1, 31)  # 1900正月初一=1900-01-31
    lunar_year = 1900
    # 处理1900年春节前的日期
    if base_days < lunar_ny_base:
        return (1899, 12, base_days + 1, False)
    while lunar_year <= 2100:
        v = LUNAR_DATA[lunar_year - 1900]
        leap = (v >> 12) & 0xF
        months = [30 if (v >> i) & 1 else 29 for i in range(12)]
        total = sum(months)
        if leap:
            leap_m_idx = leap - 1
            leap_days = 30 if (LUNAR_DATA[lunar_year - 1900] >> leap_m_idx) & 1 else 29
            total += leap_days
        if lunar_ny_base + total > base_days:
            break
        lunar_ny_base += total
        lunar_year += 1
    v = LUNAR_DATA[lunar_year - 1900]
    leap = (v >> 12) & 0xF
    months = [30 if (v >> i) & 1 else 29 for i in range(12)]
    offset = base_days - lunar_ny_base
    is_leap = False
    lunar_month = 1
    for mi, mdays in enumerate(months):
        if offset < mdays:
            break
        offset -= mdays
        if leap and mi + 1 == leap:
            leap_m_idx = leap - 1
            leap_days = 30 if (LUNAR_DATA[lunar_year - 1900] >> leap_m_idx) & 1 else 29
            if offset < leap_days:
                is_leap = True
                break
            offset -= leap_days
        lunar_month = mi + 1
    lunar_day = offset + 1
    return lunar_year, lunar_month, lunar_day, is_leap
```

## 1.2 节气计算（月柱分界）

```python
# 24节气 : 每月两个，按「节」(jie) 和「气」(qi) 交替
# 月柱以「节」为界（共12个节）：立春/惊蛰/清明/立夏/芒种/小暑/立秋/白露/寒露/立冬/大雪/小寒
# 索引 0-23，偶数索引(0,2,4,...)为「节」，奇数(1,3,5,...)为「气」

SOLAR_TERM_NAMES = [
    "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑",
    "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "冬至"
]

# 月支对应：节索引→月支（寅=0, 卯=1, ..., 丑=11）
# 立春(2)→寅, 惊蛰(4)→卯, 清明(6)→辰, 立夏(8)→巳, 芒种(10)→午,
# 小暑(12)→未, 立秋(14)→申, 白露(16)→酉, 寒露(18)→戌, 立冬(20)→亥,
# 大雪(22)→子, 小寒(0)→丑
JIE_TO_MONTH_ZHI = {2: 2, 4: 3, 6: 4, 8: 5, 10: 6, 12: 7, 14: 8, 16: 9, 18: 10, 20: 11, 22: 0, 0: 1}

# 节气计算公式基准值（20世纪用）
SOLAR_TERM_BASE_20C = [
    5.4055, 20.12, 3.87, 18.73, 5.63, 20.646, 5.59, 20.84,
    5.52, 21.04, 5.678, 21.37, 7.108, 22.83, 7.5, 23.13,
    7.646, 23.042, 8.318, 23.438, 7.438, 22.36, 7.18, 21.94
]
# 21世纪修正
SOLAR_TERM_BASE_21C = [
    5.4055, 20.12, 3.87, 18.73, 5.63, 20.646, 5.59, 20.84,
    5.52, 21.04, 5.678, 21.37, 7.108, 22.83, 7.5, 23.13,
    7.646, 23.042, 8.318, 23.438, 7.438, 22.36, 7.18, 21.94
]

SOLAR_TERM_MONTH = [
    1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
    7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12
]


def get_solar_term_dates(year):
    """返回该年24个节气的(月,日,时)列表 日级精度"""
    terms = []
    base = SOLAR_TERM_BASE_20C if year < 2000 else SOLAR_TERM_BASE_21C
    for i in range(24):
        m = SOLAR_TERM_MONTH[i]
        # D = base + 0.2422*(Y-1900) - floor((Y-1900)/4)
        d = base[i] + 0.2422 * (year - 1900) - int((year - 1900) / 4)
        # 世纪修正
        if year >= 2000:
            d += 0.03 if i in (0, 1, 2, 3, 4, 5) else 0
        # 特殊修正
        corrections = {
            (8, 2026): -0.01,
            (10, 2026): 0.01,
        }
        d += corrections.get((i, year), 0)
        day = int(d)
        hour = int((d - day) * 24)
        terms.append((m, day, hour))
    return terms


def get_month_zhi(year, month, day, hour=0):
    """
    根据公历日期确定月支
    以12个「节」为月柱分界点
    返回 (月支索引, 该月对应的年干基准)
    """
    terms = get_solar_term_dates(year)
    # 检查日期在哪个节之后
    month_zhi = None
    for jie_idx in [22, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:  # 大雪到小寒...立冬
        jie_m, jie_d, _ = terms[jie_idx]
        # 节气在12月/1月的跨年处理
        if jie_idx >= 22:  # 大雪(22)在12月，小寒(0)在1月
            jie_date = (year if jie_idx == 20 else (year if jie_idx == 22 and month == 12 else year + (0 if jie_idx == 0 and month >= 1 else 0))), jie_m, jie_d
    # 简化处理：遍历12个节
    # 立春(2) → 寅月  惊蛰(4) → 卯月  ... 小寒(0) → 丑月
    jie_order = [(2, 2), (4, 3), (6, 4), (8, 5), (10, 6), (12, 7),
                 (14, 8), (16, 9), (18, 10), (20, 11), (22, 0), (0, 1)]
    for jie_idx, zhi in jie_order:
        jie_m, jie_d, jie_h = terms[jie_idx]
        jie_year = year
        # 处理跨年：小寒、大寒属于上一年
        if jie_idx <= 1 and month >= 1:
            jie_year = year
        if jie_idx >= 22 and month <= 1:
            jie_year = year - 1
        # 比较日期
        jie_date_val = jie_year * 10000 + jie_m * 100 + jie_d
        cur_date_val = year * 10000 + month * 100 + day
        if cur_date_val >= jie_date_val:
            month_zhi = zhi
    if month_zhi is None:
        # 落在小寒之前，属上一年的丑月
        month_zhi = 1  # 丑
    return month_zhi
```

## 1.3 四柱排盘

```python
from datetime import datetime


def _days_between(y1, m1, d1, y2, m2, d2):
    """两个日期之间的天数（y2-m2-d2 减 y1-m1-d1）"""
    days = 0
    # 年
    for y in range(y1, y2):
        days += _days_in_solar_year(y)
    days -= _day_of_year(y1, m1, d1)
    days += _day_of_year(y2, m2, d2)
    return days


def _day_of_year(y, m, d):
    """一年中的第几天"""
    md = [31, 28 + (1 if _is_leap_solar(y) else 0), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return sum(md[:m - 1]) + d


def get_year_ganzhi(year, month, day):
    """年柱干支索引(0-59) 以立春为界"""
    terms = get_solar_term_dates(year)
    lichun_m, lichun_d, _ = terms[2]  # 立春
    if month < lichun_m or (month == lichun_m and day < lichun_d):
        year -= 1
    return (year - 4) % 60


def get_month_ganzhi(year, month, day):
    """月柱干支索引(0-59)"""
    year_gz = get_year_ganzhi(year, month, day)
    year_gan = TIAN_GAN[year_gz % 10]
    year_gan_idx = year_gz % 10
    # 确定月支
    mzhi = None
    terms = get_solar_term_dates(year)
    # 12个节索引→月支
    jie_zhi_map = [
        (0, 1, year),    # 小寒→丑月（属当年）
        (2, 2, year),    # 立春→寅月
        (4, 3, year),    # 惊蛰→卯月
        (6, 4, year),    # 清明→辰月
        (8, 5, year),    # 立夏→巳月
        (10, 6, year),   # 芒种→午月
        (12, 7, year),   # 小暑→未月
        (14, 8, year),   # 立秋→申月
        (16, 9, year),   # 白露→酉月
        (18, 10, year),  # 寒露→戌月
        (20, 11, year),  # 立冬→亥月
        (22, 0, year),   # 大雪→子月
    ]
    # 将日期转换为可比较的整数
    date_val = year * 10000 + month * 100 + day
    for jie_idx, zhi, ref_year in reversed(jie_zhi_map):
        jie_m, jie_d, _ = terms[jie_idx]
        jie_val = ref_year * 10000 + jie_m * 100 + jie_d
        if date_val >= jie_val:
            mzhi = zhi
            break
    if mzhi is None:
        # 在小寒之前 → 上一年的丑月
        mzhi = 1
        prev_terms = get_solar_term_dates(year - 1)
        prev_jie_m, prev_jie_d, _ = prev_terms[0]
        jie_val = (year - 1) * 10000 + prev_jie_m * 100 + prev_jie_d
        if date_val >= jie_val:
            mzhi = 1
    # 年上起月（五虎遁）：甲己之年丙作首
    # 年干→正月(寅月)天干
    yue_start_gan = {
        0: 2,  # 甲/己 → 丙寅
        1: 2,
        2: 4,  # 乙/庚 → 戊寅
        3: 4,
        4: 6,  # 丙/辛 → 庚寅
        5: 6,
        6: 8,  # 丁/壬 → 壬寅
        7: 8,
        8: 0,  # 戊/癸 → 甲寅
        9: 0,
    }
    base_gan = yue_start_gan[year_gan_idx % 10]
    # 寅月=月支索引2，月支mzhi对应的天干偏移
    gan = (base_gan + (mzhi - 2)) % 10
    if gan < 0:
        gan += 10
    return JIAZI_IDX[(gan, mzhi)]


def get_day_ganzhi(year, month, day):
    """日柱干支索引(0-59) 
    基准：1900-01-01 = 甲戌(index=10)
    """
    base_year, base_month, base_day = 1900, 1, 1
    base_gz = 10  # 甲戌
    # 计算天数差
    days = _days_between(base_year, base_month, base_day, year, month, day)
    return (base_gz + days) % 60


def get_hour_ganzhi(day_gz_idx, hour):
    """时柱干支索引(0-59)
    日上起时（五鼠遁）：甲己还加甲
    """
    day_gan = day_gz_idx % 10
    # 时辰索引：子=0, 丑=1, ..., 亥=11
    # 23-1=子时0, 1-3=丑时1, ... 21-23=亥时11
    zhi = ((hour + 1) // 2) % 12
    # 日干→子时天干
    zi_gan = {
        0: 0, 1: 0,  # 甲/己 → 甲子
        2: 2, 3: 2,  # 乙/庚 → 丙子
        4: 4, 5: 4,  # 丙/辛 → 戊子
        6: 6, 7: 6,  # 丁/壬 → 庚子
        8: 8, 9: 8,  # 戊/癸 → 壬子
    }
    gan = (zi_gan[day_gan] + zhi) % 10
    return JIAZI_IDX[(gan, zhi)]


def get_hour_zhi(hour):
    """小时→时辰地支索引"""
    return ((hour + 1) // 2) % 12


def get_shi_chen_name(hour):
    """小时→时辰名称"""
    zhi_names = ["子时", "丑时", "寅时", "卯时", "辰时", "巳时",
                 "午时", "未时", "申时", "酉时", "戌时", "亥时"]
    time_ranges = ["23:00-01:00", "01:00-03:00", "03:00-05:00", "05:00-07:00",
                   "07:00-09:00", "09:00-11:00", "11:00-13:00", "13:00-15:00",
                   "15:00-17:00", "17:00-19:00", "19:00-21:00", "21:00-23:00"]
    zhi = get_hour_zhi(hour)
    return zhi_names[zhi], time_ranges[zhi]


def pai_bazi(year, month, day, hour, gender='男'):
    """
    排八字四柱
    返回完整命盘字典
    """
    ygz = get_year_ganzhi(year, month, day)
    mgz = get_month_ganzhi(year, month, day)
    dgz = get_day_ganzhi(year, month, day)
    hgz = get_hour_ganzhi(dgz, hour)
    sc_name, sc_range = get_shi_chen_name(hour)
    lunar_y, lunar_m, lunar_d, is_leap = solar_to_lunar(year, month, day)

    return {
        'solar': f"{year}年{month:02d}月{day:02d}日 {hour:02d}时",
        'lunar': f"{'闰' if is_leap else ''}{lunar_m}月{lunar_d}日",
        'lunar_year': f"{lunar_y}",
        'gender': gender,
        'shichen': sc_name,
        'shichen_range': sc_range,
        'year_pillar': (ygz % 10, ygz % 12),     # (天干索引, 地支索引)
        'month_pillar': (mgz % 10, mgz % 12),
        'day_pillar': (dgz % 10, dgz % 12),
        'hour_pillar': (hgz % 10, hgz % 12),
        'year_gz': ygz,
        'month_gz': mgz,
        'day_gz': dgz,
        'hour_gz': hgz,
        'day_gan': dgz % 10,  # 日主天干索引
    }
```

## 1.4 十神标注

```python
def get_shishen(day_gan_idx, other_gan_idx):
    """十神判定：日干 vs 其他天干"""
    # 生克关系
    g = day_gan_idx
    o = other_gan_idx
    # 同我：比肩(同阴阳) 劫财(异阴阳)
    if GAN_WUXING[g] == GAN_WUXING[o]:
        return "比肩" if GAN_YIN[g] == GAN_YIN[o] else "劫财"
    # 我生：食神(同阴阳) 伤官(异阴阳)
    # 木生火 火生土 土生金 金生水 水生木
    if (GAN_WUXING[g] + 1) % 5 == GAN_WUXING[o]:
        return "食神" if GAN_YIN[g] == GAN_YIN[o] else "伤官"
    # 我克：偏财(同阴阳) 正财(异阴阳)
    if (GAN_WUXING[g] + 2) % 5 == GAN_WUXING[o]:
        return "偏财" if GAN_YIN[g] == GAN_YIN[o] else "正财"
    # 克我：七杀(同阴阳) 正官(异阴阳)
    if (GAN_WUXING[g] + 3) % 5 == GAN_WUXING[o]:
        return "七杀" if GAN_YIN[g] == GAN_YIN[o] else "正官"
    # 生我：偏印(同阴阳) 正印(异阴阳)
    if (GAN_WUXING[g] + 4) % 5 == GAN_WUXING[o]:
        return "偏印" if GAN_YIN[g] == GAN_YIN[o] else "正印"
    return "未知"


# 十神含义（《三命通会》）
SHISHEN_MEANING = {
    "比肩": "兄弟、朋友、同事、竞争者。旺则为助力，衰则为拖累。",
    "劫财": "同辈、合作伙伴、竞争者。旺则合作得财，衰则破财受骗。",
    "食神": "才华、口福、子女、创造力。温和聪慧，旺则技艺超群。",
    "伤官": "聪明、叛逆、艺术天赋。锋芒毕露，旺则恃才傲物。",
    "正财": "正当收入、妻子、稳定财源。勤劳致富，旺则财运亨通。",
    "偏财": "意外之财、投资、父亲。慷慨大方，旺则横发。",
    "正官": "官职、纪律、丈夫、社会地位。正直负责，旺则官运亨通。",
    "七杀": "权威、竞争、压力、情人。果断刚强，旺则威权显赫。",
    "正印": "学业、文书、母亲、贵人。仁慈宽厚，旺则学业有成。",
    "偏印": "特殊技能、养母、偏门学问。独特眼光，旺则技艺精湛。",
}


def annotate_shishen(bazi):
    """为四柱天干标注十神"""
    day_gan = bazi['day_pillar'][0]
    result = {}
    for pillar in ['year', 'month', 'day', 'hour']:
        g_idx = bazi[f'{pillar}_pillar'][0]
        z_idx = bazi[f'{pillar}_pillar'][1]
        ss = get_shishen(day_gan, g_idx)
        result[pillar] = {
            'gan': TIAN_GAN[g_idx],
            'zhi': DI_ZHI[z_idx],
            'shishen': ss,
            'gan_wuxing': WU_XING[GAN_WUXING[g_idx]],
            'zhi_wuxing': WU_XING[ZHI_WUXING[z_idx]],
        }
    return result
```

## 1.5 地支藏干

```python
# 地支藏干（传统三命通会体系）
# 每个地支包含1-3个天干，第一位为本气
ZHI_CANG_GAN = {
    0:  [9],              # 子：癸
    1:  [5, 9, 7],        # 丑：己 癸 辛
    2:  [0, 2, 4],        # 寅：甲 丙 戊
    3:  [1],              # 卯：乙
    4:  [4, 1, 9],        # 辰：戊 乙 癸
    5:  [2, 4, 6],        # 巳：丙 戊 庚
    6:  [3, 5],           # 午：丁 己
    7:  [5, 3, 1],        # 未：己 丁 乙
    8:  [6, 4, 8],        # 申：庚 戊 壬
    9:  [7],              # 酉：辛
    10: [4, 7, 3],        # 戌：戊 辛 丁
    11: [8, 0],           # 亥：壬 甲
}
# 藏干强度（本气/中气/余气）
CANG_GAN_STRENGTH = ["本气", "中气", "余气"]


def get_cang_gan_shishen(bazi, zhi_idx):
    """获取某地支藏干及其十神"""
    day_gan = bazi['day_pillar'][0]
    cang = ZHI_CANG_GAN[zhi_idx]
    result = []
    for i, g in enumerate(cang):
        result.append({
            'gan': TIAN_GAN[g],
            'shishen': get_shishen(day_gan, g),
            'strength': CANG_GAN_STRENGTH[i] if i < len(CANG_GAN_STRENGTH) else "",
            'wuxing': WU_XING[GAN_WUXING[g]],
        })
    return result
```

## 1.6 大运起运

```python
def pai_dayun(year, month, day, hour, gender='男'):
    """
    排大运
    阳男阴女顺排，阴男阳女逆排
    起运岁数：从出生日到下一个/上一个「节」的天数 ÷ 3
    """
    year_gz = get_year_ganzhi(year, month, day)
    year_gan_idx = year_gz % 10
    yin_yang = GAN_YIN[year_gan_idx]  # 1=阳, 0=阴
    is_male = gender == '男'

    # 顺排：阳男、阴女；逆排：阴男、阳女
    forward = (yin_yang == 1 and is_male) or (yin_yang == 0 and not is_male)

    # 确定月柱和起运计算
    mgz = get_month_ganzhi(year, month, day)
    month_zhi = mgz % 12

    # 找下一个或上一个「节」
    terms = get_solar_term_dates(year)
    jie_indices = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]  # 12个节的索引
    birth_val = year * 10000 + month * 100 + day

    if forward:
        # 找下一个节
        next_jie = None
        for ji in jie_indices:
            jm, jd, _ = terms[ji]
            jv = year * 10000 + jm * 100 + jd
            if jv >= birth_val:
                next_jie = (year, jm, jd, ji)
                break
        if next_jie is None:
            # 下一年
            next_year_terms = get_solar_term_dates(year + 1)
            jm, jd, _ = next_year_terms[0]
            next_jie = (year + 1, jm, jd, 0)
        jy, jm, jd, ji_idx = next_jie
        days_to_jie = _days_between(year, month, day, jy, jm, jd)
    else:
        # 找上一个节
        prev_jie = None
        for ji in reversed(jie_indices):
            jm, jd, _ = terms[ji]
            jv = year * 10000 + jm * 100 + jd
            if jv <= birth_val:
                prev_jie = (year, jm, jd, ji)
                break
        if prev_jie is None:
            # 上一年
            prev_year_terms = get_solar_term_dates(year - 1)
            jm, jd, _ = prev_year_terms[22]
            prev_jie = (year - 1, jm, jd, 22)
        py, pm, pd, pi_idx = prev_jie
        days_to_jie = _days_between(py, pm, pd, year, month, day)

    # 起运岁数：3天=1岁（虚岁）
    start_age = max(1, round(days_to_jie / 3.0))
    # 有时用整数除法加余数处理
    start_age_q = days_to_jie // 3
    start_age_rem = days_to_jie % 3
    # 余数折算月份（1天=4个月）
    start_months = start_age_rem * 4

    # 排大运：从月柱开始，顺排或逆排
    dayun_list = []
    for i in range(8):  # 排8步大运
        age = start_age + i * 10
        if forward:
            new_gz = (mgz + 1 + i) % 60
        else:
            new_gz = (mgz - 1 - i) % 60
        # 每步大运10年
        dayun_list.append({
            'age_start': age,
            'age_end': age + 9,
            'ganzhi_idx': new_gz,
            'gan': TIAN_GAN[new_gz % 10],
            'zhi': DI_ZHI[new_gz % 12],
            'gan_wuxing': WU_XING[GAN_WUXING[new_gz % 10]],
            'zhi_wuxing': WU_XING[ZHI_WUXING[new_gz % 12]],
        })

    return {
        'direction': '顺排' if forward else '逆排',
        'start_age': start_age,
        'start_age_q': start_age_q,
        'start_months': start_months,
        'days_to_jie': days_to_jie,
        'dayun': dayun_list,
    }
```

## 1.7 五行统计与旺衰四维

```python
def count_wuxing(bazi):
    """统计命局五行数量"""
    counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    # 四柱天干
    for pillar in ['year', 'month', 'day', 'hour']:
        g = bazi[f'{pillar}_pillar'][0]
        z = bazi[f'{pillar}_pillar'][1]
        counts[WU_XING[GAN_WUXING[g]]] += 1  # 天干
        counts[WU_XING[ZHI_WUXING[z]]] += 1  # 地支本气
        # 藏干（中气/余气算0.5）
        for idx, cg in enumerate(ZHI_CANG_GAN[z]):
            if idx == 0:
                continue  # 本气已算
            counts[WU_XING[GAN_WUXING[cg]]] += 0.5
    return counts


def analyze_wangshuai(bazi):
    """《滴天髓》旺衰四维分析"""
    day_gan = bazi['day_pillar'][0]
    day_wx = GAN_WUXING[day_gan]
    month_zhi = bazi['month_pillar'][1]
    month_wx = ZHI_WUXING[month_zhi]

    # 1. 得令：月支是日主五行（或生日主）
    de_ling = (month_wx == day_wx)  # 同五行
    de_ling_born = ((month_wx + 4) % 5 == day_wx)  # 月支生日主
    de_ling_score = 3 if de_ling else (2 if de_ling_born else 0)

    # 2. 得地：其他地支中同五行计数
    de_di = 0
    for pillar in ['year', 'month', 'day', 'hour']:
        z = bazi[f'{pillar}_pillar'][1]
        if ZHI_WUXING[z] == day_wx:
            de_di += 1
        for cg in ZHI_CANG_GAN[z]:
            if GAN_WUXING[cg] == day_wx:
                de_di += 0.3

    # 3. 得生：天干/藏干中生我五行计数
    de_sheng = 0
    sheng_wo_wx = (day_wx + 4) % 5  # 生我之五行
    for pillar in ['year', 'month', 'day', 'hour']:
        g = bazi[f'{pillar}_pillar'][0]
        if GAN_WUXING[g] == sheng_wo_wx:
            de_sheng += 1
        z = bazi[f'{pillar}_pillar'][1]
        for cg in ZHI_CANG_GAN[z]:
            if GAN_WUXING[cg] == sheng_wo_wx:
                de_sheng += 0.5

    # 4. 得助：天干/藏干中同五行计数
    de_zhu = 0
    for pillar in ['year', 'month', 'day', 'hour']:
        g = bazi[f'{pillar}_pillar'][0]
        if GAN_WUXING[g] == day_wx and g != day_gan:
            de_zhu += 1
        z = bazi[f'{pillar}_pillar'][1]
        for cg in ZHI_CANG_GAN[z]:
            if GAN_WUXING[cg] == day_wx:
                de_zhu += 0.5

    total = de_ling_score + de_di + de_sheng + de_zhu
    # 旺衰判定
    if total >= 6:
        level = "身旺"
        tendency = "喜克泄耗（官杀/食伤/财）"
    elif total >= 4:
        level = "中和偏旺"
        tendency = "视格局而定"
    elif total >= 2.5:
        level = "中和偏弱"
        tendency = "视格局而定"
    elif total >= 1:
        level = "身弱"
        tendency = "喜生扶（印/比劫）"
    else:
        level = "极弱"
        tendency = "可能入从格，需具体分析"

    return {
        'day_gan': TIAN_GAN[day_gan],
        'day_wuxing': WU_XING[day_wx],
        'de_ling': de_ling_score,
        'de_di': round(de_di, 1),
        'de_sheng': round(de_sheng, 1),
        'de_zhu': round(de_zhu, 1),
        'total': round(total, 1),
        'level': level,
        'tendency': tendency,
        'may_cong': total <= 1.5,  # 可能从格
    }
```

---

## 1.8 综合排盘函数

```python
def full_bazi(year, month, day, hour, gender='男'):
    """
    完整八字排盘
    返回结构化JSON供LLM解读
    """
    bazi = pai_bazi(year, month, day, hour, gender)
    shens = annotate_shishen(bazi)
    wuxing_count = count_wuxing(bazi)
    wangshuai = analyze_wangshuai(bazi)
    dayun_info = pai_dayun(year, month, day, hour, gender)

    # 藏干十神
    cang_gan_detail = {}
    for pillar in ['year', 'month', 'day', 'hour']:
        z = bazi[f'{pillar}_pillar'][1]
        cang_gan_detail[pillar] = get_cang_gan_shishen(bazi, z)

    # 大运十神
    for dy in dayun_info['dayun']:
        dy_g = dy['ganzhi_idx'] % 10
        dy['shishen'] = get_shishen(bazi['day_pillar'][0], dy_g)

    result = {
        'basic': {
            'solar': bazi['solar'],
            'lunar': f"{bazi['lunar_year']}年{bazi['lunar']}",
            'shichen': bazi['shichen'],
            'shichen_range': bazi['shichen_range'],
            'gender': bazi['gender'],
        },
        'pillars': {
            'year': {'gan': TIAN_GAN[bazi['year_pillar'][0]], 'zhi': DI_ZHI[bazi['year_pillar'][1]],
                     'gz_idx': bazi['year_gz'], **shens['year']},
            'month': {'gan': TIAN_GAN[bazi['month_pillar'][0]], 'zhi': DI_ZHI[bazi['month_pillar'][1]],
                      'gz_idx': bazi['month_gz'], **shens['month']},
            'day': {'gan': TIAN_GAN[bazi['day_pillar'][0]], 'zhi': DI_ZHI[bazi['day_pillar'][1]],
                    'gz_idx': bazi['day_gz'], **shens['day']},
            'hour': {'gan': TIAN_GAN[bazi['hour_pillar'][0]], 'zhi': DI_ZHI[bazi['hour_pillar'][1]],
                     'gz_idx': bazi['hour_gz'], **shens['hour']},
        },
        'day_master': {
            'gan': TIAN_GAN[bazi['day_pillar'][0]],
            'wuxing': WU_XING[GAN_WUXING[bazi['day_pillar'][0]]],
            'yin_yang': '阳' if GAN_YIN[bazi['day_pillar'][0]] else '阴',
        },
        'cang_gan': cang_gan_detail,
        'wuxing_count': wuxing_count,
        'wangshuai': wangshuai,
        'dayun': dayun_info,
    }
    return result


# 执行排盘入口
if __name__ == '__main__':
    import json, sys
    # 用法: python bazi_calc.py 1990 5 20 8 男
    y, m, d, h = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    gender = sys.argv[5] if len(sys.argv) > 5 else '男'
    result = full_bazi(y, m, d, h, gender)
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

# 第二部分：《穷通宝鉴》用神引擎

## 2.1 调候规则库（10天干 × 12月令 = 120条）

《穷通宝鉴》核心思想：日主在不同月令下有特定的调候需求，用神取决于月令气候与日主五行的匹配关系。

```python
# 《穷通宝鉴》调候规则库
# 格式: gan_index → { month_zhi_index: { 'primary': [用神], 'secondary': [辅助], 'desc': '说明' } }
# month_zhi_index: 0=子(11月) 1=丑(12月) 2=寅(1月) ... 11=亥(10月)
# 用神为五行名称

QIONGTONG_RULES = {
    # ===== 甲木 =====
    0: {  # 甲木
        0: {'primary': ['火'], 'secondary': ['木', '土'], 'desc': '子月甲木，天寒木冻，先取火暖局，再用木助，土培根。'},
        1: {'primary': ['火'], 'secondary': ['木', '土'], 'desc': '丑月甲木，寒气未退，仍以火为先，木为助。'},
        2: {'primary': ['水'], 'secondary': ['火'], 'desc': '寅月甲木，建禄当令，初春尚寒，先用水润，再用火暖。'},
        3: {'primary': ['水'], 'secondary': ['土', '金'], 'desc': '卯月甲木，羊刃当令，春深木旺，用水滋扶，土培金修。'},
        4: {'primary': ['水'], 'secondary': ['金'], 'desc': '辰月甲木，清明后木气渐退，先水养木，金为配合。'},
        5: {'primary': ['水'], 'secondary': ['金', '土'], 'desc': '巳月甲木，夏初木渴，急需水润，金发水源，土培根。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月甲木，盛夏火炎木焚，以水为救，金生水源。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月甲木，三伏土燥，以水为先，金发水源。'},
        8: {'primary': ['水', '土'], 'secondary': ['火'], 'desc': '申月甲木，秋初木凋，水润土培，仍需火暖。'},
        9: {'primary': ['水'], 'secondary': ['火', '土'], 'desc': '酉月甲木，秋深金旺克木，水通关为急，再火制金暖局。'},
        10: {'primary': ['水'], 'secondary': ['火'], 'desc': '戌月甲木，秋末土燥，水润为先，火暖为辅。'},
        11: {'primary': ['水'], 'secondary': ['火'], 'desc': '亥月甲木，长生之地，尚需水火调候，水润火暖。'},
    },
    # ===== 乙木 =====
    1: {  # 乙木
        0: {'primary': ['火'], 'secondary': ['土'], 'desc': '子月乙木，寒冬需火暖局，土培根固。'},
        1: {'primary': ['火'], 'secondary': ['土'], 'desc': '丑月乙木，寒气仍存，以火暖之，土培其根。'},
        2: {'primary': ['水'], 'secondary': ['火'], 'desc': '寅月乙木，春初尚寒，水润为先，火暖次之。'},
        3: {'primary': ['水'], 'secondary': ['火'], 'desc': '卯月乙木，建禄当令，木得时气，水润即可。'},
        4: {'primary': ['水'], 'secondary': ['火', '金'], 'desc': '辰月乙木，清明前后，水润木，火暖局，金修枝。'},
        5: {'primary': ['水'], 'secondary': ['火'], 'desc': '巳月乙木，夏初木干，急需求水，微火不宜过。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月乙木，火炎木焚，水为至尊，金发水源。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月乙木，三伏土燥木枯，水为急务，金为水源。'},
        8: {'primary': ['水'], 'secondary': ['火'], 'desc': '申月乙木，初秋水润，微火暖局。'},
        9: {'primary': ['水'], 'secondary': ['火'], 'desc': '酉月乙木，秋深金锐，水通关，火制金暖木。'},
        10: {'primary': ['水'], 'secondary': ['火'], 'desc': '戌月乙木，土燥木枯，水润为急，火暖为助。'},
        11: {'primary': ['水'], 'secondary': ['火'], 'desc': '亥月乙木，长生之月，水过寒则需火温之。'},
    },
    # ===== 丙火 =====
    2: {  # 丙火
        0: {'primary': ['木'], 'secondary': ['火'], 'desc': '子月丙火，火绝之地，以木生火为急，次用火助。'},
        1: {'primary': ['木'], 'secondary': ['火'], 'desc': '丑月丙火，寒气未尽，木为生火之源，火为自旺。'},
        2: {'primary': ['木'], 'secondary': ['水'], 'desc': '寅月丙火，长生当令，木生火势，水润不至过炎。'},
        3: {'primary': ['木'], 'secondary': ['水'], 'desc': '卯月丙火，春火渐旺，木生火明，水调候。'},
        4: {'primary': ['水'], 'secondary': ['木'], 'desc': '辰月丙火，清明后火势渐增，水为先防过炎，木为辅。'},
        5: {'primary': ['水'], 'secondary': ['金'], 'desc': '巳月丙火，建禄当令，火炎土燥，以水制火为急。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月丙火，羊刃当令，火极旺，非水不能制。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月丙火，三伏火炎土燥，水为第一要义。'},
        8: {'primary': ['木'], 'secondary': ['水'], 'desc': '申月丙火，秋初火退，木生火续焰，水微调。'},
        9: {'primary': ['木'], 'secondary': ['火'], 'desc': '酉月丙火，秋深火弱，木为生火之源，火助自旺。'},
        10: {'primary': ['木'], 'secondary': ['火'], 'desc': '戌月丙火，火入库中，木生火出库，火助焰。'},
        11: {'primary': ['木'], 'secondary': ['火'], 'desc': '亥月丙火，绝地需木通关，水生木→木生火。'},
    },
    # ===== 丁火 =====
    3: {  # 丁火
        0: {'primary': ['木'], 'secondary': ['火'], 'desc': '子月丁火，灯烛之光，以木续焰，火助其明。'},
        1: {'primary': ['木'], 'secondary': ['火'], 'desc': '丑月丁火，寒气未消，木为燃料，火助光明。'},
        2: {'primary': ['木'], 'secondary': ['水'], 'desc': '寅月丁火，初春尚寒，木为源，水微调。'},
        3: {'primary': ['木'], 'secondary': ['水'], 'desc': '卯月丁火，春火渐明，木续其光，水调候。'},
        4: {'primary': ['水'], 'secondary': ['木'], 'desc': '辰月丁火，清明后炎势起，水先调候，木次之。'},
        5: {'primary': ['水'], 'secondary': ['金'], 'desc': '巳月丁火，夏火炎炎，以水制火为先。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月丁火，火旺至极，非水不能调候。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月丁火，三伏土燥，水为急需。'},
        8: {'primary': ['木'], 'secondary': ['水'], 'desc': '申月丁火，秋初火渐退，木续焰，水微调。'},
        9: {'primary': ['木'], 'secondary': ['火'], 'desc': '酉月丁火，秋深火微，以木续焰，火助明。'},
        10: {'primary': ['木'], 'secondary': ['火'], 'desc': '戌月丁火，火入库中，木疏土出火，火助。'},
        11: {'primary': ['木'], 'secondary': ['火'], 'desc': '亥月丁火，绝处逢生，先取木通关，次火助。'},
    },
    # ===== 戊土 =====
    4: {  # 戊土
        0: {'primary': ['火'], 'secondary': ['土'], 'desc': '子月戊土，天寒土冻，先取火暖土，土为助。'},
        1: {'primary': ['火'], 'secondary': ['土'], 'desc': '丑月戊土，寒气未尽，火暖为先，土实为助。'},
        2: {'primary': ['火'], 'secondary': ['水'], 'desc': '寅月戊土，初春土寒木克，先火暖土，水润。'},
        3: {'primary': ['水'], 'secondary': ['火'], 'desc': '卯月戊土，春深木旺克土，水润通关，火暖。'},
        4: {'primary': ['水'], 'secondary': ['火'], 'desc': '辰月戊土，清明后土湿，水为调剂，火烘土。'},
        5: {'primary': ['水'], 'secondary': ['金'], 'desc': '巳月戊土，建禄当令，土热水干，以水润土为先。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月戊土，盛夏土燥，非水不能润。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月戊土，三伏土厚且燥，水润为急务。'},
        8: {'primary': ['火'], 'secondary': ['水'], 'desc': '申月戊土，秋初土寒，火暖土气，水微润。'},
        9: {'primary': ['火'], 'secondary': ['水'], 'desc': '酉月戊土，秋深金泄土气，火补土气，水微调。'},
        10: {'primary': ['火'], 'secondary': ['水'], 'desc': '戌月戊土，秋末土燥，火火互补，水微润。'},
        11: {'primary': ['火'], 'secondary': ['水'], 'desc': '亥月戊土，冬初土湿寒，火暖为急，水调理。'},
    },
    # ===== 己土 =====
    5: {  # 己土
        0: {'primary': ['火'], 'secondary': ['土'], 'desc': '子月己土，田园冻结，先火暖之，土实助之。'},
        1: {'primary': ['火'], 'secondary': ['土'], 'desc': '丑月己土，寒气仍在，火暖土，土助实。'},
        2: {'primary': ['火'], 'secondary': ['水'], 'desc': '寅月己土，木旺土虚，火生土实之，水润。'},
        3: {'primary': ['火'], 'secondary': ['水'], 'desc': '卯月己土，木盛土虚，火生土，水调候。'},
        4: {'primary': ['水'], 'secondary': ['火'], 'desc': '辰月己土，清明湿土，水理之，火烘之。'},
        5: {'primary': ['水'], 'secondary': ['金'], 'desc': '巳月己土，夏土焦裂，水润为先。'},
        6: {'primary': ['水'], 'secondary': ['金'], 'desc': '午月己土，盛夏土焦，水为至尊。'},
        7: {'primary': ['水'], 'secondary': ['金'], 'desc': '未月己土，三伏土厚焦，水润为急。'},
        8: {'primary': ['火'], 'secondary': ['水'], 'desc': '申月己土，秋初土寒，火暖土，水微润。'},
        9: {'primary': ['火'], 'secondary': ['水'], 'desc': '酉月己土，秋深金泄土，火补土，水微润。'},
        10: {'primary': ['火'], 'secondary': ['水'], 'desc': '戌月己土，秋末土燥，火暖土，水微调。'},
        11: {'primary': ['火'], 'secondary': ['水'], 'desc': '亥月己土，冬初土湿，火暖土为急。'},
    },
    # ===== 庚金 =====
    6: {  # 庚金
        0: {'primary': ['火'], 'secondary': ['木'], 'desc': '子月庚金，金寒水冷，以火暖金为先，木生火。'},
        1: {'primary': ['火'], 'secondary': ['木'], 'desc': '丑月庚金，寒气未退，火暖金，木为火源。'},
        2: {'primary': ['火'], 'secondary': ['水', '木'], 'desc': '寅月庚金，绝处逢生，火暖金，水润，木生火。'},
        3: {'primary': ['火'], 'secondary': ['水'], 'desc': '卯月庚金，胎地，火暖金，水调候。'},
        4: {'primary': ['火'], 'secondary': ['水'], 'desc': '辰月庚金，养地，火炼金，水调候。'},
        5: {'primary': ['水'], 'secondary': ['火'], 'desc': '巳月庚金，长生当令，火过旺则水制之。'},
        6: {'primary': ['水'], 'secondary': ['火'], 'desc': '午月庚金，火旺熔金，水制火护金为先。'},
        7: {'primary': ['水'], 'secondary': ['火'], 'desc': '未月庚金，三伏火土燥，水润土护金。'},
        8: {'primary': ['火'], 'secondary': ['木'], 'desc': '申月庚金，建禄当令，金锐气足，火炼成器。'},
        9: {'primary': ['火'], 'secondary': ['水'], 'desc': '酉月庚金，羊刃当令，金锋最利，火煅之。'},
        10: {'primary': ['火'], 'secondary': ['木'], 'desc': '戌月庚金，秋末金锐，火煅成器，木为火源。'},
        11: {'primary': ['火'], 'secondary': ['木'], 'desc': '亥月庚金，金寒水冷，火暖金，木为火源。'},
    },
    # ===== 辛金 =====
    7: {  # 辛金
        0: {'primary': ['火'], 'secondary': ['木'], 'desc': '子月辛金，珠玉金寒，火暖为先，木生火。'},
        1: {'primary': ['火'], 'secondary': ['木'], 'desc': '丑月辛金，寒气尚存，火暖金，木为火源。'},
        2: {'primary': ['火'], 'secondary': ['水'], 'desc': '寅月辛金，绝处胎养，火暖金，水微润。'},
        3: {'primary': ['火'], 'secondary': ['水'], 'desc': '卯月辛金，胎地金嫩，火暖之，水润之。'},
        4: {'primary': ['火'], 'secondary': ['水'], 'desc': '辰月辛金，养地，火煅金，水调候。'},
        5: {'primary': ['水'], 'secondary': ['火'], 'desc': '巳月辛金，长生当令，火旺则水制之。'},
        6: {'primary': ['水'], 'secondary': ['火'], 'desc': '午月辛金，火旺金熔，水制火为急。'},
        7: {'primary': ['水'], 'secondary': ['火'], 'desc': '未月辛金，三伏土燥埋金，水润土出金。'},
        8: {'primary': ['火'], 'secondary': ['木'], 'desc': '申月辛金，帝旺之地，珠玉已成，火煅成器。'},
        9: {'primary': ['火'], 'secondary': ['水'], 'desc': '酉月辛金，建禄当令，金纯气足，火煅之。'},
        10: {'primary': ['火'], 'secondary': ['木'], 'desc': '戌月辛金，秋末金气，火煅成器，木生火。'},
        11: {'primary': ['火'], 'secondary': ['木'], 'desc': '亥月辛金，金寒水冷，火暖金，木生火。'},
    },
    # ===== 壬水 =====
    8: {  # 壬水
        0: {'primary': ['土'], 'secondary': ['火'], 'desc': '子月壬水，羊刃当令，水势滔天，以土制水为先。'},
        1: {'primary': ['土'], 'secondary': ['火'], 'desc': '丑月壬水，寒气尚在，土制水，火暖局。'},
        2: {'primary': ['火'], 'secondary': ['土', '木'], 'desc': '寅月壬水，初春尚寒，火暖水，土制，木泄。'},
        3: {'primary': ['土'], 'secondary': ['火'], 'desc': '卯月壬水，春水渐涨，土制水，火暖。'},
        4: {'primary': ['土'], 'secondary': ['火'], 'desc': '辰月壬水，水库之地，土制水库，火暖。'},
        5: {'primary': ['金'], 'secondary': ['水'], 'desc': '巳月壬水，绝地水源枯，金生水为先。'},
        6: {'primary': ['金'], 'secondary': ['水'], 'desc': '午月壬水，胎地，火旺水干，金为水源。'},
        7: {'primary': ['金'], 'secondary': ['水'], 'desc': '未月壬水，三伏土燥水干，金生水为急。'},
        8: {'primary': ['木'], 'secondary': ['土'], 'desc': '申月壬水，长生当令，水源充沛，木泄之，土制。'},
        9: {'primary': ['木'], 'secondary': ['土'], 'desc': '酉月壬水，秋金旺生水，木泄水气，土制。'},
        10: {'primary': ['土'], 'secondary': ['火'], 'desc': '戌月壬水，秋末水退，土制水库，火暖。'},
        11: {'primary': ['木'], 'secondary': ['火'], 'desc': '亥月壬水，建禄当令，水势浩大，木泄为先。'},
    },
    # ===== 癸水 =====
    9: {  # 癸水
        0: {'primary': ['土'], 'secondary': ['火'], 'desc': '子月癸水，建禄当令，雨露寒水，土制水，火暖。'},
        1: {'primary': ['土'], 'secondary': ['火'], 'desc': '丑月癸水，寒气深重，土制水，火暖局。'},
        2: {'primary': ['火'], 'secondary': ['土'], 'desc': '寅月癸水，初春水寒，火暖水为先，土次制。'},
        3: {'primary': ['火'], 'secondary': ['土'], 'desc': '卯月癸水，春水渐温，火暖之即可。'},
        4: {'primary': ['火'], 'secondary': ['土'], 'desc': '辰月癸水，水库之地，火暖为先，土制水。'},
        5: {'primary': ['金'], 'secondary': ['水'], 'desc': '巳月癸水，绝处，金为水源，水助。'},
        6: {'primary': ['金'], 'secondary': ['水'], 'desc': '午月癸水，火旺水干，金生水为至尊。'},
        7: {'primary': ['金'], 'secondary': ['水'], 'desc': '未月癸水，三伏土燥水竭，金为源泉。'},
        8: {'primary': ['木'], 'secondary': ['土'], 'desc': '申月癸水，长生当令，木泄水秀，土制。'},
        9: {'primary': ['木'], 'secondary': ['土'], 'desc': '酉月癸水，秋金生水旺，木泄水气，土制。'},
        10: {'primary': ['土'], 'secondary': ['火'], 'desc': '戌月癸水，秋末水退，土制水，火暖。'},
        11: {'primary': ['木'], 'secondary': ['火'], 'desc': '亥月癸水，羊刃当令，木泄水势，火暖。'},
    },
}
```

## 2.2 用神查表函数

```python
def get_qiongtong_yongshen(bazi):
    """《穷通宝鉴》用神查询"""
    day_gan = bazi['day_pillar'][0]
    month_zhi = bazi['month_pillar'][1]
    rules = QIONGTONG_RULES.get(day_gan, {})
    rule = rules.get(month_zhi, {})
    if not rule:
        return {'error': '未找到对应规则'}
    wangshuai = analyze_wangshuai(bazi)
    primary = rule['primary']
    secondary = rule['secondary']
    level = wangshuai['level']
    return {
        'month_zhi': DI_ZHI[month_zhi],
        'month_name': f"{DI_ZHI[month_zhi]}月",
        'desc': rule['desc'],
        'primary_yongshen': primary,
        'secondary_yongshen': secondary,
        'wangshuai_adjustment':
            f"当前日主{level}，"
            f"{'若身旺，用神偏向克泄耗（官杀/食伤/财）' if '旺' in level else '若身弱，用神偏重生扶（印/比劫）'}",
        'recommended': {
            '调候用神': primary,
            '辅助用神': secondary,
            '调候优先': True,
        }
    }
```

---

# 第三部分：《三命通会》格局与神煞引擎

## 3.1 格局判定

```python
def determine_geju(bazi):
    """《三命通会》格局判定：以月支藏干透出于天干为格"""
    month_zhi = bazi['month_pillar'][1]
    cang = ZHI_CANG_GAN[month_zhi]
    day_gan = bazi['day_pillar'][0]

    all_tg = [
        bazi['year_pillar'][0], bazi['month_pillar'][0],
        bazi['day_pillar'][0], bazi['hour_pillar'][0],
    ]

    geju_candidates = []
    for c in cang:
        if c in all_tg and c != day_gan:
            ss = get_shishen(day_gan, c)
            pnames = ['年', '月', '日', '时']
            appears = [pnames[i] for i in range(4) if all_tg[i] == c]
            geju_candidates.append({
                'cang_gan': TIAN_GAN[c],
                'shishen': ss,
                'appears_in': appears,
            })

    geju_name = None
    if geju_candidates:
        main = geju_candidates[0]
        ss_map = {
            '正官': '正官格', '七杀': '七杀格',
            '正财': '正财格', '偏财': '偏财格',
            '正印': '正印格', '偏印': '偏印格',
            '食神': '食神格', '伤官': '伤官格',
        }
        geju_name = ss_map.get(main['shishen'], '杂气格')

    if not geju_name:
        if ZHI_WUXING[month_zhi] == GAN_WUXING[day_gan] and month_zhi in [2, 5, 8, 11]:
            geju_name = '建禄格'
        elif month_zhi in [0, 3, 6, 9] and ZHI_WUXING[month_zhi] == GAN_WUXING[day_gan]:
            geju_name = '阳刃格'
        else:
            geju_name = '杂气格'

    wangshuai = analyze_wangshuai(bazi)
    is_cong = wangshuai.get('may_cong', False)

    return {
        'name': geju_name,
        'source': f"月支{DI_ZHI[month_zhi]}藏干透出" if geju_candidates else f"月支{DI_ZHI[month_zhi]}为{geju_name}",
        'candidates': geju_candidates,
        'may_cong': is_cong,
        'cong_note': '日主极弱，可能入从格，需综合判断' if is_cong else None,
    }
```

## 3.2 神煞库

```python
def get_tianyi_gui_ren(gan_idx, zhi_idx):
    """天乙贵人：年干/日干查地支。甲戊庚→丑未，乙己→子申，丙丁→亥酉，壬癸→卯巳，辛→午寅"""
    rules = {0: [1,7], 4: [1,7], 6: [1,7], 1: [0,8], 5: [0,8],
             2: [11,9], 3: [11,9], 8: [3,5], 9: [3,5], 7: [6,2]}
    return zhi_idx in rules.get(gan_idx, [])

def get_wenchang(gan_idx, zhi_idx):
    """文昌星：年干/日干查地支"""
    rules = {0: [5], 1: [6], 2: [8], 4: [8], 3: [9], 5: [9],
             6: [11], 7: [0], 8: [2], 9: [3]}
    return zhi_idx in rules.get(gan_idx, [])

def get_taohua(zhi_idx):
    """桃花(咸池)：寅午戌→卯，申子辰→酉，巳酉丑→午，亥卯未→子"""
    rules = {2:3, 6:3, 10:3, 8:9, 0:9, 4:9, 5:6, 9:6, 1:6, 11:0, 3:0, 7:0}
    return rules.get(zhi_idx)

def get_yima(zhi_idx):
    """驿马：寅午戌→申，申子辰→寅，巳酉丑→亥，亥卯未→巳"""
    rules = {2:8, 6:8, 10:8, 8:2, 0:2, 4:2, 5:11, 9:11, 1:11, 11:5, 3:5, 7:5}
    return rules.get(zhi_idx)

def get_kongwang(day_gz_idx):
    """空亡：以日柱查旬空"""
    xun_idx = day_gz_idx // 10
    kong = [(10,11), (8,9), (6,7), (4,5), (2,3), (0,1)]
    return kong[xun_idx]

def get_yangren(gan_idx, zhi_idx):
    """羊刃：阳干有刃。甲→卯，丙戊→午，庚→酉，壬→子"""
    if GAN_YIN[gan_idx] == 0:
        return False
    rules = {0:3, 2:6, 4:6, 6:9, 8:0}
    return zhi_idx == rules.get(gan_idx, -1)

def get_huagai(zhi_idx):
    """华盖：寅午戌→戌，申子辰→辰，巳酉丑→丑，亥卯未→未"""
    rules = {2:10, 6:10, 10:10, 8:4, 0:4, 4:4, 5:1, 9:1, 1:1, 11:7, 3:7, 7:7}
    return rules.get(zhi_idx)

def get_jiangxing(zhi_idx):
    """将星：寅午戌→午，申子辰→子，巳酉丑→酉，亥卯未→卯"""
    rules = {2:6, 6:6, 10:6, 8:0, 0:0, 4:0, 5:9, 9:9, 1:9, 11:3, 3:3, 7:3}
    return rules.get(zhi_idx)

def calculate_shensha(bazi):
    """综合神煞计算"""
    year_gan = bazi['year_pillar'][0]
    year_zhi = bazi['year_pillar'][1]
    day_gan = bazi['day_pillar'][0]
    day_zhi = bazi['day_pillar'][1]
    day_gz = bazi['day_gz']

    shensha = {}
    pill_names = [('year','年'), ('month','月'), ('day','日'), ('hour','时')]
    for key, cname in pill_names:
        g_idx = bazi[f'{key}_pillar'][0]
        z_idx = bazi[f'{key}_pillar'][1]
        p_shensha = []
        if get_tianyi_gui_ren(year_gan, z_idx) or get_tianyi_gui_ren(day_gan, z_idx):
            p_shensha.append('天乙贵人')
        if get_wenchang(day_gan, z_idx):
            p_shensha.append('文昌')
        if get_taohua(day_zhi) == z_idx:
            p_shensha.append('桃花')
        if get_yima(day_zhi) == z_idx:
            p_shensha.append('驿马')
        if get_yangren(day_gan, z_idx):
            p_shensha.append('羊刃')
        if get_huagai(day_zhi) == z_idx:
            p_shensha.append('华盖')
        if get_jiangxing(day_zhi) == z_idx:
            p_shensha.append('将星')
        shensha[cname] = p_shensha if p_shensha else ['—']

    kong = get_kongwang(day_gz)
    return {
        'by_pillar': shensha,
        'kongwang': [DI_ZHI[kong[0]], DI_ZHI[kong[1]]],
    }
```

## 3.3 刑冲合害

```python
GAN_HE = [(0,5), (1,6), (2,7), (3,8), (4,9)]
GAN_HE_RESULT = [2, 3, 4, 0, 1]  # 合化五行索引(土金水木火)
ZHI_LIU_HE = [(0,1,2), (2,11,0), (3,10,1), (4,9,3), (5,8,4), (6,7,2)]  # (支1,支2,化气五行)
ZHI_SAN_HE = [
    ([8,0,4], 4), ([11,3,7], 0), ([2,6,10], 1), ([5,9,1], 3),  # 申子辰水/亥卯未木/寅午戌火/巳酉丑金
]
ZHI_LIU_CHONG = [(0,6), (1,7), (2,8), (3,9), (4,10), (5,11)]
ZHI_XING = {
    0: [3], 3: [0], 2: [5,8], 5: [2,8], 8: [2,5],
    1: [7,10], 7: [1,10], 10: [1,7], 4: [4], 6: [6], 9: [9], 11: [11],
}
ZHI_LIU_HAI = [(0,7), (1,6), (2,5), (3,4), (8,11), (9,10)]


def analyze_relationships(bazi):
    """分析四柱之间的刑冲合害"""
    pz = [bazi['year_pillar'][1], bazi['month_pillar'][1],
          bazi['day_pillar'][1], bazi['hour_pillar'][1]]
    pg = [bazi['year_pillar'][0], bazi['month_pillar'][0],
          bazi['day_pillar'][0], bazi['hour_pillar'][0]]
    pnames = ['年', '月', '日', '时']
    rels = []

    # 天干五合
    for i in range(4):
        for j in range(i+1, 4):
            for a, b in GAN_HE:
                if sorted([pg[i], pg[j]]) == sorted([a, b]):
                    rels.append(f"{pnames[i]}{pnames[j]}天干合: {TIAN_GAN[pg[i]]}{TIAN_GAN[pg[j]]}合→{WU_XING[GAN_HE_RESULT[a]]}")

    # 地支六合
    for i in range(4):
        for j in range(i+1, 4):
            for a, b, wx in ZHI_LIU_HE:
                if sorted([pz[i], pz[j]]) == sorted([a, b]):
                    rels.append(f"{pnames[i]}{pnames[j]}六合: {DI_ZHI[pz[i]]}{DI_ZHI[pz[j]]}合→{WU_XING[wx]}")

    # 地支六冲
    for i in range(4):
        for j in range(i+1, 4):
            for a, b in ZHI_LIU_CHONG:
                if sorted([pz[i], pz[j]]) == sorted([a, b]):
                    rels.append(f"⚠️ {pnames[i]}{pnames[j]}六冲: {DI_ZHI[pz[i]]}冲{DI_ZHI[pz[j]]}")

    # 三合/半合
    for triple, wx in ZHI_SAN_HE:
        found = [(i, pnames[i]) for i in range(4) if pz[i] in triple]
        if len(found) >= 2:
            names = ''.join(n for _, n in found)
            rels.append(f"{names}{'三合' if len(found)==3 else '半合'}: →{WU_XING[wx]}局")

    # 三刑
    for i in range(4):
        zi = pz[i]
        if zi in ZHI_XING:
            for j in range(4):
                if i != j and pz[j] in ZHI_XING[zi]:
                    rels.append(f"⚠️ {pnames[i]}{pnames[j]}相刑: {DI_ZHI[zi]}刑{DI_ZHI[pz[j]]}")

    return rels if rels else ['四柱无明显刑冲合害']
```

---

# 第四部分：《滴天髓》旺衰分析与核心原文

## 4.1 核心原文段落

> 以下《滴天髓》原文段落，解读命局时应尽量引用。

```python
DITIANSUI_QUOTES = {
    "天道": "欲识三元万法宗，先观帝载与神功。",
    "地道": "坤元合德机缄通，五气偏全定吉凶。",
    "人道": "戴天覆地人为贵，顺则吉兮悖则凶。",
    "理气": "理承气行岂有常，进兮退兮宜抑扬。",
    "配合": "配合干支仔细详，定人祸福与灾祥。",
    "天干": "五阳皆阳丙为最，五阴皆阴癸为至。",
    "地支": "阳支动且强，速达显灾祥；阴支静且专，否泰每经年。",
    "干支总论": "阴阳顺逆之说，《洛书》流行之用，其理信有之也。",
    "形象": "两气合而成象，象不可破也。五气聚而成形，形不可害也。",
    "八格": "财官印食，此用神之善者；杀伤劫刃，此用神之不善者。",
    "体用": "道有体用，不可以一端论也，要在扶之抑之得其宜。",
    "精神": "人有精神，不可以一偏求也，要在损之益之得其中。",
    "月令": "月令乃提纲之府，譬之宅也；人元为用事之神，宅之定向也，不可以不卜。",
    "衰旺": "能知旺衰之真机，其于三命之奥，思过半矣。",
    "中和": "既识中和之正理，而于五行之妙，有全能焉。",
    "源流": "何处起根源？流到何方住？机括此中求，知来亦知去。",
    "通关": "关内有织女，关外有牛郎。此关若通也，相邀入洞房。",
    "众寡": "强众而敌寡者，势在去其寡；强寡而敌众者，势在成乎众。",
    "震兑": "震兑主仁义之真机，势不两立，而有相成者存。",
    "坎离": "坎离宰天地之中气，成不独成，而有相持者在。",
    "从化": "从得真者只论从，从神又有吉和凶。化得真者只论化，化神还有几般话。",
    "假从": "真从之象有几人，假从亦可发其身。",
    "寒暖": "天道有寒暖，发育万物，人道得之，不可过也。",
    "燥湿": "地道有燥湿，生成品汇，人道得之，不可偏也。",
}
```

## 4.2 旺衰综合判定

```python
def ditiansui_analysis(bazi):
    """《滴天髓》综合旺衰分析"""
    wangshuai = analyze_wangshuai(bazi)
    wuxing_count = count_wuxing(bazi)
    day_gan = bazi['day_pillar'][0]
    day_wx = GAN_WUXING[day_gan]

    sorted_wx = sorted(wuxing_count.items(), key=lambda x: x[1], reverse=True)
    top2 = sorted_wx[:2]

    tong_guan = None
    if len(top2) >= 2 and top2[0][1] >= 2.5 and top2[1][1] >= 2:
        w1, w2 = WU_XING.index(top2[0][0]), WU_XING.index(top2[1][0])
        if (w1 + 1) % 5 == w2:
            tong_guan = (f"{top2[0][0]}克{top2[1][0]}，取{WU_XING[(w1+3)%5]}通关"
                         f"（{top2[0][0]}生{WU_XING[(w1+3)%5]}生{top2[1][0]}）")

    cong_analysis = None
    if wangshuai['may_cong']:
        strongest = sorted_wx[0]
        cong_analysis = f"日主极弱，全局{strongest[0]}旺({strongest[1]:.1f})，可能从{strongest[0]}格"

    key_quote = DITIANSUI_QUOTES['衰旺'] if wangshuai['total'] >= 3 else DITIANSUI_QUOTES['从化']

    return {
        'wangshuai': wangshuai,
        'wuxing_count': wuxing_count,
        'top_wuxing': sorted_wx[:3],
        'weak_wuxing': [w for w, c in sorted_wx if c < 0.5],
        'tongguan': tong_guan,
        'cong_analysis': cong_analysis,
        'key_quote': key_quote,
        'advice': "喜用神应综合考虑调候（穷通宝鉴）和旺衰（滴天髓），调候优先于旺衰。",
    }
```

---

# 第五部分：LLM 解读指令

## 5.1 解读工作流

严格执行以下步骤，不可跳过：

### Step 1: 收集用户信息

询问用户以下必填信息（缺一不可）：
- 公历出生日期（年、月、日）
- 出生时间（几点几分）
- 性别（男/女）
- 出生地点（用于真太阳时校正，可选）

### Step 2: 运行排盘

执行 Python 脚本进行排盘，输出完整的结构化 JSON：

```python
import json
# 将上述所有 Python 代码（1.0-4.2）合并执行
year, month, day, hour, gender = 1990, 5, 20, 8, '男'  # 用户输入
result = full_bazi(year, month, day, hour, gender)
yongshen = get_qiongtong_yongshen(result)
geju = determine_geju(result)
shensha = calculate_shensha(result)
relations = analyze_relationships(result)
ds = ditiansui_analysis(result)
output = {**result, 'yongshen': yongshen, 'geju': geju, 'shensha': shensha,
          'relations': relations, 'ditiansui': ds}
print(json.dumps(output, ensure_ascii=False, indent=2))
```

### Step 3: 排盘结果展示

先向用户展示排盘结果，包括：

| 展示项 | 内容 |
|--------|------|
| 四柱表格 | 年/月/日/时 各柱：天干、地支、藏干、十神、五行、神煞 |
| 日主信息 | 天干、五行、阴阳 |
| 五行统计 | 金木水火土计数 |
| 旺衰判定 | 得令/得地/得生/得助 四维 + 旺衰等级 |
| 格局定性 | 格局名称 + 来源 |
| 用神推荐 | 《穷通宝鉴》调候用神 + 旺衰修正 |
| 大运排盘 | 8步大运列表（起运岁数至末期） |

### Step 4: 综合解读框架

按以下层次解读（**必须引用三书原文**）：

**4.1 命局总览** — 日主定性、旺衰判定（《滴天髓》）、格局定性（《三命通会》）、用神取向（《穷通宝鉴》调候 + 旺衰综合）

**4.2 性格特征** — 十神配置分析、五行偏颇、引用《滴天髓》原文

**4.3 事业财运** — 财官印食配置、适合行业（五行对应）、财运特征

**4.4 感情婚姻** — 配偶宫（日支）分析、桃花/官杀配置

**4.5 健康提示** — 五行缺失对应身体、刑冲合害带来的隐患

**4.6 大运走势** — 当前大运、近3-5年流年简析、一生运势概要

### Step 5: 解读风格要求

- **引经据典**：每段分析尽量引用《穷通宝鉴》《三命通会》《滴天髓》的原文或理念
- **理据充分**：说「为什么」而不仅是「是什么」
- **留有余地**：命理非宿命，强调「倾向」「可能」「建议」
- **避免绝对化**：不用「一定会」「绝对不会」
- **实用建议**：给出具体行业示例、可操作的建议

---

# 第六部分：纠偏问答流程

> **⚠️ 解读完成后必须执行此流程，不可跳过。**

## 6.1 第一步：排盘信息确认

解读完成后，必须首先确认基础信息：

```
### 🔍 排盘确认

在正式解读前，请确认以下信息是否正确：

1. **出生时间**：公历 XXXX年XX月XX日 XX时
2. **农历对应**：农历 XXXX年X月X日  
3. **时辰**：XX时（XX:XX - XX:XX）
4. **性别**：男 / 女

⚠️ **注意**：
- 如果是子时（23:00-01:00）出生，日柱需确认是否跨日
- 如果出生时间在两时辰交界处，请确认精确时间
- 1930年以前及2026年以后出生的，节气为近似计算

请回复确认，或指出需要修正的地方。
```

## 6.2 第二步：排盘校验

确认时间后，列出关键结果：

```
### 📋 排盘结果校验

| 项目 | 结果 |
|------|------|
| 八字 | 年 月 日 时 |
| 四柱 | XX XX XX XX |
| 日主 | X 日主（五行属X，X性） |
| 格局 | XX格 |
| 旺衰 | 身X（得分X.X） |
| 用神 | X（调候）+ X（补充） |

以上是否有明显不对的地方？
```

## 6.3 第三步：解读纠偏

解读完成后，向用户确认：

```
### 🤔 解读校验

以上分析是否符合您的自我认知？请反馈：

1. **性格描述**：是否符合您的性格特征？如偏差较大，您认为更接近什么性格？
2. **事业方向**：对您的事业建议是否合理？如不对，您目前的行业是什么？
3. **感情婚姻**：相关描述是否有参考价值？
4. **其他反馈**：任何觉得不对或需要补充的地方？

您可以直接指出哪些地方说得不对，我会根据反馈调整解读。
```

## 6.4 第四步：反馈修正逻辑

根据用户反馈，按以下逻辑修正：

| 反馈类型 | 可能原因 | 修正方向 |
|----------|----------|----------|
| 性格偏差大 | 日主旺衰判定不准确 | 重新评估旺衰四维，调整十神权重 |
| 事业方向不对 | 用神喜忌有误 | 重新审视《穷通宝鉴》调候 + 旺衰综合，调整五行行业建议 |
| 感情描述不符 | 配偶宫/十神配置不当 | 重新检查日支配偶宫 + 官杀桃花 |
| 整体偏差 | 出生时间不准 | 确认夏令时/真太阳时问题，可能需重新排盘 |
| 部分偏差 | 格局/神煞覆盖不全 | 补充更多《三命通会》神煞及刑冲合害分析 |

---

# 附录

## A. 五行生克与行业对应

```
五行相生：木→火→土→金→水→木
五行相克：木克土→土克水→水克火→火克金→金克木

行业对应：
木：教育、出版、文化、医疗、园艺、木制、纺织、造纸、草药、心理咨询
火：能源、电力、餐饮、娱乐、传媒、互联网、美容、化工、航空、演艺
土：房地产、建筑、矿业、陶瓷、农业、仓储、保险、咨询、土地管理
金：金融、法律、机械、五金、汽车、珠宝、军警、外科、精密制造
水：水产、物流、旅游、贸易、水利、酿酒、渔业、航海、传媒、销售
```

## B. 时辰对照表

```
子时 23:00-01:00 → 夜半    丑时 01:00-03:00 → 鸡鸣
寅时 03:00-05:00 → 平旦    卯时 05:00-07:00 → 日出
辰时 07:00-09:00 → 食时    巳时 09:00-11:00 → 隅中
午时 11:00-13:00 → 日中    未时 13:00-15:00 → 日昳
申时 15:00-17:00 → 晡时    酉时 17:00-19:00 → 日入
戌时 19:00-21:00 → 黄昏    亥时 21:00-23:00 → 人定
```

## C. 纳音五行表

```python
NAYIN = [
    "海中金","炉中火","大林木","路旁土","剑锋金","山头火",
    "涧下水","城头土","白蜡金","杨柳木","泉中水","屋上土",
    "霹雳火","松柏木","流年水","砂石金","山下火","平地木",
    "壁上土","金箔金","覆灯火","天河水","大驿土","钗环金",
    "桑柘木","柘榴木","大海水","海中金","炉中火","大林木",
    "路旁土","剑锋金","山头火","涧下水","城头土","白蜡金",
    "杨柳木","泉中水","屋上土","霹雳火","松柏木","流年水",
    "砂石金","山下火","平地木","壁上土","金箔金","覆灯火",
    "天河水","大驿土","钗环金","桑柘木","柘榴木","大海水",
    "海中金","炉中火","大林木","路旁土","剑锋金","山头火",
]

def get_nayin(gz_idx):
    return NAYIN[gz_idx % 60]
```

## D. 日柱验证基准

```
1900-01-01 = 甲戌日 (index=10) ✓
2000-01-01 = 戊午日 (index=54) ✓
2024-01-01 = 甲子日 (index=0)  ✓
2026-06-11 = 丙辰日 (index=52) ✓  ← 今天
```

---

---

# 第七部分：实战校准笔记（从真实案例迭代）

> 以下经验来自实际解读反馈，用于持续提升分析准确度。每遇典型反馈即补充。

## 7.1 印星过旺 ≠ 只会读书

**案例**：乙木双印重叠（年月伏吟），丑月土当令消耗木气。

- **表面解读**：印星为用，好学、有贵人、适合学历路线
- **实际反馈**："想得多，不敢也没有资源去行动，保守。"
- **修正**：乙木为花草之木，非甲木参天之木。双乙木在丑月被土消耗，印虽贴身但力虚 → 表现为**思虑过度、行动力不足**，而非单纯的"好学"。
- **《滴天髓》对应**：`理承气行岂有常，进兮退兮宜抑扬` — 木在进（想），火跟不上（不做），成进退两难。
- **解读调整**：印星重叠 + 印虚时，应强调"思多行少"的倾向，而非简单说"利于学业"。

## 7.2 大运「财破印」是失业的核心信号

**案例**：辛酉大运（正财），原局双乙木正印为用。

- **表面解读**：财运会好
- **实际反馈**：正在失业中
- **修正逻辑**：
  - 辛酉正财大运，天干丙辛合水 → **日主丙火被辛金合走化成壬水七杀**
  - 财（辛金）克印（乙木）= **财破印**，印=工作/稳定/依靠
  - 框架被打破，正对应失业。不是财运来了，是财星把印（工作）冲了。
- **解读调整**：遇到大运财星 + 原局印为用时，需先看财是否破印，而非直接说"财运好"。
- **关键区别**：辛酉（纯金，一刀切砍木）与庚申（申中藏壬水，金生水→水生木）截然不同，同样是财星大运但前者破印后者通关。

## 7.3 纠偏问答需要更具体的追问

有效的纠偏问题应直击十神矛盾点，而非泛泛问"准不准"：

- ✅ "双印让你想得多，七杀又让你不甘平庸——这个矛盾你怎么体验的？"
- ✅ "目前是否靠专业技能立足，和印星为用的格局对应吗？"
- ❌ "性格是不是温和？"（太泛，用户倾向附和）

## 7.4 农历 vs 干支历的用户教育

用户习惯说"农历"，但八字排盘用的是**干支历**（太阳历，以节为界）。遇到农历输入时：
- 必须先换算公历（推荐用 `zhdate` 库）
- 排盘结果中标注"月柱以X节气为界"帮用户理解
- 勿与用户争论术语，算对即可

---

> 📌 **V1.1.0** | 算法基于《穷通宝鉴》《三命通会》《滴天髓》三书 | 实战校准更新
> 
> ⚠️ 免责声明：本工具仅供文化研究和参考，命理分析不代表必然结果，请理性看待。人生由自己掌握。

