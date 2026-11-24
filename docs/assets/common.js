/* MiraiBoard 共通: データ・ヘッダー・小さな部品 */
const MB = window.MB;
const OKR = MB.okr, KR = OKR.kr_index;
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const ext = (u, t) => u ? `<a class="u" href="${esc(u)}" target="_blank" rel="noopener">${esc(t || u)}</a>` : esc(t || '');
const srcHtml = s => s ? `出典: <a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a>${s.checked ? `（${esc(s.checked)} 確認）` : ''}` : '<span style="color:var(--warn)">出典未確認</span>';
const OKR_SRC = { name: `チームみらい 公開OKR ${OKR.period}（更新日 ${OKR.updated_at}）`, url: OKR.source.url };

/* 状態は色だけに頼らず、形（アイコン）と文字でも示す */
const SC = { '達成': 'done', '順調': 'ok', '注意': 'warn', '未着手': 'todo' };
const ICON = {
  done: '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.5 6.3l2.3 2.2 4.7-5"/></svg>',
  ok: '<svg viewBox="0 0 12 12"><circle cx="6" cy="6" r="3.2" fill="currentColor"/></svg>',
  warn: '<svg viewBox="0 0 12 12" fill="currentColor"><path d="M6 1.5l4.6 8.4H1.4z"/></svg>',
  todo: '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="6" cy="6" r="3.6"/></svg>',
};
const st = s => { const c = SC[s] || 'todo'; return `<span class="st ${c}">${ICON[c]}${esc(s)}</span>`; };
const mk = id => { const k = KR[id]; if (!k) return ''; const c = SC[k.status] || 'todo';
  return `<span class="mk ${c}" tabindex="0" data-tip="${esc(`<b>${k.summary}</b>${k.owner}・${k.status}${k.progress ? '・' + k.progress : ''}`)}">${ICON[c]}</span>`; };
const ratio = p => { const m = /^([\d.]+)\/([\d.]+)/.exec(p || ''); if (!m) return null; const v = +m[1] / +m[2]; return isFinite(v) ? v : null; };
const legend = () => `<div class="legend">状態: ${['達成', '順調', '注意', '未着手'].map(st).join('')}</div>`;

/* ヘッダーとフッター */
const PAGES = [['index.html', '概要'], ['flow.html', '政策づくりの現場'], ['people.html', '議員12人'], ['org.html', '体制と目標'], ['timeline.html', '年表'], ['more.html', '理念・求人・出典']];
function chrome(active) {
  const logo = '<svg width="28" height="28" viewBox="0 0 28 28"><defs><linearGradient id="mbLogo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b8a66"/><stop offset="1" stop-color="#6fe4c2"/></linearGradient></defs><rect width="28" height="28" rx="8" fill="url(#mbLogo)"/><path d="M7 19V9l7 6 7-6v10" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.body.insertAdjacentHTML('afterbegin', `<header class="bar"><div class="w"><a class="brand" href="index.html">${logo}MiraiBoard</a><nav class="tabsnav">${PAGES.map(([h, t]) => `<a href="${h}" class="${h === active ? 'on' : ''}">${t}</a>`).join('')}</nav><span class="stamp">更新 ${esc(MB.updated)}</span></div></header>`);
  document.body.insertAdjacentHTML('beforeend', `<footer class="ft"><div class="w">MiraiBoard は、チームみらいの公開情報をまとめた非公式の台帳です。すべての項目に出典があります。見えるのは表に出た動きだけで、党内の作業や議員事務所の実務はほとんど見えません。最終更新 ${esc(MB.updated)}。</div></footer><div class="tip" id="tip"></div>`);
  const tip = $('#tip');
  const show = e => { const t = e.target.closest('[data-tip]'); if (!t) { tip.classList.remove('on'); return; } tip.innerHTML = t.dataset.tip.replace(/&lt;(\/?b)&gt;/g, '<$1>'); const r = t.getBoundingClientRect(); tip.classList.add('on'); const x = Math.min(innerWidth - tip.offsetWidth - 12, Math.max(12, r.left + r.width / 2 - tip.offsetWidth / 2)); tip.style.left = x + 'px'; tip.style.top = (r.top - tip.offsetHeight - 10 < 8 ? r.bottom + 10 : r.top - tip.offsetHeight - 10) + 'px'; };
  addEventListener('mouseover', show); addEventListener('focusin', show); addEventListener('scroll', () => tip.classList.remove('on'), { passive: true });
}

/* 議員の写真（読めないときは頭文字） */
const photo = m => `<div class="ph-img"><img src="${esc(m.photo)}" alt="${esc(m.name)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.outerHTML='<div class=&quot;ini&quot;>${esc(m.name.slice(0, 1))}</div>'"></div>`;
const roles = m => m.party_roles.filter(r => !r.startsWith('（')).map(r => r.replace(/^チームみらい/, ''));
const officeOf = id => OKR.offices.find(o => o.id === id);
