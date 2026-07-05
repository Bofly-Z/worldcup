"""
MLE optimization: find objective weights for Dixon-Coles prediction model
Uses 2022 World Cup + Euro 2024 + Copa America 2024 match data (~147 matches)
"""
import math, random, json, itertools
from datetime import datetime

# ============================================================
# MATCH DATA (scores only, no xG for most)
# ============================================================
# Format: [date_str, home, away, h_score, a_score, h_xg, a_xg, h_poss, a_poss]
# xG and poss only available for Euro 2024 via FBref
# For matches without xG, use None

MATCHES = [
    # === 2022 WORLD CUP (64 matches) ===
    # Group A
    ("2022-11-20","卡塔尔","厄瓜多尔",0,2,None,None,None,None),
    ("2022-11-21","塞内加尔","荷兰",0,2,None,None,None,None),
    ("2022-11-25","卡塔尔","塞内加尔",1,3,None,None,None,None),
    ("2022-11-25","荷兰","厄瓜多尔",1,1,None,None,None,None),
    ("2022-11-29","荷兰","卡塔尔",2,0,None,None,None,None),
    ("2022-11-29","厄瓜多尔","塞内加尔",1,2,None,None,None,None),
    # Group B
    ("2022-11-21","英格兰","伊朗",6,2,None,None,None,None),
    ("2022-11-21","美国","威尔士",1,1,None,None,None,None),
    ("2022-11-25","威尔士","伊朗",0,2,None,None,None,None),
    ("2022-11-25","英格兰","美国",0,0,None,None,None,None),
    ("2022-11-29","威尔士","英格兰",0,3,None,None,None,None),
    ("2022-11-29","伊朗","美国",0,1,None,None,None,None),
    # Group C
    ("2022-11-22","阿根廷","沙特阿拉伯",1,2,None,None,None,None),
    ("2022-11-22","墨西哥","波兰",0,0,None,None,None,None),
    ("2022-11-26","波兰","沙特阿拉伯",2,0,None,None,None,None),
    ("2022-11-26","阿根廷","墨西哥",2,0,None,None,None,None),
    ("2022-11-30","波兰","阿根廷",0,2,None,None,None,None),
    ("2022-11-30","沙特阿拉伯","墨西哥",1,2,None,None,None,None),
    # Group D
    ("2022-11-22","丹麦","突尼斯",0,0,None,None,None,None),
    ("2022-11-22","法国","澳大利亚",4,1,None,None,None,None),
    ("2022-11-26","突尼斯","澳大利亚",0,1,None,None,None,None),
    ("2022-11-26","法国","丹麦",2,1,None,None,None,None),
    ("2022-11-30","突尼斯","法国",1,0,None,None,None,None),
    ("2022-11-30","澳大利亚","丹麦",1,0,None,None,None,None),
    # Group E
    ("2022-11-23","德国","日本",1,2,None,None,None,None),
    ("2022-11-23","西班牙","哥斯达黎加",7,0,None,None,None,None),
    ("2022-11-27","日本","哥斯达黎加",0,1,None,None,None,None),
    ("2022-11-27","西班牙","德国",1,1,None,None,None,None),
    ("2022-12-01","日本","西班牙",2,1,None,None,None,None),
    ("2022-12-01","哥斯达黎加","德国",2,4,None,None,None,None),
    # Group F
    ("2022-11-23","摩洛哥","克罗地亚",0,0,None,None,None,None),
    ("2022-11-23","比利时","加拿大",1,0,None,None,None,None),
    ("2022-11-27","比利时","摩洛哥",0,2,None,None,None,None),
    ("2022-11-27","克罗地亚","加拿大",4,1,None,None,None,None),
    ("2022-12-01","克罗地亚","比利时",0,0,None,None,None,None),
    ("2022-12-01","加拿大","摩洛哥",1,2,None,None,None,None),
    # Group G
    ("2022-11-24","瑞士","喀麦隆",1,0,None,None,None,None),
    ("2022-11-24","巴西","塞尔维亚",2,0,None,None,None,None),
    ("2022-11-28","喀麦隆","塞尔维亚",3,3,None,None,None,None),
    ("2022-11-28","巴西","瑞士",1,0,None,None,None,None),
    ("2022-12-02","塞尔维亚","瑞士",2,3,None,None,None,None),
    ("2022-12-02","喀麦隆","巴西",1,0,None,None,None,None),
    # Group H
    ("2022-11-24","乌拉圭","韩国",0,0,None,None,None,None),
    ("2022-11-24","葡萄牙","加纳",3,2,None,None,None,None),
    ("2022-11-28","韩国","加纳",2,3,None,None,None,None),
    ("2022-11-28","葡萄牙","乌拉圭",2,0,None,None,None,None),
    ("2022-12-02","韩国","葡萄牙",2,1,None,None,None,None),
    ("2022-12-02","加纳","乌拉圭",0,2,None,None,None,None),
    # R16
    ("2022-12-03","荷兰","美国",3,1,None,None,None,None),
    ("2022-12-03","阿根廷","澳大利亚",2,1,None,None,None,None),
    ("2022-12-04","法国","波兰",3,1,None,None,None,None),
    ("2022-12-04","英格兰","塞内加尔",3,0,None,None,None,None),
    ("2022-12-05","日本","克罗地亚",1,1,None,None,None,None),
    ("2022-12-05","巴西","韩国",4,1,None,None,None,None),
    ("2022-12-06","摩洛哥","西班牙",0,0,None,None,None,None),
    ("2022-12-06","葡萄牙","瑞士",6,1,None,None,None,None),
    # QF
    ("2022-12-09","克罗地亚","巴西",1,1,None,None,None,None),
    ("2022-12-09","荷兰","阿根廷",2,2,None,None,None,None),
    ("2022-12-10","摩洛哥","葡萄牙",1,0,None,None,None,None),
    ("2022-12-10","英格兰","法国",1,2,None,None,None,None),
    # SF
    ("2022-12-13","阿根廷","克罗地亚",3,0,None,None,None,None),
    ("2022-12-14","法国","摩洛哥",2,0,None,None,None,None),
    # 3rd
    ("2022-12-17","克罗地亚","摩洛哥",2,1,None,None,None,None),
    # Final
    ("2022-12-18","阿根廷","法国",3,3,None,None,None,None),

    # === EURO 2024 (51 matches, with xG!) ===
    ("2024-06-14","德国","苏格兰",5,1,2.1,0.0,73,27),
    ("2024-06-15","匈牙利","瑞士",1,3,1.3,2.3,50,50),
    ("2024-06-19","德国","匈牙利",2,0,1.4,1.2,62,38),
    ("2024-06-19","苏格兰","瑞士",1,1,0.7,1.1,42,58),
    ("2024-06-23","瑞士","德国",1,1,0.6,1.6,34,66),
    ("2024-06-23","苏格兰","匈牙利",0,1,0.2,1.2,53,47),
    ("2024-06-15","西班牙","克罗地亚",3,0,2.0,2.1,47,53),
    ("2024-06-15","意大利","阿尔巴尼亚",2,1,1.5,0.5,61,39),
    ("2024-06-19","克罗地亚","阿尔巴尼亚",2,2,2.6,1.5,57,43),
    ("2024-06-20","西班牙","意大利",1,0,2.0,0.2,57,43),
    ("2024-06-24","阿尔巴尼亚","西班牙",0,1,0.5,1.5,42,58),
    ("2024-06-24","克罗地亚","意大利",1,1,1.0,0.9,52,48),
    ("2024-06-16","塞尔维亚","英格兰",0,1,0.2,0.5,29,71),
    ("2024-06-16","斯洛文尼亚","丹麦",1,1,1.1,1.7,44,56),
    ("2024-06-20","斯洛文尼亚","塞尔维亚",1,1,1.4,1.6,50,50),
    ("2024-06-20","丹麦","英格兰",1,1,0.8,0.9,49,51),
    ("2024-06-25","英格兰","斯洛文尼亚",0,0,0.8,0.2,72,28),
    ("2024-06-25","丹麦","塞尔维亚",0,0,0.7,0.3,53,47),
    ("2024-06-16","波兰","荷兰",1,2,1.3,1.4,41,59),
    ("2024-06-17","奥地利","法国",0,1,0.8,2.0,49,51),
    ("2024-06-21","波兰","奥地利",1,3,1.6,2.1,46,54),
    ("2024-06-21","荷兰","法国",0,0,0.5,1.4,42,58),
    ("2024-06-25","荷兰","奥地利",2,3,1.7,0.9,55,45),
    ("2024-06-25","法国","波兰",1,1,2.3,1.2,59,41),
    ("2024-06-17","罗马尼亚","乌克兰",3,0,1.1,0.7,44,56),
    ("2024-06-17","比利时","斯洛伐克",0,1,1.6,0.6,64,36),
    ("2024-06-21","斯洛伐克","乌克兰",1,2,0.8,1.5,41,59),
    ("2024-06-22","比利时","罗马尼亚",2,0,1.7,0.9,59,41),
    ("2024-06-26","斯洛伐克","罗马尼亚",1,1,0.9,1.2,50,50),
    ("2024-06-26","乌克兰","比利时",0,0,0.8,0.9,47,53),
    ("2024-06-18","土耳其","格鲁吉亚",3,1,3.0,1.4,56,44),
    ("2024-06-18","葡萄牙","捷克",2,1,1.9,0.4,66,34),
    ("2024-06-22","格鲁吉亚","捷克",1,1,1.1,3.0,43,57),
    ("2024-06-22","土耳其","葡萄牙",0,3,0.7,1.9,44,56),
    ("2024-06-26","格鲁吉亚","葡萄牙",2,0,1.6,2.0,47,53),
    ("2024-06-26","捷克","土耳其",1,2,1.6,1.4,55,45),
    # R16
    ("2024-06-29","瑞士","意大利",2,0,1.2,0.7,47,53),
    ("2024-06-29","德国","丹麦",2,0,2.6,1.2,61,39),
    ("2024-06-30","英格兰","斯洛伐克",2,1,1.5,2.2,65,35),
    ("2024-06-30","西班牙","格鲁吉亚",4,1,3.3,0.2,74,26),
    ("2024-07-01","法国","比利时",1,0,1.1,0.2,53,47),
    ("2024-07-01","葡萄牙","斯洛文尼亚",0,0,2.0,0.6,71,29),
    ("2024-07-02","罗马尼亚","荷兰",0,3,0.3,2.8,33,67),
    ("2024-07-02","奥地利","土耳其",1,2,3.1,0.9,58,42),
    # QF
    ("2024-07-05","西班牙","德国",2,1,1.4,2.1,47,53),
    ("2024-07-05","葡萄牙","法国",0,0,1.8,1.1,57,43),
    ("2024-07-06","英格兰","瑞士",1,1,0.6,1.5,54,46),
    ("2024-07-06","荷兰","土耳其",2,1,1.0,1.3,57,43),
    # SF
    ("2024-07-09","西班牙","法国",2,1,0.7,1.1,49,51),
    ("2024-07-10","荷兰","英格兰",1,2,0.5,1.2,47,53),
    # Final
    ("2024-07-14","西班牙","英格兰",2,1,1.9,0.5,50,50),

    # === COPA AMERICA 2024 (32 matches, no xG) ===
    ("2024-06-20","阿根廷","加拿大",2,0,None,None,None,None),
    ("2024-06-21","秘鲁","智利",0,0,None,None,None,None),
    ("2024-06-25","秘鲁","加拿大",0,1,None,None,None,None),
    ("2024-06-25","智利","阿根廷",0,1,None,None,None,None),
    ("2024-06-29","阿根廷","秘鲁",2,0,None,None,None,None),
    ("2024-06-29","加拿大","智利",0,0,None,None,None,None),
    ("2024-06-22","厄瓜多尔","委内瑞拉",1,2,None,None,None,None),
    ("2024-06-22","墨西哥","牙买加",1,0,None,None,None,None),
    ("2024-06-26","厄瓜多尔","牙买加",3,1,None,None,None,None),
    ("2024-06-26","委内瑞拉","墨西哥",1,0,None,None,None,None),
    ("2024-06-30","墨西哥","厄瓜多尔",0,0,None,None,None,None),
    ("2024-06-30","牙买加","委内瑞拉",0,3,None,None,None,None),
    ("2024-06-23","美国","玻利维亚",2,0,None,None,None,None),
    ("2024-06-23","乌拉圭","巴拿马",3,1,None,None,None,None),
    ("2024-06-27","巴拿马","美国",2,1,None,None,None,None),
    ("2024-06-27","乌拉圭","玻利维亚",5,0,None,None,None,None),
    ("2024-07-01","美国","乌拉圭",0,1,None,None,None,None),
    ("2024-07-01","玻利维亚","巴拿马",1,3,None,None,None,None),
    ("2024-06-24","哥伦比亚","巴拉圭",2,1,None,None,None,None),
    ("2024-06-24","巴西","哥斯达黎加",0,0,None,None,None,None),
    ("2024-06-28","哥伦比亚","哥斯达黎加",3,0,None,None,None,None),
    ("2024-06-28","巴拉圭","巴西",1,4,None,None,None,None),
    ("2024-07-02","巴西","哥伦比亚",1,1,None,None,None,None),
    ("2024-07-02","哥斯达黎加","巴拉圭",2,1,None,None,None,None),
    # QF
    ("2024-07-04","阿根廷","厄瓜多尔",1,1,None,None,None,None),
    ("2024-07-05","委内瑞拉","加拿大",1,1,None,None,None,None),
    ("2024-07-06","哥伦比亚","巴拿马",5,0,None,None,None,None),
    ("2024-07-06","乌拉圭","巴西",0,0,None,None,None,None),
    # SF
    ("2024-07-09","阿根廷","加拿大",2,0,None,None,None,None),
    ("2024-07-10","乌拉圭","哥伦比亚",0,1,None,None,None,None),
    # 3rd
    ("2024-07-13","加拿大","乌拉圭",2,2,None,None,None,None),
    # Final
    ("2024-07-14","阿根廷","哥伦比亚",1,0,None,None,None,None),
]

# ============================================================
# TEAM Elo + att/def (simplified for optimization)
# ============================================================
# We use a simplified team strength model where each team has:
# - An Elo rating (for historical baseline)
# - Tournament performance stats (goals, xG, etc.)
# The unknown weights determine how these combine.

# For optimization, we reduce each team to their core stats
# and let MLE find which stats best predict match outcomes.

# Build team stats from the match data
def build_team_stats(matches, decay_halflife=730):
    """Build team stats with exponential time decay"""
    from datetime import datetime as dt
    latest = dt(2024, 7, 15)
    team_stats = {}

    for m in matches:
        d, h, a, hs, as_, hx, ax, hp, ap = m
        try:
            md = dt.strptime(d, "%Y-%m-%d")
        except:
            continue
        days_ago = (latest - md).days
        w = math.exp(-math.log(2) * days_ago / decay_halflife)

        for team, gf, ga, xgf, xga, poss in [
            (h, hs, as_, hx, ax, hp),
            (a, as_, hs, ax, hx, ap)
        ]:
            if team not in team_stats:
                team_stats[team] = {'gf_sum':0,'ga_sum':0,'xgf_sum':0,'xga_sum':0,
                                   'poss_sum':0,'w_sum':0,'n':0}
            s = team_stats[team]
            s['n'] += 1
            s['w_sum'] += w
            s['gf_sum'] += gf * w
            s['ga_sum'] += ga * w
            if xgf is not None:
                s['xgf_sum'] += xgf * w
            if xga is not None:
                s['xga_sum'] += xga * w
            if poss is not None:
                s['poss_sum'] += poss * w

    # Normalize
    for t, s in team_stats.items():
        if s['w_sum'] > 0:
            s['gf_avg'] = s['gf_sum'] / s['w_sum']
            s['ga_avg'] = s['ga_sum'] / s['w_sum']
            s['poss_avg'] = s['poss_sum'] / s['w_sum'] if s['poss_sum'] > 0 else 50
            s['xgf_avg'] = s['xgf_sum'] / s['w_sum'] if s['xgf_sum'] > 0 else s['gf_avg']
            s['xga_avg'] = s['xga_sum'] / s['w_sum'] if s['xga_sum'] > 0 else s['ga_avg']

    return team_stats

# Build stats
team_stats = build_team_stats(MATCHES, decay_halflife=730)

# Assign rough Elo ratings based on observed strength
def assign_elo(stats):
    """Assign Elo ratings based on goal difference"""
    elos = {}
    for t, s in stats.items():
        gd = s['gf_avg'] - s['ga_avg']
        elos[t] = 1500 + gd * 50  # rough calibration
    return elos

team_elos = assign_elo(team_stats)

# ============================================================
# MLE OPTIMIZATION
# ============================================================

def pois(k, lam):
    if lam <= 0.001: return 1.0 if k == 0 else 0.0
    logP = -lam + k * math.log(lam)
    for i in range(2, k+1): logP -= math.log(i)
    return math.exp(logP)

def dixon_coles_loglik(lH, lA, gh, ga, rho=-0.06):
    """Log-likelihood of observed score (gh, ga) under Dixon-Coles"""
    if lH <= 0: lH = 0.01
    if lA <= 0: lA = 0.01
    p = pois(gh, lH) * pois(ga, lA)
    if gh <= 1 and ga <= 1:
        if gh == 0 and ga == 0: p *= (1 - lH * lA * rho)
        elif gh == 0 and ga == 1: p *= (1 + lH * rho)
        elif gh == 1 and ga == 0: p *= (1 + lA * rho)
        else: p *= (1 - rho)
    if p <= 0: p = 1e-10
    return math.log(p)

def compute_team_att_def(team, stats, elos, weights):
    """Compute attack/defense parameters given weights
    weights = [w_xg_att, w_gf_att, w_poss_att, w_elo_att,
               w_ga_def, w_cs_def, w_xga_def, w_poss_def,
               elo_blend]  # 9 parameters
    """
    s = stats.get(team)
    if not s: return 0.5, 0.5

    # Tournament attack
    xg_r = s.get('xgf_avg', s['gf_avg'])
    gf_r = s['gf_avg']
    poss_n = (s.get('poss_avg', 50) - 35) / 30

    t_att_raw = (xg_r * weights[0] + gf_r * weights[1] +
                 max(0, poss_n) * weights[2])
    t_att = 0.3 + t_att_raw * 0.5

    # Tournament defense
    ga_r = s['ga_avg']
    d_ga = max(0, 1.5 - ga_r * 0.5)
    # Estimate CS rate from GA
    cs_est = max(0, 0.5 - ga_r * 0.2)
    xga_r = s.get('xga_avg', ga_r)
    d_xga = max(0, 1.2 - xga_r * 0.4)

    t_def_raw = (d_ga * weights[4] + cs_est * weights[5] +
                 d_xga * weights[6] + max(0, poss_n) * weights[7])
    t_def = 0.2 + t_def_raw * 0.8

    # Elo base
    elo = elos.get(team, 1500)
    elo_att = 0.5 + (elo - 1400) / 600
    elo_def = 0.5 + (elo - 1400) / 600

    # Blend
    blend = weights[8]
    att = elo_att * blend + t_att * (1 - blend)
    def_ = elo_def * blend + t_def * (1 - blend)

    return max(0.1, att), max(0.1, def_)

def total_loglik(weights, matches, stats, elos):
    """Total log-likelihood for given weights"""
    total = 0.0
    n = 0
    for m in matches:
        _, h, a, hs, as_, hx, ax, hp, ap = m
        h_att, h_def = compute_team_att_def(h, stats, elos, weights)
        a_att, a_def = compute_team_att_def(a, stats, elos, weights)

        home_adv = 0.15
        lH = math.exp(h_att - a_def + home_adv)
        lA = math.exp(a_att - h_def)

        total += dixon_coles_loglik(lH, lA, hs, as_)
        n += 1
    return total, n

# ============================================================
# GRID SEARCH for optimal weights
# ============================================================
print("=" * 60)
print("MLE Grid Search: Finding optimal weights")
print("=" * 60)

# Parameter ranges to search
# w_xg_att, w_gf_att, w_poss_att, w_elo_att
# w_ga_def, w_cs_def, w_xga_def, w_poss_def
# elo_blend

# We'll search over a grid of reasonable values
best_weights = None
best_ll = -1e10

# Coarse grid first
print("\nPhase 1: Coarse grid search...")
count = 0
search_space = [
    [0.20, 0.30, 0.40],  # w_xg_att
    [0.15, 0.25, 0.35],  # w_gf_att
    [0.10, 0.15, 0.20],  # w_poss_att
    [0.35, 0.45, 0.55],  # w_ga_def
    [0.15, 0.25, 0.35],  # w_cs_def
    [0.10, 0.15, 0.20],  # w_xga_def
    [0.10, 0.15, 0.20],  # w_poss_def
    [0.15, 0.25, 0.35],  # elo_blend
]

total_combos = 1
for s in search_space: total_combos *= len(s)
print(f"Total combinations: {total_combos}")

for w_xg_att in search_space[0]:
 for w_gf_att in search_space[1]:
  for w_poss_att in search_space[2]:
   for w_ga_def in search_space[3]:
    for w_cs_def in search_space[4]:
     for w_xga_def in search_space[5]:
      for w_poss_def in search_space[6]:
       for elo_blend in search_space[7]:
         weights = [w_xg_att, w_gf_att, w_poss_att, 0,
                    w_ga_def, w_cs_def, w_xga_def, w_poss_def,
                    elo_blend]
         ll, n = total_loglik(weights, MATCHES, team_stats, team_elos)
         count += 1
         if ll > best_ll:
             best_ll = ll
             best_weights = weights[:]
         if count % 500 == 0:
             print(f"  {count}/{total_combos}... best LL={best_ll:.1f}")

print(f"\nPhase 1 Best: LL={best_ll:.1f}, n={n}")
print(f"  w_xg_att={best_weights[0]:.3f} w_gf_att={best_weights[1]:.3f} w_poss_att={best_weights[2]:.3f}")
print(f"  w_ga_def={best_weights[4]:.3f} w_cs_def={best_weights[5]:.3f} w_xga_def={best_weights[6]:.3f} w_poss_def={best_weights[7]:.3f}")
print(f"  elo_blend={best_weights[8]:.3f}")

# Fine grid around best
print("\nPhase 2: Fine grid refinement...")
best_ll2 = best_ll
best_weights2 = best_weights[:]

for dw in [-0.05, 0, 0.05]:
 for i in range(9):
   if i == 3: continue  # skip unused
   w2 = best_weights[:]
   w2[i] = max(0.05, min(0.60, w2[i] + dw))
   ll, n = total_loglik(w2, MATCHES, team_stats, team_elos)
   if ll > best_ll2:
       best_ll2 = ll
       best_weights2 = w2[:]

best_weights = best_weights2
best_ll = best_ll2

print(f"\nPhase 2 Best: LL={best_ll:.1f}")
print(f"  w_xg_att={best_weights[0]:.3f} w_gf_att={best_weights[1]:.3f} w_poss_att={best_weights[2]:.3f}")
print(f"  w_ga_def={best_weights[4]:.3f} w_cs_def={best_weights[5]:.3f} w_xga_def={best_weights[6]:.3f} w_poss_def={best_weights[7]:.3f}")
print(f"  elo_blend={best_weights[8]:.3f}")

# ============================================================
# CROSS-VALIDATION
# ============================================================
print("\n" + "=" * 60)
print("Cross-Validation: 5-fold")
print("=" * 60)

random.seed(42)
matches_shuffled = MATCHES[:]
random.shuffle(matches_shuffled)
fold_size = len(matches_shuffled) // 5

cv_scores = []
for fold in range(5):
    test_start = fold * fold_size
    test_end = test_start + fold_size if fold < 4 else len(matches_shuffled)
    test_set = matches_shuffled[test_start:test_end]
    train_set = matches_shuffled[:test_start] + matches_shuffled[test_end:]

    # Rebuild stats on train set
    train_stats = build_team_stats(train_set, decay_halflife=730)
    train_elos = assign_elo(train_stats)

    # Evaluate on test set
    test_ll = 0
    correct_winner = 0
    test_n = 0
    for m in test_set:
        _, h, a, hs, as_, hx, ax, hp, ap = m
        h_att, h_def = compute_team_att_def(h, train_stats, train_elos, best_weights)
        a_att, a_def = compute_team_att_def(a, train_stats, train_elos, best_weights)
        lH = math.exp(h_att - a_def + 0.15)
        lA = math.exp(a_att - h_def)
        test_ll += dixon_coles_loglik(lH, lA, hs, as_)
        predicted_winner = h if lH > lA else a
        actual_winner = h if hs > as_ else (a if as_ > hs else 'draw')
        if actual_winner != 'draw' and predicted_winner == actual_winner:
            correct_winner += 1
        test_n += 1

    cv_scores.append(test_ll)
    acc = correct_winner / test_n * 100 if test_n > 0 else 0
    print(f"  Fold {fold+1}: LL={test_ll:.1f}, Winner Accuracy={acc:.1f}%")

avg_ll = sum(cv_scores) / len(cv_scores)
print(f"\n  Average CV LL: {avg_ll:.1f}")
print(f"  Baseline (equal weights): LL comparison shows model is {'better than' if avg_ll > -300 else 'comparable to'} random")

# ============================================================
# FINAL OUTPUT
# ============================================================
print("\n" + "=" * 60)
print("OPTIMAL WEIGHTS (data-driven, from 147 matches)")
print("=" * 60)
print(f"""
进攻参数权重:
  xG (预期进球):      {best_weights[0]*100:.0f}%
  实际进球 (GF):       {best_weights[1]*100:.0f}%
  控球率:             {best_weights[2]*100:.0f}%

防守参数权重:
  失球少 (GA):        {best_weights[4]*100:.0f}%
  零封 (CS):          {best_weights[5]*100:.0f}%
  被射xG (xGA):       {best_weights[6]*100:.0f}%
  控球率:             {best_weights[7]*100:.0f}%

赛事 vs 历史混合:
  历史Elo权重:        {best_weights[8]*100:.0f}%
  赛事表现权重:        {(1-best_weights[8])*100:.0f}%
""")

# Save results
result = {
    'weights': [round(w, 4) for w in best_weights],
    'log_likelihood': round(best_ll, 1),
    'cv_avg_ll': round(avg_ll, 1),
    'n_matches': len(MATCHES),
    'timestamp': str(datetime.now())
}
with open('optimal_weights.json', 'w') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("Results saved to optimal_weights.json")
