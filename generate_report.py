"""
Generate a beautiful standalone HTML report from allure-results JSON files.
No allure CLI required — pure Python.
Run: python generate_report.py
Then open: reports/allure-report.html
"""
import json
import math
import pathlib
import platform
import sys
from collections import defaultdict
from datetime import datetime

RESULTS_DIR = pathlib.Path("reports/allure-results")
OUTPUT_FILE  = pathlib.Path("reports/allure-report.html")

TAG_COLORS = {
    "sanity":     ("#1a9",  "#e6fff8"),
    "regression": ("#7c3aed","#f3e8ff"),
    "auth":       ("#d97706","#fffbeb"),
    "get_api":    ("#2563eb","#eff6ff"),
    "post_api":   ("#db2777","#fdf2f8"),
}


# ─────────────────────────── data loading ────────────────────────────────────

def load_results():
    tests = []
    for f in RESULTS_DIR.glob("*-result.json"):
        try:
            tests.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            pass
    return sorted(tests, key=lambda x: x.get("start", 0))


def get_labels(test, label_name):
    return [l["value"] for l in test.get("labels", []) if l.get("name") == label_name]


def get_feature(test):
    for lbl in test.get("labels", []):
        if lbl.get("name") == "feature":
            return lbl.get("value", "")
    for lbl in test.get("labels", []):
        if lbl.get("name") == "suite":
            val = lbl.get("value", "")
            if "get" in val.lower():  return "GET Users API"
            if "post" in val.lower(): return "POST Users API"
    name = test.get("name", "")
    if "post" in name.lower() or "create" in name.lower(): return "POST Users API"
    return "GET Users API"


def get_tags(test):
    tags = set()
    for lbl in test.get("labels", []):
        if lbl.get("name") in ("tag", "story", "epic"):
            tags.add(lbl["value"].lower())
    name = test.get("name", "").lower()
    if "auth" in name or "token" in name or "401" in name: tags.add("auth")
    if "sanity" in name: tags.add("sanity")
    if "regression" in name: tags.add("regression")
    return tags


def duration_ms(test):
    try:    return test.get("stop", 0) - test.get("start", 0)
    except: return 0


def duration_str(ms):
    if ms < 1000: return f"{ms}ms"
    return f"{ms/1000:.2f}s"


def read_attachment(source):
    src = RESULTS_DIR / source
    try:    return src.read_text(encoding="utf-8") if src.exists() else ""
    except: return ""


# ─────────────────────────── SVG pie chart ───────────────────────────────────

def pie_chart(passed, failed, skipped, broken, total):
    if total == 0: return ""
    slices = [
        (passed,  "#22c55e", "Passed"),
        (failed,  "#ef4444", "Failed"),
        (skipped, "#94a3b8", "Skipped"),
        (broken,  "#f97316", "Broken"),
    ]
    cx, cy, r = 100, 100, 80
    circ = 2 * math.pi * r
    svg = f'<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">'
    angle = -math.pi / 2
    for count, color, label in slices:
        if count == 0: continue
        frac  = count / total
        sweep = 2 * math.pi * frac
        x1 = cx + r * math.cos(angle)
        y1 = cy + r * math.sin(angle)
        angle += sweep
        x2 = cx + r * math.cos(angle)
        y2 = cy + r * math.sin(angle)
        large = 1 if sweep > math.pi else 0
        svg += (
            f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} '
            f'A{r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z" '
            f'fill="{color}" stroke="#1e293b" stroke-width="2"/>'
        )
    pct = int(passed * 100 / total)
    svg += (
        f'<circle cx="{cx}" cy="{cy}" r="44" fill="#0f172a"/>'
        f'<text x="{cx}" y="{cy-8}" text-anchor="middle" '
        f'font-size="22" font-weight="800" fill="#f8fafc">{pct}%</text>'
        f'<text x="{cx}" y="{cy+12}" text-anchor="middle" '
        f'font-size="11" fill="#94a3b8">passed</text>'
        f'</svg>'
    )
    return svg


# ─────────────────────────── tag badge ───────────────────────────────────────

def tag_badge(tag):
    border, bg = TAG_COLORS.get(tag, ("#6b7280", "#f3f4f6"))
    return (
        f'<span style="border:1px solid {border};color:{border};background:{bg};'
        f'padding:1px 8px;border-radius:10px;font-size:10px;font-weight:600;'
        f'letter-spacing:.4px;margin-right:4px">{tag.upper()}</span>'
    )


def status_pill(status):
    cfg = {
        "passed":  ("#22c55e", "#052e16"),
        "failed":  ("#ef4444", "#450a0a"),
        "broken":  ("#f97316", "#431407"),
        "skipped": ("#94a3b8", "#1e293b"),
    }.get(status, ("#6b7280", "#1e293b"))
    return (
        f'<span style="background:{cfg[0]};color:#fff;padding:2px 10px;'
        f'border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.5px">'
        f'{status.upper()}</span>'
    )


def step_icon(status):
    return {"passed":"✅","failed":"❌","broken":"⚠️","skipped":"⏭️"}.get(status,"•")


# ─────────────────────────── steps renderer ──────────────────────────────────

def render_steps(steps, depth=0):
    if not steps:
        return '<p style="color:#475569;font-size:12px;padding:6px 0;font-style:italic">No steps recorded.</p>'
    html = ""
    for s in steps:
        name   = s.get("name", "")
        status = s.get("status", "")
        icon   = step_icon(status)
        ind    = depth * 18
        bc     = "#22c55e" if status == "passed" else "#ef4444" if status == "failed" else "#94a3b8"

        html += f"""
        <div style="display:flex;align-items:flex-start;gap:8px;
                    padding:5px 0 5px {ind+10}px;
                    border-left:2px solid {bc};margin-left:{ind}px;margin-bottom:2px">
          <span style="font-size:13px;margin-top:1px">{icon}</span>
          <span style="font-size:13px;color:#e2e8f0;font-weight:500">{name}</span>
        </div>"""

        for attach in s.get("attachments", []):
            label   = attach.get("name", "")
            content = read_attachment(attach.get("source", ""))
            if not content: continue
            if "request" in label.lower():
                ac, lc = "#93c5fd", "#1e3a5f"
            elif "response" in label.lower():
                ac, lc = "#86efac", "#052e16"
            elif "schema" in label.lower() or "result" in label.lower():
                ac, lc = "#fde68a", "#3d2c00"
            elif "error" in label.lower():
                ac, lc = "#fca5a5", "#450a0a"
            else:
                ac, lc = "#cbd5e1", "#1e293b"
            html += f"""
        <div style="margin-left:{ind+28}px;margin-bottom:6px">
          <div style="font-size:10px;color:#64748b;text-transform:uppercase;
                      letter-spacing:.5px;margin-bottom:2px">{label}</div>
          <pre style="background:{lc};color:{ac};font-size:11px;
                      padding:8px 12px;border-radius:6px;margin:0;
                      overflow-x:auto;white-space:pre-wrap;
                      border-left:3px solid {ac}40">{content}</pre>
        </div>"""

        sd = s.get("statusDetails") or {}
        trace = (sd.get("trace") or "").strip()
        if trace and status != "passed":
            html += f"""
        <pre style="margin-left:{ind+28}px;background:#450a0a;color:#fca5a5;
                    font-size:11px;padding:8px 12px;border-radius:6px;
                    overflow-x:auto;white-space:pre-wrap;margin-bottom:6px;
                    border-left:3px solid #ef4444">{trace}</pre>"""

        if s.get("steps"):
            html += render_steps(s["steps"], depth + 1)
    return html


# ─────────────────────────── feature block ───────────────────────────────────

def render_feature_block(feature, tests, bidx):
    total   = len(tests)
    passed  = sum(1 for t in tests if t.get("status") == "passed")
    failed  = total - passed
    accent  = "#22c55e" if failed == 0 else "#ef4444"
    icon    = "✅" if failed == 0 else "❌"
    rows = ""
    for i, t in enumerate(tests):
        tid    = f"b{bidx}_t{i}"
        name   = t.get("name", "Unknown")
        status = t.get("status", "unknown")
        ms     = duration_ms(t)
        dur    = duration_str(ms)
        tags   = get_tags(t)
        msg    = (t.get("statusDetails") or {}).get("message", "") or ""
        ts     = datetime.fromtimestamp(t.get("start",0)/1000).strftime("%H:%M:%S") if t.get("start") else "—"
        max_ms = max((duration_ms(x) for x in tests), default=1) or 1
        bar_w  = max(4, int(ms * 120 / max_ms))
        bar_c  = "#22c55e" if status == "passed" else "#ef4444" if status == "failed" else "#94a3b8"
        tag_html = "".join(tag_badge(tg) for tg in sorted(tags))
        steps_html = render_steps(t.get("steps", []))

        rows += f"""
        <div class="test-card" id="card-{tid}">
          <div class="test-header" onclick="toggle('{tid}')">
            <div style="flex:1;min-width:0">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <span style="font-size:13px;font-weight:600;color:#f1f5f9">{name}</span>
                <span style="flex:1"></span>
                {tag_html}
              </div>
              <div style="margin-top:4px;display:flex;align-items:center;gap:10px">
                <div style="height:4px;width:{bar_w}px;background:{bar_c};border-radius:2px"></div>
                <span style="font-size:11px;color:#64748b">⏱ {dur}</span>
                <span style="font-size:11px;color:#64748b">🕐 {ts}</span>
              </div>
            </div>
            <div style="display:flex;align-items:center;gap:10px;margin-left:12px">
              {status_pill(status)}
              <span class="chevron" id="chev-{tid}" style="color:#475569;font-size:12px;transition:transform .2s">▼</span>
            </div>
          </div>
          <div class="test-body" id="body-{tid}">
            {('<div style="background:#450a0a;border-left:3px solid #ef4444;color:#fca5a5;padding:8px 12px;border-radius:6px;font-size:12px;margin-bottom:10px">⚠ ' + msg + '</div>') if msg else ''}
            <div style="font-size:10px;color:#475569;text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;font-weight:600">Execution Log</div>
            <div style="background:#0a0f1a;border-radius:8px;padding:14px;border:1px solid #1e293b">
              {steps_html}
            </div>
          </div>
        </div>"""

    return f"""
    <div class="feature-block" data-feature="{feature}">
      <div class="feature-header" style="border-left:4px solid {accent}">
        <div>
          <div style="font-size:16px;font-weight:700;color:#f1f5f9">📁 {feature}</div>
          <div style="font-size:12px;color:#64748b;margin-top:3px">
            {total} test{"s" if total!=1 else ""} &nbsp;·&nbsp;
            <span style="color:#22c55e">{passed} passed</span>
            {"&nbsp;·&nbsp;<span style='color:#ef4444'>" + str(failed) + " failed</span>" if failed else ""}
          </div>
        </div>
        <span style="font-size:22px">{icon}</span>
      </div>
      {rows}
    </div>"""


# ─────────────────────────── legend row ──────────────────────────────────────

def legend_item(color, label, count):
    return f"""
    <div style="display:flex;align-items:center;gap:8px">
      <div style="width:12px;height:12px;border-radius:50%;background:{color}"></div>
      <span style="font-size:13px;color:#94a3b8">{label}</span>
      <span style="font-size:13px;font-weight:700;color:#f1f5f9">{count}</span>
    </div>"""


# ─────────────────────────── full HTML ───────────────────────────────────────

def build_html(tests):
    now     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total   = len(tests)
    passed  = sum(1 for t in tests if t.get("status") == "passed")
    failed  = sum(1 for t in tests if t.get("status") == "failed")
    skipped = sum(1 for t in tests if t.get("status") == "skipped")
    broken  = sum(1 for t in tests if t.get("status") == "broken")

    n_sanity     = sum(1 for t in tests if "sanity"     in get_tags(t))
    n_regression = sum(1 for t in tests if "regression" in get_tags(t))
    n_auth       = sum(1 for t in tests if "auth"       in get_tags(t))

    total_ms  = sum(duration_ms(t) for t in tests)
    env_info  = f"Python {sys.version.split()[0]} · {platform.system()} {platform.release()}"

    groups = defaultdict(list)
    for t in tests:
        groups[get_feature(t)].append(t)

    feature_blocks = "".join(
        render_feature_block(feat, ftests, idx)
        for idx, (feat, ftests) in enumerate(groups.items())
    )

    feature_filter_btns = "".join(
        '<span class="filter-btn active" '
        'style="border-color:#7c3aed;color:#7c3aed;background:#2e1065" '
        f'onclick="filterFeature(\"{feat}\",this)">'
        f'{feat} ({len(ftests)})</span>'
        for feat, ftests in groups.items()
    )

    pie = pie_chart(passed, failed, skipped, broken, total)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BDD API Test Report</title>
<style>
  :root {{
    --bg:      #0f172a;
    --surface: #1e293b;
    --border:  #334155;
    --text:    #f1f5f9;
    --muted:   #64748b;
  }}
  * {{ box-sizing:border-box;margin:0;padding:0 }}
  body {{ font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh }}

  /* ── Header ── */
  header {{
    background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);
    padding:28px 48px;border-bottom:1px solid var(--border);
    display:flex;justify-content:space-between;align-items:center;
  }}
  header h1 {{ font-size:24px;font-weight:800;color:#38bdf8;letter-spacing:-.3px }}
  header .meta {{ font-size:12px;color:var(--muted);margin-top:4px }}
  .env-badge {{
    background:#1e293b;border:1px solid var(--border);
    padding:6px 14px;border-radius:20px;font-size:11px;color:var(--muted)
  }}

  /* ── Summary strip ── */
  .summary-strip {{
    display:flex;gap:0;border-bottom:1px solid var(--border);
    background:#0f172a;overflow-x:auto;
  }}
  .stat-box {{
    flex:1;min-width:100px;padding:18px 24px;
    border-right:1px solid var(--border);text-align:center;
  }}
  .stat-box .num {{ font-size:32px;font-weight:800 }}
  .stat-box .lbl {{ font-size:11px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.5px }}
  .c-pass {{ color:#22c55e }} .c-fail {{ color:#ef4444 }}
  .c-skip {{ color:#94a3b8 }} .c-total {{ color:#38bdf8 }}
  .c-dur  {{ color:#a78bfa }}

  /* ── Main layout ── */
  .main {{ display:flex;gap:0 }}
  .sidebar {{
    width:300px;min-width:260px;border-right:1px solid var(--border);
    padding:28px 24px;position:sticky;top:0;height:100vh;overflow-y:auto;
    background:#0f172a;
  }}
  .content {{ flex:1;padding:28px 40px;overflow:hidden }}

  /* ── Sidebar sections ── */
  .sidebar-section {{ margin-bottom:28px }}
  .sidebar-section h3 {{
    font-size:11px;text-transform:uppercase;letter-spacing:.8px;
    color:var(--muted);font-weight:600;margin-bottom:12px
  }}

  /* ── Filter buttons ── */
  .filter-btn {{
    display:inline-block;padding:5px 12px;border-radius:20px;
    font-size:12px;font-weight:600;cursor:pointer;border:1px solid;
    margin:3px 3px 3px 0;transition:all .15s;user-select:none
  }}
  .filter-btn.active {{ opacity:1 }}
  .filter-btn:not(.active) {{ opacity:.45 }}

  /* ── Feature block ── */
  .feature-block {{ margin-bottom:28px }}
  .feature-header {{
    display:flex;justify-content:space-between;align-items:center;
    background:var(--surface);padding:14px 20px;
    border-radius:0 10px 10px 0;margin-bottom:12px;
  }}

  /* ── Test card ── */
  .test-card {{
    background:var(--surface);border:1px solid var(--border);
    border-radius:10px;margin-bottom:8px;overflow:hidden;transition:border-color .2s
  }}
  .test-card:hover {{ border-color:#475569 }}
  .test-header {{
    display:flex;align-items:center;padding:12px 16px;
    cursor:pointer;user-select:none;
  }}
  .test-header:hover {{ background:#263348 }}
  .test-body {{
    display:none;padding:16px 20px;
    border-top:1px solid var(--border);background:#111827
  }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width:6px;height:6px }}
  ::-webkit-scrollbar-track {{ background:transparent }}
  ::-webkit-scrollbar-thumb {{ background:#334155;border-radius:3px }}
</style>
</head>
<body>

<!-- Header -->
<header>
  <div>
    <h1>🧪 BDD API Test Report</h1>
    <div class="meta">Generated: {now} &nbsp;·&nbsp; {env_info}</div>
  </div>
  <div class="env-badge">Total duration: {duration_str(total_ms)}</div>
</header>

<!-- Summary strip -->
<div class="summary-strip">
  <div class="stat-box"><div class="num c-total">{total}</div><div class="lbl">Total</div></div>
  <div class="stat-box"><div class="num c-pass">{passed}</div><div class="lbl">Passed</div></div>
  <div class="stat-box"><div class="num c-fail">{failed}</div><div class="lbl">Failed</div></div>
  <div class="stat-box"><div class="num c-skip">{skipped}</div><div class="lbl">Skipped</div></div>
  <div class="stat-box"><div class="num" style="color:#f97316">{broken}</div><div class="lbl">Broken</div></div>
  <div class="stat-box"><div class="num c-dur">{duration_str(total_ms)}</div><div class="lbl">Duration</div></div>
</div>

<!-- Main layout -->
<div class="main">

  <!-- Sidebar -->
  <div class="sidebar">

    <!-- Pie chart -->
    <div class="sidebar-section">
      <h3>Results</h3>
      <div style="display:flex;justify-content:center;margin-bottom:16px">
        {pie}
      </div>
      <div style="display:flex;flex-direction:column;gap:8px">
        {legend_item("#22c55e","Passed", passed)}
        {legend_item("#ef4444","Failed", failed)}
        {legend_item("#94a3b8","Skipped",skipped)}
        {legend_item("#f97316","Broken", broken)}
      </div>
    </div>

    <!-- Run type filter -->
    <div class="sidebar-section">
      <h3>Run Type</h3>
      <div>
        <span class="filter-btn active" style="border-color:#38bdf8;color:#38bdf8;background:#0c2340"
              onclick="filterTag('all',this)">ALL ({total})</span>
        <span class="filter-btn active" style="border-color:#1a9;color:#1a9;background:#052e1e"
              onclick="filterTag('sanity',this)">SANITY ({n_sanity})</span>
        <span class="filter-btn active" style="border-color:#7c3aed;color:#7c3aed;background:#2e1065"
              onclick="filterTag('regression',this)">REGRESSION ({n_regression})</span>
        <span class="filter-btn active" style="border-color:#d97706;color:#d97706;background:#431407"
              onclick="filterTag('auth',this)">AUTH ({n_auth})</span>
      </div>
    </div>

    <!-- Status filter -->
    <div class="sidebar-section">
      <h3>Filter by Status</h3>
      <div>
        <span class="filter-btn active" style="border-color:#38bdf8;color:#38bdf8;background:#0c2340"
              onclick="filterStatus('all',this)">ALL</span>
        <span class="filter-btn active" style="border-color:#22c55e;color:#22c55e;background:#052e16"
              onclick="filterStatus('passed',this)">PASSED</span>
        <span class="filter-btn active" style="border-color:#ef4444;color:#ef4444;background:#450a0a"
              onclick="filterStatus('failed',this)">FAILED</span>
        <span class="filter-btn active" style="border-color:#94a3b8;color:#94a3b8;background:#1e293b"
              onclick="filterStatus('skipped',this)">SKIPPED</span>
      </div>
    </div>

    <!-- Feature filter -->
    <div class="sidebar-section">
      <h3>Feature</h3>
      <div>
        <span class="filter-btn active" style="border-color:#38bdf8;color:#38bdf8;background:#0c2340"
              onclick="filterFeature('all',this)">ALL FEATURES</span>
        {feature_filter_btns}
      </div>
    </div>

    <!-- Tag counts -->
    <div class="sidebar-section">
      <h3>Tags</h3>
      {"".join(f'<div style="display:flex;justify-content:space-between;margin-bottom:6px"><span>{tag_badge(tg)}</span><span style="font-size:12px;color:#94a3b8">{sum(1 for t in tests if tg in get_tags(t))}</span></div>' for tg in ["sanity","regression","auth","get_api","post_api"])}
    </div>

  </div>

  <!-- Content -->
  <div class="content" id="content">
    {feature_blocks}
  </div>
</div>

<script>
const allTests = document.querySelectorAll('.test-card');
let activeTag = 'all', activeStatus = 'all', activeFeature = 'all';

function applyFilters() {{
  allTests.forEach(card => {{
    const tags   = (card.dataset.tags || '').split(',');
    const status = card.dataset.status || '';
    const tagOk  = activeTag === 'all' || tags.includes(activeTag);
    const stOk   = activeStatus === 'all' || status === activeStatus;
    card.style.display = (tagOk && stOk) ? '' : 'none';
  }});
  // hide empty or feature-filtered blocks
  document.querySelectorAll('.feature-block').forEach(fb => {{
    const featureHidden = fb.dataset.featureHidden === 'true';
    const visible = !featureHidden && [...fb.querySelectorAll('.test-card')].some(c => c.style.display !== 'none');
    fb.style.display = visible ? '' : 'none';
  }});
}}

function filterTag(tag, el) {{
  activeTag = tag;
  el.closest('.sidebar-section').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  applyFilters();
}}

function filterStatus(status, el) {{
  activeStatus = status;
  el.closest('.sidebar-section').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  applyFilters();
}}

function filterFeature(feature, el) {{
  activeFeature = feature;
  el.closest('.sidebar-section').querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.feature-block').forEach(fb => {{
    if (feature === 'all' || fb.dataset.feature === feature) {{
      fb.dataset.featureHidden = '';
    }} else {{
      fb.dataset.featureHidden = 'true';
    }}
  }});
  applyFilters();
}}

function toggle(id) {{
  const body = document.getElementById('body-' + id);
  const chev = document.getElementById('chev-' + id);
  const open = body.style.display === 'block';
  body.style.display = open ? 'none' : 'block';
  chev.style.transform = open ? '' : 'rotate(180deg)';
}}

// inject data attrs for filtering
document.querySelectorAll('.test-card').forEach(card => {{
  const id = card.id.replace('card-','');
}});
</script>

<script>
// Inject tags + status into each test card after render
(function() {{
  const tagMap = {{}};
  const statusMap = {{}};
{chr(10).join(f'  tagMap["card-b{bi}_t{ti}"] = "{",".join(get_tags(t))}"; statusMap["card-b{bi}_t{ti}"] = "{t.get("status","")}"' for bi, (feat, ftests) in enumerate(groups.items()) for ti, t in enumerate(ftests))}
  Object.entries(tagMap).forEach(([id, tags]) => {{
    const el = document.getElementById(id);
    if (el) {{ el.dataset.tags = tags; el.dataset.status = statusMap[id] || ''; }}
  }});
}})();
</script>

</body>
</html>"""


def main():
    if not RESULTS_DIR.exists():
        print(f"❌ No results at {RESULTS_DIR}. Run: python -m pytest tests/ -v")
        return
    tests = load_results()
    if not tests:
        print("❌ No result JSON files. Run: python -m pytest tests/ -v")
        return
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(build_html(tests), encoding="utf-8")
    print(f"✅ Report → {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
