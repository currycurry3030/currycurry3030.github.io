/* Stanford AI study engine.
 *
 * A day page is a single shell (`dayNN_YYYY-MM-DD.html`) that loads its content
 * from `dayNN_modules.js` (window.STUDY_DAY) and renders it here. PC and mobile
 * share the same file: the layout follows the viewport by default and can be
 * pinned with the header toggle or a `?layout=pc|mobile` query parameter.
 */
(() => {
  const D = window.STUDY_DAY;
  if (!D) {
    document.body.innerHTML = '<p>Study data load failed.</p>';
    return;
  }

  const root = document.getElementById('study-app');
  const esc = (s) =>
    String(s).replace(
      /[&<>"']/g,
      (c) =>
        ({
          '&': '&amp;',
          '<': '&lt;',
          '>': '&gt;',
          '"': '&quot;',
          "'": '&#39;'
        })[c]
    );

  /* ---------------- layout preference ---------------- */

  const LAYOUT_KEY = 'stanford-study-layout';
  const LAYOUTS = ['auto', 'pc', 'mobile'];
  const NARROW = window.matchMedia('(max-width: 780px)');

  const readLayout = () => {
    const fromQuery = new URLSearchParams(location.search).get('layout');
    if (LAYOUTS.includes(fromQuery)) return fromQuery;
    const stored = localStorage.getItem(LAYOUT_KEY);
    return LAYOUTS.includes(stored) ? stored : 'auto';
  };

  let layout = readLayout();

  const isMobile = () => (layout === 'auto' ? NARROW.matches : layout === 'mobile');

  const layoutLabel = () =>
    ({
      auto: '🔄 자동 레이아웃',
      pc: '💻 PC 고정',
      mobile: '📱 모바일 고정'
    })[layout];

  function applyLayout() {
    document.body.classList.toggle('mobile', isMobile());
    const btn = document.getElementById('layoutBtn');
    if (btn) btn.textContent = layoutLabel();
  }

  function cycleLayout() {
    layout = LAYOUTS[(LAYOUTS.indexOf(layout) + 1) % LAYOUTS.length];
    localStorage.setItem(LAYOUT_KEY, layout);
    applyLayout();
  }

  NARROW.addEventListener('change', applyLayout);

  /* ---------------- progress ---------------- */

  let done = new Set(JSON.parse(localStorage.getItem(D.progressKey) || '[]'));
  let cur = Math.max(
    0,
    Math.min(D.modules.length - 1, Number(location.hash.replace('#m', '')) || 0)
  );

  /* ---------------- rendering ---------------- */

  const moduleHtml = (m, i) => `<section class="module" id="m${i}">
    <div class="head"><span class="badge">${esc(m.sourceLabel)}</span><h2>${esc(m.title)}</h2></div>
    <div class="card core"><h3>🟢 핵심 · 1시간 핵심 코스</h3><ul>${m.core
      .map((x) => `<li>${esc(x)}</li>`)
      .join('')}</ul></div>
    <div class="card easy"><h3>🔵 쉬운 한국어 설명 · 1시간 핵심 코스</h3><p>${esc(m.easy)}</p></div>
    <div class="card prof"><h3>🟣 교수 설명 복원 · Deep Dive</h3><p>${esc(m.professor)}</p></div>
    <div class="card work"><h3>🟠 AI/Agent 실무 연결 · Deep Dive</h3><p>${esc(m.practical)}</p></div>
    <div class="card"><h3>📌 핵심용어</h3><div class="terms">${m.terms
      .map((x) => `<div class="term"><b>${esc(x[0])}</b>${esc(x[1])}</div>`)
      .join('')}</div></div>
    <div class="card"><h3>🧠 Quiz · Active Recall</h3>${m.quiz
      .map(
        (q, j) =>
          `<div class="q"><b>Q${j + 1}. ${esc(q[0])}</b><br><button class="answer-btn" data-toggle-answer>정답 보기</button><div class="ans">${esc(q[1])}</div></div>`
      )
      .join('')}</div>
    <button class="done" data-done="${i}">${done.has(i) ? '✓ 완료' : '○ 완료 처리'}</button>
    <div class="foot">
      <button class="navbtn" data-go="${i - 1}" ${i === 0 ? 'disabled' : ''}>← 이전</button>
      <button class="navbtn" data-go="${i + 1}" ${i === D.modules.length - 1 ? 'disabled' : ''}>다음 →</button>
    </div>
  </section>`;

  function shell() {
    root.innerHTML = `<div class="app">
      <aside class="side">
        <h1>${esc(D.course)} · Day ${String(D.day).padStart(2, '0')}</h1>
        <div class="small">${esc(D.date)} · ${esc(D.title)}</div>
        <div class="bar"><div id="bar"></div></div>
        <div class="small" id="pt"></div>
        <div class="mobileNav"><select id="sel"></select></div>
        <div class="module-nav" id="nav"></div>
      </aside>
      <main class="main">
        <section class="hero">
          <div class="small" style="color:#fff">${esc(D.course)} · ${esc(D.date)}</div>
          <h2>${esc(D.title)}</h2>
          <p>${esc(D.subtitle)}</p>
          <div class="acts">
            <a class="btn" href="../index.html">← 30일 마스터</a>
            <button class="btn" id="layoutBtn" type="button"></button>
            ${D.sourceLinks
              .map(
                (x) =>
                  `<a class="btn" target="_blank" rel="noopener" href="${esc(x.url)}">${esc(x.label)} ↗</a>`
              )
              .join('')}
          </div>
          <div class="mode-note"><b>학습 모드:</b> 1시간 핵심 코스는 핵심·쉬운 설명·Quiz 중심. 시간이 있으면 교수 설명 복원·실무 연결·용어까지 Deep Dive.</div>
        </section>
        <section class="sys"><b>오늘의 시스템 위치 · ${esc(D.systemPosition)}</b><br>${esc(D.systemMapping)}</section>
        <div id="mods">${D.modules.map(moduleHtml).join('')}</div>
      </main>
    </div>`;
  }

  function update() {
    document.getElementById('pt').textContent = `${done.size} / ${D.modules.length} 완료`;
    document.getElementById('bar').style.width = `${(100 * done.size) / D.modules.length}%`;
  }

  function show() {
    document.querySelectorAll('.module').forEach((e, i) => e.classList.toggle('on', i === cur));
    document
      .querySelectorAll('.module-nav button')
      .forEach((e, i) => e.classList.toggle('on', i === cur));
    const s = document.getElementById('sel');
    if (s) s.value = cur;
    history.replaceState(null, '', `#m${cur}`);
    update();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function go(i) {
    if (i < 0 || i >= D.modules.length) return;
    cur = i;
    show();
  }

  /* ---------------- bootstrap ---------------- */

  shell();
  applyLayout();

  const nav = document.getElementById('nav');
  const sel = document.getElementById('sel');
  nav.innerHTML = D.modules
    .map(
      (m, i) =>
        `<button data-go="${i}">${i + 1}. ${esc(m.sourceLabel)} · ${esc(m.title)}</button>`
    )
    .join('');
  sel.innerHTML = D.modules
    .map((m, i) => `<option value="${i}">${i + 1}. ${esc(m.title)}</option>`)
    .join('');
  sel.addEventListener('change', (e) => go(+e.target.value));

  document.addEventListener('click', (e) => {
    if (e.target.closest('#layoutBtn')) cycleLayout();

    const answer = e.target.closest('[data-toggle-answer]');
    if (answer) answer.nextElementSibling.classList.toggle('on');

    const g = e.target.closest('[data-go]');
    if (g) go(+g.dataset.go);

    const b = e.target.closest('[data-done]');
    if (b) {
      const i = +b.dataset.done;
      done.has(i) ? done.delete(i) : done.add(i);
      localStorage.setItem(D.progressKey, JSON.stringify([...done]));
      b.textContent = done.has(i) ? '✓ 완료' : '○ 완료 처리';
      update();
    }
  });

  show();
  window.StudyEngine = { go, render: show };
})();
