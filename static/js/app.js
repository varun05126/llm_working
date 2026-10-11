// SkillHer Vanilla Progressive Enhancement (< 3 KB)
document.addEventListener('DOMContentLoaded', function () {
  // 1. Form submit loading states
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

  // 2. Client-side assessment step progression (progressive enhancement)
  var steps = document.querySelectorAll('.assessment-step-card');
  if (steps.length > 1) {
    var currentIndex = 0;
    var nextBtn = document.getElementById('jsNextStep');
    var prevBtn = document.getElementById('jsPrevStep');
    var submitBtn = document.getElementById('jsSubmitAssessment');
    var stepCounter = document.getElementById('jsStepCounter');

    function showStep(index) {
      steps.forEach(function (step, i) {
        step.style.display = i === index ? 'block' : 'none';
      });
      if (stepCounter) {
        stepCounter.textContent = (index + 1) + ' / ' + steps.length;
      }
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

    // Initialize first step
    showStep(0);
  }

  // 3. Rating button selection visual toggle
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

  // 4. Milestone progress tracker
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

        // Optional server-side sync if recommendation id is present
        var recId = cb.getAttribute('data-rec-id');
        var skillId = cb.getAttribute('data-skill-id');
        if (recId && skillId) {
          fetch('/api/milestone/toggle/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || ''
            },
            body: JSON.stringify({
              recommendation_id: recId,
              skill_id: skillId,
              completed: cb.checked
            })
          }).catch(function () {});
        }
      });
    });

    updateProgress();
  }
});
