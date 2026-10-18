// One question per screen, with Back / Next and fields that appear only when they apply.
// Without JavaScript the page still works: every question shows as one long form.
(function () {
  document.documentElement.classList.add("js");

  document.addEventListener("click", function (event) {
    if (event.target.closest("[data-print]")) window.print();
  });

  var form = document.querySelector("[data-quiz]");
  if (!form) return;

  var screens = Array.prototype.slice.call(form.querySelectorAll("[data-screen]"));
  var progressText = form.querySelector("[data-progress-text]");
  var progressBar = form.querySelector("[data-progress-bar]");
  var lang = document.documentElement.lang;
  var current = 0;

  function value(name) {
    var field = form.elements[name];
    if (!field) return "";
    if (field.length !== undefined && !field.tagName) return field.value;   // radio group
    if (field.type === "checkbox") return field.checked ? field.value : "";
    return field.value;
  }

  function matches(condition) {
    return Object.keys(condition).every(function (name) {
      return condition[name].indexOf(value(name)) !== -1;
    });
  }

  function updateFields() {
    form.querySelectorAll("[data-field][data-show-if]").forEach(function (field) {
      field.hidden = !matches(JSON.parse(field.getAttribute("data-show-if")));
    });
  }

  function show(index, moveFocus) {
    current = index;
    screens.forEach(function (screen, i) { screen.hidden = i !== index; });
    var text = lang === "fr"
      ? "Question " + (index + 1) + " sur " + screens.length
      : "Question " + (index + 1) + " of " + screens.length;
    progressText.textContent = text;
    progressBar.style.width = ((index + 1) / screens.length * 100) + "%";
    if (moveFocus) {
      var heading = screens[index].querySelector(".question");
      heading.focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
    }
  }

  function screenIsValid(screen) {
    var ok = true;
    screen.querySelectorAll("[data-required]").forEach(function (input) {
      var field = input.closest("[data-field]");
      var old = field.querySelector(".error[data-js]");
      if (old) old.remove();
      if (!field.hidden && !input.value.trim()) {
        ok = false;
        var message = document.createElement("p");
        message.className = "error";
        message.setAttribute("data-js", "");
        message.id = input.name + "-error";
        message.textContent = lang === "fr" ? "Répondez à cette question pour continuer." : "Answer this to continue.";
        field.appendChild(message);
        input.setAttribute("aria-invalid", "true");
        input.setAttribute("aria-describedby", message.id);
        input.focus();
      } else {
        input.removeAttribute("aria-invalid");
      }
    });
    return ok;
  }

  form.addEventListener("click", function (event) {
    if (event.target.closest("[data-next]")) {
      if (screenIsValid(screens[current])) show(current + 1, true);
    } else if (event.target.closest("[data-back]")) {
      show(current - 1, true);
    }
  });

  // Enter moves to the next question instead of submitting the whole form early.
  form.addEventListener("keydown", function (event) {
    if (event.key !== "Enter" || event.target.tagName === "BUTTON") return;
    event.preventDefault();
    var next = screens[current].querySelector("[data-next]");
    if (next) next.click();
    else if (screenIsValid(screens[current])) form.requestSubmit();
  });

  form.addEventListener("submit", function (event) {
    if (!screenIsValid(screens[current])) event.preventDefault();
  });

  form.addEventListener("change", updateFields);

  updateFields();
  var start = screens.findIndex(function (screen) { return screen.hasAttribute("data-start"); });
  show(start === -1 ? 0 : start, start !== -1);
})();
