(function () {
  var PAGES = [
    { href: 'main.html', label: 'Ana Sayfa' },
    { href: 'KBN-Adim0-Veri-Tablosu.html', label: 'Adım 0 Veri' },
    { href: 'KBN-ISO12100-Kapak-Risk-Degerlendirme.html', label: 'ISO 12100 Kapak' },
    { href: 'KBN-ISO13849-Kapak-Risk-Degerlendirme.html', label: 'ISO 13849 Kapak' },
    { href: 'KBN-Kapak-Guvenli-Durum-Analizi.html', label: 'Güvenli Durum' },
    { href: 'KBN-PLr-D-Yol-Haritasi.html', label: 'PLr D Yol Haritası' },
    { href: 'KBN-Konfig-AB-Uygulama-Plani.html', label: 'Konfig A/B Plan' },
    { href: 'KBN-ISO12100-Risk-Degerlendirme.html', label: '12100 Taslak' },
    { href: 'KBN-piston-pnomatik-hat.html', label: 'Pnömatik Hat' },
    { href: 'kabin-kapak-piston-valf.html', label: 'Simülasyon' }
  ];

  var current = (window.location.pathname.split('/').pop() || 'main.html').toLowerCase();
  if (current === '' || current === 'index.html') current = 'main.html';

  var root = document.getElementById('kbn-nav-root');
  if (!root) return;

  var html = '<nav class="kbn-site-nav"><div class="nav-inner">';
  var brandActive = current === 'main.html' ? ' nav-brand active' : ' nav-brand';
  html += '<a href="main.html" class="' + brandActive.trim() + '">KBN Kapak</a><span class="nav-sep"></span>';

  PAGES.forEach(function (p) {
    if (p.href === 'main.html') return;
    var active = current === p.href.toLowerCase() ? ' class="active"' : '';
    html += '<a href="' + p.href + '"' + active + '>' + p.label + '</a>';
  });

  html += '</div></nav>';
  root.innerHTML = html;
})();
