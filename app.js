/* ============================================================
   NOURA — App utilities shared across all pages
   ============================================================ */

const NouraUI = (function(){

  function ringColor(pct){
    // 0-70 green -> 70-92 amber -> 92-100+ red
    if(pct <= 70) return getComputedStyle(document.documentElement).getPropertyValue('--green').trim();
    if(pct <= 92) return getComputedStyle(document.documentElement).getPropertyValue('--amber').trim();
    return getComputedStyle(document.documentElement).getPropertyValue('--red').trim();
  }

  function setRing(svgCircle, pct, opts){
    opts = opts || {};
    const r = svgCircle.r.baseVal.value;
    const c = 2 * Math.PI * r;
    const clamped = Math.max(0, Math.min(1, pct));
    svgCircle.style.strokeDasharray = c;
    // animate from full offset to target
    requestAnimationFrame(function(){
      svgCircle.style.strokeDashoffset = c * (1 - clamped);
    });
    if(!opts.color){
      svgCircle.style.stroke = ringColor(clamped*100);
    } else {
      svgCircle.style.stroke = opts.color;
    }
  }

  function countUp(el, target, duration){
    duration = duration || 1200;
    const start = 0;
    const startTime = performance.now();
    function tick(now){
      const p = Math.min(1, (now - startTime) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = Math.round(start + (target - start) * eased);
      el.textContent = val;
      if(p < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    }
    requestAnimationFrame(tick);
  }

  function toast(msg){
    let el = document.querySelector('.toast');
    if(!el){
      el = document.createElement('div');
      el.className = 'toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    requestAnimationFrame(function(){ el.classList.add('show'); });
    clearTimeout(el._t);
    el._t = setTimeout(function(){ el.classList.remove('show'); }, 2600);
  }

  function markActiveNav(){
    const page = document.body.dataset.page;
    if(!page) return;
    document.querySelectorAll('[data-nav]').forEach(function(el){
      el.classList.toggle('active', el.dataset.nav === page);
    });
  }

  function verdictBadgeClass(verdict){
    if(verdict === 'great') return 'badge-green';
    if(verdict === 'good') return 'badge-amber';
    return 'badge-red';
  }
  function verdictColor(verdict){
    const root = getComputedStyle(document.documentElement);
    if(verdict === 'great') return root.getPropertyValue('--green').trim();
    if(verdict === 'good') return root.getPropertyValue('--amber').trim();
    return root.getPropertyValue('--red').trim();
  }

  document.addEventListener('DOMContentLoaded', markActiveNav);

  return { setRing, countUp, toast, ringColor, markActiveNav, verdictBadgeClass, verdictColor };
})();
