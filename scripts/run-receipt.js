/*
 * Run Receipt: swap the printed snapshot for the newest run, live.
 *
 * The home page is built with a snapshot of a run (scripts/refresh_run_receipt.py).
 * If the Run Receipt app publishes a latest-run feed (the owner turns on
 * "Publish my latest run" in its settings), this fetches it on load and reprints the
 * receipt. Any failure (feed off, offline, bad data) leaves the snapshot as is.
 */
(function () {
  var card = document.querySelector('.receipt-card[data-feed]');
  if (!card || !window.fetch) return;
  var feed = card.getAttribute('data-feed');
  if (!/^https:\/\/|^http:\/\/localhost[:/]/.test(feed)) return;

  function text(sel, value) { var el = card.querySelector(sel); if (el && value) el.textContent = value; }
  function clean(v, re) { return typeof v === 'string' && re.test(v) ? v : null; }

  var ctl = window.AbortController ? new AbortController() : null;
  var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 6000);
  fetch(feed, { mode: 'cors', credentials: 'omit', cache: 'no-cache', signal: ctl ? ctl.signal : undefined })
    .then(function (r) { if (!r.ok) throw new Error('feed ' + r.status); return r.json(); })
    .then(function (run) {
      clearTimeout(timer);
      var title = typeof run.title === 'string' ? run.title.slice(0, 60) : null;
      var date = clean(run.date, /^\d{4}-\d{2}-\d{2}$/);
      var km = typeof run.distance_km === 'number' && run.distance_km > 0 && run.distance_km < 1000
        ? String(+run.distance_km.toFixed(2)) : null;
      if (!title || !date || !km) return;                       // not a run: keep the snapshot
      var pace = clean(run.pace, /^\d{1,2}:\d{2}\/km$/);
      var order = clean(run.order, /^\d{1,8}$/);
      text('.rc-item', '1× ' + title.toUpperCase());
      text('.rc-date', date);
      if (order) text('.rc-order', 'ORDER #' + order);
      text('.rc-total strong', km);
      text('.rc-foot', (pace ? pace + ' · ' : '') + '★ PAID IN FULL');
      var photo = card.querySelector('.rc-photo');
      var img = typeof run.image === 'string' && /^https:\/\/|^http:\/\/localhost[:/]/.test(run.image) ? run.image : null;
      if (photo) {
        if (img) { photo.src = img; photo.hidden = false; card.classList.remove('rc-nophoto'); }
        else { photo.hidden = true; card.classList.add('rc-nophoto'); }   // route-only runs: no picture, a stamp
      }
      var link = card.querySelector('.receipt');
      if (link) link.setAttribute('aria-label', 'Run receipt: ' + title + ', ' + km + ' km on ' + date);
      card.setAttribute('data-live', '');
    })
    .catch(function () { clearTimeout(timer); });
})();
