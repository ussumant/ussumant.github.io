(function () {
  var thumb = document.getElementById('reelThumb');
  var lightbox = document.getElementById('reelLightbox');
  var backdrop = document.getElementById('reelBackdrop');
  var stage = document.getElementById('reelStage');
  var video = document.getElementById('reelVideo');
  var controls = stage ? stage.querySelector('.reel-controls') : null;
  var time = document.getElementById('reelTime');
  var restart = document.getElementById('reelRestart');
  if (!thumb || !lightbox || !stage || !video || !controls || !time || !restart) return;

  var transition = 'transform 0.55s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.45s ease, box-shadow 0.55s cubic-bezier(0.22, 1, 0.36, 1)';
  var fullShadow = '0 20px 60px rgba(0, 0, 0, 0.25)';
  var endHandler = null;
  var safety = null;

  function shadowAtScale(scale) {
    var safeScale = scale > 0.01 ? scale : 1;
    return '0 ' + (4 / safeScale).toFixed(2) + 'px ' + (14 / safeScale).toFixed(2) + 'px rgba(0, 0, 0, 0.1)';
  }

  function formatTime(value) {
    if (!isFinite(value)) value = 0;
    var minutes = Math.floor(value / 60);
    var seconds = Math.floor(value % 60);
    return minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
  }

  function updateTime() {
    time.textContent = formatTime(video.currentTime) + ' / ' + formatTime(video.duration);
  }

  function clearHandlers() {
    if (endHandler) {
      video.removeEventListener('transitionend', endHandler);
      endHandler = null;
    }
    if (safety) {
      clearTimeout(safety);
      safety = null;
    }
  }

  function deltaTransform(fromRect, toRect) {
    var scale = fromRect.width / toRect.width;
    var dx = (fromRect.left + fromRect.width / 2) - (toRect.left + toRect.width / 2);
    var dy = (fromRect.top + fromRect.height / 2) - (toRect.top + toRect.height / 2);
    return 'translate(' + dx + 'px, ' + dy + 'px) scale(' + scale + ')';
  }

  function resume() {
    var promise = video.play();
    if (promise && promise.catch) promise.catch(function () {});
  }

  function open() {
    if (lightbox.classList.contains('active')) return;
    clearHandlers();

    var first = video.getBoundingClientRect();
    lightbox.classList.add('active');
    video.style.opacity = '1';
    thumb.style.height = thumb.offsetHeight + 'px';
    thumb.style.visibility = 'hidden';
    stage.insertBefore(video, controls);
    video.style.transition = 'none';
    video.style.transform = 'none';

    var last = video.getBoundingClientRect();
    var scale = first.width / last.width;
    video.style.transform = deltaTransform(first, last);
    video.style.boxShadow = shadowAtScale(scale);
    void video.offsetWidth;

    requestAnimationFrame(function () {
      video.style.transition = transition;
      video.style.transform = 'none';
      video.style.boxShadow = fullShadow;
      backdrop.classList.add('show');
    });

    resume();
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    endHandler = function (event) {
      if (event.target === video && event.propertyName === 'transform') {
        lightbox.classList.add('controls-on');
        clearHandlers();
      }
    };
    video.addEventListener('transitionend', endHandler);
    safety = setTimeout(function () {
      lightbox.classList.add('controls-on');
      clearHandlers();
    }, 800);
  }

  function close() {
    if (!lightbox.classList.contains('active')) return;
    clearHandlers();
    lightbox.classList.remove('controls-on');

    var first = video.getBoundingClientRect();
    var home = thumb.getBoundingClientRect();
    var target = {
      left: home.left,
      top: home.top,
      width: home.width,
      height: home.width * (first.height / first.width)
    };
    var scale = target.width / first.width;
    video.style.transition = 'none';
    video.style.transform = 'none';
    video.style.opacity = '1';
    void video.offsetWidth;

    requestAnimationFrame(function () {
      video.style.transition = transition;
      video.style.transform = deltaTransform(target, first);
      video.style.boxShadow = shadowAtScale(scale);
      backdrop.classList.remove('show');
    });

    function done() {
      if (!lightbox.classList.contains('active')) return;
      lightbox.classList.remove('active');
      lightbox.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      video.style.transition = 'none';
      video.style.transform = 'none';
      video.style.opacity = '';
      video.style.boxShadow = '';
      thumb.appendChild(video);
      thumb.style.height = '';
      thumb.style.visibility = '';
      resume();
      clearHandlers();
      thumb.focus();
    }

    endHandler = function (event) {
      if (event.target === video && event.propertyName === 'transform') done();
    };
    video.addEventListener('transitionend', endHandler);
    safety = setTimeout(done, 750);
  }

  thumb.addEventListener('click', open);
  thumb.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      open();
    }
  });
  backdrop.addEventListener('click', close);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && lightbox.classList.contains('active')) close();
  });
  restart.addEventListener('click', function () {
    video.currentTime = 0;
    resume();
  });
  video.addEventListener('timeupdate', updateTime);
  video.addEventListener('loadedmetadata', updateTime);

  function reelLive() {
    video.style.opacity = '1';
  }

  function reelStill() {
    if (!lightbox.classList.contains('active')) video.style.opacity = '0';
  }

  video.style.opacity = '0';
  video.addEventListener('playing', reelLive);
  video.addEventListener('pause', reelStill);
  video.addEventListener('ended', reelStill);
  resume();

  function resumeIfVisible() {
    if (document.visibilityState === 'visible' && video.paused) resume();
  }
  document.addEventListener('visibilitychange', resumeIfVisible);
  window.addEventListener('pageshow', resumeIfVisible);
  window.addEventListener('focus', resumeIfVisible);
})();

(function () {
  var root = document.documentElement;
  var logo = document.querySelector('[data-typing-logo]');
  if (!logo) return;

  function reveal() {
    root.classList.remove('js-typing');
  }

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) {
    reveal();
    return;
  }

  function run() {
    try {
      var sleep = function (milliseconds) {
        return new Promise(function (resolve) { setTimeout(resolve, milliseconds); });
      };
      var caret = document.createElement('span');
      caret.className = 'caret';
      var logoOriginal = Array.prototype.map.call(logo.childNodes, function (node) {
        return node.cloneNode(true);
      });
      var scene = document.querySelector('.home-scene');
      var main = document.querySelector('main');
      var fadeElements = [];

      if (scene) {
        fadeElements = fadeElements.concat(Array.prototype.filter.call(scene.children, function (element) {
          return element !== logo;
        }));
      }
      if (main) {
        fadeElements = fadeElements.concat(Array.prototype.filter.call(main.children, function (element) {
          return element !== scene && element.tagName !== 'SCRIPT';
        }));
      }

      logo.replaceChildren();
      fadeElements.forEach(function (element) {
        element.style.transition = 'none';
        element.style.opacity = '0';
      });
      reveal();

      function typeInto(nodes, target) {
        return nodes.reduce(function (promise, child) {
          return promise.then(function () {
            if (child.nodeType === 3) {
              var text = document.createTextNode('');
              target.appendChild(text);
              target.appendChild(caret);
              return Array.from(child.textContent).reduce(function (chain, character) {
                return chain.then(function () {
                  text.textContent += character;
                  return sleep(character === ' ' ? 110 : 220);
                });
              }, Promise.resolve());
            }
            if (child.nodeType === 1) {
              var clone = child.cloneNode(false);
              target.appendChild(clone);
              target.appendChild(caret);
              return typeInto(Array.prototype.slice.call(child.childNodes), clone);
            }
            return Promise.resolve();
          });
        }, Promise.resolve());
      }

      function hopCaret() {
        return sleep(180).then(function () {
          return new Promise(function (resolve) {
            var done = false;
            function finish() {
              if (done) return;
              done = true;
              caret.removeEventListener('animationend', finish);
              resolve();
            }
            caret.addEventListener('animationend', finish);
            caret.style.animation = 'caretHop 0.34s linear 1';
            setTimeout(finish, 500);
          });
        });
      }

      var fontReady = document.fonts && document.fonts.load
        ? Promise.race([document.fonts.load('22px "Pixelify Sans"'), sleep(2500)])
        : Promise.resolve();

      Promise.all([sleep(1300), fontReady])
        .then(function () { return typeInto(logoOriginal, logo); })
        .then(hopCaret)
        .then(function () { return sleep(500); })
        .then(function () {
          if (caret.parentNode) caret.parentNode.removeChild(caret);
          fadeElements.forEach(function (element) {
            element.style.transition = 'opacity 1.3s ease';
            element.style.opacity = '1';
          });
          setTimeout(function () {
            fadeElements.forEach(function (element) {
              element.style.transition = '';
              element.style.opacity = '';
            });
          }, 1350);
        });
    } catch (error) {
      reveal();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
