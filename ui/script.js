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
        populateTemplateDropdown();
    });
    pywebview.api.get_user_templates().then(templates => {
        userTemplates = templates || [];
        populateTemplateDropdown();
    });
    
    // Check for previous state
    pywebview.api.get_state().then(state => {
        if (state && state.current_emails && state.current_emails.length > 0 && state.last_index < state.current_emails.length) {
            document.getElementById('btn-recovery').classList.remove('hidden');
            document.getElementById('btn-recovery').classList.add('flex');
        }
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
    
    // User Templates
    const userContainer = document.getElementById('user-templates');
    userContainer.innerHTML = '';
    if (userTemplates.length === 0) {
        userContainer.innerHTML = '<div class="col-span-1 md:col-span-2 text-sm text-slate-500 text-center py-4">No saved templates yet.</div>';
    } else {
        userTemplates.forEach((tpl, idx) => {
            const btn = document.createElement('div');
            btn.className = 'bg-slate-800 border border-slate-700 hover:border-blue-500 p-4 rounded-xl cursor-pointer transition-all hover:shadow-lg group relative';
            btn.innerHTML = `
                <div class="flex items-center justify-between mb-2">
                    <div class="w-8 h-8 rounded bg-blue-500/10 text-blue-400 flex items-center justify-center">
                        <i class="fa-solid fa-file-code"></i>
                    </div>
                </div>
                <h4 class="text-white font-medium text-sm pr-8">${tpl.name}</h4>
                <div class="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button class="text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 w-7 h-7 rounded flex items-center justify-center transition-colors" title="Delete Template" onclick="event.stopPropagation(); deleteUserTemplate(${idx})">
                        <i class="fa-solid fa-trash text-xs"></i>
                    </button>
                </div>
                <div class="absolute inset-0 z-0" onclick="loadPresetTemplate(${idx}, 'user')"></div>
            `;
            userContainer.appendChild(btn);
        });
    }
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
    
    // Some grapejs versions fail to inline accurately if components are empty or complex. Better to inject raw CSS into head.
    const html = editor.getHtml();
    const css = editor.getCss();
    const fullHtml = `<html><head><style>${css}</style></head><body>${html}</body></html>`;
    
    pywebview.api.save_user_template(name, fullHtml).then(res => {
        if(res.success) {
            showToast(res.message);
            nameInput.value = '';
            pywebview.api.get_user_templates().then(t => { 
                userTemplates = t || []; 
                renderTemplateGallery(); 
                populateTemplateDropdown();
            });
        } else {
            showToast(res.message, true);
        }
    });
}

function deleteUserTemplate(idx) {
    if(confirm("Are you sure you want to delete this template?")) {
        pywebview.api.delete_user_template(idx).then(res => {
            if(res.success) {
                showToast(res.message);
                pywebview.api.get_user_templates().then(t => { 
                    userTemplates = t || []; 
                    renderTemplateGallery(); 
                    populateTemplateDropdown();
                });
            } else {
                showToast(res.message, true);
            }
        });
    }
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

    // Auto-save silently
    let autoSaveTimeout;
    editor.on('change:changesCount', () => {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            const html = editor.getHtml();
            const css = editor.getCss();
            const fullHtml = `<html><head><style>${css}</style></head><body>${html}</body></html>`;
            pywebview.api.save_template(fullHtml);
        }, 1000);
    });

    pywebview.api.get_template().then(html => {
        if(html && html.trim() !== '') {
            editor.setComponents(html);
        }
    });
}

function populateTemplateDropdown() {
    const select = document.getElementById('send_template_select');
    if (!select) return;
    select.innerHTML = '<option value="editor">🔥 Current Editor Layout</option>';
    
    presetTemplates.forEach((tpl, idx) => {
        select.innerHTML += `<option value="sys_${idx}">[System] ${tpl.name}</option>`;
    });
    userTemplates.forEach((tpl, idx) => {
        select.innerHTML += `<option value="user_${idx}">[My Templates] ${tpl.name}</option>`;
    });
}

function saveTemplate() {
    if(!editor) return;
    const html = editor.getHtml();
    const css = editor.getCss();
    const fullHtml = `<html><head><style>${css}</style></head><body>${html}</body></html>`;
    pywebview.api.save_template(fullHtml).then(res => {
        if(res.success) {
            showToast(res.message);
        } else {
            showToast(res.message, true);
        }
    });
}

// Settings
function loadSettings() {
    pywebview.api.get_settings().then(settings => {
        if(settings) {
            document.getElementById('smtp_server').value = settings.smtp_server || '';
            document.getElementById('smtp_port').value = settings.smtp_port || '';
            document.getElementById('smtp_user').value = settings.smtp_user || '';
            document.getElementById('smtp_password').value = settings.smtp_password || '';
            document.getElementById('from_email').value = settings.from_email || '';
            document.getElementById('from_name').value = settings.from_name || '';
            document.getElementById('set_delay').value = settings.delay || 1.0;
            document.getElementById('set_jitter').checked = settings.jitter || false;
            document.getElementById('disable_safety').checked = settings.disable_safety || false;
        }
    });
}

function saveSettings() {
    const settings = {
        smtp_server: document.getElementById('smtp_server').value,
        smtp_port: document.getElementById('smtp_port').value,
        smtp_user: document.getElementById('smtp_user').value,
        smtp_password: document.getElementById('smtp_password').value,
        from_email: document.getElementById('from_email').value,
        from_name: document.getElementById('from_name').value,
        delay: parseFloat(document.getElementById('set_delay').value) || 1.0,
        jitter: document.getElementById('set_jitter').checked,
        disable_safety: document.getElementById('disable_safety').checked
    };
    
    pywebview.api.save_settings(settings).then(res => {
        if(res.success) {
            showToast(res.message);
        } else {
            showToast(res.message, true);
        }
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

function clearCache() {
    if(confirm("Are you sure you want to wipe all session data and cache?")) {
        pywebview.api.clear_cache().then(res => {
            if(res.success) {
                loadedEmails = [];
                updateRecipientCount();
                
                document.getElementById('prog-bar').style.width = '0%';
                document.getElementById('prog-sent-num').innerText = '0';
                document.getElementById('prog-failed-num').innerText = '0';
                document.getElementById('prog-sent').innerText = '0';
                document.getElementById('prog-total').innerText = '0';
                
                document.getElementById('btn-recovery').classList.add('hidden');
                document.getElementById('btn-recovery').classList.remove('flex');
                
                showToast(res.message);
            } else {
                showToast(res.message, true);
            }
        });
    }
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
    const tplConfig = document.getElementById('template-select-config');

    if(mode === 'template') {
        btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        txtConfig.classList.add('hidden');
        tplConfig.classList.remove('hidden');
    } else {
        btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        txtConfig.classList.remove('hidden');
        tplConfig.classList.add('hidden');
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

    let selectedHtml = "";
    if (currentSendMode === 'template') {
        const sel = document.getElementById('send_template_select').value;
        if (sel === 'editor') {
            if (editor) selectedHtml = editor.runCommand('gjs-get-inlined-html');
        } else if (sel.startsWith('sys_')) {
            let idx = parseInt(sel.split('_')[1]);
            selectedHtml = presetTemplates[idx].html;
        } else if (sel.startsWith('user_')) {
            let idx = parseInt(sel.split('_')[1]);
            selectedHtml = userTemplates[idx].html;
        }
    }

    pywebview.api.start_sending(loadedEmails, subject, currentSendMode, plainText, selectedHtml, limitInput, resume).then(res => {
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

function recoverState() {
    pywebview.api.get_state().then(state => {
        if (state && state.current_emails) {
            loadedEmails = state.current_emails;
            updateRecipientCount();
            document.getElementById('subject').value = state.subject || "";
            if (state.mode) {
                setSendMode(state.mode);
            }
            if (state.plain_text) {
                document.getElementById('plain_text_message').value = state.plain_text;
            }
            
            document.getElementById('prog-total').innerText = state.total_emails || 0;
            document.getElementById('prog-sent').innerText = state.sent_emails || 0;
            document.getElementById('prog-sent-num').innerText = state.sent_emails || 0;
            document.getElementById('prog-failed-num').innerText = state.failed_emails || 0;
            
            let total = state.total_emails || 0;
            let percent = total > 0 ? Math.round(((state.sent_emails + state.failed_emails) / total) * 100) : 0;
            document.getElementById('prog-bar').style.width = `${percent}%`;

            document.getElementById('btn-recovery').classList.add('hidden');
            document.getElementById('btn-recovery').classList.remove('flex');
            document.getElementById('btn-send').classList.add('hidden');
            document.getElementById('btn-resume').classList.remove('hidden');
            document.getElementById('btn-resume').classList.add('flex');
            
            showToast("Previous session recovered! Press Resume to continue.");
        }
    });
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
            
            if (sent + failed >= total && total > 0) {
                // Completed
                document.getElementById('btn-send').classList.remove('hidden');
                document.getElementById('btn-send').classList.add('flex');
                document.getElementById('btn-resume').classList.add('hidden');
                document.getElementById('btn-resume').classList.remove('flex');
                
                // Auto-clear cache
                pywebview.api.clear_cache().then(() => {
                    loadedEmails = [];
                    updateRecipientCount();
                    showToast("Campaign finished! Cache auto-cleared.");
                });
            } else {
                // Stopped or paused
                document.getElementById('btn-send').classList.add('hidden');
                document.getElementById('btn-send').classList.remove('flex');
                document.getElementById('btn-resume').classList.remove('hidden');
                document.getElementById('btn-resume').classList.add('flex');
                if (res.paused) {
                    showToast("Sending Paused (Safety Limit Reached)");
                }
            }
        }
    });
}

// Queue Modal functions
function openQueueModal() {
    pywebview.api.get_queue(loadedEmails).then(q => {
        const modal = document.getElementById('queue-modal');
        const list = document.getElementById('queue-list');
        list.innerHTML = '';
        
        let pendingCount = 0;
        let sentCount = 0;
        let failedCount = 0;
        
        if (q.emails.length === 0) {
            list.innerHTML = '<div class="text-sm text-slate-500 text-center mt-6">The queue is currently empty.</div>';
        }
        
        q.emails.forEach((email, idx) => {
            const row = document.createElement('div');
            row.className = 'flex justify-between items-center bg-slate-800/50 hover:bg-slate-700/50 p-3 rounded-lg border border-slate-700/50 mb-2 transition-colors';
            
            let statusBadge = '';
            const status = q.statuses ? q.statuses[email] : null;
            
            if (status === 'sent') {
                sentCount++;
                row.classList.add('border-l-2', 'border-l-emerald-500');
                statusBadge = '<span class="text-xs font-medium bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-full"><i class="fa-solid fa-check mr-1"></i> Sent</span>';
            } else if (status === 'failed') {
                failedCount++;
                row.classList.add('border-l-2', 'border-l-rose-500');
                statusBadge = '<span class="text-xs font-medium bg-rose-500/10 text-rose-400 px-2 py-1 rounded-full"><i class="fa-solid fa-xmark mr-1"></i> Failed</span>';
            } else {
                pendingCount++;
                row.classList.add('border-l-2', 'border-l-slate-500');
                statusBadge = `
                    <button onclick="removeFromQueue('${email}')" class="text-rose-400 hover:text-rose-300 mr-3 text-sm focus:outline-none" title="Remove from queue"><i class="fa-solid fa-trash"></i></button>
                    <span class="text-xs font-medium bg-slate-500/10 text-slate-400 px-2 py-1 rounded-full"><i class="fa-solid fa-clock mr-1"></i> Pending</span>
                `;
            }
            
            row.innerHTML = `
                <div class="flex items-center space-x-3">
                    <span class="text-slate-500 text-xs w-6 text-right">${idx + 1}.</span>
                    <span class="text-slate-200 text-sm font-medium">${email}</span>
                </div>
                <div>${statusBadge}</div>
            `;
            list.appendChild(row);
        });
        
        document.getElementById('queue-total-label').innerText = `Sent: ${sentCount} | Pending: ${pendingCount} | Failed: ${failedCount}`;
        
        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.remove('opacity-0'), 10);
    });
}

function closeQueueModal() {
    const modal = document.getElementById('queue-modal');
    modal.classList.add('opacity-0');
    setTimeout(() => modal.classList.add('hidden'), 300);
}

function removeFromQueue(email) {
    pywebview.api.remove_from_queue(email).then(res => {
        if(res.success) {
            loadedEmails = loadedEmails.filter(e => e !== email);
            updateRecipientCount();
            openQueueModal(); // refresh UI
            showToast(res.message);
        } else {
            if (res.message === "Email not found.") {
                let initialLen = loadedEmails.length;
                loadedEmails = loadedEmails.filter(e => e !== email);
                if (loadedEmails.length < initialLen) {
                    updateRecipientCount();
                    openQueueModal(); // refresh UI
                    showToast(email + " removed.");
                    return;
                }
            }
            showToast(res.message, true);
        }
    });
}
