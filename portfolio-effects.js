// A single animation frame per pointer update; disabled on touch/reduced motion.
(function () {
  var cover = document.querySelector('.portfolio-cover');
  if (!cover) return;
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var pointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  var frame = null;
  var x = 50;
  var y = 45;

  function reset() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    cover.style.removeProperty('--light-x');
    cover.style.removeProperty('--light-y');
  }

  cover.addEventListener('pointermove', function (event) {
    if (motion.matches || !pointer.matches) return;
    var rect = cover.getBoundingClientRect();
    x = (event.clientX - rect.left) / rect.width * 100;
    y = (event.clientY - rect.top) / rect.height * 100;
    if (frame !== null) return;
    frame = requestAnimationFrame(function () {
      cover.style.setProperty('--light-x', x.toFixed(1) + '%');
      cover.style.setProperty('--light-y', y.toFixed(1) + '%');
      frame = null;
    });
  }, { passive: true });
  cover.addEventListener('pointerleave', reset);
  motion.addEventListener('change', reset);
  pointer.addEventListener('change', reset);
})();
