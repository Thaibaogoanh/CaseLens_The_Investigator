'use strict';
(() => {
  let serverConfig = null;
  const dialog = $('#personal-ai-dialog');
  $('#personal-ai-btn').addEventListener('click', () => {
    if (state.busy || !state.config) return;
    $('#personal-status').textContent = window.personalAI ? 'Your key is active for this tab. Enter a key to replace it.' : 'Using server settings. You can override them for this tab.';
    dialog.showModal();
  });
  $('#personal-provider').addEventListener('change', () => {
    $('#personal-model').value = $('#personal-provider').value === 'gemini' ? 'gemini-3.8-flash' : 'gpt-4.1-mini';
  });
  function refresh() {
    modeNote(); setBusy(false);
    if (state.result) renderReport();
    $('#connection').textContent = window.personalAI ? `Your ${window.personalAI.provider} key` : (state.config.ai_available ? 'Live AI configured' : 'Sample mode ready');
    $('#personal-ai-btn').textContent = window.personalAI ? 'Your key active · settings' : 'API settings';
  }
  $('#personal-ai-form').addEventListener('submit', event => {
    event.preventDefault();
    if (state.busy || !state.config) return;
    if (!['localhost','127.0.0.1','[::1]'].includes(location.hostname) && location.protocol !== 'https:') {
      $('#personal-status').textContent = 'Use HTTPS before entering credentials on a public deployment.'; return;
    }
    const key = $('#personal-key').value.trim();
    if (!/^[\x21-\x7E]{1,1024}$/.test(key)) { $('#personal-status').textContent = 'Check the key: no spaces or line breaks.'; return; }
    if (!serverConfig) serverConfig = {...state.config};
    window.personalAI = {key, provider:$('#personal-provider').value, model:$('#personal-model').value.trim()};
    state.config = {...serverConfig, ai_available:true, provider:window.personalAI.provider, model:window.personalAI.model, review_model:window.personalAI.model};
    $('#personal-key').value = ''; dialog.close(); refresh();
    tell('Your key will be used for new AI requests. Existing reports retain their original model labels.');
  });
  $('#personal-clear').addEventListener('click', () => {
    if (state.busy) return;
    window.personalAI = null; $('#personal-key').value = '';
    if (serverConfig) state.config = {...serverConfig};
    dialog.close(); refresh(); tell('Personal key cleared. Server settings restored.');
  });
})();
