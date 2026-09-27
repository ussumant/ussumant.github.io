/*
 * Knockout — tap the 🥊 and the page takes a punch: it shakes, a pixel K.O.
 * lands, and every word on screen drops into a pile you can throw around.
 * The referee counts to ten, then the page gets back up (or tap "get up").
 *
 * Physics + animation load only on the first punch: /assets/vendor/gsap.min.js,
 * /assets/vendor/matter.min.js and /scripts/gravity.js (from the web-motion
 * building block). Sounds are synthesised with Web Audio — no audio files.
 * Reduced motion: no drop; the K.O. just flashes and fades.
 */
(function () {
  var glove = document.querySelector('.ko-glove');
  var scene = document.getElementById('main');   // everything on screen can go down
  if (!glove || !scene) return;

  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var state = 'up';           // up → loading → down → rising → up
  var gv, split = [], ui = {}, countTimer = null, audio = null;

  // ---------------------------------------------------------------- loading
  function load(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = src; s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  var ready = null;
  function libs() {
    if (!ready) {
      ready = Promise.all([
        window.gsap ? null : load('/assets/vendor/gsap.min.js'),
        window.Matter ? null : load('/assets/vendor/matter.min.js')
      ]).then(function () { return window.WebMotionWild && window.WebMotionWild.gravity ? null : load('/scripts/gravity.js'); });
    }
    return ready;
  }
  // warm the cache when someone is about to punch (never under reduced motion)
  if (!reduced) {
    glove.addEventListener('pointerenter', libs, { once: true });
    glove.addEventListener('focus', libs, { once: true });
  }

  // ------------------------------------------------------------------ sound
  function ctx() {
    if (!audio) { var AC = window.AudioContext || window.webkitAudioContext; if (AC) audio = new AC(); }
    if (audio && audio.state === 'suspended') audio.resume();
    return audio;
  }
  function thud() {
    var a = ctx(); if (!a) return;
    var t = a.currentTime, o = a.createOscillator(), g = a.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(38, t + 0.28);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.55, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
    o.connect(g).connect(a.destination); o.start(t); o.stop(t + 0.4);
    // the slap on top: a short burst of filtered noise
    var n = a.createBuffer(1, a.sampleRate * 0.08, a.sampleRate), d = n.getChannelData(0);
    for (var i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 3);
    var src = a.createBufferSource(), f = a.createBiquadFilter(), ng = a.createGain();
    src.buffer = n; f.type = 'lowpass'; f.frequency.value = 1800; ng.gain.value = 0.35;
    src.connect(f).connect(ng).connect(a.destination); src.start(t);
  }
  function bell() {
    var a = ctx(); if (!a) return;
    var t = a.currentTime;
    [[880, 0.22], [1318.5, 0.12], [2217, 0.05]].forEach(function (p) {
      var o = a.createOscillator(), g = a.createGain();
      o.type = 'sine'; o.frequency.value = p[0];
      g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(p[1], t + 0.005); g.gain.exponentialRampToValueAtTime(0.0001, t + 1.6);
      o.connect(g).connect(a.destination); o.start(t); o.stop(t + 1.7);
    });
  }

  // ------------------------------------------- words become things that fall
  var TEXT = '.home-scene > p, .project-list li, .charm figcaption, .charm .copyright, .home-section > h2, .home-section > p, .update-list li, .about-copy p';
  function splitWords() {
    var vh = window.innerHeight;
    // whole objects fall as one piece — mark them first so their text isn't split too
    // (a word inside a falling object would move twice and sink through the floor)
    [].forEach.call(scene.querySelectorAll('.wordmark, .reel-thumb, .charm .gifimg, .project-list li > span[aria-hidden], .live-dot, .ko-glove'), function (el) { el.setAttribute('data-ko', ''); });
    [].forEach.call(scene.querySelectorAll(TEXT), function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;            // off screen: leave it alone
      split.push(el);
      var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), nodes = [], n;
      while ((n = walker.nextNode())) if (!n.parentNode.closest('[data-ko]')) nodes.push(n);
      nodes.forEach(function (node) {
        var parts = node.textContent.split(/(\s+)/), frag = document.createDocumentFragment();
        parts.forEach(function (p) {
          if (!p) return;
          if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
          var s = document.createElement('span');
          s.className = 'ko-w'; s.setAttribute('data-ko', ''); s.textContent = p;
          frag.appendChild(s);
        });
        node.parentNode.replaceChild(frag, node);
      });
    });
  }
  // unwrap the word spans in place (never rebuild innerHTML: that would recreate
  // the glove button and drop its listeners)
  function unsplit() {
    [].forEach.call(scene.querySelectorAll('.ko-w'), function (s) { s.parentNode.replaceChild(document.createTextNode(s.textContent), s); });
    split.forEach(function (el) { el.normalize(); });
    split = [];
    [].forEach.call(scene.querySelectorAll('[data-ko]'), function (el) { el.removeAttribute('data-ko'); });
  }

  // -------------------------------------------------------------- overlay ui
  function buildUi() {
    ui.ko = document.createElement('div');
    ui.ko.className = 'ko-banner';
    ui.ko.setAttribute('role', 'status');
    ui.ko.innerHTML = '<b>K.O.</b><span class="ko-count" aria-live="off"></span>';
    ui.up = document.createElement('button');
    ui.up.type = 'button'; ui.up.className = 'ko-up'; ui.up.textContent = 'get up';
    ui.up.addEventListener('click', getUp);
    document.body.appendChild(ui.ko);
    document.body.appendChild(ui.up);
  }
  function dropUi() { if (ui.ko) ui.ko.remove(); if (ui.up) ui.up.remove(); ui = {}; }

  // ------------------------------------------------------------------ punch
  function punch() {
    if (state !== 'up') return;
    thud();
    if (reduced) {
      buildUi();
      ui.up.remove();
      ui.ko.classList.add('ko-still');
      setTimeout(dropUi, 1600);
      return;
    }
    state = 'loading';
    libs().then(function () {
      var g = window.gsap;
      splitWords();
      buildUi();
      gv = window.WebMotionWild.gravity(scene, { items: '[data-ko]', tilt: true });
      // the hit: page lurches toward the glove, then drops
      var main = scene;
      g.timeline()
        .to(main, { x: -14, y: 6, rotation: -0.6, duration: 0.05, ease: 'power4.out' })
        .to(main, { x: 9, y: -4, rotation: 0.4, duration: 0.06 })
        .to(main, { x: 0, y: 0, rotation: 0, duration: 0.18, ease: 'elastic.out(1, 0.4)', clearProps: 'transform' })
        .add(function () { gv.drop(); state = 'down'; startCount(); }, 0.12);
      g.fromTo(ui.ko.querySelector('b'), { scale: 3.2, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: -4, duration: 0.55, ease: 'back.out(2.2)', delay: 0.1 });
      g.fromTo(ui.up, { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, delay: 0.9, ease: 'power3.out' });
      ui.up.focus({ preventScroll: true });
    }).catch(function () { state = 'up'; });
  }

  function startCount() {
    var n = 0, out = ui.ko.querySelector('.ko-count');
    countTimer = setInterval(function () {
      n += 1;
      out.textContent = n < 10 ? n + '…' : '10';
      if (window.gsap) window.gsap.fromTo(out, { scale: 1.4 }, { scale: 1, duration: 0.3, ease: 'power2.out' });
      if (n >= 10) getUp();
    }, 1000);
  }

  function getUp() {
    if (state !== 'down') return;
    state = 'rising';
    clearInterval(countTimer);
    bell();
    var g = window.gsap;
    g.to([ui.ko, ui.up], { opacity: 0, duration: 0.3 });
    function done() {
      scene.removeEventListener('wild:gravity', onRestore);
      unsplit();
      dropUi();
      state = 'up';
      glove.focus({ preventScroll: true });
    }
    function onRestore(e) { if (e.detail.state === 'restore') done(); }
    scene.addEventListener('wild:gravity', onRestore);
    gv.restore();
  }

  glove.addEventListener('click', punch);
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && state === 'down') getUp(); });
})();
