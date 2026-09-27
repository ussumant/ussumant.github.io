/*!
 * gravity — switch gravity on for the page: the elements you mark fall, tumble,
 * and pile up at the bottom of the screen. Grab and throw them (mouse or finger);
 * on a phone, tilt it and the pile slides. Switch it off and everything flies
 * home to its exact spot.
 *
 *   var gv = WebMotionWild.gravity(document, { items: '[data-gravity-item]' })
 *   gv.drop() · gv.restore() · gv.toggle() · gv.dropped
 *   <button data-gravity-toggle>…</button>   (auto-wired to toggle)
 *
 * Only elements visible on screen fall; the page scroll is locked while they're
 * down. Nothing moves in the layout: the elements are only transformed, so the
 * page is exactly as it was after restore().
 * Needs gsap.min.js + matter.min.js. Reduced motion: disabled.
 */
(function (root) {
  'use strict';
  var g = root.gsap, M = root.Matter;
  if (!g || !M) { console.warn('[gravity] load gsap.min.js and matter.min.js first'); return; }
  // read live: the setting can change after the page loads
  function isReduced() { return !!(root.matchMedia && root.matchMedia('(prefers-reduced-motion: reduce)').matches); }

  function gravity(scope, o) {
    o = o || {};
    scope = scope || document;
    var state = { dropped: false };
    var engine, raf, overlay, items = [], prevOverflow, onTilt, busy = false;

    function drop() {
      if (state.dropped || busy || isReduced()) return;
      var vw = root.innerWidth, vh = root.innerHeight;
      items = [].slice.call(scope.querySelectorAll(o.items || '[data-gravity-item]')).map(function (el) {
        if (getComputedStyle(el).display === 'inline') el.style.display = 'inline-block';
        var r = el.getBoundingClientRect();
        return { el: el, r: r };
      }).filter(function (it) {
        return it.r.width > 2 && it.r.height > 2 && it.r.bottom > 0 && it.r.top < vh && it.r.right > 0 && it.r.left < vw;
      });
      if (!items.length) return;

      state.dropped = true;
      prevOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = 'hidden';

      engine = M.Engine.create();
      engine.gravity.y = 1;
      var T = 200, wall = { isStatic: true, friction: 0.4, restitution: 0.2 };
      M.Composite.add(engine.world, [
        M.Bodies.rectangle(vw / 2, vh + T / 2, vw * 3, T, wall),          // floor
        M.Bodies.rectangle(-T / 2, vh / 2 - vh, T, vh * 4, wall),         // left
        M.Bodies.rectangle(vw + T / 2, vh / 2 - vh, T, vh * 4, wall),     // right
        M.Bodies.rectangle(vw / 2, -vh * 2.5, vw * 3, T, wall)            // high ceiling so throws come back
      ]);

      items.forEach(function (it) {
        var r = it.r, cs = getComputedStyle(it.el);
        var radius = Math.min(parseFloat(cs.borderTopLeftRadius) || 0, r.width / 2, r.height / 2);
        it.home = { x: r.left + r.width / 2, y: r.top + r.height / 2 };
        it.body = M.Bodies.rectangle(it.home.x, it.home.y, r.width, r.height, {
          chamfer: radius > 1 ? { radius: radius * 0.9 } : undefined,
          restitution: 0.35, friction: 0.35, frictionAir: 0.012, density: 0.002
        });
        M.Body.setAngularVelocity(it.body, (Math.random() - 0.5) * 0.06);
        M.Body.setVelocity(it.body, { x: (Math.random() - 0.5) * 2, y: -Math.random() * 3 });
        // the page's own CSS must not fight the physics: no transform transitions,
        // rotate about the centre (the body's centre of mass). Restored afterwards.
        it.saved = { transition: it.el.style.transition, origin: it.el.style.transformOrigin };
        it.el.style.transition = 'none';
        it.el.style.transformOrigin = '50% 50%';
        it.el.style.willChange = 'transform';
        it.el.setAttribute('data-gravity-down', '');
      });
      M.Composite.add(engine.world, items.map(function (it) { return it.body; }));

      // grab-and-throw layer (sits above the page, under the toggle)
      overlay = document.createElement('div');
      overlay.setAttribute('aria-hidden', 'true');
      overlay.style.cssText = 'position:fixed;inset:0;z-index:9990;touch-action:none;cursor:grab;';
      document.body.appendChild(overlay);
      var mouse = M.Mouse.create(overlay);
      mouse.pixelRatio = 1;
      M.Composite.add(engine.world, M.MouseConstraint.create(engine, { mouse: mouse, constraint: { stiffness: 0.25, damping: 0.1, render: { visible: false } } }));
      [].forEach.call(document.querySelectorAll('[data-gravity-toggle]'), function (b) {
        b._wildZ = b.style.zIndex;
        if (getComputedStyle(b).position === 'static') b.style.position = 'relative';
        b.style.zIndex = '9991';
      });

      // phone tilt steers gravity
      if (o.tilt !== false && 'DeviceOrientationEvent' in root) {
        onTilt = function (e) {
          if (e.beta == null) return;
          var gx = Math.sin(g.utils.clamp(-90, 90, e.gamma || 0) * Math.PI / 180);
          var gy = Math.sin(g.utils.clamp(-90, 90, e.beta) * Math.PI / 180);
          if (Math.abs(gx) + Math.abs(gy) < 0.25) return;   // lying flat: keep the last direction
          engine.gravity.x = gx; engine.gravity.y = gy;
        };
        var ask = root.DeviceOrientationEvent.requestPermission;
        if (typeof ask === 'function') ask().then(function (p) { if (p === 'granted') root.addEventListener('deviceorientation', onTilt); }).catch(function () {});
        else root.addEventListener('deviceorientation', onTilt);
      }

      // fixed 60 Hz steps, whatever the display rate
      var STEP = 1000 / 60, acc = 0, last = performance.now();
      (function tick(now) {
        acc = Math.min(acc + (now - last), STEP * 4); last = now;
        while (acc >= STEP) { M.Engine.update(engine, STEP); acc -= STEP; }
        items.forEach(function (it) {
          g.set(it.el, { x: it.body.position.x - it.home.x, y: it.body.position.y - it.home.y, rotation: it.body.angle * 180 / Math.PI });
        });
        raf = requestAnimationFrame(tick);
      })(last);
      emit('drop');
    }

    function restore() {
      if (!state.dropped || busy) return;
      busy = true;
      cancelAnimationFrame(raf);
      if (onTilt) root.removeEventListener('deviceorientation', onTilt);
      overlay.remove();
      M.Engine.clear(engine);
      var tl = g.timeline({
        onComplete: function () {
          items.forEach(function (it) {
            g.set(it.el, { clearProps: 'transform' });
            it.el.style.willChange = '';
            it.el.style.transition = it.saved.transition;
            it.el.style.transformOrigin = it.saved.origin;
            it.el.removeAttribute('data-gravity-down');
          });
          document.documentElement.style.overflow = prevOverflow;
          [].forEach.call(document.querySelectorAll('[data-gravity-toggle]'), function (b) { b.style.zIndex = b._wildZ || ''; });
          state.dropped = false; busy = false;
          emit('restore');
        }
      });
      items.forEach(function (it) {
        // unwind the spin the short way round
        var rot = g.getProperty(it.el, 'rotation');
        var home = rot - 360 * Math.round(rot / 360);
        g.set(it.el, { rotation: home });
        tl.to(it.el, { x: 0, y: 0, rotation: 0, duration: 1.1, ease: 'expo.inOut' }, Math.random() * 0.25);
      });
    }

    function emit(type) { (scope === document ? document : scope).dispatchEvent(new CustomEvent('wild:gravity', { detail: { state: type } })); }
    function toggle() { if (state.dropped) restore(); else drop(); }

    return {
      drop: drop, restore: restore, toggle: toggle,
      get dropped() { return state.dropped; },
      get engine() { return engine; }
    };
  }

  root.WebMotionWild = root.WebMotionWild || {};
  root.WebMotionWild.gravity = gravity;

  function auto() {
    var toggles = document.querySelectorAll('[data-gravity-toggle]');
    if (!toggles.length) return;
    var gv = gravity(document);
    root.WebMotionWild.page = gv;
    [].forEach.call(toggles, function (b) {
      if (isReduced()) { b.setAttribute('aria-disabled', 'true'); b.title = 'Off because reduced motion is on'; return; }
      b.addEventListener('click', function () { gv.toggle(); });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', auto); else auto();
})(window);
