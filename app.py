# ============================================================
# 2026 World Cup Prediction — Flask Application
# ============================================================
from flask import Flask, render_template, jsonify, request
from data import (
    TEAMS, R16_MATCHES, QF_PATHS, SF_PATHS, PLAYERS,
    GROUPS, R32_RESULTS, FLAGS, load_match_results, get_last_update_time
)
from model import simulator, predict_match, team_power
import time, threading

app = Flask(__name__)

# ---- Background model refresh ----
def background_refresh():
    """Run MC simulation in background thread."""
    while True:
        time.sleep(300)  # every 5 minutes
        try:
            simulator.cache = None  # force refresh
            simulator.run(10000)
            print(f"[{time.strftime('%H:%M:%S')}] MC refreshed")
        except Exception as e:
            print(f"MC refresh error: {e}")

# Start background thread
import atexit
_bg_thread = threading.Thread(target=background_refresh, daemon=True)
_bg_thread.start()

@app.context_processor
def inject_globals():
    return {
        'FLAGS': FLAGS,
        'flag': lambda n: FLAGS.get(n, '🏳️'),
        'now': time.time,
        'TEAMS': TEAMS,
    }

# ---- Helper functions ----
def get_match_result(match_id):
    results, _ = load_match_results()
    return results.get(match_id)

def format_date(d):
    """Format ISO date to readable Chinese format."""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(d)
        return dt.strftime('%m月%d日 %H:%M')
    except:
        return d

# ---- Routes ----

@app.route('/')
def index():
    """Main knockout stage page."""
    mc = simulator.run(10000)
    last_update = get_last_update_time() or time.strftime('%Y-%m-%d %H:%M:%S')

    # Group R16 matches by date
    r16_predictions = []
    for m in R16_MATCHES:
        result = get_match_result(m['id'])
        pred = predict_match(m['h'], m['a'], m['homeAdv'])
        r16_predictions.append({
            'match': m,
            'result': result,
            'pred': pred,
            'date_formatted': format_date(m['date']),
        })

    # Build bracket snapshots for QF/SF/Final
    qf_slots = []
    for qf in QF_PATHS:
        m1 = next(m for m in R16_MATCHES if m['id'] == qf['from'][0])
        m2 = next(m for m in R16_MATCHES if m['id'] == qf['from'][1])
        r1 = get_match_result(qf['from'][0])
        r2 = get_match_result(qf['from'][1])
        p1 = predict_match(m1['h'], m1['a'], m1['homeAdv'])
        p2 = predict_match(m2['h'], m2['a'], m2['homeAdv'])
        adv1 = r1['winner'] if r1 else (m1['h'] if p1['pH'] > p1['pA'] else m1['a'])
        adv2 = r2['winner'] if r2 else (m2['h'] if p2['pH'] > p2['pA'] else m2['a'])
        qf_slots.append({
            'qf': qf,
            'adv1': adv1, 'adv2': adv2,
            'pct1': mc.get(adv1, {}).get('qfPct', 0),
            'pct2': mc.get(adv2, {}).get('qfPct', 0),
            'm1': m1, 'm2': m2,
        })

    sf_slots = []
    for sf in SF_PATHS:
        qf1 = next(q for q in qf_slots if q['qf']['id'] == sf['from'][0])
        qf2 = next(q for q in qf_slots if q['qf']['id'] == sf['from'][1])
        teams_in_half = set()
        for qf in [qf1, qf2]:
            m1 = qf['m1']; m2 = qf['m2']
            teams_in_half.update([m1['h'], m1['a'], m2['h'], m2['a']])
        top_teams = sorted(teams_in_half, key=lambda t: mc.get(t, {}).get('sfPct', 0), reverse=True)[:4]
        sf_slots.append({
            'sf': sf,
            'teams': [(t, mc.get(t, {}).get('sfPct', 0)) for t in top_teams],
        })

    # Championship ranking
    champ_ranking = sorted(TEAMS.keys(), key=lambda t: mc.get(t, {}).get('champPct', 0), reverse=True)

    return render_template('index.html',
        r16_predictions=r16_predictions,
        qf_slots=qf_slots,
        sf_slots=sf_slots,
        mc=mc,
        champ_ranking=champ_ranking,
        last_update=last_update,
        R32_RESULTS=R32_RESULTS,
    )

@app.route('/groups')
def groups():
    """Group stage results page."""
    return render_template('groups.html', groups=GROUPS, R32_RESULTS=R32_RESULTS)

@app.route('/teams')
def teams():
    """Team rankings & championship probabilities."""
    mc = simulator.run(10000)
    teams_sorted = sorted(TEAMS.items(), key=lambda x: mc.get(x[0], {}).get('champPct', 0), reverse=True)
    teams_data = []
    for name, dat in teams_sorted:
        p = team_power(name)
        r = mc.get(name, {})
        teams_data.append({
            'name': name, 'dat': dat, 'power': p, 'mc': r,
            'composite': p['score'] * 100,
        })
    return render_template('teams.html', teams=teams_data, mc=mc)

@app.route('/team/<name>')
def team_detail(name):
    """Individual team page with squad and probabilities."""
    if name not in TEAMS:
        return "Team not found", 404
    mc = simulator.run(10000)
    dat = TEAMS[name]
    p = team_power(name)
    r = mc.get(name, {})
    players = [pl for pl in PLAYERS if pl['team'] == name]
    # Build composite scores for template
    scores = {
        'tournament': int(p['tourn'] * 100),
        'elo': int(p['elo'] * 100),
        'player': int(p['player'] * 100),
        'momentum': int(p['mom'] * 100),
        'composite': int(p['score'] * 100),
    }
    return render_template('team.html',
        name=name, dat=dat, scores=scores, mc=r, players=players)

@app.route('/match/<match_id>')
def match_detail(match_id):
    """Individual match detail page."""
    m = next((m for m in R16_MATCHES if m['id'] == match_id), None)
    if not m:
        return "Match not found", 404
    result = get_match_result(match_id)
    pred = predict_match(m['h'], m['a'], m['homeAdv'])
    sH = team_power(m['h'])
    sA = team_power(m['a'])
    return render_template('match.html',
        match=m, result=result, pred=pred, sH=sH, sA=sA,
        date_formatted=format_date(m['date']))

@app.route('/api/meta')
def api_meta():
    """API endpoint for live polling."""
    return jsonify({
        'last_pipeline_run': get_last_update_time() or time.strftime('%Y-%m-%d %H:%M:%S'),
        'server_time': time.strftime('%Y-%m-%d %H:%M:%S'),
    })

@app.route('/api/probabilities')
def api_probabilities():
    """API endpoint for live probabilities."""
    mc = simulator.run(10000)
    return jsonify({t: {k: round(v, 2) for k, v in r.items()} for t, r in mc.items()})

# ---- Main ----
if __name__ == '__main__':
    print("=== 2026 World Cup Prediction Server ===")
    print("http://0.0.0.0:8000")
    print("Pages: / | /groups | /teams | /team/<name> | /match/<id>")
    print("API: /api/meta | /api/probabilities")
    # Pre-run MC so first request is fast
    print("Running initial MC simulation...")
    simulator.run(10000)
    print("Ready!")
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)
