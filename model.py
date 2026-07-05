# ============================================================
# 2026 World Cup Prediction — Dixon-Coles + Monte Carlo
# ============================================================
import math, random, time
from data import TEAMS, R16_MATCHES, QF_PATHS, SF_PATHS, load_match_results

# ---- Poisson PMF ----
def pois(k, lam):
    if lam <= 0.001:
        return 1.0 if k == 0 else 0.0
    logP = -lam + k * math.log(lam)
    for i in range(2, k + 1):
        logP -= math.log(i)
    return math.exp(logP)

# ---- Dixon-Coles match probability ----
def dixon_coles(lH, lA, rho=-0.06):
    maxG = 9
    pH = pD = pA = 0.0
    joint = [[0.0] * (maxG + 1) for _ in range(maxG + 1)]
    for i in range(maxG + 1):
        for j in range(maxG + 1):
            p = pois(i, lH) * pois(j, lA)
            if i <= 1 and j <= 1:
                if i == 0 and j == 0:
                    p *= (1 - lH * lA * rho)
                elif i == 0 and j == 1:
                    p *= (1 + lH * rho)
                elif i == 1 and j == 0:
                    p *= (1 + lA * rho)
                else:
                    p *= (1 - rho)
            joint[i][j] = p
            if i > j:
                pH += p
            elif i == j:
                pD += p
            else:
                pA += p
    return pH, pD, pA, joint

# ---- Team composite strength ----
def team_power(name):
    t = TEAMS.get(name)
    if not t:
        return {'att': 0, 'def': 0, 'score': 0.3}

    eloZ = (t['elo'] - 1780) / 180
    eloS = min(0.92, max(0.08, 0.50 + eloZ * 0.26))

    xgDiff = t['xgFor'] - t['xgAgainst']
    xgS = min(0.95, max(0.05, 0.50 + xgDiff / 14))
    gfRatio = t['gf'] / max(1, t['ga'])
    goalS = min(0.95, max(0.05, 0.50 + (gfRatio - 1.5) / 5))
    tournS = xgS * 0.55 + goalS * 0.30 + (t['cs'] / 5) * 0.15

    starZ = (t['starAvg'] - 74) / 18
    playerS = min(0.95, max(0.05, 0.50 + starZ * 0.28))
    momS = min(0.90, max(0.10, 0.50 + t['mom'] * 2.5))

    score = eloS * 0.15 + tournS * 0.55 + playerS * 0.20 + momS * 0.10
    return {'att': t['att'], 'def': t['def'], 'score': score,
            'tourn': tournS, 'elo': eloS, 'player': playerS, 'mom': momS}

# ---- Predict single match (analytical) ----
def predict_match(h, a, homeAdv=0.05):
    sH = team_power(h)
    sA = team_power(a)
    lH = math.exp(sH['att'] - sA['def'] + 0.12 + homeAdv)
    lA = math.exp(sA['att'] - sH['def'] + 0.12)
    pH, pD, pA, joint = dixon_coles(lH, lA)

    scores = []
    for i in range(7):
        for j in range(7):
            if joint[i][j] > 0.004:
                scores.append({'s': f"{i}-{j}", 'p': joint[i][j]})
    scores.sort(key=lambda x: -x['p'])

    return {
        'h': h, 'a': a,
        'pH': pH, 'pD': pD, 'pA': pA,
        'lH': lH, 'lA': lA,
        'scores': scores[:4],
    }

# ---- Simulate one knockout match (with ET + pens) ----
def sim_match(h, a, homeAdv=0.05, match_key=None, results_map=None):
    # Check known result
    if results_map and match_key and match_key in results_map:
        return results_map[match_key].get('winner', h)

    sH = team_power(h)
    sA = team_power(a)
    lH = math.exp(sH['att'] - sA['def'] + 0.12 + homeAdv)
    lA = math.exp(sA['att'] - sH['def'] + 0.12)

    # Sample goals
    gh = ga = -1
    cH = cA = 0.0
    r1, r2 = random.random(), random.random()
    for k in range(21):
        cH += pois(k, lH)
        if r1 < cH and gh == -1:
            gh = k
        cA += pois(k, lA)
        if r2 < cA and ga == -1:
            ga = k
        if gh != -1 and ga != -1:
            break

    # ET if draw
    if gh == ga:
        etLam = 0.32
        eH = eA = -1
        ceH = ceA = 0.0
        re1, re2 = random.random(), random.random()
        for k in range(11):
            ceH += pois(k, etLam * (1 + sH['att'] * 0.2))
            if re1 < ceH and eH == -1: eH = k
            ceA += pois(k, etLam * (1 + sA['att'] * 0.2))
            if re2 < ceA and eA == -1: eA = k
            if eH != -1 and eA != -1: break
        gh += eH; ga += eA

        # PKs
        if gh == ga:
            penProb = 0.50 + (sH['score'] - sA['score']) * 0.55
            return h if random.random() < penProb else a

    return h if gh > ga else a

# ---- Monte Carlo simulation ----
class MCSimulator:
    def __init__(self):
        self.cache = None
        self.cache_time = 0
        self.last_results_hash = ''

    def run(self, N=10000):
        results_map, _ = load_match_results()
        results_hash = str(sorted(results_map.keys())) if results_map else ''

        # Return cache if still fresh (within 5 min) and data hasn't changed
        if self.cache and (time.time() - self.cache_time < 300) and results_hash == self.last_results_hash:
            return self.cache

        teams = list(TEAMS.keys())
        res = {t: {'qf': 0, 'sf': 0, 'f': 0, 'champ': 0} for t in teams}

        # ID mapping
        id_map = {
            "R16A": "R16-1", "R16B": "R16-2", "R16C": "R16-3", "R16D": "R16-4",
            "R16E": "R16-5", "R16F": "R16-6", "R16G": "R16-7", "R16H": "R16-8",
            "QF1": "QF-1", "QF2": "QF-2", "QF3": "QF-3", "QF4": "QF-4",
            "SF1": "SF-1", "SF2": "SF-2",
        }

        for _ in range(N):
            # R16
            r16w = {}
            for m in R16_MATCHES:
                key = id_map.get(m['id'], m['id'])
                r16w[m['id']] = sim_match(m['h'], m['a'], m['homeAdv'], key, results_map)

            # QF
            qfw = {}
            for qf in QF_PATHS:
                t1, t2 = r16w[qf['from'][0]], r16w[qf['from'][1]]
                key = id_map.get(qf['id'], qf['id'])
                qfw[qf['id']] = sim_match(t1, t2, 0.05, key, results_map)

            for t in r16w.values():
                if t in res: res[t]['qf'] += 1

            # SF
            sfw = {}
            for sf in SF_PATHS:
                t1, t2 = qfw[sf['from'][0]], qfw[sf['from'][1]]
                key = id_map.get(sf['id'], sf['id'])
                sfw[sf['id']] = sim_match(t1, t2, 0.05, key, results_map)

            for t in qfw.values():
                if t in res: res[t]['sf'] += 1

            # Final
            f1, f2 = sfw['SF-1'], sfw['SF-2']
            champ = sim_match(f1, f2, 0.05, 'FINAL', results_map)
            if f1 in res: res[f1]['f'] += 1
            if f2 in res: res[f2]['f'] += 1
            if champ in res: res[champ]['champ'] += 1

        # Convert to percentages
        for t in teams:
            res[t]['qfPct'] = res[t]['qf'] / N * 100
            res[t]['sfPct'] = res[t]['sf'] / N * 100
            res[t]['fPct'] = res[t]['f'] / N * 100
            res[t]['champPct'] = res[t]['champ'] / N * 100

        self.cache = res
        self.cache_time = time.time()
        self.last_results_hash = results_hash
        return res

# Global instance
simulator = MCSimulator()
