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

(function () {
  var buttons = Array.prototype.slice.call(document.querySelectorAll('.reading-node-button'));
  var nodes = Array.prototype.slice.call(document.querySelectorAll('.reading-arch-node'));
  if (!buttons.length || !nodes.length) return;

  var details = {
    observe: {
      title: 'Observe what is happening.',
      copy: 'The agent receives a local view of the sandbox: nearby agents, objects, actions, and changes in the environment.',
      points: ['Observations are written in natural language.', 'The agent is not omniscient; its world model is partial.', 'Every perception becomes a possible future memory.'],
      foot: 'The outside world is the source of new evidence.'
    },
    memory: {
      title: 'Keep the record.',
      copy: 'The memory stream is a growing list of natural-language experiences. It includes observations, plans, and reflections.',
      points: ['Each item has a description and timestamps.', 'Important events can outlive mundane ones.', 'Plans and reflections are written back into the same stream.'],
      foot: 'Persistent state turns prompts into a life history.'
    },
    retrieve: {
      title: 'Retrieve what matters now.',
      copy: 'The full history is too large and too distracting to place in every prompt. Retrieval selects a compact set of memories that can inform the current decision.',
      points: ['Use the current situation as a query.', 'Balance recency, importance, and relevance.', 'Pass only the top-ranked memories onward.'],
      foot: 'Attention over an external, persistent notebook.'
    },
    reflect: {
      title: 'Turn events into meaning.',
      copy: 'Reflection synthesizes several observations into a higher-level insight about the agent, another person, or the world.',
      points: ['Recent memories suggest questions worth asking.', 'Relevant evidence is retrieved for each question.', 'The resulting insight becomes a new memory.'],
      foot: 'A history starts to feel like a point of view.'
    },
    plan: {
      title: 'Shape the next hours.',
      copy: 'Planning creates a broad daily agenda, decomposes it into smaller actions, and gives the agent a way to stay coherent across time.',
      points: ['Plans include location, start time, and duration.', 'High-level plans are recursively decomposed.', 'Unexpected events can trigger a re-plan.'],
      foot: 'A plan is a temporary spine, not a promise.'
    },
    act: {
      title: 'Change the world.',
      copy: 'The model’s chosen action is translated into movement, dialogue, or an object-state change in Smallville.',
      points: ['Actions create consequences in the sandbox.', 'Those consequences are perceived again.', 'The loop continues with a changed context.'],
      foot: 'Generated language becomes a testable event.'
    }
  };

  var title = document.querySelector('[data-reading-detail-title]');
  var copy = document.querySelector('[data-reading-detail-copy]');
  var list = document.querySelector('[data-reading-detail-list]');
  var foot = document.querySelector('[data-reading-detail-foot]');

  function select(name) {
    var detail = details[name];
    if (!detail) return;
    buttons.forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.readingNode === name));
    });
    nodes.forEach(function (node) {
      var active = node.dataset.readingNode === name;
      node.classList.toggle('is-focus', active);
      node.classList.toggle('is-dim', !active);
    });
    title.textContent = detail.title;
    copy.textContent = detail.copy;
    list.innerHTML = detail.points.map(function (point) { return '<li>' + point + '</li>'; }).join('');
    foot.textContent = detail.foot;
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', function () { select(button.dataset.readingNode); });
  });
  nodes.forEach(function (node) {
    node.addEventListener('click', function () { select(node.dataset.readingNode); });
  });
  select('retrieve');
})();
