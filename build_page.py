#!/usr/bin/env python3
"""data.json から GitHub Pages 用 index.html を生成する。
STAR_DB_URL は Firebase Realtime Database のベースURL（__STAR_DB_URL__ は未設定プレースホルダ）。"""
import json, pathlib

HERE = pathlib.Path(__file__).parent
data = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
data_js = json.dumps(data, ensure_ascii=False)
STAR_DB_URL = "https://dousei-bukken-stars-default-rtdb.asia-southeast1.firebasedatabase.app"

TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>同棲物件の候補リスト</title>
<style>
  :root{
    --bg:#FAF7F1; --card:#FFFFFF; --ink:#2B2620; --sub:#7A7264; --line:#E7DFD2;
    --ok:#2E7D4F; --okbg:#E7F3EC; --ask:#9A6B12; --askbg:#FBF1DA; --sub2:#6B7280; --sub2bg:#EFF1F4;
    --new:#C2410C; --newbg:#FDEBDD; --room:#1D4ED8; --roombg:#E3EBFD; --upd:#6D28D9; --updbg:#EFE7FC;
    --star:#E8A812; --danger:#C62828;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);font-family:"Hiragino Kaku Gothic ProN","Hiragino Sans","Noto Sans JP",sans-serif;-webkit-text-size-adjust:100%}
  .wrap{max-width:860px;margin:0 auto;padding:20px 14px 60px}
  header h1{font-size:22px;margin:4px 0 6px;letter-spacing:.02em}
  .meta{color:var(--sub);font-size:13px;line-height:1.7}
  .meta b{color:var(--ink)}
  .hint{font-size:12px;color:var(--sub);margin-top:2px}
  .changes{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:16px 0}
  .changes h2{font-size:14px;margin:0 0 8px}
  .changes .row{font-size:13px;line-height:1.8}
  .filters{position:sticky;top:0;background:var(--bg);padding:10px 0 8px;z-index:5}
  .chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
  .chip{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 12px;font-size:13px;cursor:pointer;color:var(--ink)}
  .chip.on{background:var(--ink);color:#fff;border-color:var(--ink)}
  .chip.star.on{background:var(--star);border-color:var(--star);color:#fff}
  .search{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:10px;font-size:14px;background:var(--card)}
  .bldg{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:14px 14px 8px;margin:12px 0}
  .bldg h3{font-size:16px;margin:0 0 2px}
  .bldg .loc{font-size:12.5px;color:var(--sub);line-height:1.6}
  .room{border-top:1px dashed var(--line);padding:10px 0 8px;margin-top:10px;position:relative}
  .room:first-of-type{border-top:none;margin-top:6px}
  .roomtop{display:flex;align-items:flex-start;gap:8px}
  .roomname{font-weight:700;font-size:14.5px}
  .badges{display:flex;flex-wrap:wrap;gap:4px;margin:4px 0}
  .badge{font-size:11px;padding:2px 8px;border-radius:999px;font-weight:600}
  .b-ok{background:var(--okbg);color:var(--ok)} .b-ask{background:var(--askbg);color:var(--ask)} .b-sub{background:var(--sub2bg);color:var(--sub2)}
  .b-new{background:var(--newbg);color:var(--new)} .b-room{background:var(--roombg);color:var(--room)} .b-upd{background:var(--updbg);color:var(--upd)}
  .price{font-size:15px;font-weight:700}
  .price small{font-weight:400;color:var(--sub);font-size:12px}
  .facts{font-size:13px;color:#4A4438;line-height:1.75}
  .note{font-size:12.5px;color:var(--sub);line-height:1.7}
  .expiry{font-size:12px;color:var(--sub)}
  .expiry.soon{color:var(--ask);font-weight:700}
  .expiry.urgent{color:var(--danger);font-weight:700}
  .starbtn{margin-left:auto;flex:none;width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:#fff;font-size:22px;line-height:1;color:#CBC2B2;cursor:pointer}
  .starbtn.on{color:var(--star);border-color:var(--star);background:#FFF8E1}
  .srclink{display:inline-block;margin-top:4px;font-size:12.5px;color:var(--room);text-decoration:none;border:1px solid var(--roombg);padding:4px 10px;border-radius:8px;background:#F5F8FF}
  .empty{color:var(--sub);text-align:center;padding:30px 0;font-size:14px}
  footer{color:var(--sub);font-size:12px;text-align:center;margin-top:28px;line-height:1.8}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>同棲物件の候補リスト</h1>
    <div class="meta" id="summary"></div>
    <div class="hint">★を付けると、二人の画面で共有されます。</div>
  </header>

  <section class="changes" id="changes"></section>

  <div class="filters">
    <div class="chips" id="statusChips">
      <button class="chip on" data-status="">すべて</button>
      <button class="chip" data-status="全条件クリア">全条件クリア</button>
      <button class="chip" data-status="要問合せ">要問合せ</button>
      <button class="chip" data-status="予備">予備</button>
      <button class="chip star" id="starChip">★のみ</button>
      <button class="chip" id="tokyoChip">東京のみ</button>
    </div>
    <div class="chips" id="changeChips">
      <button class="chip on" data-change="">変更：すべて</button>
      <button class="chip" data-change="new">新規のみ</button>
      <button class="chip" data-change="room">別部屋追加のみ</button>
      <button class="chip" data-change="upd">情報更新のみ</button>
    </div>
    <input class="search" id="search" type="search" placeholder="建物名・エリア・駅で検索">
  </div>

  <main id="list"></main>
  <div class="empty" id="empty" style="display:none">条件に合う物件がありません</div>

  <footer>条件：蒲田まで電車で1時間以内／家賃＋管理費14万円以内／2DK・2LDK・3DK・3LDK／独立洗面台・ウォシュレット・ガス2口以上（ガス栓のみも可）／普通借家<br>掲載期限は募集サイト側の表示に基づきます。最新の募集状況は各リンク先でご確認ください。</footer>
</div>

<script>
const DATA = __DATA_JSON__;
const DB_URL = "__STAR_DB_URL__";
const STAR_URL = DB_URL.includes("__STAR") ? null : DB_URL.replace(/\/$/,"") + "/stars.json";
const LS_KEY = "dousei-bukken-stars-v1";

let stars = {};
try { stars = JSON.parse(localStorage.getItem(LS_KEY) || "{}") || {}; } catch(e){ stars = {}; }

const yen = n => (Math.round(n*10000)).toLocaleString("ja-JP");
function fmtMan(n){ return (Math.round(n*100)/100).toString(); }
function priceHTML(r){
  if (r.rent == null && r.total != null) return `<span class="price">合計 ${fmtMan(r.total)}万円</span> <small>（内訳は未確認）</small>`;
  if (r.rent == null) return `<span class="price">家賃は未確認</span>`;
  let s = `<span class="price">${fmtMan(r.total != null ? r.total : r.rent)}万円</span>`;
  if (r.fee != null) s += ` <small>（賃料${fmtMan(r.rent)}万円＋管理費${yen(r.fee)}円）</small>`;
  else s += ` <small>（賃料${fmtMan(r.rent)}万円・管理費は未確認）</small>`;
  return s;
}
function expiryHTML(r){
  if (!r.expiry) return "";
  const [y,m,d] = r.expiry.split("-").map(Number);
  const exp = new Date(y, m-1, d); const now = new Date(); now.setHours(0,0,0,0);
  const days = Math.round((exp - now)/86400000);
  let cls = "expiry", tail = "";
  if (days <= 3){ cls += " urgent"; tail = `（あと${days}日）`; }
  else if (days <= 7){ cls += " soon"; tail = `（あと${days}日）`; }
  return `<span class="${cls}">掲載期限 ${m}/${d}${tail}</span>`;
}
function badgeCls(change){
  if (!change) return "";
  if (change.startsWith("新規")) return "b-new";
  if (change === "別部屋追加") return "b-room";
  return "b-upd";
}
function statusCls(s){ return s === "全条件クリア" ? "b-ok" : (s === "要問合せ" ? "b-ask" : "b-sub"); }
function regionOf(area){
  const a = area || "";
  if (a.includes("川崎市") || a.includes("横浜市")) return "kawasaki";
  if (a.includes("さいたま市") || a.includes("埼玉県")) return "saitama";
  return "tokyo";
}
function regionRank(area){ const r = regionOf(area); return r === "tokyo" ? 0 : (r === "kawasaki" ? 1 : 2); }

function renderSummary(){
  const rooms = DATA.buildings.flatMap(b => b.rooms);
  const cnt = s => rooms.filter(r => r.status === s).length;
  document.getElementById("summary").innerHTML =
    `${DATA.updated.replace(/-/g,"/")} 時点 ・ <b>${DATA.buildings.length}棟・全${rooms.length}部屋</b>（全条件クリア ${cnt("全条件クリア")}件 ／ 要問合せ ${cnt("要問合せ")}件 ／ 予備 ${cnt("予備")}件）`;
}
function renderChanges(){
  const groups = [["新規 11/26","新規"],["別部屋追加","別部屋追加"],["情報更新","情報更新"]];
  const rooms = [];
  DATA.buildings.forEach(b => b.rooms.forEach(r => rooms.push({b, r})));
  let html = "<h2>今回の変更点</h2>";
  let any = false;
  for (const [tag] of groups){
    const items = rooms.filter(x => x.r.change === tag);
    if (!items.length) continue;
    any = true;
    const names = items.map(x => x.b.name + (x.r.room ? " " + x.r.room : "")).join("、");
    html += `<div class="row"><span class="badge ${badgeCls(tag)}">${tag}</span> ${names}</div>`;
  }
  document.getElementById("changes").innerHTML = any ? html : "<h2>今回の変更点</h2><div class='row'>変更はありません</div>";
}

let filterStatus = "", filterStar = false, filterText = "", filterTokyo = false, filterChange = "";
function roomMatches(b, r){
  if (filterChange === "new" && !(r.change && r.change.startsWith("新規"))) return false;
  if (filterChange === "room" && r.change !== "別部屋追加") return false;
  if (filterChange === "upd" && r.change !== "情報更新") return false;
  if (filterTokyo && regionOf(b.area) !== "tokyo") return false;
  if (filterStatus && r.status !== filterStatus) return false;
  if (filterStar && !stars[r.id]) return false;
  if (filterText){
    const hay = (b.name + " " + (b.area||"") + " " + (b.station||"") + " " + (r.room||"")).toLowerCase();
    if (!hay.includes(filterText.toLowerCase())) return false;
  }
  return true;
}
function renderList(){
  const main = document.getElementById("list");
  let html = "", shown = 0;
  const ordered = [...DATA.buildings].sort((x, y) => regionRank(x.area) - regionRank(y.area));
  for (const b of ordered){
    const rs = b.rooms.filter(r => roomMatches(b, r));
    if (!rs.length) continue;
    shown += rs.length;
    html += `<section class="bldg"><h3>${b.name}</h3><div class="loc">${b.area || ""}${b.station ? " ・ " + b.station : ""}</div>`;
    for (const r of rs){
      const on = !!stars[r.id];
      html += `<div class="room">
        <div class="roomtop">
          <div>
            ${r.room ? `<span class="roomname">${r.room}</span> ` : ""}<span class="facts">${r.layout || ""}${r.size ? " ・ " + r.size + "㎡" : ""}</span>
            <div class="badges">
              <span class="badge ${statusCls(r.status)}">${r.status}</span>
              ${r.change ? `<span class="badge ${badgeCls(r.change)}">${r.change}</span>` : ""}
            </div>
          </div>
          <button class="starbtn ${on ? "on" : ""}" data-star="${r.id}" aria-label="お気に入り">${on ? "★" : "☆"}</button>
        </div>
        <div>${priceHTML(r)}</div>
        <div class="facts">${r.kamata_min ? "蒲田まで" + r.kamata_min : ""} ${expiryHTML(r)}</div>
        ${r.note ? `<div class="note">${r.note}</div>` : ""}
        ${r.url ? `<a class="srclink" href="${r.url}" target="_blank" rel="noopener">掲載ページを見る（${r.source || "リンク"}）</a>` : ""}
      </div>`;
    }
    html += `</section>`;
  }
  main.innerHTML = html;
  document.getElementById("empty").style.display = shown ? "none" : "block";
  main.querySelectorAll("[data-star]").forEach(btn => btn.addEventListener("click", () => toggleStar(btn.dataset.star)));
}

/* ===== ★の共有（Firebase Realtime Database の REST API） ===== */
function saveLocal(){ try { localStorage.setItem(LS_KEY, JSON.stringify(stars)); } catch(e){} }
let putTimer = null;
function schedulePut(){
  if (!STAR_URL) return;
  clearTimeout(putTimer);
  putTimer = setTimeout(() => {
    fetch(STAR_URL, { method:"PUT", headers:{"Content-Type":"application/json"}, body: JSON.stringify(stars) }).catch(()=>{});
  }, 500);
}
function mergeFromServer(server){
  if (!server || typeof server !== "object") return false;
  let changed = false;
  for (const k of Object.keys(server)) if (server[k] && !stars[k]){ stars[k] = true; changed = true; }
  return changed;
}
function syncFromServer(){
  if (!STAR_URL) return;
  fetch(STAR_URL).then(r => r.json()).then(server => {
    if (mergeFromServer(server)){ saveLocal(); renderList(); schedulePut(); }
  }).catch(()=>{});
}
function toggleStar(id){
  if (stars[id]) delete stars[id]; else stars[id] = true;
  saveLocal(); renderList(); schedulePut();
}
document.addEventListener("visibilitychange", () => { if (!document.hidden) syncFromServer(); });

/* ===== フィルター ===== */
document.getElementById("statusChips").addEventListener("click", e => {
  const btn = e.target.closest("[data-status]");
  if (!btn) return;
  document.querySelectorAll("#statusChips [data-status]").forEach(c => c.classList.remove("on"));
  btn.classList.add("on");
  filterStatus = btn.dataset.status;
  renderList();
});
document.getElementById("changeChips").addEventListener("click", e => {
  const btn = e.target.closest("[data-change]");
  if (!btn) return;
  document.querySelectorAll("#changeChips [data-change]").forEach(c => c.classList.remove("on"));
  btn.classList.add("on");
  filterChange = btn.dataset.change;
  renderList();
});
document.getElementById("starChip").addEventListener("click", e => {
  filterStar = !filterStar;
  e.currentTarget.classList.toggle("on", filterStar);
  renderList();
});
document.getElementById("tokyoChip").addEventListener("click", e => {
  filterTokyo = !filterTokyo;
  e.currentTarget.classList.toggle("on", filterTokyo);
  renderList();
});
document.getElementById("search").addEventListener("input", e => { filterText = e.target.value.trim(); renderList(); });

renderSummary(); renderChanges(); renderList(); syncFromServer();
</script>
</body>
</html>
"""

html = TEMPLATE.replace("__DATA_JSON__", data_js).replace("__STAR_DB_URL__", STAR_DB_URL)
out = HERE / "index.html"
out.write_text(html, encoding="utf-8")
print("wrote", out, len(html), "bytes")
