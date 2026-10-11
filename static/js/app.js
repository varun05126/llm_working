// SkillHer Progressive Enhancement & 3D Interactive Controller (< 12 KB)
document.addEventListener('DOMContentLoaded', function () {
  'use strict';
  document.documentElement.classList.add('js-enabled');

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isFinePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  // 1. Scroll Reveal (IntersectionObserver)
  var revealElements = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && revealElements.length > 0) {
    var revealObserver = new IntersectionObserver(function (entries, obs) {
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
      revealObserver.observe(el);
    });
  } else {
    revealElements.forEach(function (el) { el.classList.add('revealed'); });
  }

  // 2. 3D Scene Controller & Pointer Parallax (+-8deg)
  var scenes = document.querySelectorAll('.scene3d');
  if (scenes.length > 0 && !prefersReducedMotion) {
    // Visibility & Off-screen pause
    if ('IntersectionObserver' in window) {
      var sceneObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.remove('paused');
          } else {
            entry.target.classList.add('paused');
          }
        });
      }, { threshold: 0.05 });

      scenes.forEach(function (sc) { sceneObserver.observe(sc); });
    }

    document.addEventListener('visibilitychange', function () {
      scenes.forEach(function (sc) {
        if (document.hidden) {
          sc.classList.add('paused');
        } else {
          sc.classList.remove('paused');
        }
      });
    });

    // Pointer Parallax (RAF driven)
    if (isFinePointer) {
      scenes.forEach(function (scene) {
        var targetRx = 0;
        var targetRy = 0;
        var currentRx = 0;
        var currentRy = 0;
        var isRafActive = false;

        function updateTilt() {
          currentRx += (targetRx - currentRx) * 0.1;
          currentRy += (targetRy - currentRy) * 0.1;

          scene.style.setProperty('--rx', currentRx.toFixed(2) + 'deg');
          scene.style.setProperty('--ry', currentRy.toFixed(2) + 'deg');

          if (Math.abs(targetRx - currentRx) > 0.05 || Math.abs(targetRy - currentRy) > 0.05) {
            requestAnimationFrame(updateTilt);
          } else {
            isRafActive = false;
          }
        }

        scene.addEventListener('mousemove', function (e) {
          var rect = scene.getBoundingClientRect();
          var x = (e.clientX - rect.left) / rect.width - 0.5;
          var y = (e.clientY - rect.top) / rect.height - 0.5;

          // Parallax range: +-8 degrees
          targetRx = -y * 16;
          targetRy = x * 16;

          if (!isRafActive) {
            isRafActive = true;
            requestAnimationFrame(updateTilt);
          }
        });

        scene.addEventListener('mouseleave', function () {
          targetRx = 0;
          targetRy = 0;
          if (!isRafActive) {
            isRafActive = true;
            requestAnimationFrame(updateTilt);
          }
        });
      });
    }
  }

  // 3. Scroll Story Controller ("Learn → Build → Lead")
  var storyPanels = document.querySelectorAll('.story-panel[data-story-stage]');
  var storyScene = document.getElementById('storyScene');

  if (storyPanels.length > 0 && storyScene && 'IntersectionObserver' in window) {
    var storyObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var stage = entry.target.getAttribute('data-story-stage');
          if (stage) {
            storyScene.setAttribute('data-stage', stage);
            // Highlight active panel
            storyPanels.forEach(function (p) { p.classList.remove('active'); });
            entry.target.classList.add('active');
          }
        }
      });
    }, { rootMargin: '-25% 0px -25% 0px', threshold: 0.3 });

    storyPanels.forEach(function (panel) {
      storyObserver.observe(panel);
    });
  }

  // 4. Form Loading States
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
        submitBtn.textContent = 'Generating blueprint...';
      }
    });
  });

  // 5. Assessment Wizard Step Transitions
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

  // 6. Rating Buttons
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

  // 7. Milestone Progress Tracker & Server Synchronization
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

        // Sync with API
        var recId = cb.getAttribute('data-rec-id');
        var key = cb.getAttribute('data-milestone-key');
        if (recId && key) {
          var csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
          var csrf = csrfInput ? csrfInput.value : '';
          fetch('/api/milestone/toggle/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrf
            },
            body: JSON.stringify({
              recommendation_id: recId,
              milestone_key: key,
              completed: cb.checked
            })
          }).catch(function (err) {
            console.error('Milestone sync failed', err);
          });
        }
      });
    });

    updateProgress();
  }

  // 8. Results Celebration Canvas Burst
  var celebrationEl = document.getElementById('celebrationBurst');
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

    var colors = ['#b83280', '#f472b6', '#f5a623', '#fbbf24', '#701a75'];
    var particles = [];
    var count = 36;
    var originX = window.innerWidth / 2;
    var originY = Math.min(window.innerHeight * 0.35, 260);

    for (var i = 0; i < count; i++) {
      var angle = (Math.PI * 2 * i) / count + (Math.random() * 0.2 - 0.1);
      var speed = 3.0 + Math.random() * 4.5;
      particles.push({
        x: originX, y: originY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 1.8,
        radius: 2.5 + Math.random() * 2.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        alpha: 1, decay: 0.015 + Math.random() * 0.01
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
          p.vy += 0.09; p.vx *= 0.98;
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
      if (activeCount > 0 && elapsed < 1400) {
        requestAnimationFrame(animate);
      } else if (canvas.parentNode) {
        canvas.parentNode.removeChild(canvas);
      }
    }
    requestAnimationFrame(animate);
  }
});
