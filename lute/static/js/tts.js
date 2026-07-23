/**
 * Edge-TTS + SpeechSynthesis voice synthesis and Google auto-translation
 * integration for the Lute reading page.
 *
 * Primary TTS:  browser SpeechSynthesis API (like the working userscript)
 * Fallback TTS: backend /tts/<lang>/<text> endpoint (edge-tts)
 * Translate:    backend /api/translate/<sl>/<tl>/<text> endpoint
 *
 * Features:
 *   - Top-bar control panel (play all / pause / stop / speed slider).
 *   - Sentence-level 🔊 buttons at each paragraph / sentence row.
 *   - Word hover pronunciation (200 ms delay) via event delegation.
 *   - Auto-translation: when a term edit form opens with an empty
 *     #translation, the translation is fetched and auto-filled.
 */
(function () {
  "use strict";

  // ------------------------------------------------------------------
  // 0. Language detection
  // ------------------------------------------------------------------

  // Shared cache for cross-frame communication
  if (!window.top.__LUTE_TTS_CACHE__) {
    window.top.__LUTE_TTS_CACHE__ = {
      trans: {},
      lastWord: "",
      sl: "en",
      tl: "",
      selectedVoice: "",
      lastSpokenWord: "",
      detectedLang: "",
    };
  }
  const globalCache = window.top.__LUTE_TTS_CACHE__;

  // Read SL from: local input -> shared cache -> default
  const SL_INPUT = document.getElementById("tts_lang");
  if (SL_INPUT) {
    globalCache.sl = SL_INPUT.value || globalCache.sl || "en";
  }
  let SL = globalCache.sl || "en";

  // Read TL from: navigator.language -> shared cache -> default
  globalCache.tl = navigator.language || globalCache.tl || "zh-CN";
  let TL = globalCache.tl;

  const LANG_NAME_MAP = {
    japanese: "ja", japan: "ja",
    spanish: "es", espanol: "es",
    french: "fr", francais: "fr",
    german: "de", deutsch: "de",
    english: "en",
    chinese: "zh", mandarin: "zh",
    korean: "ko",
    russian: "ru",
    arabic: "ar",
    turkish: "tr", turkce: "tr",
    czech: "cs", cesky: "cs",
    sanskrit: "sa",
    hindi: "hi",
    indonesian: "id",
    portuguese: "pt",
    italian: "it",
  };

  // Cached language detection – only runs once per page load.
  let _cachedLang = null;
  function detectTextLanguage() {
    if (_cachedLang) return _cachedLang;
    if (SL_INPUT && SL_INPUT.value) {
      _cachedLang = SL_INPUT.value;
      return _cachedLang;
    }
    const textDiv =
      (window.top && window.top.document.getElementById("thetext")) ||
      document.getElementById("thetext");
    if (textDiv) {
      const content = textDiv.innerText || textDiv.textContent || "";
      if (content) {
        const sample = content.slice(0, 500);
        if (/[\u3040-\u309F\u30A0-\u30FF]/.test(sample)) { _cachedLang = "ja"; return _cachedLang; }
        if (/[\uAC00-\uD7AF\u1100-\u11FF]/.test(sample)) { _cachedLang = "ko"; return _cachedLang; }
        if (/[\u0900-\u097F]/.test(sample)) { _cachedLang = "hi"; return _cachedLang; }
        if (/[\u0600-\u06FF]/.test(sample)) { _cachedLang = "ar"; return _cachedLang; }
        if (/[\u0400-\u04FF]/.test(sample)) { _cachedLang = "ru"; return _cachedLang; }
        if (/[řěščžňů]/i.test(sample)) { _cachedLang = "cs"; return _cachedLang; }
        if (/[ğşı]/i.test(sample)) { _cachedLang = "tr"; return _cachedLang; }
        if (/[äöüß]/i.test(sample)) { _cachedLang = "de"; return _cachedLang; }
        if (/[ñ¿¡]/i.test(sample)) { _cachedLang = "es"; return _cachedLang; }
        if (/[œæ]/i.test(sample) ||
            (/[éèêàç]/i.test(sample) &&
              /\b(le|la|les|un|une|et|est|du|des)\b/i.test(sample))) { _cachedLang = "fr"; return _cachedLang; }
        if (/\b(the|and|is|in|to|of|that|it|was|for|on|are)\b/i.test(sample)) { _cachedLang = "en"; return _cachedLang; }
      }
    }
    _cachedLang = SL;
    return _cachedLang;
  }

  function getCurrentLangCode() {
    return detectTextLanguage();
  }

  // ------------------------------------------------------------------
  // 0b. User settings (read from LUTE_USER_SETTINGS)
  // ------------------------------------------------------------------

  function getSetting(key, defaultValue) {
    try {
      if (window.LUTE_USER_SETTINGS && window.LUTE_USER_SETTINGS[key] !== undefined) {
        var val = window.LUTE_USER_SETTINGS[key];
        if (val === "1" || val === 1 || val === true) return true;
        if (val === "0" || val === 0 || val === false) return false;
        return val;
      }
    } catch (_) {}
    return defaultValue;
  }

  var SETTINGS = {
    enabled: getSetting("tts_enabled", true),
    hoverPronunciation: getSetting("tts_hover_pronunciation", true),
    clickPronunciation: getSetting("tts_click_pronunciation", true),
    showControlPanel: getSetting("tts_show_control_panel", true),
    showSentenceButtons: getSetting("tts_show_sentence_buttons", true),
  };

  // If TTS is completely disabled, stop here
  if (!SETTINGS.enabled) {
    return;
  }

  // ------------------------------------------------------------------
  // 1. Speech synthesis (primary: browser SpeechSynthesis,
  //    fallback: backend /tts/ endpoint)
  // ------------------------------------------------------------------

  let currentUtterance = null;
  let globalSpeed = 1.0;
  let hoverTimer = null;

  function selectBestVoiceForLang(voices, targetLang) {
    if (!voices || voices.length === 0) return null;
    let matched = voices.filter(function (v) {
      return v.lang.toLowerCase().startsWith(targetLang);
    });
    if (matched.length === 0 && targetLang === "sa") {
      matched = voices.filter(function (v) {
        return v.lang.toLowerCase().startsWith("hi");
      });
    }
    if (matched.length === 0) return null;
    const keywords = ["online", "natural", "neural", "google", "microsoft"];
    for (const kw of keywords) {
      const found = matched.find(function (v) {
        return v.name.toLowerCase().includes(kw);
      });
      if (found) return found;
    }
    return matched[0];
  }

  function getSelectedVoice() {
    if (!("speechSynthesis" in window)) return null;

    const voiceSelect = document.getElementById("lute-voice-select");
    if (voiceSelect && voiceSelect.value) {
      const voices = window.speechSynthesis.getVoices();
      const found = voices.find(function (v) {
        return v.name === voiceSelect.value;
      });
      if (found) return found;
    }

    if (globalCache.selectedVoice) {
      const voices = window.speechSynthesis.getVoices();
      const found = voices.find(function (v) {
        return v.name === globalCache.selectedVoice;
      });
      if (found) return found;
    }

    return null;
  }

  function speakText(text, isFullText) {
    let cleanText = text.replace(/[#＃]/g, "").trim();
    if (!cleanText) return;

    if ("speechSynthesis" in window) {
      if (!isFullText && window.speechSynthesis.speaking && currentUtterance)
        return;
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}

      const utterance = new SpeechSynthesisUtterance();
      utterance.text = cleanText;

      let activeVoice = getSelectedVoice();
      const voices = window.speechSynthesis.getVoices();
      const detectedLang = getCurrentLangCode();

      if (!activeVoice && voices.length > 0) {
        activeVoice = selectBestVoiceForLang(voices, detectedLang);
      }

      if (activeVoice) {
        utterance.voice = activeVoice;
        utterance.lang = activeVoice.lang;
      } else {
        utterance.lang = detectedLang;
      }

      utterance.rate = globalSpeed;
      if (isFullText) {
        currentUtterance = utterance;
        utterance.onend = function () {
          currentUtterance = null;
          updatePlayButtonState(false);
        };
      }

      setTimeout(function () {
        window.speechSynthesis.speak(utterance);
      }, 20);
      return;
    }

    // --- Fallback: backend /tts/ endpoint ---
    const lang = getCurrentLangCode();
    const url = "/tts/" + lang + "/" + encodeURIComponent(cleanText);
    const audio = new Audio(url);
    audio.playbackRate = globalSpeed;
    if (isFullText) {
      audio.play().catch(function () {});
      currentUtterance = {
        stop: function () {
          audio.pause();
          audio.removeAttribute("src");
          audio.load();
        },
      };
      audio.addEventListener("ended", function () {
        currentUtterance = null;
        updatePlayButtonState(false);
      });
    } else {
      audio.play().catch(function () {});
    }
  }

  function stopFullText() {
    if ("speechSynthesis" in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (_) {}
    }
    if (currentUtterance && currentUtterance.stop) currentUtterance.stop();
    currentUtterance = null;
    updatePlayButtonState(false);
  }

  function pauseFullText() {
    if ("speechSynthesis" in window && window.speechSynthesis.speaking)
      window.speechSynthesis.pause();
  }

  function updatePlayButtonState(isPlaying) {
    const playBtn =
      document.getElementById("btn-lute-play") ||
      document.getElementById("tts-play");
    if (playBtn) {
      playBtn.innerHTML = isPlaying ? "🔊" : "▶";
      playBtn.style.background = isPlaying ? "#40c057" : "";
    }
  }

  // ------------------------------------------------------------------
  // 3. Text helpers
  // ------------------------------------------------------------------

  function cleanSentenceText(rawText) {
    return rawText
      .replace(/[#＃]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function getCleanFullText() {
    const textDiv = document.getElementById("thetext");
    if (!textDiv) return "";
    const rows = textDiv.querySelectorAll(".textsentence");
    if (rows.length === 0) {
      const pRows = textDiv.querySelectorAll(".textrow, p");
      if (pRows.length === 0) {
        return cleanSentenceText(textDiv.innerText || textDiv.textContent || "");
      }
      let segments = [];
      pRows.forEach(function (row) {
        const clone = row.cloneNode(true);
        const icons = clone.querySelectorAll(".lute-sentence-play-btn");
        icons.forEach(function (icon) { icon.remove(); });
        let rowText = clone.innerText || clone.textContent || "";
        if (rowText.trim()) segments.push(rowText.trim());
      });
      return cleanSentenceText(segments.join("\n"));
    }
    let segments = [];
    rows.forEach(function (row) {
      const clone = row.cloneNode(true);
      const icons = clone.querySelectorAll(".lute-sentence-play-btn");
      icons.forEach(function (icon) { icon.remove(); });
      let rowText = clone.innerText || clone.textContent || "";
      if (rowText.trim()) segments.push(rowText.trim());
    });
    return cleanSentenceText(segments.join("\n"));
  }

  function playFullText() {
    const fullText = getCleanFullText();
    if (fullText) speakText(fullText, true);
  }

  // ------------------------------------------------------------------
  // 4. Sentence 🔊 button injection
  // ------------------------------------------------------------------

  function injectSentencePlayButtons() {
    const textDiv = document.getElementById("thetext");
    if (!textDiv) return;

    const sentences = textDiv.querySelectorAll(".textsentence");
    if (sentences.length > 0) {
      sentences.forEach(function (s) {
        if (s.querySelector(".lute-sentence-play-btn")) return;
        const btn = document.createElement("span");
        btn.className = "lute-sentence-play-btn";
        btn.innerText = "🔊";
        btn.style.cssText =
          "display:inline-block;cursor:pointer;margin-right:4px;" +
          "user-select:none;font-size:14px;vertical-align:middle;";
        if (s.firstChild) s.insertBefore(btn, s.firstChild);
        else s.appendChild(btn);
      });
      return;
    }

    const rows = textDiv.querySelectorAll(".textrow, p");
    rows.forEach(function (row) {
      if (row.querySelector(".lute-sentence-play-btn")) return;
      const btn = document.createElement("span");
      btn.className = "lute-sentence-play-btn";
      btn.innerText = "🔊";
      btn.style.cssText =
        "display:inline-block;cursor:pointer;margin-right:8px;" +
        "user-select:none;font-size:14px;";
      if (row.firstChild) row.insertBefore(btn, row.firstChild);
      else row.appendChild(btn);
    });
  }

  // ------------------------------------------------------------------
  // 5. Event delegation (word hover + sentence click)
  // ------------------------------------------------------------------

  function setupEventDelegation() {
    const textDiv = document.getElementById("thetext");
    if (!textDiv || textDiv.dataset.delegated === "true") return;
    textDiv.dataset.delegated = "true";

    // Word hover pronunciation
    if (SETTINGS.hoverPronunciation) {
      textDiv.addEventListener("mouseover", function (e) {
        const wordSpan = e.target.closest("span.word, span[id^=\"w\"]");
        if (!wordSpan) return;
        const text =
          wordSpan.innerText || wordSpan.textContent || "";
        const cleanText = text.replace(/[#＃]/g, "").trim();
        if (!cleanText) return;
        clearTimeout(hoverTimer);
        hoverTimer = setTimeout(function () {
          if (
            !(window.speechSynthesis && window.speechSynthesis.speaking &&
              currentUtterance)
          ) {
            speakText(cleanText);
          }
        }, 200);
      });

      textDiv.addEventListener("mouseout", function (e) {
        const wordSpan = e.target.closest("span.word, span[id^=\"w\"]");
        if (wordSpan && !wordSpan.contains(e.relatedTarget)) {
          clearTimeout(hoverTimer);
        }
      });
    }

    // Sentence play button click
    textDiv.addEventListener("click", function (e) {
      const btn = e.target.closest(".lute-sentence-play-btn");
      if (!btn) return;
      e.stopPropagation();

      const row = btn.parentElement;
      if (!row) return;

      const tempRow = row.cloneNode(true);
      const icon = tempRow.querySelector(".lute-sentence-play-btn");
      if (icon) icon.remove();

      const cleanSentence = cleanSentenceText(
        tempRow.innerText || tempRow.textContent || ""
      );
      if (cleanSentence) {
        if (currentUtterance) stopFullText();
        speakText(cleanSentence);
      }
    });
  }

  // ------------------------------------------------------------------
  // 6. Auto-translate (term form observer)
  // ------------------------------------------------------------------

  let _isFilling = false;

  function forceFill(el, text) {
    if (!el) return;
    _isFilling = true;
    try {
      const setter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        "value"
      ).set;
      setter.call(el, text);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    } catch (_) {
      el.value = text;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
    setTimeout(function () { _isFilling = false; }, 50);
  }

  // ------------------------------------------------------------------
  // 6b. Client-side translation with multiple API fallbacks
  // ------------------------------------------------------------------

  function withTimeout(promise, ms) {
    var timer = new Promise(function (_, reject) {
      setTimeout(function () { reject(new Error("timeout")); }, ms);
    });
    return Promise.race([promise, timer]).catch(function () { return ""; });
  }

  function translateViaGoogle(sl, tl, text) {
    var url =
      "https://translate.googleapis.com/translate_a/single" +
      "?client=gtx&sl=" + sl + "&tl=" + tl + "&dt=t&q=" +
      encodeURIComponent(text);
    return withTimeout(
      fetch(url).then(function (r) { return r.json(); }),
      4000
    ).then(function (data) {
      if (data && data[0] && data[0][0]) {
        var result = data[0][0][0] || "";
        if (result && result.toLowerCase() === text.toLowerCase()) return "";
        return result;
      }
      return "";
    }).catch(function () { return ""; });
  }

  function translateViaMyMemory(sl, tl, text) {
    var langpair = sl + "|" + tl;
    var url =
      "https://api.mymemory.translated.net/get?q=" +
      encodeURIComponent(text) +
      "&langpair=" + encodeURIComponent(langpair);
    return withTimeout(
      fetch(url).then(function (r) { return r.json(); }),
      8000
    ).then(function (data) {
      if (data && data.responseData && data.responseData.translatedText) {
        var result = data.responseData.translatedText;
        if (result && result.toLowerCase() === text.toLowerCase()) return "";
        return result;
      }
      return "";
    }).catch(function () { return ""; });
  }

  function translateViaBackend(sl, tl, text) {
    var url =
      "/api/translate/" + sl + "/" + tl + "/" + encodeURIComponent(text);
    return withTimeout(
      fetch(url).then(function (r) { return r.json(); }),
      8000
    ).then(function (data) {
      if (data && data.translation) return data.translation;
      return "";
    }).catch(function () { return ""; });
  }

  function translateText(sl, tl, text) {
    return translateViaGoogle(sl, tl, text).then(function (result) {
      if (result) return result;
      return translateViaMyMemory(sl, tl, text);
    }).then(function (result) {
      if (result) return result;
      return translateViaBackend(sl, tl, text);
    }).catch(function () { return ""; });
  }

  // Debounced form checker – only runs when the form is actually visible.
  let _formCheckTimer = null;
  let _lastFormState = "";

  function processTranslationFlow() {
    // Quick check: is there a term form visible?
    const docs = [document];
    try {
      if (window.top && window.top.document && window.top.document !== document) {
        docs.push(window.top.document);
      }
    } catch (_) {}

    for (const doc of docs) {
      const textInput =
        doc.getElementById("text") ||
        doc.querySelector('input[name="text"]');
      const translationInput =
        doc.getElementById("translation") ||
        doc.querySelector('textarea[name="translation"]');

      if (!textInput || !textInput.value) continue;

      const word = textInput.value.trim();

      // Quick fingerprint to skip if nothing changed
      const formState = word + "|" + (translationInput ? translationInput.value : "");
      if (formState === _lastFormState) return;
      _lastFormState = formState;

      // Speak the word (only from the top/main frame)
      var isTopFrame = (window === window.top);
      if (isTopFrame && SETTINGS.clickPronunciation && globalCache.lastWord !== word) {
        speakText(word);
        globalCache.lastWord = word;
      }

      if (
        translationInput &&
        (!translationInput.value ||
          translationInput.value === "Translating...")
      ) {
        if (_isFilling) continue;

        if (globalCache.trans[word]) {
          forceFill(translationInput, globalCache.trans[word]);
        } else {
          forceFill(translationInput, "Translating...");
          const sl = getCurrentLangCode();
          const tl = TL;

          translateText(sl, tl, word)
            .then(function (translated) {
              if (translated) {
                globalCache.trans[word] = translated;
                let freshTarget =
                  doc.getElementById("translation") ||
                  doc.querySelector('textarea[name="translation"]');
                if (!freshTarget) {
                  freshTarget =
                    document.getElementById("translation") ||
                    document.querySelector('textarea[name="translation"]');
                }
                forceFill(freshTarget, translated);
              } else {
                let freshTarget =
                  doc.getElementById("translation") ||
                  doc.querySelector('textarea[name="translation"]');
                if (!freshTarget) {
                  freshTarget =
                    document.getElementById("translation") ||
                    document.querySelector('textarea[name="translation"]');
                }
                if (freshTarget && freshTarget.value === "Translating...") {
                  forceFill(freshTarget, "");
                }
              }
            })
            .catch(function () {
              let freshTarget =
                doc.getElementById("translation") ||
                doc.querySelector('textarea[name="translation"]');
              if (freshTarget && freshTarget.value === "Translating...") {
                forceFill(freshTarget, "");
              }
            });
        }
      }
      return;
    }
  }

  // Debounced form check – avoids excessive scanning.
  function debouncedFormCheck() {
    if (_formCheckTimer) clearTimeout(_formCheckTimer);
    _formCheckTimer = setTimeout(function () {
      _formCheckTimer = null;
      processTranslationFlow();
    }, 150);
  }

  // ------------------------------------------------------------------
  // 7. Control panel (injected or existing)
  // ------------------------------------------------------------------

  function injectControlPanel() {
    const existingPanel = document.getElementById("tts-control-panel");
    if (existingPanel) {
      wirePanelEvents(existingPanel);
      updateVoiceList();
      return;
    }

    const targetContainer =
      document.querySelector(".book-header") ||
      (document.getElementById("thetext") &&
        document.getElementById("thetext").parentElement);
    if (!targetContainer) return;

    if (!document.getElementById("lute-tts-panel")) {
      const panel = document.createElement("div");
      panel.id = "lute-tts-panel";
      panel.style.cssText =
        "display:inline-flex;align-items:center;background:#f1f3f5;" +
        "padding:6px 12px;margin:10px 0;border-radius:8px;" +
        "border:1px solid #dee2e6;gap:10px;font-family:sans-serif;" +
        "flex-wrap:wrap;z-index:9999;";
      panel.innerHTML =
        '<button id="btn-lute-play" title="Play" ' +
        'style="padding:5px 10px;background:#228be6;color:#fff;border:none;' +
        'border-radius:4px;cursor:pointer;font-size:14px;line-height:1;">▶</button>' +
        '<button id="btn-lute-pause" title="Pause" ' +
        'style="padding:5px 10px;background:#fab005;color:#fff;border:none;' +
        'border-radius:4px;cursor:pointer;font-size:14px;line-height:1;">⏸</button>' +
        '<button id="btn-lute-stop" title="Stop" ' +
        'style="padding:5px 10px;background:#fa5252;color:#fff;border:none;' +
        'border-radius:4px;cursor:pointer;font-size:14px;line-height:1;">⏹</button>' +
        '<div style="display:flex;align-items:center;gap:4px;' +
        'border-left:1px solid #ccc;padding-left:8px;">' +
        '<span title="Voice" style="font-size:14px;">🗣️</span>' +
        '<select id="lute-voice-select" style="padding:2px 4px;font-size:12px;' +
        'border-radius:4px;max-width:160px;border:1px solid #ccc;' +
        'background:#fff;color:#333;"></select>' +
        "</div>" +
        '<div style="display:flex;align-items:center;gap:4px;' +
        'border-left:1px solid #ccc;padding-left:8px;">' +
        '<span title="Speed" style="font-size:14px;">⚡</span>' +
        '<input id="lute-speed-slider" type="range" min="0.5" max="2.0" ' +
        'step="0.05" value="' + globalSpeed +
        '" style="width:70px;cursor:pointer;vertical-align:middle;" />' +
        '<span id="lute-speed-val" style="font-size:11px;font-weight:bold;' +
        'color:#228be6;min-width:32px;">' + globalSpeed.toFixed(2) + "x</span>" +
        "</div>";
      targetContainer.insertBefore(panel, targetContainer.firstChild);
      wirePanelEvents(panel);
      updateVoiceList();
    }
  }

  function wirePanelEvents(panel) {
    const playBtn = panel.querySelector("#btn-lute-play") || panel.querySelector("#tts-play");
    const pauseBtn = panel.querySelector("#btn-lute-pause") || panel.querySelector("#tts-pause");
    const stopBtn = panel.querySelector("#btn-lute-stop") || panel.querySelector("#tts-stop");
    const speedSlider = panel.querySelector("#lute-speed-slider") || panel.querySelector("#tts-rate");
    const speedVal = panel.querySelector("#lute-speed-val") || panel.querySelector("#tts-rate-val");

    if (playBtn && !playBtn.dataset.wired) {
      playBtn.dataset.wired = "true";
      playBtn.addEventListener("click", function () {
        if (window.speechSynthesis && window.speechSynthesis.paused && window.speechSynthesis.speaking) {
          window.speechSynthesis.resume();
        } else {
          playFullText();
        }
      });
    }
    if (pauseBtn && !pauseBtn.dataset.wired) {
      pauseBtn.dataset.wired = "true";
      pauseBtn.addEventListener("click", function () {
        if (window.speechSynthesis && window.speechSynthesis.paused) {
          window.speechSynthesis.resume();
        } else {
          pauseFullText();
        }
      });
    }
    if (stopBtn && !stopBtn.dataset.wired) {
      stopBtn.dataset.wired = "true";
      stopBtn.addEventListener("click", stopFullText);
    }
    if (speedSlider && !speedSlider.dataset.wired) {
      speedSlider.dataset.wired = "true";
      speedSlider.addEventListener("input", function (e) {
        const val = parseFloat(e.target.value);
        globalSpeed = val;
        if (speedVal) speedVal.innerText = val.toFixed(2) + "x";
      });
    }
    const voiceSel = panel.querySelector("#lute-voice-select") || panel.querySelector("#tts-voice-select");
    if (voiceSel && !voiceSel.dataset.wired) {
      voiceSel.dataset.wired = "true";
      voiceSel.addEventListener("change", function (e) {
        globalCache.selectedVoice = e.target.value;
      });
    }
  }

  function updateVoiceList() {
    const voiceSelect = document.getElementById("lute-voice-select");
    if (!voiceSelect || !("speechSynthesis" in window)) return;
    let voices = window.speechSynthesis.getVoices();
    if (voices.length === 0) return;

    const previousSelected = voiceSelect.value;
    voiceSelect.innerHTML = "";
    voices.sort(function (a, b) { return a.lang.localeCompare(b.lang); });

    const detectedLang = getCurrentLangCode();
    const recommendedVoice = selectBestVoiceForLang(voices, detectedLang);

    voices.forEach(function (voice) {
      const option = document.createElement("option");
      option.value = voice.name;
      option.textContent = "[" + voice.lang + "] " + voice.name;
      if (previousSelected && voices.some(function (v) { return v.name === previousSelected; })) {
        if (previousSelected === voice.name) option.selected = true;
      } else if (recommendedVoice && voice.name === recommendedVoice.name) {
        option.selected = true;
      }
      voiceSelect.appendChild(option);
    });

    if (voiceSelect.value) {
      globalCache.selectedVoice = voiceSelect.value;
    }
  }

  // ------------------------------------------------------------------
  // 8. Lightweight observers (optimized for performance)
  // ------------------------------------------------------------------

  // UI observer: only watches #thetext for top-level child changes.
  // Does NOT use subtree:true — that was the main bottleneck on
  // Japanese pages with hundreds of word spans.
  let _uiObserver = null;
  let _uiDebounceTimer = null;
  function startUIObserver() {
    if (_uiObserver) return;
    const textDiv = document.getElementById("thetext");
    if (!textDiv) return;

    _uiObserver = new MutationObserver(function (mutations) {
      let needsUpdate = false;
      for (const m of mutations) {
        if (m.addedNodes.length > 0) { needsUpdate = true; break; }
      }
      if (!needsUpdate) return;

      // Debounce: wait 100ms before processing, so multiple rapid
      // mutations (e.g., from add_status_classes + start_hover_mode)
      // only trigger one call.
      if (_uiDebounceTimer) clearTimeout(_uiDebounceTimer);
      _uiDebounceTimer = setTimeout(function () {
        _uiDebounceTimer = null;
        if (SETTINGS.showSentenceButtons) injectSentencePlayButtons();
        setupEventDelegation();
      }, 100);
    });

    // Only observe childList (no subtree) — top-level changes only.
    // This catches $('#thetext').html(data) without firing on every
    // individual word span modification.
    _uiObserver.observe(textDiv, { childList: true });
  }

  // Form observer: lightweight — only fires on body childList changes
  // (e.g., when Lute opens a term form iframe).  No attribute watching.
  let _formObserver = null;
  function startFormObserver() {
    if (_formObserver) return;
    _formObserver = new MutationObserver(function () {
      debouncedFormCheck();
    });

    // Only observe childList (not attributes) to reduce overhead.
    _formObserver.observe(document.body, { childList: true, subtree: false });
  }

  // ------------------------------------------------------------------
  // 9. Boot
  // ------------------------------------------------------------------

  function boot() {
    // Initial setup — only on the main reading page.
    if (document.getElementById("thetext")) {
      if (SETTINGS.showControlPanel) injectControlPanel();
      if (SETTINGS.showSentenceButtons) injectSentencePlayButtons();
      setupEventDelegation();
      startUIObserver();
    }

    // Start lightweight form observer (detects term form iframe open)
    startFormObserver();

    // Check for existing term form immediately
    processTranslationFlow();

    // SpeechSynthesis voices — only load on main page, not iframe
    if (document.getElementById("thetext") && "speechSynthesis" in window) {
      window.speechSynthesis.getVoices();
      window.speechSynthesis.onvoiceschanged = updateVoiceList;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
