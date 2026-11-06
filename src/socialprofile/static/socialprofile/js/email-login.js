(function () {
  "use strict";

  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function qs(root, sel) {
    return root.querySelector(sel);
  }

  function qsa(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  function csrfToken(form) {
    var input = form && form.querySelector('[name="csrfmiddlewaretoken"]');
    if (input && input.value) return input.value;
    var cookie = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return cookie ? decodeURIComponent(cookie[1]) : "";
  }

  function show(el, on) {
    if (!el) return;
    if (on) {
      el.removeAttribute("hidden");
      el.hidden = false;
    } else {
      el.setAttribute("hidden", "hidden");
      el.hidden = true;
    }
    el.classList.toggle("is-active", !!on);
  }

  function clearFieldErrors(root) {
    qsa(root, "[data-sp-field-error]").forEach(function (box) {
      box.textContent = "";
      box.hidden = true;
      box.setAttribute("hidden", "hidden");
    });
    qsa(root, "[aria-invalid='true']").forEach(function (el) {
      el.removeAttribute("aria-invalid");
    });
    setChooseError(root, "");
  }

  function setChooseError(root, message) {
    var box = qs(root, "[data-sp-email-error]");
    if (!box) return;
    if (message) {
      box.textContent = message;
      box.hidden = false;
      box.removeAttribute("hidden");
    } else {
      box.textContent = "";
      box.hidden = true;
      box.setAttribute("hidden", "hidden");
    }
  }

  function setFieldError(root, field, message, scope) {
    clearFieldErrors(root);
    if (!field || !message) return;
    var ctx = scope || qs(root, ".sp-email-panel.is-active") || root;
    var box = qs(ctx, '[data-sp-field-error="' + field + '"]');
    var input = qs(ctx, '[data-sp-field="' + field + '"]');
    if (!box) box = qs(root, '[data-sp-field-error="' + field + '"]');
    if (!input) input = qs(root, '[data-sp-field="' + field + '"]');
    if (box) {
      box.textContent = message;
      box.hidden = false;
      box.removeAttribute("hidden");
    } else {
      setChooseError(root, message);
    }
    if (input) {
      input.setAttribute("aria-invalid", "true");
      try {
        input.focus();
      } catch (e) {
        /* ignore */
      }
    }
  }

  function toast(detail, level) {
    if (!detail) return;
    if (typeof Swal === "undefined") return;
    var icon = level === "success" ? "success" : level === "error" ? "error" : "info";
    Swal.fire({
      toast: true,
      position: "top-end",
      icon: icon,
      title: detail,
      showConfirmButton: false,
      timer: 4500,
      timerProgressBar: true,
    });
  }

  function syncEmail(root) {
    var emailInput = qs(root, "[data-sp-email-primary]");
    if (!emailInput) return "";
    var value = (emailInput.value || "").trim();
    emailInput.value = value;
    qsa(root, "[data-sp-email-mirror]").forEach(function (el) {
      el.value = value;
    });
    return value;
  }

  function validateEmail(root) {
    var value = syncEmail(root);
    var input = qs(root, "[data-sp-email-primary]");
    var msgRequired =
      root.getAttribute("data-msg-email-required") || "Enter your email.";
    var msgInvalid =
      root.getAttribute("data-msg-email-invalid") ||
      "Enter a valid email address.";
    if (!value) {
      setChooseError(root, msgRequired);
      if (input) {
        input.setAttribute("aria-invalid", "true");
        input.focus();
      }
      return false;
    }
    if (!EMAIL_RE.test(value)) {
      setChooseError(root, msgInvalid);
      if (input) {
        input.setAttribute("aria-invalid", "true");
        input.focus();
      }
      return false;
    }
    setChooseError(root, "");
    if (input) input.removeAttribute("aria-invalid");
    return true;
  }

  function setMode(root, mode) {
    root.setAttribute("data-sp-mode", mode);
    qsa(root, "[data-sp-panel]").forEach(function (panel) {
      show(panel, panel.getAttribute("data-sp-panel") === mode);
    });
    syncEmail(root);
    var focusSel = {
      choose: "[data-sp-email-primary]",
      login: "[data-sp-login-password]",
      register: "[data-sp-register-password]",
      otp: "[data-sp-otp-code]",
      reset: "[data-sp-reset-email]",
    }[mode];
    var focusEl = focusSel ? qs(root, focusSel) : null;
    if (focusEl) {
      try {
        focusEl.focus();
      } catch (e) {
        /* ignore */
      }
    }
  }

  function setBusy(form, busy) {
    if (!form) return;
    if (busy) {
      form.setAttribute("aria-busy", "true");
    } else {
      form.removeAttribute("aria-busy");
    }
    qsa(form, "button[type='submit']").forEach(function (btn) {
      btn.disabled = !!busy;
      btn.classList.toggle("is-loading", !!busy);
    });
  }

  function handleResult(root, data, form) {
    if (!data) return;
    if (data.purpose) {
      qsa(root, "[data-sp-otp-purpose]").forEach(function (el) {
        el.value = data.purpose;
      });
    }
    if (data.next_step) {
      setMode(root, data.next_step);
    }
    if (data.field && data.detail && !data.ok) {
      setFieldError(root, data.field, data.detail, form);
      return;
    }
    clearFieldErrors(root);
    if (data.detail) {
      toast(
        data.detail,
        data.ok === false ? "error" : data.level || "info"
      );
    }
    if (data.redirect) {
      window.location.assign(data.redirect);
    }
  }

  function clientRegisterChecks(root, form) {
    var pwd = form.querySelector('[data-sp-field="password"]');
    var confirm = form.querySelector('[data-sp-field="password_confirm"]');
    var msgMismatch =
      root.getAttribute("data-msg-password-mismatch") ||
      "Passwords do not match.";
    if (confirm && pwd && (pwd.value || "") !== (confirm.value || "")) {
      setFieldError(root, "password_confirm", msgMismatch, form);
      return false;
    }
    return true;
  }

  function submitAjax(root, form) {
    syncEmail(root);
    clearFieldErrors(root);
    if (!clientRegisterChecks(root, form)) return Promise.resolve();
    setBusy(form, true);
    var body = new FormData(form);
    return fetch(form.action, {
      method: "POST",
      body: body,
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrfToken(form),
      },
    })
      .then(function (res) {
        var ctype = (res.headers.get("content-type") || "").toLowerCase();
        if (ctype.indexOf("application/json") !== -1) {
          return res.json().then(function (data) {
            return { res: res, data: data };
          });
        }
        if (res.redirected && res.url) {
          window.location.assign(res.url);
          return null;
        }
        window.location.reload();
        return null;
      })
      .then(function (pack) {
        if (!pack) return;
        handleResult(root, pack.data, form);
      })
      .catch(function () {
        toast(
          root.getAttribute("data-msg-network") ||
            "Network error. Please try again.",
          "error"
        );
      })
      .finally(function () {
        setBusy(form, false);
      });
  }

  function init(root) {
    if (!root || root.getAttribute("data-sp-ready") === "1") return;
    root.setAttribute("data-sp-ready", "1");

    var emailInput = qs(root, "[data-sp-email-primary]");
    if (emailInput) {
      emailInput.addEventListener("input", function () {
        setChooseError(root, "");
        emailInput.removeAttribute("aria-invalid");
        syncEmail(root);
      });
      emailInput.addEventListener("change", function () {
        syncEmail(root);
      });
      emailInput.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter") {
          ev.preventDefault();
          var loginBtn = qs(root, '[data-sp-goto="login"]');
          if (loginBtn) loginBtn.click();
        }
      });
    }

    qsa(root, "[data-sp-goto]").forEach(function (btn) {
      btn.addEventListener("click", function (ev) {
        ev.preventDefault();
        var mode = btn.getAttribute("data-sp-goto");
        if (mode === "choose") {
          clearFieldErrors(root);
          setMode(root, mode);
          return;
        }
        if (!validateEmail(root)) return;
        clearFieldErrors(root);
        setMode(root, mode);
      });
    });

    qsa(root, "form").forEach(function (form) {
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        submitAjax(root, form);
      });
    });

    setMode(root, root.getAttribute("data-sp-mode") || "choose");
  }

  function boot() {
    qsa(document, "[data-sp-email-wizard]").forEach(init);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
