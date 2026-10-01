"""NWIS front-end layer: styling + presentation widgets only. No backend logic lives here."""
import base64
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------------- background art
# Replace HERO_PHOTO with a real photo URL/data-URI to use a photograph instead.
HERO_PHOTO = ""

_HERO_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 640' preserveAspectRatio='xMidYMid slice'>
<defs><linearGradient id='g' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#0A2342'/><stop offset='1' stop-color='#123A66'/></linearGradient></defs>
<rect width='1600' height='640' fill='url(#g)'/>
<g fill='none' stroke='#ffffff' stroke-opacity='.05'>""" + "".join(
    f"<path d='M0 {60+i*38} Q400 {30+i*38} 800 {60+i*38} T1600 {60+i*38}'/>" for i in range(8)) + """</g>
<path d='M0 430 Q300 400 620 440 T1240 420 T1600 440 V640 H0Z' fill='#1B5E7B' fill-opacity='.45'/>
<path d='M0 480 Q360 450 700 490 T1300 470 T1600 495 V640 H0Z' fill='#139A9A' fill-opacity='.35'/>
<path d='M0 535 Q300 510 640 540 T1260 525 T1600 545 V640 H0Z' fill='#C9A35E' fill-opacity='.35'/>
<path d='M0 590 Q400 570 800 592 T1600 585 V640 H0Z' fill='#E4572E' fill-opacity='.30'/>
<g stroke='#ffffff' stroke-opacity='.55' stroke-width='2' fill='none'>
<path d='M1290 120 L1230 430 M1290 120 L1350 430 M1250 300 L1330 300 M1240 360 L1340 360 M1262 240 L1318 240 M1250 300 L1340 360 M1330 300 L1240 360 M1262 240 L1330 300'/>
<path d='M1290 120 V90' stroke-opacity='.9'/></g>
<path d='M1290 430 V610' stroke='#E4572E' stroke-width='3' stroke-dasharray='6 6'/>
<circle cx='1290' cy='610' r='6' fill='#E4572E'/>
</svg>"""
_HERO_URL = "data:image/svg+xml;base64," + base64.b64encode(_HERO_SVG.encode()).decode()
_CONTOUR = "data:image/svg+xml;base64," + base64.b64encode(
    ("<svg xmlns='http://www.w3.org/2000/svg' width='520' height='520'><g fill='none' stroke='#0A2342' stroke-opacity='.05'>"
     + "".join(f"<ellipse cx='260' cy='260' rx='{30+i*28}' ry='{20+i*21}' transform='rotate({i*4} 260 260)'/>" for i in range(10))
     + "</g></svg>").encode()).decode()

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600;700&display=swap');
:root{--ink:#0A2342;--ink2:#123A66;--paper:#F4F6F8;--flare:#E4572E;--teal:#139A9A;--amber:#F2A33A;--line:#D9E0E8}
html,body,[class*="css"],.stApp{font-family:'IBM Plex Sans',sans-serif;color:var(--ink)}
.stApp{background:var(--paper) url(CONTOUR) repeat}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1180px;padding-top:0!important;padding-bottom:4rem}
h1,h2,h3{font-family:'IBM Plex Sans Condensed',sans-serif;letter-spacing:-.01em}
/* utility + nav */
.util{display:flex;justify-content:flex-end;gap:22px;font-size:12.5px;padding:10px 4px;color:#5B6B7F}
.util a{color:#5B6B7F;text-decoration:none}.util a:hover{color:var(--flare)}
.nav{display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid var(--line);border-radius:6px;padding:12px 22px;margin-bottom:14px}
.brand{font-family:'IBM Plex Sans Condensed';font-weight:700;font-size:24px;color:var(--ink);display:flex;align-items:center;gap:10px}
.brand i{width:14px;height:14px;background:var(--flare);display:inline-block;clip-path:polygon(50% 0,100% 100%,0 100%)}
.nav .links{display:flex;gap:26px;font-weight:500;font-size:14.5px}
.nav .links a{color:var(--ink);text-decoration:none;padding:4px 0;border-bottom:2px solid transparent}
.nav .links a:hover{border-color:var(--flare)}
.pill{font-size:12px;padding:4px 10px;border-radius:99px;background:#E6F6F6;color:#0B6E6E;font-weight:600}
/* hero */
.hero{position:relative;border-radius:8px;overflow:hidden;color:#fff;padding:78px 56px 70px;min-height:400px;
 background:linear-gradient(90deg,rgba(10,35,66,.94) 0%,rgba(10,35,66,.55) 62%,rgba(10,35,66,.1) 100%),url(HERO) center/cover}
.hero h1{font-size:54px;line-height:1.04;font-weight:700;max-width:640px;margin:0 0 18px;color:#fff;padding:0}
.hero p{font-size:18px;max-width:560px;color:#D7E3F0;line-height:1.55;margin:0 0 28px}
.btn{display:inline-block;padding:12px 24px;border-radius:4px;font-weight:600;font-size:15px;text-decoration:none!important;margin-right:12px}
.btn.p{background:var(--flare);color:#fff!important}.btn.p:hover{background:#c9441f}
.btn.s{border:1.5px solid rgba(255,255,255,.7);color:#fff!important}.btn.s:hover{background:rgba(255,255,255,.12)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin:14px 0 6px;background:#fff;border:1px solid var(--line);border-radius:6px}
.stats div{padding:18px 22px;border-right:1px solid var(--line)}.stats div:last-child{border:0}
.stats b{display:block;font-family:'IBM Plex Sans Condensed';font-size:30px;color:var(--ink)}
.stats span{font-size:13px;color:#5B6B7F}
/* quick start */
.quick{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 8px}
.quick a{background:#fff;border:1px solid var(--line);border-radius:4px;padding:9px 16px;font-size:14px;font-weight:500;color:var(--ink);text-decoration:none}
.quick a:hover{border-color:var(--flare);color:var(--flare)}
/* section heads */
.sec{margin:46px 0 14px;padding-left:16px;border-left:4px solid var(--flare)}
.sec h2{margin:0;font-size:30px;font-weight:700;padding:0}
.sec p{margin:4px 0 0;color:#5B6B7F;font-size:15px}
/* streamlit widgets */
[data-testid="stFileUploader"] section{background:#fff;border:2px dashed #9FB3C8;border-radius:8px;padding:28px}
.stButton>button,.stDownloadButton>button{border-radius:4px;font-weight:600;padding:.6rem 1.4rem}
.stButton>button[kind="primary"]{background:var(--flare);border:0;color:#fff}
.stButton>button[kind="primary"]:hover{background:#c9441f}
[data-testid="stMetric"]{background:#fff;border:1px solid var(--line);border-top:3px solid var(--teal);border-radius:6px;padding:16px 18px}
[data-testid="stMetricValue"]{font-family:'IBM Plex Sans Condensed';font-weight:700}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:6px;overflow:hidden}
[data-testid="stExpander"]{background:#fff;border:1px solid var(--line);border-radius:6px}
[data-testid="stStatus"]{background:#fff;border-radius:6px}
hr{border-color:var(--line)!important}
/* sidebar */
[data-testid="stSidebar"]{background:var(--ink)}
[data-testid="stSidebar"] *{color:#E6EEF7}
.wf{list-style:none;margin:6px 0 0;padding:0 0 0 18px;border-left:2px solid #2C4F7C}
.wf li{position:relative;padding:7px 0 7px 12px;font-size:14px}
.wf li:before{content:"";position:absolute;left:-25px;top:13px;width:10px;height:10px;border-radius:50%;background:var(--ink);border:2px solid var(--flare)}
.wf li.plan:before{border-color:#6F89A8}.wf li.plan{opacity:.65}
.foot{margin-top:60px;background:var(--ink);color:#B8C7D9;padding:30px 36px;border-radius:8px;font-size:13.5px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}
@media(max-width:800px){.hero{padding:44px 24px}.hero h1{font-size:34px}.stats{grid-template-columns:1fr 1fr}.nav .links{display:none}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}
</style>
""".replace("HERO", HERO_PHOTO or _HERO_URL).replace("CONTOUR", _CONTOUR)


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


def header():
    st.markdown("""
<div class="util"><a href="#explorer">Depth explorer</a><a href="#pipeline">Pipeline</a><a href="#status">Prototype status</a></div>
<div class="nav"><div class="brand"><i></i>NWIS</div>
<div class="links"><a href="#upload">Upload WCR</a><a href="#database">Database</a><a href="#explorer">Risk explorer</a><a href="#pipeline">Pipeline</a><a href="#status">Status</a></div>
<span class="pill">Prototype</span></div>
<div class="hero"><h1>Every well drilled before is a warning for the next one.</h1>
<p>NWIS reads historical well reports, finds the wells most like yours, and shows what went wrong at the same formation and depth, before the bit gets there.</p>
<a class="btn p" href="#upload">Upload a report</a><a class="btn s" href="#explorer">Try the depth explorer</a></div>
<div class="stats"><div><b>PDF → data</b><span>OCR and NLP extraction</span></div><div><b>Similar wells</b><span>Ranked by overall similarity</span></div>
<div><b>4 risk types</b><span>Stuck pipe, kick, losses, tight hole</span></div><div><b>Online + offline</b><span>Cloud and local server sync</span></div></div>
<div class="quick"><a href="#upload">Upload WCR</a><a href="#database">Browse database</a><a href="#explorer">Check a depth</a><a href="#pipeline">See the pipeline</a></div>
""", unsafe_allow_html=True)


def sidebar_workflow():
    steps = [("WCR / DDR report", 0), ("OCR and text extraction", 0), ("NLP information extraction", 0),
             ("Structured data", 0), ("Supabase database", 0), ("Similar well identification", 1),
             ("Real-time eRTMAC data", 1), ("Risk prediction + SHAP", 1), ("Recommendations", 1), ("GIS dashboard", 1)]
    items = "".join(f'<li class="{"plan" if p else ""}">{t}</li>' for t, p in steps)
    st.sidebar.markdown(f'<h3 style="margin-bottom:2px">NWIS workflow</h3><small>Solid dot: working. Faded: planned.</small><ul class="wf">{items}</ul>',
                        unsafe_allow_html=True)


def section(title, sub=""):
    import re
    clean = re.sub(r"^[^A-Za-z0-9]+", "", title)
    clean = re.sub(r"^\d+\.\s*", "", clean)
    anchors = {"upload": "upload", "depth risk": "explorer", "extracted": "extracted", "nlp": "nlp", "structured database": "database",
               "database overview": "overview", "nwis end": "pipeline", "prototype": "status"}
    aid = next((v for k, v in anchors.items() if clean.lower().startswith(k)), "")
    st.markdown(f'<div class="sec" id="{aid}"><h2>{clean}</h2>{f"<p>{sub}</p>" if sub else ""}</div>', unsafe_allow_html=True)


def footer():
    st.markdown('<div class="foot"><span><b>NWIS</b> drilling intelligence prototype</span>'
                '<span>WCR → OCR → NLP → Structured database → Risk insight</span></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- interactive components
_BASE = """<style>@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@600;700&display=swap');
*{box-sizing:border-box}body{margin:0;font-family:'IBM Plex Sans',sans-serif;color:#0A2342;background:transparent}
:root{--ink:#0A2342;--flare:#E4572E;--teal:#139A9A;--amber:#F2A33A;--line:#D9E0E8}
.card{background:#fff;border:1px solid var(--line);border-radius:8px;padding:18px}h4{margin:0 0 10px;font:700 17px 'IBM Plex Sans Condensed'}
@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>"""

_PIPE = _BASE + """
<style>.row{display:flex;gap:0;overflow-x:auto;padding:6px 2px 14px}.st{flex:0 0 112px;text-align:center;cursor:pointer;position:relative;padding:0 4px}
.st .dot{width:46px;height:46px;border-radius:50%;margin:0 auto 8px;background:#fff;border:3px solid #9FB3C8;display:grid;place-items:center;font-weight:700;transition:.2s}
.st.ok .dot{border-color:var(--teal)}.st.on .dot{background:var(--ink);color:#fff;border-color:var(--flare);transform:scale(1.12)}
.st small{font-size:12.5px;line-height:1.25;display:block}
.st:not(:last-child):after{content:"";position:absolute;top:22px;left:calc(50% + 28px);width:calc(100% - 56px);height:3px;background:repeating-linear-gradient(90deg,#9FB3C8 0 6px,transparent 6px 12px)}
.st.ok:not(:last-child):after{background:repeating-linear-gradient(90deg,var(--teal) 0 6px,transparent 6px 12px);animation:flow 1s linear infinite}
@keyframes flow{to{background-position:12px 0}}
#d{margin-top:4px;display:flex;gap:14px;align-items:flex-start}#d b{font:700 20px 'IBM Plex Sans Condensed'}#d p{margin:4px 0 0;font-size:14.5px;line-height:1.5;max-width:760px}
.tag{font-size:12px;font-weight:600;padding:3px 10px;border-radius:99px;white-space:nowrap}.tag.ok{background:#E6F6F6;color:#0B6E6E}.tag.pl{background:#FDEBE5;color:#B3401D}</style>
<div class="card"><div class="row" id="r"></div><div id="d"></div></div>
<script>
const S=[["WCR / DDR PDFs","Well completion and daily drilling reports are uploaded as PDFs.",1],["OCR","Text is read from the PDF; scanned pages fall back to OCR.",1],["NLP extraction","Depths, formations, casing and events are pulled out as structured fields.",1],["Database","Structured wells are stored in the database (Supabase / PostgreSQL, PostGIS planned for maps).",1],
["Similar wells","Overall Well Similarity ranks historical wells by how closely they match the current one.",0],["Formation-depth match","Finds what happened in similar wells at the same formation and depth.",0],["Risk model","XGBoost / Random Forest estimate the probability of each drilling risk.",0],["SHAP","Shows which parameters pushed each risk up or down.",0],["Alerts","Turns risk probabilities into alerts with recommended actions.",0],["Dashboard","Engineers enter a depth and see live parameters, evidence and advice.",0]];
const r=document.getElementById('r'),d=document.getElementById('d');
S.forEach((s,i)=>{const e=document.createElement('div');e.className='st'+(s[2]?' ok':'');e.innerHTML=`<div class="dot">${i+1}</div><small>${s[0]}</small>`;e.onclick=()=>pick(i);r.appendChild(e)});
function pick(i){[...r.children].forEach((c,j)=>c.classList.toggle('on',j==i));const s=S[i];d.innerHTML=`<span class="tag ${s[2]?'ok':'pl'}">${s[2]?'Working':'Planned'}</span><div><b>${s[0]}</b><p>${s[1]}</p></div>`}
pick(0);let k=0;const t=setInterval(()=>{k=(k+1)%S.length;pick(k)},3200);r.onclick=()=>clearInterval(t);
</script>"""

_EXPL = _BASE + """
<style>.top{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.top input[type=number]{width:110px;font:600 18px 'IBM Plex Sans';padding:8px 10px;border:1.5px solid #9FB3C8;border-radius:4px;color:var(--ink)}
.top input[type=range]{flex:1;min-width:200px;accent-color:#E4572E}
.sim{font-size:12px;background:#FFF4DF;color:#8A5A00;padding:4px 10px;border-radius:99px;font-weight:600}
.grid{display:grid;grid-template-columns:120px 1fr 1fr;gap:14px}@media(max-width:820px){.grid{grid-template-columns:1fr}}
#col{position:relative;height:430px;border-radius:6px;overflow:hidden;border:1px solid var(--line)}#col div.f{position:absolute;left:0;right:0;font-size:10.5px;padding:3px 6px;color:#0A2342;overflow:hidden}
#bit{position:absolute;left:0;right:0;height:3px;background:var(--flare);box-shadow:0 0 0 2px #fff}#bit:after{content:"";position:absolute;right:-1px;top:-5px;border:6px solid transparent;border-left:9px solid var(--flare)}
.g{display:flex;align-items:center;gap:10px;margin:9px 0;font-size:14px}.g span:first-child{width:104px}.bar{flex:1;height:14px;background:#EDF1F5;border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;border-radius:99px;transition:width .4s,background .4s}
.g b{width:44px;text-align:right}.sh{display:flex;align-items:center;font-size:13px;margin:5px 0}.sh span{width:128px}.sh .t{flex:1;height:12px;position:relative;background:linear-gradient(90deg,#EDF1F5 50%,#EDF1F5 50%)}.sh .t i{position:absolute;top:0;height:100%}
.sh .t:before{content:"";position:absolute;left:50%;top:-2px;bottom:-2px;width:1px;background:#8DA0B5}
table{width:100%;border-collapse:collapse;font-size:13.5px}td,th{padding:7px 6px;border-bottom:1px solid var(--line);text-align:left}th{font-weight:600;color:#5B6B7F;font-size:12.5px}
.rec{margin-top:12px;padding:12px 14px;border-left:4px solid var(--flare);background:#FDF3EF;font-size:14.5px;line-height:1.5;border-radius:0 6px 6px 0}
.live{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-top:14px}.live div{background:#0A2342;color:#fff;border-radius:6px;padding:10px;text-align:center}.live b{display:block;font:700 22px 'IBM Plex Sans Condensed'}.live small{opacity:.75;font-size:11.5px}
.sync{margin-left:auto;display:flex;align-items:center;gap:8px;font-size:13px}.sw{width:38px;height:20px;border-radius:99px;background:var(--teal);position:relative;cursor:pointer;transition:.2s}.sw:after{content:"";position:absolute;top:2px;left:20px;width:16px;height:16px;border-radius:50%;background:#fff;transition:.2s}.sw.off{background:#8DA0B5}.sw.off:after{left:2px}
#map{width:100%;height:150px;background:#EAF1F6;border-radius:6px}
</style>
<div class="card">
<div class="top"><label><b>Depth (m)</b></label><input type="number" id="n" min="0" max="4600" value="2650"><input type="range" id="s" min="0" max="4600" value="2650">
<span class="sim">Simulated data</span><div class="sync"><span id="st">Cloud: synced</span><div class="sw" id="sw" title="Switch between cloud and local server"></div></div></div>
<div class="grid"><div id="col"></div>
<div><h4>Risk probability at this depth</h4><div id="g"></div><h4 style="margin-top:18px">Why (SHAP-style)</h4><div id="sh"></div></div>
<div><h4>Similar wells with events here</h4><table><thead><tr><th>Well</th><th>Match</th><th>Event</th></tr></thead><tbody id="tb"></tbody></table>
<h4 style="margin-top:16px">Well locations</h4><svg id="map" viewBox="0 0 300 150"></svg></div></div>
<div class="rec" id="rec"></div>
<div class="live" id="live"></div></div>
<script>
const F=[["Alluvium",0,350,"#EBDDB5",[.05,.05,.12,.04]],["Tipam Sandstone",350,1400,"#F0C987",[.1,.08,.3,.1]],["Girujan Clay",1400,2300,"#C9B29B",[.3,.1,.15,.4]],["Surma Shale",2300,3200,"#9FA9B5",[.45,.2,.2,.5]],["Barail Group",3200,4000,"#8FB1B0",[.3,.35,.4,.3]],["Kopili Shale",4000,4600,"#6E7F96",[.4,.55,.25,.45]]];
const R=["Stuck pipe","Kick","Lost circulation","Tight hole"];
const W=[["NW-014",[62,40],"Stuck pipe"],["NW-027",[120,88],"Tight hole"],["NW-033",[180,52],"Lost circulation"],["NW-041",[232,100],"Kick"],["NW-052",[90,120],"Stuck pipe"]];
const FE=["Pore pressure gradient","Mud weight","Torque","Hole inclination","ROP","Lithology: shale"];
const n=document.getElementById('n'),s=document.getElementById('s');let cur=0;
const col=document.getElementById('col');F.forEach(f=>{const e=document.createElement('div');e.className='f';e.style.cssText=`top:${f[1]/4600*100}%;height:${(f[2]-f[1])/4600*100}%;background:${f[3]}`;e.textContent=f[0];col.appendChild(e)});
const bit=document.createElement('div');bit.id='bit';col.appendChild(bit);
const cl=v=>v>.55?'#E4572E':v>.35?'#F2A33A':'#139A9A';
function upd(d){d=Math.max(0,Math.min(4600,+d||0));n.value=d;s.value=d;bit.style.top=d/4600*100+'%';
const f=F.find(x=>d>=x[1]&&d<=x[2])||F[5];const dep=d/4600;
const p=f[4].map((b,i)=>Math.min(.95,b+.18*dep+.07*Math.sin(d/180+i*1.7)));
document.getElementById('g').innerHTML=`<div style="font-size:13px;margin-bottom:4px">Formation: <b>${f[0]}</b></div>`+p.map((v,i)=>`<div class="g"><span>${R[i]}</span><div class="bar"><i style="width:${v*100}%;background:${cl(v)}"></i></div><b>${Math.round(v*100)}%</b></div>`).join('');
const top=p.indexOf(Math.max(...p));
const sv=FE.map((x,i)=>Math.sin(d/260+i*2.1)*(.9-i*.1));
document.getElementById('sh').innerHTML=FE.map((x,i)=>{const v=sv[i];return `<div class="sh"><span>${x}</span><div class="t"><i style="${v>0?'left:50%':'right:50%'};width:${Math.abs(v)*50}%;background:${v>0?'#E4572E':'#139A9A'}"></i></div></div>`}).join('')+'<small style="color:#5B6B7F">Orange raises risk, teal lowers it.</small>';
const ws=W.map((w,i)=>[w[0],Math.round(94-i*6-Math.abs(Math.sin(d/300+i))*8),w[2],w[1]]).sort((a,b)=>b[1]-a[1]);
document.getElementById('tb').innerHTML=ws.slice(0,4).map(w=>`<tr><td><b>${w[0]}</b></td><td>${w[1]}%</td><td>${w[2]}</td></tr>`).join('');
document.getElementById('map').innerHTML='<g stroke="#C3D2DF" stroke-width=".6">'+[1,2,3,4,5].map(i=>`<line x1="${i*50}" y1="0" x2="${i*50}" y2="150"/><line x1="0" y1="${i*25}" x2="300" y2="${i*25}"/>`).join('')+'</g>'+'<circle cx="150" cy="75" r="7" fill="#0A2342"/><text x="160" y="72" font-size="9" fill="#0A2342">Current</text>'+ws.map((w,i)=>`<circle cx="${w[3][0]+ (i%2?20:0)}" cy="${w[3][1]}" r="${3+w[1]/30}" fill="${i<2?'#E4572E':'#139A9A'}" fill-opacity=".8"/><text x="${w[3][0]+(i%2?20:0)+8}" y="${w[3][1]+3}" font-size="8" fill="#0A2342">${w[0]}</text>`).join('');
const adv=["Reduce time stationary, run a wiper trip and keep overpull limits in view.","Check mud weight against pore pressure and verify flow with a flow check at connections.","Prepare lost-circulation material and reduce pump rate before entering this interval.","Ream tight spots slowly and review hole cleaning and torque trend."];
document.getElementById('rec').innerHTML=`<b>${R[top]} is the highest risk at ${d} m (${Math.round(p[top]*100)}%).</b> ${adv[top]}`}
n.oninput=()=>upd(n.value);s.oninput=()=>upd(s.value);
const L=[["WOB","kN",120],["RPM","rpm",95],["SPP","kPa",18500],["ROP","m/h",14],["Torque","kN·m",11]];
const live=document.getElementById('live');
function tick(){live.innerHTML=L.map(l=>`<div><b>${(l[2]*(1+(Math.random()-.5)*.08)).toFixed(l[2]<30?1:0)}</b><small>${l[0]} (${l[1]}), live eRTMAC</small></div>`).join('')}
tick();setInterval(tick,1200);
let off=false,q=0;const sw=document.getElementById('sw'),st=document.getElementById('st');
sw.onclick=()=>{off=!off;sw.classList.toggle('off',off);q=off?3:0;st.textContent=off?'Local server: offline, 3 changes queued':'Cloud: synced'};
setInterval(()=>{if(off){q++;st.textContent=`Local server: offline, ${q} changes queued`}},4000);
upd(2650);
</script>"""


def _embed(html, height, scrolling=False):
    # st.iframe exists in newer Streamlit; components.html in older ones.
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=scrolling)


def pipeline_component():
    _embed(_PIPE, 210)


def explorer_component():
    _embed(_EXPL, 900, scrolling=True)
