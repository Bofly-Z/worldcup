# ============================================================
# 2026 World Cup Prediction — Data Module
# ============================================================
import json, os, time

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# ---- Team comprehensive data ----
TEAMS = {
    "阿根廷":  {"elo":2006,"att":1.13,"def":1.31,"xgFor":9.28,"xgAgainst":2.74,"gf":11,"ga":3,"cs":2,"poss":54,"shotsOT":6.5,"form":[1,1,1],"mom":0.12,"starAvg":86.4,"fifa":3,"group":"J"},
    "西班牙":  {"elo":2002,"att":1.20,"def":1.27,"xgFor":8.83,"xgAgainst":2.10,"gf":9,"ga":1,"cs":4,"poss":61,"shotsOT":7.2,"form":[1,1,0],"mom":0.08,"starAvg":85.2,"fifa":2,"group":"H"},
    "法国":    {"elo":1995,"att":1.08,"def":1.17,"xgFor":7.52,"xgAgainst":2.35,"gf":13,"ga":2,"cs":2,"poss":52,"shotsOT":7.8,"form":[1,1,1],"mom":0.15,"starAvg":88.6,"fifa":1,"group":"I"},
    "巴西":    {"elo":1931,"att":1.19,"def":1.30,"xgFor":7.10,"xgAgainst":3.42,"gf":9,"ga":5,"cs":1,"poss":55,"shotsOT":6.8,"form":[1,0,0],"mom":0.06,"starAvg":86.0,"fifa":6,"group":"C"},
    "英格兰":  {"elo":1927,"att":1.01,"def":1.23,"xgFor":8.47,"xgAgainst":3.10,"gf":12,"ga":5,"cs":2,"poss":58,"shotsOT":6.0,"form":[0,1,1],"mom":0.04,"starAvg":85.8,"fifa":4,"group":"L"},
    "摩洛哥":  {"elo":1912,"att":0.68,"def":1.17,"xgFor":5.85,"xgAgainst":3.55,"gf":7,"ga":3,"cs":2,"poss":44,"shotsOT":4.2,"form":[1,1,0],"mom":0.10,"starAvg":78.8,"fifa":8,"group":"C"},
    "墨西哥":  {"elo":1904,"att":0.74,"def":0.95,"xgFor":5.62,"xgAgainst":3.80,"gf":10,"ga":6,"cs":2,"poss":48,"shotsOT":5.0,"form":[1,1,0],"mom":0.09,"starAvg":77.8,"fifa":14,"group":"A"},
    "哥伦比亚":{"elo":1901,"att":0.92,"def":1.17,"xgFor":6.38,"xgAgainst":2.90,"gf":6,"ga":2,"cs":3,"poss":51,"shotsOT":5.5,"form":[1,1,1],"mom":0.11,"starAvg":80.6,"fifa":12,"group":"K"},
    "葡萄牙":  {"elo":1892,"att":1.08,"def":1.11,"xgFor":7.25,"xgAgainst":3.68,"gf":8,"ga":4,"cs":1,"poss":53,"shotsOT":6.2,"form":[1,0,1],"mom":0.02,"starAvg":82.4,"fifa":5,"group":"K"},
    "比利时":  {"elo":1840,"att":1.04,"def":0.94,"xgFor":6.90,"xgAgainst":4.15,"gf":8,"ga":5,"cs":0,"poss":50,"shotsOT":5.8,"form":[1,0,1],"mom":-0.02,"starAvg":81.6,"fifa":9,"group":"G"},
    "瑞士":    {"elo":1852,"att":0.85,"def":0.86,"xgFor":8.57,"xgAgainst":2.50,"gf":7,"ga":2,"cs":2,"poss":49,"shotsOT":5.2,"form":[1,1,0],"mom":0.05,"starAvg":76.8,"fifa":19,"group":"B"},
    "挪威":    {"elo":1850,"att":0.84,"def":0.71,"xgFor":5.18,"xgAgainst":4.40,"gf":9,"ga":5,"cs":1,"poss":46,"shotsOT":4.8,"form":[0,1,1],"mom":0.03,"starAvg":80.2,"fifa":38,"group":"I"},
    "巴拉圭":  {"elo":1731,"att":0.49,"def":0.88,"xgFor":3.95,"xgAgainst":5.20,"gf":4,"ga":6,"cs":0,"poss":38,"shotsOT":3.0,"form":[0,1,1],"mom":0.08,"starAvg":72.0,"fifa":42,"group":"D"},
    "加拿大":  {"elo":1769,"att":0.62,"def":0.74,"xgFor":5.10,"xgAgainst":3.90,"gf":7,"ga":4,"cs":2,"poss":43,"shotsOT":4.5,"form":[1,1,0],"mom":0.07,"starAvg":75.6,"fifa":30,"group":"B"},
    "埃及":    {"elo":1777,"att":0.50,"def":0.85,"xgFor":4.35,"xgAgainst":4.10,"gf":5,"ga":4,"cs":1,"poss":42,"shotsOT":3.8,"form":[0,1,1],"mom":-0.01,"starAvg":76.4,"fifa":33,"group":"G"},
    "美国":    {"elo":1787,"att":0.72,"def":0.77,"xgFor":6.15,"xgAgainst":3.60,"gf":10,"ga":4,"cs":1,"poss":47,"shotsOT":5.8,"form":[1,1,0],"mom":0.06,"starAvg":77.0,"fifa":16,"group":"D"},
}

# ---- R16 bracket ----
R16_MATCHES = [
    {"id":"R16-1","h":"加拿大","a":"摩洛哥","date":"2026-07-05T01:00+08","venue":"休斯敦 NRG","homeAdv":0.10},
    {"id":"R16-2","h":"巴拉圭","a":"法国","date":"2026-07-05T05:00+08","venue":"费城 林肯金融","homeAdv":0.05},
    {"id":"R16-3","h":"巴西","a":"挪威","date":"2026-07-06T04:00+08","venue":"纽约 大都会人寿","homeAdv":0.05},
    {"id":"R16-4","h":"墨西哥","a":"英格兰","date":"2026-07-06T08:00+08","venue":"墨西哥城 阿兹特克","homeAdv":0.28},
    {"id":"R16-5","h":"葡萄牙","a":"西班牙","date":"2026-07-07T03:00+08","venue":"达拉斯 AT&T","homeAdv":0.05},
    {"id":"R16-6","h":"美国","a":"比利时","date":"2026-07-07T08:00+08","venue":"西雅图 流明","homeAdv":0.18},
    {"id":"R16-7","h":"阿根廷","a":"埃及","date":"2026-07-08T00:00+08","venue":"亚特兰大 梅赛德斯-奔驰","homeAdv":0.05},
    {"id":"R16-8","h":"瑞士","a":"哥伦比亚","date":"2026-07-08T04:00+08","venue":"温哥华 BC Place","homeAdv":0.05},
]

QF_PATHS = [
    {"id":"QF-1","from":["R16-1","R16-2"],"date":"7月9日","venue":"福克斯堡"},
    {"id":"QF-2","from":["R16-3","R16-4"],"date":"7月11日","venue":"迈阿密"},
    {"id":"QF-3","from":["R16-5","R16-6"],"date":"7月10日","venue":"洛杉矶"},
    {"id":"QF-4","from":["R16-7","R16-8"],"date":"7月12日","venue":"堪萨斯城"},
]

SF_PATHS = [
    {"id":"SF-1","from":["QF-1","QF-3"],"date":"7月14日","venue":"达拉斯"},
    {"id":"SF-2","from":["QF-2","QF-4"],"date":"7月15日","venue":"亚特兰大"},
]

# ---- Star players ----
PLAYERS = [
    {"name":"姆巴佩","team":"法国","club":"皇家马德里","age":27,"g":44,"a":5,"cr":8.7,"tg":7,"ta":2,"tr":8.9,"val":200},
    {"name":"梅西","team":"阿根廷","club":"迈阿密国际","age":39,"g":21,"a":12,"cr":8.3,"tg":7,"ta":1,"tr":8.7,"val":25},
    {"name":"哈兰德","team":"挪威","club":"曼城","age":25,"g":34,"a":5,"cr":7.9,"tg":7,"ta":0,"tr":8.3,"val":200},
    {"name":"凯恩","team":"英格兰","club":"拜仁慕尼黑","age":32,"g":36,"a":9,"cr":8.2,"tg":6,"ta":2,"tr":8.1,"val":100},
    {"name":"维尼修斯","team":"巴西","club":"皇家马德里","age":25,"g":20,"a":14,"cr":7.8,"tg":4,"ta":1,"tr":8.0,"val":200},
    {"name":"登贝莱","team":"法国","club":"巴黎圣日耳曼","age":29,"g":18,"a":16,"cr":8.0,"tg":4,"ta":2,"tr":8.4,"val":80},
    {"name":"亚马尔","team":"西班牙","club":"巴塞罗那","age":18,"g":18,"a":21,"cr":8.1,"tg":2,"ta":3,"tr":8.2,"val":180},
    {"name":"贝林厄姆","team":"英格兰","club":"皇家马德里","age":22,"g":22,"a":13,"cr":8.3,"tg":4,"ta":2,"tr":7.9,"val":180},
    {"name":"C罗","team":"葡萄牙","club":"利雅得胜利","age":41,"g":35,"a":11,"cr":8.0,"tg":3,"ta":0,"tr":7.6,"val":12},
    {"name":"萨拉赫","team":"埃及","club":"利物浦","age":34,"g":29,"a":15,"cr":8.4,"tg":2,"ta":2,"tr":7.8,"val":50},
    {"name":"德布劳内","team":"比利时","club":"曼城","age":33,"g":6,"a":18,"cr":8.0,"tg":1,"ta":3,"tr":7.7,"val":45},
    {"name":"佩德里","team":"西班牙","club":"巴塞罗那","age":23,"g":8,"a":14,"cr":7.9,"tg":1,"ta":2,"tr":7.9,"val":120},
    {"name":"戴维","team":"加拿大","club":"里尔","age":26,"g":27,"a":8,"cr":7.8,"tg":3,"ta":1,"tr":7.7,"val":60},
    {"name":"普利西奇","team":"美国","club":"AC米兰","age":27,"g":15,"a":11,"cr":7.7,"tg":2,"ta":3,"tr":7.8,"val":45},
    {"name":"迪亚斯","team":"哥伦比亚","club":"利物浦","age":29,"g":18,"a":8,"cr":7.9,"tg":3,"ta":1,"tr":8.1,"val":85},
    {"name":"劳塔罗","team":"阿根廷","club":"国际米兰","age":28,"g":25,"a":7,"cr":7.7,"tg":3,"ta":2,"tr":7.8,"val":110},
    {"name":"罗德里戈","team":"巴西","club":"皇家马德里","age":25,"g":19,"a":10,"cr":7.7,"tg":2,"ta":2,"tr":7.7,"val":110},
    {"name":"萨卡","team":"英格兰","club":"阿森纳","age":24,"g":16,"a":12,"cr":7.8,"tg":2,"ta":1,"tr":7.6,"val":150},
    {"name":"恩博洛","team":"瑞士","club":"摩纳哥","age":29,"g":16,"a":5,"cr":7.4,"tg":3,"ta":1,"tr":7.5,"val":20},
    {"name":"阿什拉夫","team":"摩洛哥","club":"巴黎圣日耳曼","age":27,"g":5,"a":9,"cr":7.6,"tg":1,"ta":2,"tr":7.6,"val":70},
    {"name":"厄德高","team":"挪威","club":"阿森纳","age":27,"g":11,"a":13,"cr":7.8,"tg":1,"ta":3,"tr":7.5,"val":100},
    {"name":"B费","team":"葡萄牙","club":"曼联","age":31,"g":15,"a":13,"cr":7.7,"tg":2,"ta":2,"tr":7.6,"val":70},
    {"name":"巴洛贡","team":"美国","club":"摩纳哥","age":25,"g":22,"a":6,"cr":7.5,"tg":3,"ta":0,"tr":7.4,"val":40},
    {"name":"阿尔米隆","team":"巴拉圭","club":"纽卡斯尔","age":32,"g":8,"a":6,"cr":7.1,"tg":1,"ta":1,"tr":7.0,"val":15},
    {"name":"马尔穆什","team":"埃及","club":"曼城","age":27,"g":18,"a":10,"cr":7.7,"tg":1,"ta":1,"tr":7.3,"val":60},
]

# ---- Group stage results (all 48 teams for completeness) ----
GROUPS = {
    "A": [
        {"team":"墨西哥","p":9,"gf":7,"ga":2,"gd":5},
        {"team":"南非","p":5,"gf":4,"ga":4,"gd":0},
        {"team":"韩国","p":4,"gf":4,"ga":5,"gd":-1},
        {"team":"捷克","p":0,"gf":2,"ga":6,"gd":-4},
    ],
    "B": [
        {"team":"瑞士","p":7,"gf":6,"ga":2,"gd":4},
        {"team":"加拿大","p":5,"gf":8,"ga":5,"gd":3},
        {"team":"波黑","p":4,"gf":3,"ga":4,"gd":-1},
        {"team":"卡塔尔","p":0,"gf":2,"ga":8,"gd":-6},
    ],
    "C": [
        {"team":"巴西","p":9,"gf":8,"ga":2,"gd":6},
        {"team":"摩洛哥","p":6,"gf":5,"ga":3,"gd":2},
        {"team":"苏格兰","p":3,"gf":3,"ga":6,"gd":-3},
        {"team":"海地","p":0,"gf":1,"ga":6,"gd":-5},
    ],
    "D": [
        {"team":"美国","p":7,"gf":9,"ga":4,"gd":5},
        {"team":"巴拉圭","p":5,"gf":4,"ga":5,"gd":-1},
        {"team":"土耳其","p":4,"gf":5,"ga":5,"gd":0},
        {"team":"澳大利亚","p":0,"gf":2,"ga":6,"gd":-4},
    ],
    "E": [
        {"team":"德国","p":7,"gf":10,"ga":3,"gd":7},
        {"team":"科特迪瓦","p":6,"gf":5,"ga":4,"gd":1},
        {"team":"厄瓜多尔","p":4,"gf":4,"ga":5,"gd":-1},
        {"team":"库拉索","p":0,"gf":1,"ga":8,"gd":-7},
    ],
    "F": [
        {"team":"荷兰","p":9,"gf":10,"ga":2,"gd":8},
        {"team":"日本","p":6,"gf":5,"ga":4,"gd":1},
        {"team":"瑞典","p":3,"gf":4,"ga":6,"gd":-2},
        {"team":"突尼斯","p":0,"gf":2,"ga":9,"gd":-7},
    ],
    "G": [
        {"team":"比利时","p":7,"gf":7,"ga":4,"gd":3},
        {"team":"埃及","p":5,"gf":4,"ga":3,"gd":1},
        {"team":"伊朗","p":4,"gf":3,"ga":4,"gd":-1},
        {"team":"新西兰","p":0,"gf":2,"ga":6,"gd":-4},
    ],
    "H": [
        {"team":"西班牙","p":7,"gf":8,"ga":1,"gd":7},
        {"team":"乌拉圭","p":5,"gf":5,"ga":4,"gd":1},
        {"team":"佛得角","p":4,"gf":3,"ga":5,"gd":-2},
        {"team":"沙特阿拉伯","p":0,"gf":1,"ga":7,"gd":-6},
    ],
    "I": [
        {"team":"法国","p":9,"gf":11,"ga":2,"gd":9},
        {"team":"挪威","p":6,"gf":6,"ga":4,"gd":2},
        {"team":"塞内加尔","p":3,"gf":4,"ga":6,"gd":-2},
        {"team":"伊拉克","p":0,"gf":1,"ga":10,"gd":-9},
    ],
    "J": [
        {"team":"阿根廷","p":9,"gf":9,"ga":1,"gd":8},
        {"team":"奥地利","p":6,"gf":5,"ga":4,"gd":1},
        {"team":"阿尔及利亚","p":3,"gf":3,"ga":5,"gd":-2},
        {"team":"约旦","p":0,"gf":1,"ga":8,"gd":-7},
    ],
    "K": [
        {"team":"葡萄牙","p":7,"gf":6,"ga":3,"gd":3},
        {"team":"哥伦比亚","p":7,"gf":5,"ga":2,"gd":3},
        {"team":"民主刚果","p":3,"gf":3,"ga":5,"gd":-2},
        {"team":"乌兹别克斯坦","p":0,"gf":1,"ga":5,"gd":-4},
    ],
    "L": [
        {"team":"英格兰","p":7,"gf":7,"ga":3,"gd":4},
        {"team":"克罗地亚","p":5,"gf":5,"ga":4,"gd":1},
        {"team":"加纳","p":4,"gf":3,"ga":4,"gd":-1},
        {"team":"巴拿马","p":0,"gf":1,"ga":5,"gd":-4},
    ],
}

# ---- R32 results ----
R32_RESULTS = [
    {"h":"加拿大","a":"南非","hs":1,"as":0,"winner":"加拿大"},
    {"h":"巴西","a":"日本","hs":2,"as":1,"winner":"巴西"},
    {"h":"德国","a":"巴拉圭","hs":1,"as":1,"ps":4,"pa":3,"winner":"巴拉圭"},
    {"h":"荷兰","a":"摩洛哥","hs":1,"as":1,"ps":2,"pa":3,"winner":"摩洛哥"},
    {"h":"挪威","a":"科特迪瓦","hs":2,"as":1,"winner":"挪威"},
    {"h":"法国","a":"瑞典","hs":3,"as":0,"winner":"法国"},
    {"h":"墨西哥","a":"厄瓜多尔","hs":2,"as":0,"winner":"墨西哥"},
    {"h":"英格兰","a":"民主刚果","hs":2,"as":1,"winner":"英格兰"},
    {"h":"比利时","a":"塞内加尔","hs":3,"as":2,"winner":"比利时"},
    {"h":"美国","a":"波黑","hs":2,"as":0,"winner":"美国"},
    {"h":"西班牙","a":"奥地利","hs":3,"as":0,"winner":"西班牙"},
    {"h":"葡萄牙","a":"克罗地亚","hs":2,"as":1,"winner":"葡萄牙"},
    {"h":"瑞士","a":"阿尔及利亚","hs":2,"as":0,"winner":"瑞士"},
    {"h":"澳大利亚","a":"埃及","hs":1,"as":1,"ps":2,"pa":4,"winner":"埃及"},
    {"h":"阿根廷","a":"佛得角","hs":3,"as":2,"winner":"阿根廷"},
    {"h":"哥伦比亚","a":"加纳","hs":1,"as":0,"winner":"哥伦比亚"},
]

# ---- Opponent strength estimation ----
# 预计算非 R16 球队的 Elo 估算（含小组难度调整 + 迭代校准）

def _build_opponent_elo_estimates():
    """迭代估算所有非 R16 球队 Elo，考虑小组难度。

    核心思路：R16 球队在小组拿 9 分 → 小组较弱，对手积分含金量低；
    R16 球队只拿 7 分 → 小组竞争激烈，对手积分含金量高。
    小组难度 = (12 - R16积分) / 3，即 9 分组=1.0，7 分组=1.67
    """
    estimates = {}

    # 先算每组的小组难度系数
    group_difficulty = {}
    for group_name, teams in GROUPS.items():
        r16_pts = 9
        for t in teams:
            if t['team'] in TEAMS:
                r16_pts = t['p']
                break
        group_difficulty[group_name] = (12 - r16_pts) / 3  # 1.0 ~ 1.67

    # 第一轮：用难度系数调整后的积分估算
    for group_name, teams in GROUPS.items():
        diff = group_difficulty[group_name]
        for t in teams:
            if t['team'] not in TEAMS:
                adj_p = t['p'] * diff
                adj_gd = t['gd'] * diff
                estimates[t['team']] = 1580 + 28 * adj_p + 14 * adj_gd

    # 第二轮：迭代一次，用第一轮结果重新算小组平均，再做微调
    for group_name, teams in GROUPS.items():
        group_elos = []
        for t in teams:
            if t['team'] in TEAMS:
                group_elos.append(TEAMS[t['team']]['elo'])
            elif t['team'] in estimates:
                group_elos.append(estimates[t['team']])
        group_avg = sum(group_elos) / len(group_elos) if group_elos else 1700

        for t in teams:
            if t['team'] not in TEAMS:
                # 在强组拿分含金量更高：用该组平均 Elo 相对于全局做微调
                group_bonus = (group_avg - 1700) * 0.15
                estimates[t['team']] += group_bonus

    return estimates


_ELO_ESTIMATES_CACHE = None


def estimate_opponent_elo(team_name):
    """估算任意球队 Elo（R16 球队用真实值，其他用小组难度迭代估算）"""
    global _ELO_ESTIMATES_CACHE
    if team_name in TEAMS:
        return TEAMS[team_name]['elo']
    if _ELO_ESTIMATES_CACHE is None:
        _ELO_ESTIMATES_CACHE = _build_opponent_elo_estimates()
    return _ELO_ESTIMATES_CACHE.get(team_name, 1580)


def get_team_opponents(team_name):
    """找出某队全部 4 个对手（3 小组 + 1 R32）"""
    t = TEAMS.get(team_name)
    if not t:
        return []
    opponents = []
    group_name = t['group']
    if group_name in GROUPS:
        for team in GROUPS[group_name]:
            if team['team'] != team_name:
                opponents.append(team['team'])
    for m in R32_RESULTS:
        if m['h'] == team_name:
            opponents.append(m['a'])
        elif m['a'] == team_name:
            opponents.append(m['h'])
    return opponents


def get_opponent_adjustment(team_name):
    """计算对手强度调整因子（>1 = 对手更强，赛果含金量更高）"""
    opponents = get_team_opponents(team_name)
    if not opponents:
        return 1.0
    # 该队对手平均 Elo
    opp_elos = [estimate_opponent_elo(o) for o in opponents]
    avg_opp_elo = sum(opp_elos) / len(opp_elos)
    # 全局基线：全部 16 队对手的平均 Elo
    all_opp_elos = []
    for t in TEAMS:
        all_opp_elos.extend([estimate_opponent_elo(o) for o in get_team_opponents(t)])
    baseline = sum(all_opp_elos) / len(all_opp_elos) if all_opp_elos else avg_opp_elo
    # 限制调整幅度，防止极端值
    adj = avg_opp_elo / baseline
    return min(1.12, max(0.88, adj))


FLAGS = {
    "阿根廷":"🇦🇷","西班牙":"🇪🇸","法国":"🇫🇷","巴西":"🇧🇷","英格兰":"🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "摩洛哥":"🇲🇦","墨西哥":"🇲🇽","哥伦比亚":"🇨🇴","葡萄牙":"🇵🇹","比利时":"🇧🇪",
    "瑞士":"🇨🇭","挪威":"🇳🇴","巴拉圭":"🇵🇾","加拿大":"🇨🇦","埃及":"🇪🇬","美国":"🇺🇸",
}
FLAGS_HTML = {k: f'<span class="tflag">{v}</span>' for k, v in FLAGS.items()}
for k, v in FLAGS.items():
    FLAGS[k] = v

# ---- Load live results from data.json ----
def load_match_results():
    results = {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for stage in ['R32','R16','QF','SF','FINAL','THIRD']:
            matches = data.get('matches', {}).get(stage, [])
            if isinstance(matches, dict):
                matches = [matches]
            for m in matches:
                if m.get('winner'):
                    results[m['id']] = m
        return results, data.get('lastUpdated', '')
    except:
        return {}, ''

def get_last_update_time():
    _, t = load_match_results()
    return t
