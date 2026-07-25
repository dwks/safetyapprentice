// Shared behaviour for every page: navbar background on scroll, fade-in
// reveals, and the grouped nav dropdowns / mobile menu.

window.addEventListener('scroll', function () {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

(function () {
  var els = document.querySelectorAll('.fade-in');
  if (!els.length) return;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) entry.target.classList.add('visible');
    });
  }, { threshold: 0.1 });
  els.forEach(function (el) { observer.observe(el); });
})();

(function () {
  var bar = document.getElementById('navbar');
  var links = document.getElementById('navLinks');
  var toggle = document.getElementById('navToggleTop');
  var groups = Array.prototype.slice.call(document.querySelectorAll('.nav-group'));

  function closeGroups(except) {
    groups.forEach(function (g) {
      if (g === except) return;
      g.classList.remove('open');
      g.querySelector('.nav-link--group').setAttribute('aria-expanded', 'false');
    });
  }
  function closeMenu() {
    closeGroups(null);
    if (links) links.classList.remove('open');
    if (toggle) toggle.setAttribute('aria-expanded', 'false');
  }

  groups.forEach(function (g) {
    var btn = g.querySelector('.nav-link--group');
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !g.classList.contains('open');
      closeGroups(g);
      g.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });

  if (toggle) {
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      if (!open) closeGroups(null);
    });
  }

  document.addEventListener('click', function (e) {
    if (!bar.contains(e.target)) closeMenu();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });
})();
