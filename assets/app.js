// The Morning Commit: service worker + phone layout helpers.
(function () {
  if (window.matchMedia('(max-width:760px)').matches) {
    document.documentElement.classList.add('mc-phone');
  }

  function isDesktop() {
    return window.matchMedia('(min-width:761px)').matches;
  }

  function syncDetails() {
    var desk = isDesktop();
    document.querySelectorAll('details.more').forEach(function (d) {
      if (desk) d.setAttribute('open', '');
      else if (!d.dataset.user) d.removeAttribute('open');
    });
  }

  function words(text, n) {
    var w = (text || '').trim().split(/\s+/).filter(Boolean);
    if (!w.length) return '';
    return w.slice(0, n).join(' ') + (w.length > n ? '…' : '');
  }

  // Old editions: turn the wrapping ticker sentence into scrollable chips.
  function upgradeTicker() {
    if (document.querySelector('.liked')) return;
    var t = document.querySelector('.ticker');
    if (!t) return;
    var text = t.textContent.replace(/^[\s\S]*?▸\s*/, '').trim();
    if (!text) return;
    var parts = text.split(/\s*◆\s*/).map(function (s) { return s.trim(); }).filter(Boolean);
    if (parts.length < 2) return;
    var nav = document.createElement('nav');
    nav.className = 'liked liked-js';
    nav.setAttribute('aria-label', 'Most-liked in the past 48 hours');
    nav.innerHTML = '<div class="liked-label">Most-liked, past 48h</div><div class="liked-track"></div>';
    var track = nav.querySelector('.liked-track');
    parts.forEach(function (p) {
      var a = document.createElement('div');
      a.className = 'chip chip-text';
      var m = p.match(/^(.*?)(\s+(?:♥|🔖|👁|\$|HN|passes).*)?$/i);
      var title = ((m && m[1]) || p).trim();
      var n = ((m && m[2]) || '').trim();
      a.innerHTML = '<span class="chip-t"></span><span class="chip-n"></span>';
      a.querySelector('.chip-t').textContent = title;
      a.querySelector('.chip-n').textContent = n;
      track.appendChild(a);
    });
    t.after(nav);
  }

  // Old editions: collapse long write-ups, try-it commands and quotes behind a tap.
  function upgradeLegacy() {
    document.querySelectorAll('article.card').forEach(function (card) {
      if (card.querySelector('details.more')) return;
      if (!card.querySelector('.hook')) {
        var first = card.querySelector('.txt p');
        if (first) {
          var hook = document.createElement('p');
          hook.className = 'hook';
          hook.textContent = words(first.textContent, 15);
          var anchor = card.querySelector('.badges') || card.querySelector('h3');
          if (anchor) anchor.insertAdjacentElement('afterend', hook);
        }
      }
      var move = [];
      card.querySelectorAll('figcaption, .txt, .tryit, .links').forEach(function (el) { move.push(el); });
      if (!move.length) return;
      var details = document.createElement('details');
      details.className = 'more';
      var sum = document.createElement('summary');
      sum.textContent = 'Read the story';
      details.appendChild(sum);
      move.forEach(function (el) { details.appendChild(el); });
      card.appendChild(details);
    });

    var lead = document.querySelector('section.lead');
    if (lead && !lead.querySelector('details.more')) {
      var cols = lead.querySelector('.cols');
      if (cols) {
        var wrap = cols.parentNode;
        var d = document.createElement('details');
        d.className = 'more lead-more';
        var s = document.createElement('summary');
        s.textContent = 'Read the story';
        d.appendChild(s);
        wrap.insertBefore(d, cols);
        d.appendChild(cols);
        var links = wrap.querySelector(':scope > .links');
        if (links) d.appendChild(links);
      }
      var side = lead.querySelector('aside.side');
      if (side && !side.querySelector('details.more')) {
        var d2 = document.createElement('details');
        d2.className = 'more side-more';
        var s2 = document.createElement('summary');
        s2.textContent = 'Try it tonight';
        d2.appendChild(s2);
        while (side.firstChild) d2.appendChild(side.firstChild);
        side.appendChild(d2);
      }
    }

    var pull = document.querySelector('.pull');
    if (pull && !pull.closest('details.more')) {
      var d3 = document.createElement('details');
      d3.className = 'more quotes-more';
      var s3 = document.createElement('summary');
      s3.textContent = 'Quotes from today';
      pull.parentNode.insertBefore(d3, pull);
      d3.appendChild(s3);
      d3.appendChild(pull);
    }
  }

  function initLayout() {
    upgradeTicker();
    upgradeLegacy();
    syncDetails();
    document.addEventListener('click', function (e) {
      var s = e.target.closest && e.target.closest('details.more > summary');
      if (s) s.parentElement.dataset.user = '1';
    }, true);
    var mq = window.matchMedia('(max-width:760px)');
    var on = function () {
      document.documentElement.classList.toggle('mc-phone', mq.matches);
      document.querySelectorAll('details.more').forEach(function (d) { delete d.dataset.user; });
      syncDetails();
    };
    if (mq.addEventListener) mq.addEventListener('change', on);
    else if (mq.addListener) mq.addListener(on);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initLayout);
  else initLayout();

  if (!('serviceWorker' in navigator)) return;
  var me = document.currentScript || document.querySelector('script[src*="assets/app.js"]');
  var root = new URL('../', me.src);
  window.addEventListener('load', function () {
    navigator.serviceWorker.register(new URL('sw.js', root).href, { scope: root.pathname }).catch(function () {});
  });
})();
