"""Self-contained interactive hero (animated skyline, count-up stats, clickable AQI scale)."""
from __future__ import annotations

import json

from aqi import assets
from aqi.config import AQI_CATEGORIES, AQI_STATIONS, METEO_STATIONS
from aqi.content import AQI_ROWS, METEO_ROWS

TITLE = "Spatiotemporal Air Quality Index (AQI) Modeling in DKI Jakarta"
SUBTITLE = "Categorical Boosting with an Attention Mechanism"

_TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}body{margin:0;padding:2px;font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;color:#0B1B33;background:transparent}
.hero{position:relative;overflow:hidden;border-radius:24px;min-height:300px;background:#0B1B33;color:#fff;isolation:isolate}
.hero svg.sky{position:absolute;inset:0;width:100%;height:100%;z-index:-1}
.layer{transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.smog{animation:drift 22s ease-in-out infinite alternate}.tw{animation:tw 3.2s ease-in-out infinite}
.copy{padding:44px 40px 120px;max-width:680px;background:linear-gradient(90deg,rgba(11,27,51,.82),rgba(11,27,51,0))}
.eyebrow{font-size:12px;font-weight:700;letter-spacing:.14em;color:#8FB4FF;margin-bottom:12px}
h1{margin:0 0 10px;font-size:clamp(22px,4.2vw,34px);line-height:1.2;letter-spacing:-.02em;font-weight:800}
.sub{margin:0;color:#C3D2EA;font-size:clamp(13px,2vw,16px)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:12px 0}
.stat,.panelcard{background:#fff;border:1px solid #E3E8F1;border-radius:18px;padding:18px 20px;transition:transform .25s ease,box-shadow .25s ease}
.stat:hover,.panelcard:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(11,27,51,.10)}
.stat b{display:block;font-size:clamp(20px,3vw,30px);font-weight:800;letter-spacing:-.02em}
.stat span,.muted{font-size:12px;font-weight:600;color:#5B6B86}
.panelcard h2{margin:0 0 4px;font-size:16px;font-weight:800}
.scale{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 18px}
.chip{font:600 13px/1 inherit;font-family:inherit;min-height:40px;padding:0 16px;border-radius:999px;border:1px solid #E3E8F1;background:#F4F6FB;color:#0B1B33;cursor:pointer;transition:all .2s}
.chip:hover{background:#E6EDFF}.chip.on{background:#0B1B33;border-color:#0B1B33;color:#fff}
.chip:focus-visible{outline:3px solid #8FB4FF;outline-offset:2px}
.track{position:relative;height:12px;border-radius:99px;margin:6px 0 22px;background:linear-gradient(90deg,#22A06B 0 20%,#E8B100 20% 40%,#F97316 40% 60%,#DC2626 60% 80%,#9333EA 80%)}
.needle{position:absolute;top:-6px;width:24px;height:24px;margin-left:-12px;border-radius:50%;border:4px solid #fff;box-shadow:0 2px 10px rgba(11,27,51,.35);transition:left .7s cubic-bezier(.2,.8,.2,1),background .4s}
#panel{min-height:84px}#panel.flip{animation:fade .5s ease both}
#cat{font-size:22px;font-weight:800;margin-right:10px}#range{font-weight:700;color:#5B6B86}
#advice{margin:6px 0 0;font-size:14px;line-height:1.6;color:#33435F}
@keyframes drift{from{transform:translateX(-30px)}to{transform:translateX(40px)}}
@keyframes tw{0%,100%{opacity:.15}50%{opacity:.95}}@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (max-width:640px){.copy{padding:28px 20px 90px}.hero{min-height:250px;border-radius:20px}.stats{grid-template-columns:1fr 1fr}.stat{padding:14px 16px}.panelcard{padding:16px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body>
<section class="hero" aria-label="Project overview">__SKYLINE__
<div class="copy"><div class="eyebrow">PM2.5 FORECASTING · DKI JAKARTA</div><h1>__TITLE__</h1><p class="sub">__SUBTITLE__</p></div></section>
<section class="stats" aria-label="Dataset at a glance">__STATS__</section>
<section class="panelcard"><h2>Explore the AQI scale</h2><div class="muted">Tap a category — it also cycles automatically</div>
<div class="scale" role="group" aria-label="AQI categories">__CHIPS__</div>
<div class="track" aria-hidden="true"><div class="needle" id="needle"></div></div>
<div id="panel" aria-live="polite"><span id="cat"></span><span id="range"></span><p id="advice"></p></div></section>
<script>
(function(){
const CATS=__DATA__;
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
function fit(){try{window.frameElement.style.height=document.documentElement.scrollHeight+'px'}catch(e){}}
function count(el){const end=+el.dataset.count,fmt=n=>n.toLocaleString('en-US');
 if(reduce){el.textContent=fmt(end);return}
 const t0=performance.now();(function f(t){const p=Math.min(1,(t-t0)/1400);el.textContent=fmt(Math.round(end*(1-Math.pow(1-p,3))));if(p<1)requestAnimationFrame(f)})(t0)}
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){count(e.target);io.unobserve(e.target)}}),{threshold:.3});
$$('[data-count]').forEach(el=>io.observe(el));
let cur=0,timer=null;
function select(i,user){cur=i;const c=CATS[i];
 $$('.chip').forEach((b,j)=>{b.classList.toggle('on',j===i);b.setAttribute('aria-pressed',String(j===i))});
 const n=$('#needle');n.style.left=((i+.5)*20)+'%';n.style.background=c.color;
 $('#cat').textContent=c.label;$('#cat').style.color=c.color;$('#range').textContent='AQI '+c.range;$('#advice').textContent=c.advice;
 const p=$('#panel');p.classList.remove('flip');void p.offsetWidth;p.classList.add('flip');
 if(user&&timer){clearInterval(timer);timer=null}}
$$('.chip').forEach((b,i)=>b.addEventListener('click',()=>select(i,true)));
if(!reduce)timer=setInterval(()=>select((cur+1)%CATS.length),4200);
select(0);
const hero=$('.hero'),layers=$$('.layer');
if(!reduce)hero.addEventListener('pointermove',e=>{const r=hero.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5;
 layers.forEach((l,i)=>l.style.transform='translateX('+(x*(i+1)*-16)+'px)')});
addEventListener('load',fit);addEventListener('resize',fit);new ResizeObserver(fit).observe(document.body);fit();
})();
</script></body></html>"""


def _stat(label: str, value: int) -> str:
    return f'<div class="stat"><b data-count="{value}">0</b><span>{label}</span></div>'


def build_hero_html() -> str:
    skyline = assets.read_text("hero_skyline.svg").replace("<svg ", '<svg class="sky" ', 1)
    stats = "".join([
        _stat("AQI rows", AQI_ROWS), _stat("Meteorology rows", METEO_ROWS),
        _stat("Monitoring stations", len(AQI_STATIONS) + len(METEO_STATIONS)), _stat("Models benchmarked", 8),
    ])
    chips = "".join(
        f'<button class="chip" type="button" aria-pressed="false">{c["label"]}</button>' for c in AQI_CATEGORIES)
    return (_TEMPLATE.replace("__SKYLINE__", skyline).replace("__TITLE__", TITLE)
            .replace("__SUBTITLE__", SUBTITLE).replace("__STATS__", stats).replace("__CHIPS__", chips)
            .replace("__DATA__", json.dumps(list(AQI_CATEGORIES))))
