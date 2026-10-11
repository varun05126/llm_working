// SkillHer Progressive Enhancement (< 6 KB)
document.addEventListener('DOMContentLoaded', function () {
  document.documentElement.classList.add('js-enabled');

  // 1. Scroll reveal (IntersectionObserver)
  var revealElements = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealElements.length > 0) {
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          obs.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.1 });

    revealElements.forEach(function (el, index) {
      if (el.classList.contains('step-card') || el.classList.contains('pioneer-card')) {
        el.style.transitionDelay = ((index % 5) * 80) + 'ms';
      }
      observer.observe(el);
    });
  } else {
    revealElements.forEach(function (el) { el.classList.add('revealed'); });
  }

  // 2. Form loading states
  var forms = document.querySelectorAll('form[data-loading]');
  forms.forEach(function (form) {
    form.addEventListener('submit', function () {
      var loader = document.getElementById('loadingState');
      var content = document.getElementById('formContent');
      if (loader) loader.style.display = 'block';
      if (content) content.style.display = 'none';
      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Generating plan...';
      }
    });
  });

  // 3. Assessment wizard step transitions
  var steps = document.querySelectorAll('.assessment-step-card');
  if (steps.length > 1) {
    var currentIndex = 0;
    var nextBtn = document.getElementById('jsNextStep');
    var prevBtn = document.getElementById('jsPrevStep');
    var submitBtn = document.getElementById('jsSubmitAssessment');
    var stepCounter = document.getElementById('jsStepCounter');

    function showStep(index) {
      steps.forEach(function (step, i) {
        if (i === index) {
          step.style.display = 'block';
          step.classList.remove('fade-in');
          void step.offsetWidth;
          step.classList.add('fade-in');
        } else {
          step.style.display = 'none';
        }
      });
      if (stepCounter) stepCounter.textContent = (index + 1) + ' / ' + steps.length;
      if (prevBtn) prevBtn.style.display = index === 0 ? 'none' : 'inline-block';
      if (nextBtn) nextBtn.style.display = index === steps.length - 1 ? 'none' : 'inline-block';
      if (submitBtn) submitBtn.style.display = index === steps.length - 1 ? 'inline-block' : 'none';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    if (nextBtn) {
      nextBtn.addEventListener('click', function () {
        if (currentIndex < steps.length - 1) {
          currentIndex++;
          showStep(currentIndex);
        }
      });
    }

    if (prevBtn) {
      prevBtn.addEventListener('click', function () {
        if (currentIndex > 0) {
          currentIndex--;
          showStep(currentIndex);
        }
      });
    }

    showStep(0);
  }

  // 4. Rating buttons
  var ratingBtns = document.querySelectorAll('.rating-btn');
  ratingBtns.forEach(function (btn) {
    var input = btn.querySelector('input[type="radio"]');
    if (input && input.checked) btn.classList.add('selected');
    btn.addEventListener('click', function () {
      var groupName = input.name;
      document.querySelectorAll('input[name="' + groupName + '"]').forEach(function (r) {
        r.closest('.rating-btn').classList.remove('selected');
      });
      input.checked = true;
      btn.classList.add('selected');
    });
  });

  // 5. Milestone progress tracker
  var checkboxes = document.querySelectorAll('.milestone-check');
  if (checkboxes.length > 0) {
    function updateProgress() {
      var total = checkboxes.length;
      var checked = document.querySelectorAll('.milestone-check:checked').length;
      var pct = total === 0 ? 0 : Math.round((checked / total) * 100);
      var fill = document.getElementById('roadmapProgressFill');
      var text = document.getElementById('roadmapProgressText');
      if (fill) fill.style.width = pct + '%';
      if (text) text.textContent = pct + '% completed';
    }

    checkboxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        var parent = cb.closest('.milestone-item');
        if (parent) {
          if (cb.checked) parent.classList.add('done');
          else parent.classList.remove('done');
        }
        updateProgress();
      });
    });

    updateProgress();
  }

  // 6. Results celebration (under 1 KB, respects reduced motion)
  var celebrationEl = document.getElementById('celebrationBurst');
  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (celebrationEl && !prefersReducedMotion) {
    var recId = celebrationEl.getAttribute('data-rec-id') || 'general';
    var storageKey = 'skillher_celebrated_' + recId;
    if (!sessionStorage.getItem(storageKey)) {
      sessionStorage.setItem(storageKey, '1');
      createCelebrationBurst(celebrationEl);
    }
  }

  function createCelebrationBurst(container) {
    var canvas = document.createElement('canvas');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '99999';
    container.appendChild(canvas);

    var ctx = canvas.getContext('2d');
    if (!ctx) return;

    var isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    var colors = ['#b83280', '#f472b6', '#ec4899', '#db2777', isDark ? '#f5f5f5' : '#111111'];
    var particles = [];
    var count = 28;
    var originX = window.innerWidth / 2;
    var originY = Math.min(window.innerHeight * 0.35, 260);

    for (var i = 0; i < count; i++) {
      var angle = (Math.PI * 2 * i) / count + (Math.random() * 0.2 - 0.1);
      var speed = 2.5 + Math.random() * 4;
      particles.push({
        x: originX, y: originY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.5,
        radius: 2 + Math.random() * 2,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: 1, decay: 0.016 + Math.random() * 0.01
      });
    }

    var startTime = performance.now();
    function animate(currentTime) {
      var elapsed = currentTime - startTime;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      var activeCount = 0;
      particles.forEach(function (p) {
        if (p.alpha > 0.01) {
          activeCount++;
          p.x += p.vx; p.y += p.vy;
          p.vy += 0.08; p.vx *= 0.98;
          p.alpha -= p.decay;
          ctx.save();
          ctx.globalAlpha = Math.max(0, p.alpha);
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        }
      });
      if (activeCount > 0 && elapsed < 1300) {
        requestAnimationFrame(animate);
      } else if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
    }
    requestAnimationFrame(animate);
  }
});
