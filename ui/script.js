let editor;
let loadedEmails = [];
let progressInterval;
let currentSendMode = 'template';
let presetTemplates = [];
let userTemplates = [];
let galleryTab = 'sys';

// Tab Switching
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => {
        el.classList.add('hidden');
        el.classList.remove('block', 'flex');
    });
    
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('bg-slate-800', 'text-white');
        el.classList.add('text-slate-400');
    });

    const target = document.getElementById(`tab-${tabId}`);
    if(tabId === 'builder') {
        target.classList.remove('hidden');
        target.classList.add('flex');
        if(!editor) initGrapesJS();
    } else {
        target.classList.remove('hidden');
        target.classList.add('block');
    }

    const btn = document.getElementById(`btn-${tabId}`);
    btn.classList.add('bg-slate-800', 'text-white');
    btn.classList.remove('text-slate-400');
}

// Initial PyWebView Ready Hook
window.addEventListener('pywebviewready', function() {
    loadSettings();
    document.getElementById('btn-dashboard').classList.add('bg-slate-800', 'text-white');
    
    // Fetch templates
    pywebview.api.get_preset_templates().then(templates => {
        presetTemplates = templates;
        renderTemplateGallery();
    });
    pywebview.api.get_user_templates().then(templates => {
        userTemplates = templates || [];
    });
});

// Toast Notifications
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-msg');
    const iconEl = document.getElementById('toast-icon');

    msgEl.innerText = msg;
    
    if (isError) {
        iconEl.className = 'fa-solid fa-triangle-exclamation text-rose-400 text-xl mr-3';
        toast.className = 'fixed bottom-6 right-6 bg-slate-800 border-l-4 border-rose-500 shadow-2xl rounded-lg p-4 flex items-center transform transition-all duration-300 z-50 translate-y-0 opacity-100';
    } else {
        iconEl.className = 'fa-solid fa-circle-check text-emerald-400 text-xl mr-3';
        toast.className = 'fixed bottom-6 right-6 bg-slate-800 border-l-4 border-emerald-500 shadow-2xl rounded-lg p-4 flex items-center transform transition-all duration-300 z-50 translate-y-0 opacity-100';
    }

    setTimeout(() => {
        toast.classList.add('translate-y-24', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 4000);
}

// SMTP Presets
function applySmtpPreset(provider) {
    if(provider === 'gmail') {
        document.getElementById('smtp_server').value = 'smtp.gmail.com';
        document.getElementById('smtp_port').value = '587';
    } else if(provider === 'outlook') {
        document.getElementById('smtp_server').value = 'smtp-mail.outlook.com';
        document.getElementById('smtp_port').value = '587';
    } else if(provider === 'yahoo') {
        document.getElementById('smtp_server').value = 'smtp.mail.yahoo.com';
        document.getElementById('smtp_port').value = '465'; // Usually 465 or 587
    }
    showToast(`Applied ${provider} preset.`);
}

// Template Gallery
function toggleTemplateGallery() {
    const gallery = document.getElementById('template-gallery');
    if (gallery.classList.contains('-translate-x-full')) {
        gallery.classList.remove('-translate-x-full');
        renderTemplateGallery();
    } else {
        gallery.classList.add('-translate-x-full');
    }
}

function switchGallery(tab) {
    galleryTab = tab;
    const btnSys = document.getElementById('tab-sys');
    const btnUser = document.getElementById('tab-user');
    if (tab === 'sys') {
        btnSys.className = 'flex-1 py-1.5 text-xs font-bold rounded-md bg-slate-700 text-white shadow transition-all';
        btnUser.className = 'flex-1 py-1.5 text-xs font-bold rounded-md text-slate-400 hover:text-white transition-all';
    } else {
        btnUser.className = 'flex-1 py-1.5 text-xs font-bold rounded-md bg-slate-700 text-white shadow transition-all';
        btnSys.className = 'flex-1 py-1.5 text-xs font-bold rounded-md text-slate-400 hover:text-white transition-all';
    }
    renderTemplateGallery();
}

function renderTemplateGallery() {
    const container = document.getElementById('gallery-container');
    container.innerHTML = '';
    const items = galleryTab === 'sys' ? presetTemplates : userTemplates;
    
    if (items.length === 0) {
        container.innerHTML = '<div class="text-sm text-slate-500 text-center mt-4">No templates found.</div>';
        return;
    }
    
    items.forEach((tpl, idx) => {
        const btn = document.createElement('button');
        btn.className = 'w-full text-left bg-slate-800 hover:bg-slate-700 p-3 rounded-lg border border-slate-700 transition-colors flex items-center justify-between group';
        btn.onclick = () => loadPresetTemplate(idx, galleryTab);
        btn.innerHTML = `
            <span class="text-sm text-slate-200">${tpl.name}</span>
            <i class="fa-solid fa-chevron-right text-slate-500 text-xs opacity-0 group-hover:opacity-100 transition-opacity"></i>
        `;
        container.appendChild(btn);
    });
}

function loadPresetTemplate(idx, type) {
    if(!editor) return;
    const tpl = type === 'sys' ? presetTemplates[idx] : userTemplates[idx];
    if (tpl) {
        editor.setComponents(tpl.html);
        toggleTemplateGallery();
        showToast(`Loaded "${tpl.name}" template`);
    }
}

function saveUserTemplate() {
    const nameInput = document.getElementById('custom-template-name');
    const name = nameInput.value.trim();
    if (!name) {
        showToast("Please enter a name for the custom template", true);
        return;
    }
    if(!editor) return;
    const htmlWithCss = editor.runCommand('gjs-get-inlined-html');
    pywebview.api.save_user_template(name, htmlWithCss).then(res => {
        if(res.success) {
            showToast(res.message);
            nameInput.value = '';
            pywebview.api.get_user_templates().then(t => { userTemplates = t || []; renderTemplateGallery(); });
        } else {
            showToast(res.message, true);
        }
    });
}

// GrapesJS Initialization
function initGrapesJS() {
    editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        width: 'auto',
        fromElement: true,
        plugins: ['gjs-preset-newsletter'],
        pluginsOpts: {
            'gjs-preset-newsletter': {
                modalTitleImport: 'Import template'
            }
        },
        storageManager: false,
    });

    pywebview.api.get_template().then(html => {
        if(html && html.trim() !== '') {
            editor.setComponents(html);
        }
    });
}

function saveTemplate() {
    if(!editor) return;
    const htmlWithCss = editor.runCommand('gjs-get-inlined-html');
    pywebview.api.save_template(htmlWithCss).then(res => {
        showToast(res.message, !res.success);
    });
}

// Settings
function loadSettings() {
    pywebview.api.get_settings().then(settings => {
        document.getElementById('smtp_server').value = settings.smtp_server || '';
        document.getElementById('smtp_port').value = settings.smtp_port || '587';
        document.getElementById('smtp_user').value = settings.smtp_user || '';
        document.getElementById('smtp_password').value = settings.smtp_password || '';
        document.getElementById('from_name').value = settings.from_name || '';
        document.getElementById('delay').value = settings.delay || '1.0';
    });
}

function saveSettings() {
    const settings = {
        smtp_server: document.getElementById('smtp_server').value,
        smtp_port: document.getElementById('smtp_port').value,
        smtp_user: document.getElementById('smtp_user').value,
        smtp_password: document.getElementById('smtp_password').value,
        from_email: document.getElementById('smtp_user').value, // Auto tie to username
        from_name: document.getElementById('from_name').value,
        delay: parseFloat(document.getElementById('delay').value) || 1.0
    };
    
    pywebview.api.save_settings(settings).then(res => {
        showToast(res.message, !res.success);
    });
}

// Recipients
function importFile() {
    pywebview.api.select_file().then(res => {
        if(res.success) {
            // Append rather than replace if desired, we'll replace for simplicity but append in logic
            loadedEmails = [...new Set([...loadedEmails, ...res.emails])];
            updateRecipientCount();
            showToast(`Loaded ${res.count} emails from file.`);
        } else {
            showToast(res.message, true);
        }
    });
}

function addManualEmails() {
    const input = document.getElementById('manual_emails').value;
    if(!input.trim()) return;
    
    // Extract emails via regex roughly
    const regex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const found = input.match(regex);
    if(found) {
        loadedEmails = [...new Set([...loadedEmails, ...found])];
        updateRecipientCount();
        document.getElementById('manual_emails').value = '';
        showToast(`Added ${found.length} valid email(s).`);
    } else {
        showToast("No valid emails found.", true);
    }
}

function clearRecipients() {
    loadedEmails = [];
    updateRecipientCount();
    showToast("Recipient list cleared.");
}

function checkRisk() {
    const total = loadedEmails.length;
    pywebview.api.get_settings().then(settings => {
        const delay = parseFloat(settings.delay || 1.0);
        const warning = document.getElementById('risk-warning');
        if (total > 50 && delay < 2.0) {
            warning.classList.remove('hidden');
        } else {
            warning.classList.add('hidden');
        }
    });
}

function updateRecipientCount() {
    document.getElementById('recipient-count').innerText = loadedEmails.length;
    checkRisk();
}

// Sending Logic
function setSendMode(mode) {
    currentSendMode = mode;
    const btnTpl = document.getElementById('mode-template');
    const btnTxt = document.getElementById('mode-text');
    const txtConfig = document.getElementById('plain-text-config');

    if(mode === 'template') {
        btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        txtConfig.classList.add('hidden');
    } else {
        btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        txtConfig.classList.remove('hidden');
    }
}

function startSending(resume = false) {
    const subject = document.getElementById('subject').value;
    const plainText = document.getElementById('plain_text_message').value;
    const limitInput = parseInt(document.getElementById('safety_limit').value) || 0;

    if(!subject) {
        showToast("Please enter an email subject", true);
        return;
    }
    if(loadedEmails.length === 0) {
        showToast("Please add recipients first", true);
        return;
    }

    pywebview.api.start_sending(loadedEmails, subject, currentSendMode, plainText, limitInput, resume).then(res => {
        if(res.success) {
            document.getElementById('btn-send').classList.add('hidden');
            document.getElementById('btn-resume').classList.add('hidden');
            document.getElementById('btn-stop').classList.remove('hidden');
            document.getElementById('btn-stop').classList.add('flex');
            showToast(res.message);
            
            if(!resume) {
                document.getElementById('prog-bar').style.width = '0%';
                document.getElementById('prog-sent-num').innerText = '0';
                document.getElementById('prog-failed-num').innerText = '0';
                document.getElementById('prog-sent').innerText = '0';
            }
            
            progressInterval = setInterval(updateProgress, 500);
        } else {
            showToast(res.message, true);
        }
    });
}

function resumeSending() {
    startSending(true);
}

function stopSending() {
    pywebview.api.stop_sending(true).then(res => {
        showToast(res.message);
        document.getElementById('btn-send').classList.add('hidden');
        document.getElementById('btn-stop').classList.add('hidden');
        document.getElementById('btn-stop').classList.remove('flex');
        document.getElementById('btn-resume').classList.remove('hidden');
        document.getElementById('btn-resume').classList.add('flex');
        clearInterval(progressInterval);
    });
}

function updateProgress() {
    pywebview.api.get_progress().then(res => {
        const total = res.total;
        const sent = res.sent;
        const failed = res.failed;
        
        document.getElementById('prog-total').innerText = total;
        document.getElementById('prog-sent').innerText = sent;
        document.getElementById('prog-sent-num').innerText = sent;
        document.getElementById('prog-failed-num').innerText = failed;
        
        let percent = total > 0 ? Math.round(((sent + failed) / total) * 100) : 0;
        document.getElementById('prog-bar').style.width = `${percent}%`;
        
        if(!res.sending) {
            clearInterval(progressInterval);
            document.getElementById('btn-stop').classList.add('hidden');
            document.getElementById('btn-stop').classList.remove('flex');
            
            if (res.paused) {
                document.getElementById('btn-send').classList.add('hidden');
                document.getElementById('btn-resume').classList.remove('hidden');
                document.getElementById('btn-resume').classList.add('flex');
                showToast("Sending Paused (Safety Limit Reached)");
            } else if(total > 0 && (sent + failed) === total) {
                document.getElementById('btn-send').classList.remove('hidden');
                document.getElementById('btn-resume').classList.add('hidden');
                document.getElementById('btn-resume').classList.remove('flex');
                showToast("Campaign finished!");
            }
        }
    });
}
