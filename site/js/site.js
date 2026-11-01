// Dapata: menu mobile, cabeçalho e animações de entrada. Sem dependências.
(function () {
  var menu = document.querySelector('.menu');
  if (menu) {
    var sum = menu.querySelector('summary');
    var sync = function () {
      var aberto = menu.open;
      document.body.classList.toggle('menu-aberto', aberto);
      sum.setAttribute('aria-expanded', aberto);
      sum.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
    };
    menu.addEventListener('toggle', sync); sync();
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { menu.open = false; }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.open) { menu.open = false; sum.focus(); } });
    window.matchMedia('(min-width:1061px)').addEventListener('change', function (m) { if (m.matches) menu.open = false; });
  }
  var header = document.querySelector('header');
  var rolar = function () { header.classList.toggle('rolou', window.scrollY > 8); };
  window.addEventListener('scroll', rolar, { passive: true }); rolar();

})();
