let editor = null;
let loadedEmails = [];
let progressInterval = null;
let currentSendMode = 'template';
let presetTemplates = [];
let userTemplates = [];
let galleryTab = 'sys';
let autoSaveTimeout = null;
let isTemplateSaveInFlight = false;
let queuedTemplateHtml = null;
let queuedTemplateManual = false;
let lastSavedTemplateHtml = '';
let selectedComponent = null;
let lastSafetyToastMessage = '';
let lastPauseReasonToast = '';
let easterEggCount = 0;
let builderShortcutsBound = false;

function escapeHtml(value) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    };
    return String(value || '').replace(/[&<>"']/g, m => map[m]);
}

function normalizeEmail(email) {
    return String(email || '').trim().toLowerCase();
}

function dedupeEmails(emails) {
    const seen = new Set();
    const unique = [];
    for (const raw of emails || []) {
        const email = normalizeEmail(raw);
        if (!email || seen.has(email)) continue;
        seen.add(email);
        unique.push(email);
    }
    return unique;
}

function splitTemplateHtml(rawHtml) {
    const input = String(rawHtml || '').trim();
    if (!input) {
        return { body: '', css: '' };
    }

    try {
        const parser = new DOMParser();
        const doc = parser.parseFromString(input, 'text/html');
        const css = Array.from(doc.querySelectorAll('style'))
            .map(el => el.textContent || '')
            .join('\n')
            .trim();
        const body = (doc.body && doc.body.innerHTML) ? doc.body.innerHTML : input;
        return { body, css };
    } catch (err) {
        return { body: input, css: '' };
    }
}

function composeTemplateHtmlFromEditor() {
    if (!editor) return '';
    const html = editor.getHtml();
    const css = editor.getCss();
    return `<html><head><style>${css}</style></head><body>${html}</body></html>`;
}

function loadTemplateIntoEditor(rawHtml) {
    if (!editor) return;
    const parsed = splitTemplateHtml(rawHtml);
    // Important: clear both canvas + CSS to avoid mixing styles between templates.
    // Do NOT call setStyle('') when no <style> is provided, otherwise Grapes can drop
    // style rules derived from inline styles during import.
    editor.DomComponents.clear();
    editor.CssComposer.clear();
    editor.setComponents(parsed.body || '<div style="padding: 16px;">Start building your email here...</div>');

    if ((parsed.css || '').trim()) {
        editor.setStyle(parsed.css);
    }

    lastSavedTemplateHtml = composeTemplateHtmlFromEditor();
    setBuilderSaveIndicator('Loaded template');
}

function getEditorHtmlForSending() {
    if (!editor) return '';
    try {
        const inlined = editor.runCommand('gjs-get-inlined-html');
        if (inlined && String(inlined).trim()) {
            return inlined;
        }
    } catch (e) {
        // Fallback to manual composition below.
    }
    return composeTemplateHtmlFromEditor();
}

function setBuilderSaveIndicator(message, isError = false) {
    const indicator = document.getElementById('builder-save-indicator');
    if (!indicator) return;
    indicator.textContent = message;
    indicator.classList.remove('text-slate-400', 'text-emerald-400', 'text-rose-400', 'text-amber-400');
    if (isError) {
        indicator.classList.add('text-rose-400');
    } else if (message.toLowerCase().includes('saved') || message.toLowerCase().includes('loaded')) {
        indicator.classList.add('text-emerald-400');
    } else {
        indicator.classList.add('text-slate-400');
    }
}

function humanTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function flushQueuedTemplateSave() {
    if (isTemplateSaveInFlight || queuedTemplateHtml === null) return;

    const html = queuedTemplateHtml;
    const manual = queuedTemplateManual;
    queuedTemplateHtml = null;
    queuedTemplateManual = false;

    queueTemplateSave(html, manual);
}

function queueTemplateSave(fullHtml, manual = false) {
    const html = String(fullHtml || '');
    if (!editor) return;

    if (!manual && html === lastSavedTemplateHtml) {
        return;
    }

    if (isTemplateSaveInFlight) {
        queuedTemplateHtml = html;
        queuedTemplateManual = queuedTemplateManual || manual;
        return;
    }

    isTemplateSaveInFlight = true;

    pywebview.api.save_template(html).then(res => {
        if (res && res.success) {
            lastSavedTemplateHtml = html;
            setBuilderSaveIndicator(`Saved ${humanTime()}`);
            if (manual) {
                showToast(res.message || 'Template saved.');
            }
        } else {
            setBuilderSaveIndicator('Save failed', true);
            showToast((res && res.message) || 'Save failed.', true);
        }
    }).catch(err => {
        setBuilderSaveIndicator('Save failed', true);
        showToast(err.message || String(err), true);
    }).finally(() => {
        isTemplateSaveInFlight = false;
        flushQueuedTemplateSave();
    });
}

function readFloatInput(id, fallback) {
    const raw = document.getElementById(id)?.value;
    const parsed = Number.parseFloat(String(raw ?? '').trim());
    return Number.isFinite(parsed) ? parsed : fallback;
}

function readIntInput(id, fallback) {
    const raw = document.getElementById(id)?.value;
    const parsed = Number.parseInt(String(raw ?? '').trim(), 10);
    return Number.isFinite(parsed) ? parsed : fallback;
}

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
    if (!target) return;

    if (tabId === 'builder') {
        target.classList.remove('hidden');
        target.classList.add('flex');
        if (!editor) initGrapesJS();
    } else {
        target.classList.remove('hidden');
        target.classList.add('block');
    }

    const btn = document.getElementById(`btn-${tabId}`);
    if (btn) {
        btn.classList.add('bg-slate-800', 'text-white');
        btn.classList.remove('text-slate-400');
    }
}

window.addEventListener('pywebviewready', function () {
    loadSettings();
    const dashboardBtn = document.getElementById('btn-dashboard');
    if (dashboardBtn) {
        dashboardBtn.classList.add('bg-slate-800', 'text-white');
    }

    bindSafetyInputs();

    Promise.all([
        pywebview.api.get_preset_templates(),
        pywebview.api.get_user_templates(),
    ]).then(([presets, users]) => {
        presetTemplates = presets || [];
        userTemplates = users || [];
        renderTemplateGallery();
        populateTemplateDropdown();
    }).catch(() => {
        showToast('Could not load templates.', true);
    });

    pywebview.api.get_state().then(state => {
        if (state && state.current_emails && state.current_emails.length > 0 && state.last_index < state.current_emails.length) {
            const recoveryBtn = document.getElementById('btn-recovery');
            if (recoveryBtn) {
                recoveryBtn.classList.remove('hidden');
                recoveryBtn.classList.add('flex');
            }
        }
    });

    checkRisk();
});

function bindSafetyInputs() {
    const ids = [
        'set_delay',
        'batch_size',
        'batch_pause',
        'max_per_domain',
        'domain_cooldown',
        'max_retries',
        'retry_backoff',
        'set_jitter',
        'spread_by_domain',
        'disable_safety',
        'safety_limit',
    ];

    ids.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('input', () => checkRisk());
        el.addEventListener('change', () => checkRisk());
    });
}

function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toast-msg');
    const iconEl = document.getElementById('toast-icon');

    if (!toast || !msgEl || !iconEl) return;

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
    }, 4200);
}

function applySmtpPreset(provider) {
    if (provider === 'gmail') {
        document.getElementById('smtp_server').value = 'smtp.gmail.com';
        document.getElementById('smtp_port').value = '587';
        document.getElementById('set_delay').value = 2.0;
    } else if (provider === 'outlook') {
        document.getElementById('smtp_server').value = 'smtp-mail.outlook.com';
        document.getElementById('smtp_port').value = '587';
        document.getElementById('set_delay').value = 2.0;
    } else if (provider === 'yahoo') {
        document.getElementById('smtp_server').value = 'smtp.mail.yahoo.com';
        document.getElementById('smtp_port').value = '465';
        document.getElementById('set_delay').value = 2.5;
    }

    checkRisk();
    showToast(`Applied ${provider} preset.`);
}

function toggleTemplateGallery() {
    const gallery = document.getElementById('template-gallery');
    if (!gallery) return;

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

    if (btnSys && btnUser) {
        if (tab === 'sys') {
            btnSys.className = 'flex-1 py-1.5 text-xs font-bold rounded-md bg-slate-700 text-white shadow transition-all';
            btnUser.className = 'flex-1 py-1.5 text-xs font-bold rounded-md text-slate-400 hover:text-white transition-all';
        } else {
            btnUser.className = 'flex-1 py-1.5 text-xs font-bold rounded-md bg-slate-700 text-white shadow transition-all';
            btnSys.className = 'flex-1 py-1.5 text-xs font-bold rounded-md text-slate-400 hover:text-white transition-all';
        }
    }

    renderTemplateGallery();
}

function renderTemplateGallery() {
    const container = document.getElementById('gallery-container');
    if (!container) return;

    container.innerHTML = '';
    const items = galleryTab === 'sys' ? presetTemplates : userTemplates;

    if (!items || items.length === 0) {
        container.innerHTML = '<div class="text-sm text-slate-500 text-center mt-4">No templates found.</div>';
        return;
    }

    items.forEach((tpl, idx) => {
        const row = document.createElement('div');
        row.className = 'w-full text-left bg-slate-800 hover:bg-slate-700 p-3 rounded-lg border border-slate-700 transition-colors flex items-center justify-between group gap-2';

        const openBtn = document.createElement('button');
        openBtn.className = 'flex-1 text-left';
        openBtn.innerHTML = `<span class="text-sm text-slate-200">${escapeHtml(tpl.name || 'Untitled')}</span>`;
        openBtn.onclick = () => loadPresetTemplate(idx, galleryTab);
        row.appendChild(openBtn);

        if (galleryTab === 'user') {
            const delBtn = document.createElement('button');
            delBtn.className = 'text-rose-400 hover:text-rose-200 text-xs px-2 py-1 rounded border border-rose-500/30 hover:bg-rose-500/10';
            delBtn.innerHTML = '<i class="fa-solid fa-trash"></i>';
            delBtn.title = 'Delete template';
            delBtn.onclick = () => deleteUserTemplate(idx);
            row.appendChild(delBtn);
        } else {
            const icon = document.createElement('i');
            icon.className = 'fa-solid fa-chevron-right text-slate-500 text-xs opacity-0 group-hover:opacity-100 transition-opacity';
            row.appendChild(icon);
        }

        container.appendChild(row);
    });
}

function loadPresetTemplate(idx, type) {
    if (!editor) return;
    const templates = type === 'sys' ? presetTemplates : userTemplates;
    const tpl = templates[idx];
    if (!tpl) return;

    loadTemplateIntoEditor(tpl.html || '');
    toggleTemplateGallery();
    showToast(`Loaded "${tpl.name}" template.`);
}

function saveUserTemplate() {
    const nameInput = document.getElementById('custom-template-name');
    const name = (nameInput ? nameInput.value : '').trim();

    if (!name) {
        showToast('Please enter template name.', true);
        return;
    }

    if (!editor) {
        showToast('Builder is not ready.', true);
        return;
    }

    const fullHtml = composeTemplateHtmlFromEditor();
    pywebview.api.save_user_template(name, fullHtml).then(res => {
        if (res.success) {
            showToast(res.message || 'Template saved.');
            if (nameInput) nameInput.value = '';
            return pywebview.api.get_user_templates();
        }
        throw new Error(res.message || 'Could not save template');
    }).then(templates => {
        userTemplates = templates || [];
        renderTemplateGallery();
        populateTemplateDropdown();
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function deleteUserTemplate(idx) {
    if (!confirm('Delete this saved template?')) return;

    pywebview.api.delete_user_template(idx).then(res => {
        if (res.success) {
            showToast(res.message || 'Template deleted.');
            return pywebview.api.get_user_templates();
        }
        throw new Error(res.message || 'Delete failed');
    }).then(templates => {
        userTemplates = templates || [];
        renderTemplateGallery();
        populateTemplateDropdown();
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function addBuilderQuickBlocks() {
    if (!editor) return;

    const bm = editor.BlockManager;

    bm.add('quick-hero', {
        label: 'Hero',
        category: 'Quick Blocks',
        attributes: { class: 'fa fa-window-maximize' },
        content: `
            <section style="padding:32px; text-align:center; background:#f8fafc; border-radius:8px;">
                <h1 style="font-size:32px; color:#111827; margin:0 0 12px 0;">Big Headline Here</h1>
                <p style="font-size:16px; color:#475569; margin:0 0 20px 0;">Explain your offer in one clear sentence.</p>
                <a href="#" style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; padding:12px 24px; border-radius:6px;">Call to Action</a>
            </section>
        `,
    });

    bm.add('quick-two-columns', {
        label: '2 Columns',
        category: 'Quick Blocks',
        attributes: { class: 'fa fa-columns' },
        content: `
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:16px;">
                <tr>
                    <td style="width:50%; padding:12px; vertical-align:top;">
                        <h3 style="margin:0 0 8px 0; color:#111827;">Column One</h3>
                        <p style="margin:0; color:#475569;">Add description here.</p>
                    </td>
                    <td style="width:50%; padding:12px; vertical-align:top;">
                        <h3 style="margin:0 0 8px 0; color:#111827;">Column Two</h3>
                        <p style="margin:0; color:#475569;">Add description here.</p>
                    </td>
                </tr>
            </table>
        `,
    });

    bm.add('quick-cta', {
        label: 'CTA Strip',
        category: 'Quick Blocks',
        attributes: { class: 'fa fa-bullhorn' },
        content: `
            <div style="padding:20px; background:#0f172a; border-radius:8px; text-align:center; color:#e2e8f0; margin-top:16px;">
                <p style="margin:0 0 12px 0; font-size:15px;">Ready to take action?</p>
                <a href="#" style="display:inline-block; padding:10px 18px; background:#38bdf8; color:#0f172a; text-decoration:none; border-radius:999px; font-weight:700;">Get Started</a>
            </div>
        `,
    });
}

function initGrapesJS() {
    editor = grapesjs.init({
        container: '#gjs',
        height: '100%',
        width: 'auto',
        fromElement: false,
        allowScripts: 1,
        forceClass: false,
        plugins: ['gjs-preset-newsletter'],
        pluginsOpts: {
            'gjs-preset-newsletter': {
                modalTitleImport: 'Import template',
                cellStyle: {
                    padding: 0,
                    margin: 0,
                    'vertical-align': 'top',
                },
            },
        },
        storageManager: false,
        selectorManager: {
            componentFirst: true,
        },
        styleManager: {
            clearProperties: false,
        },
        canvas: {
            styles: [
                'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
                'https://fonts.googleapis.com/css2?family=Garamond:wght@400;700&display=swap',
                'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap'
            ],
            scripts: [],
            // Add a default style for the canvas body to ensure margin:auto works
            customStyle: 'body { margin: 0; padding: 0; background-color: #f8fafc; } .template-wrapper { margin: 0 auto; }'
        },
        deviceManager: {
            devices: [
                { name: 'Desktop', width: '' },
                { name: 'Tablet', width: '768px', widthMedia: '992px' },
                { name: 'Mobile portrait', width: '375px', widthMedia: '575px' },
            ],
        },
    });

    addBuilderQuickBlocks();
    setBuilderDevice('Desktop');

    editor.on('component:selected', comp => {
        selectedComponent = comp;
        syncQuickStylePanel();
    });

    editor.on('component:deselected', () => {
        selectedComponent = null;
        syncQuickStylePanel();
    });

    editor.on('change:changesCount', () => {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            const fullHtml = composeTemplateHtmlFromEditor();
            queueTemplateSave(fullHtml, false);
        }, 2200);
    });

    pywebview.api.get_template().then(html => {
        if (html && html.trim()) {
            loadTemplateIntoEditor(html);
        } else {
            newCanvas(false);
        }
    });

    if (!builderShortcutsBound) {
        builderShortcutsBound = true;
        window.addEventListener('keydown', handleBuilderShortcuts);
    }

    syncQuickStylePanel();
}

function handleBuilderShortcuts(e) {
    const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
    if (['input', 'textarea', 'select'].includes(tag) || (e.target && e.target.isContentEditable)) {
        return;
    }

    const cmdOrCtrl = e.metaKey || e.ctrlKey;
    if (!cmdOrCtrl) return;

    const key = String(e.key || '').toLowerCase();

    if (key === 's') {
        e.preventDefault();
        saveTemplate();
        return;
    }

    if (key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
            builderRedo();
        } else {
            builderUndo();
        }
    }
}

function builderUndo() {
    if (!editor) return;
    editor.UndoManager.undo();
}

function builderRedo() {
    if (!editor) return;
    editor.UndoManager.redo();
}

function setBuilderDevice(deviceName) {
    if (!editor) return;
    editor.setDevice(deviceName);

    const map = {
        'Desktop': 'device-desktop',
        'Tablet': 'device-tablet',
        'Mobile portrait': 'device-mobile',
    };

    ['device-desktop', 'device-tablet', 'device-mobile'].forEach(id => {
        const btn = document.getElementById(id);
        if (!btn) return;
        btn.classList.remove('bg-slate-700', 'text-white');
        btn.classList.add('text-slate-300');
    });

    const active = document.getElementById(map[deviceName]);
    if (active) {
        active.classList.add('bg-slate-700', 'text-white');
        active.classList.remove('text-slate-300');
    }
}

function insertQuickBlock(kind) {
    if (!editor) return;

    const blocks = {
        hero: `
            <section style="padding:32px; text-align:center; background:#eff6ff; border-radius:8px; margin:16px 0;">
                <h1 style="font-size:30px; color:#1e3a8a; margin:0 0 8px 0;">Your Headline</h1>
                <p style="font-size:16px; color:#334155; margin:0 0 20px 0;">Short supporting text that explains value.</p>
                <a href="#" style="display:inline-block; background:#2563eb; color:#fff; text-decoration:none; padding:12px 20px; border-radius:6px;">Get Started</a>
            </section>
        `,
        cta: `
            <div style="padding:20px; background:#0f172a; color:#e2e8f0; text-align:center; border-radius:8px; margin:16px 0;">
                <p style="margin:0 0 10px 0; font-size:16px;">Ready to move forward?</p>
                <a href="#" style="display:inline-block; padding:10px 18px; background:#22d3ee; color:#0f172a; text-decoration:none; border-radius:999px; font-weight:700;">Call to Action</a>
            </div>
        `,
        'two-col': `
            <table width="100%" cellpadding="0" cellspacing="0" style="margin:16px 0;">
                <tr>
                    <td style="width:50%; padding:12px; vertical-align:top;">
                        <h3 style="margin:0 0 8px 0; color:#111827;">Feature One</h3>
                        <p style="margin:0; color:#475569;">Brief feature description.</p>
                    </td>
                    <td style="width:50%; padding:12px; vertical-align:top;">
                        <h3 style="margin:0 0 8px 0; color:#111827;">Feature Two</h3>
                        <p style="margin:0; color:#475569;">Brief feature description.</p>
                    </td>
                </tr>
            </table>
        `,
        spacer: '<div style="height:28px;"></div>',
    };

    const html = blocks[kind];
    if (!html) return;

    const added = editor.addComponents(html);
    if (added && added.length) {
        editor.select(added[0]);
    }

    showToast('Block inserted into template.');
}

function insertMergeTag(tag) {
    if (!editor) return;

    if (selectedComponent) {
        const currentContent = String(selectedComponent.get('content') || '');
        selectedComponent.set('content', `${currentContent}${tag}`);
        showToast(`Inserted ${tag}`);
        return;
    }

    const added = editor.addComponents(`<p style="margin: 10px 0;">${escapeHtml(tag)}</p>`);
    if (added && added.length) {
        editor.select(added[0]);
    }
    showToast(`Inserted ${tag}`);
}

function normalizeColorToHex(color, fallback = '#111827') {
    const value = String(color || '').trim();
    if (!value) return fallback;

    if (value.startsWith('#')) {
        if (value.length === 4) {
            return `#${value[1]}${value[1]}${value[2]}${value[2]}${value[3]}${value[3]}`;
        }
        return value.slice(0, 7);
    }

    const rgb = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (!rgb) return fallback;

    const toHex = n => {
        const num = Math.max(0, Math.min(255, parseInt(n, 10) || 0));
        return num.toString(16).padStart(2, '0');
    };

    return `#${toHex(rgb[1])}${toHex(rgb[2])}${toHex(rgb[3])}`;
}

function syncQuickStylePanel() {
    const selectedLabel = document.getElementById('qs-selected');
    const bg = document.getElementById('qs-bg');
    const color = document.getElementById('qs-color');
    const size = document.getElementById('qs-size');
    const padding = document.getElementById('qs-padding');
    const radius = document.getElementById('qs-radius');
    const align = document.getElementById('qs-align');

    if (!selectedLabel) return;

    if (!selectedComponent) {
        selectedLabel.textContent = 'No element selected';
        return;
    }

    const tagName = selectedComponent.get('tagName') || 'component';
    selectedLabel.textContent = `Selected: <${tagName}>`;

    const style = selectedComponent.getStyle() || {};

    if (bg) bg.value = normalizeColorToHex(style['background-color'], '#ffffff');
    if (color) color.value = normalizeColorToHex(style.color, '#111827');

    if (size) {
        const fontSize = String(style['font-size'] || '').replace('px', '').trim();
        size.value = fontSize || 16;
    }

    if (padding) padding.value = style.padding || '';

    if (radius) {
        const rad = String(style['border-radius'] || '').replace('px', '').trim();
        radius.value = rad || 0;
    }

    if (align) {
        align.value = style['text-align'] || '';
    }
}

function applyQuickStyle(prop, value) {
    if (!editor || !selectedComponent) return;

    const stylePatch = {};
    stylePatch[prop] = value;
    selectedComponent.addStyle(stylePatch);
}

function newCanvas(withConfirm = true) {
    if (withConfirm) {
        if (!confirm('Start a new blank canvas? Current unsaved changes will be lost.')) {
            return;
        }
    }

    if (!editor) return;

    editor.DomComponents.clear();
    editor.CssComposer.clear();
    editor.addComponents('<section style="padding:24px;"><h2 style="margin:0 0 8px 0;">New Email Template</h2><p>Start designing your template with the quick blocks on the right.</p></section>');

    const nameInput = document.getElementById('custom-template-name');
    if (nameInput) nameInput.value = '';

    lastSavedTemplateHtml = '';
    showToast('New canvas created.');
}

function populateTemplateDropdown() {
    const select = document.getElementById('send_template_select');
    if (!select) return;

    select.innerHTML = '<option value="editor">🔥 Current Editor Layout</option>';

    userTemplates.forEach((tpl, idx) => {
        const option = document.createElement('option');
        option.value = `user_${idx}`;
        option.textContent = `[My Templates] ${tpl.name}`;
        select.appendChild(option);
    });
}

function saveTemplate() {
    if (!editor) {
        showToast('Builder is not ready.', true);
        return;
    }

    const fullHtml = composeTemplateHtmlFromEditor();
    queueTemplateSave(fullHtml, true);
}

function loadSettings() {
    pywebview.api.get_settings().then(settings => {
        if (!settings) return;

        const setValue = (id, value, fallback = '') => {
            const el = document.getElementById(id);
            if (!el) return;
            el.value = value ?? fallback;
        };

        const setChecked = (id, value) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.checked = Boolean(value);
        };

        setValue('smtp_server', settings.smtp_server, '');
        setValue('smtp_port', settings.smtp_port, '587');
        setValue('smtp_user', settings.smtp_user, '');
        setValue('smtp_password', settings.smtp_password, '');
        setValue('from_email', settings.from_email, '');
        setValue('from_name', settings.from_name, '');

        setValue('set_delay', settings.delay, 2.0);
        setValue('batch_size', settings.batch_size, 25);
        setValue('batch_pause', settings.batch_pause, 60);
        setValue('max_per_domain', settings.max_per_domain, 10);
        setValue('domain_cooldown', settings.domain_cooldown, 120);
        setValue('max_retries', settings.max_retries, 2);
        setValue('retry_backoff', settings.retry_backoff, 15);

        setChecked('set_jitter', settings.jitter);
        setChecked('spread_by_domain', settings.spread_by_domain);
        setChecked('disable_safety', settings.disable_safety);

        checkRisk();
    });
}

function saveSettings() {
    const settings = {
        smtp_server: (document.getElementById('smtp_server')?.value || '').trim(),
        smtp_port: (document.getElementById('smtp_port')?.value || '587').trim(),
        smtp_user: (document.getElementById('smtp_user')?.value || '').trim(),
        smtp_password: document.getElementById('smtp_password')?.value || '',
        from_email: (document.getElementById('from_email')?.value || '').trim(),
        from_name: (document.getElementById('from_name')?.value || '').trim(),
        delay: readFloatInput('set_delay', 2.0),
        jitter: Boolean(document.getElementById('set_jitter')?.checked),
        disable_safety: Boolean(document.getElementById('disable_safety')?.checked),
        batch_size: readIntInput('batch_size', 25),
        batch_pause: readFloatInput('batch_pause', 60),
        max_per_domain: readIntInput('max_per_domain', 10),
        domain_cooldown: readFloatInput('domain_cooldown', 120),
        max_retries: readIntInput('max_retries', 2),
        retry_backoff: readFloatInput('retry_backoff', 15),
        spread_by_domain: Boolean(document.getElementById('spread_by_domain')?.checked),
    };

    pywebview.api.save_settings(settings).then(res => {
        if (res.success) {
            if (settings.disable_safety) {
                showToast('Safety limits are fully disabled. Blocking risk is now high.', true);
            } else {
                showToast(res.message || 'Settings saved.');
            }
            loadSettings();
        } else {
            showToast(res.message || 'Could not save settings.', true);
        }
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function importFile() {
    pywebview.api.select_file().then(res => {
        if (!res.success) {
            showToast(res.message || 'Import failed.', true);
            return;
        }

        const before = loadedEmails.length;
        loadedEmails = dedupeEmails([...(loadedEmails || []), ...(res.emails || [])]);
        const added = loadedEmails.length - before;

        const domainSummary = (res.top_domains || [])
            .slice(0, 3)
            .map(([domain, count]) => `${domain} (${count})`)
            .join(', ');

        const details = [];
        details.push(`Added ${added} recipients.`);
        if (res.duplicates_removed > 0) details.push(`Removed duplicates: ${res.duplicates_removed}.`);
        if (domainSummary) details.push(`Top domains: ${domainSummary}.`);

        updateRecipientCount();
        showToast(details.join(' '));
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function addManualEmails() {
    const inputEl = document.getElementById('manual_emails');
    const input = inputEl ? inputEl.value : '';
    if (!input.trim()) return;

    const found = input.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g) || [];
    if (!found.length) {
        showToast('No valid emails found.', true);
        return;
    }

    const before = loadedEmails.length;
    loadedEmails = dedupeEmails([...(loadedEmails || []), ...found]);
    const added = loadedEmails.length - before;

    if (inputEl) inputEl.value = '';
    updateRecipientCount();

    showToast(`Added ${added} email(s).`);
}

function clearRecipients() {
    loadedEmails = [];
    updateRecipientCount();
    showToast('Recipient list cleared.');
}

function clearCache() {
    if (!confirm('Are you sure you want to wipe all session data and queue cache?')) return;

    pywebview.api.clear_cache().then(res => {
        if (!res.success) {
            showToast(res.message || 'Could not clear cache.', true);
            return;
        }

        loadedEmails = [];
        updateRecipientCount();

        document.getElementById('prog-bar').style.width = '0%';
        document.getElementById('prog-sent-num').innerText = '0';
        document.getElementById('prog-failed-num').innerText = '0';
        document.getElementById('prog-sent').innerText = '0';
        document.getElementById('prog-total').innerText = '0';

        const note = document.getElementById('progress-note');
        if (note) note.textContent = '';

        const recoveryBtn = document.getElementById('btn-recovery');
        if (recoveryBtn) {
            recoveryBtn.classList.add('hidden');
            recoveryBtn.classList.remove('flex');
        }

        showToast(res.message || 'Cache cleared.');
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function checkRisk() {
    const warning = document.getElementById('risk-warning');
    const warningText = document.getElementById('risk-warning-text');
    if (!warning || !warningText) return;

    if (loadedEmails.length === 0) {
        warning.classList.add('hidden');
        warningText.textContent = '';
        return;
    }

    pywebview.api.get_safety_recommendation(loadedEmails.length).then(info => {
        const reasons = info.reasons || [];
        const risk = info.risk_level || 'low';
        const sent24h = info.sent_last_24h || 0;

        if (risk === 'low' && reasons.length === 0) {
            warning.classList.add('hidden');
            warningText.textContent = '';
            return;
        }

        warning.classList.remove('hidden', 'text-orange-400', 'text-rose-400', 'text-amber-400');

        if (risk === 'high') {
            warning.classList.add('text-rose-400');
        } else {
            warning.classList.add('text-amber-400');
        }

        const brief = reasons.slice(0, 2).join(' ');
        warningText.textContent = `[${risk.toUpperCase()}] ${brief} Sent in last 24h: ${sent24h}.`;
    }).catch(() => {
        warning.classList.remove('hidden');
        warning.classList.add('text-orange-400');
        warningText.textContent = 'Could not fetch safety recommendation.';
    });
}

function updateRecipientCount() {
    const countEl = document.getElementById('recipient-count');
    if (countEl) {
        countEl.innerText = loadedEmails.length;
    }
    checkRisk();
}

function setSendMode(mode) {
    currentSendMode = mode;
    const btnTpl = document.getElementById('mode-template');
    const btnTxt = document.getElementById('mode-text');
    const txtConfig = document.getElementById('plain-text-config');
    const tplConfig = document.getElementById('template-select-config');

    if (mode === 'template') {
        if (btnTpl) btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        if (btnTxt) btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        if (txtConfig) txtConfig.classList.add('hidden');
        if (tplConfig) tplConfig.classList.remove('hidden');
    } else {
        if (btnTxt) btnTxt.className = 'flex-1 py-2 text-sm font-medium rounded-md bg-slate-700 text-white shadow transition-all';
        if (btnTpl) btnTpl.className = 'flex-1 py-2 text-sm font-medium rounded-md text-slate-400 hover:text-white transition-all';
        if (txtConfig) txtConfig.classList.remove('hidden');
        if (tplConfig) tplConfig.classList.add('hidden');
    }
}

function setSendingButtonsState(state) {
    const btnSend = document.getElementById('btn-send');
    const btnStop = document.getElementById('btn-stop');
    const btnResume = document.getElementById('btn-resume');

    const hide = el => {
        if (!el) return;
        el.classList.add('hidden');
        el.classList.remove('flex');
    };

    const showFlex = el => {
        if (!el) return;
        el.classList.remove('hidden');
        el.classList.add('flex');
    };

    if (state === 'sending') {
        hide(btnSend);
        hide(btnResume);
        showFlex(btnStop);
    } else if (state === 'paused') {
        hide(btnStop);
        hide(btnSend);
        showFlex(btnResume);
    } else if (state === 'ready') {
        hide(btnStop);
        hide(btnResume);
        showFlex(btnSend);
    }
}

function startSending(resume = false) {
    const subject = document.getElementById('subject')?.value || '';
    const plainText = document.getElementById('plain_text_message')?.value || '';
    const limitInput = parseInt(document.getElementById('safety_limit')?.value || '0', 10) || 0;

    if (!subject.trim()) {
        showToast('Please enter email subject.', true);
        return;
    }

    if (loadedEmails.length === 0) {
        showToast('Please add recipients first.', true);
        return;
    }

    let selectedHtml = '';
    if (currentSendMode === 'template') {
        const source = document.getElementById('send_template_select')?.value || 'editor';
        if (source === 'editor') {
            selectedHtml = getEditorHtmlForSending();
        } else if (source.startsWith('sys_')) {
            const idx = parseInt(source.split('_')[1], 10);
            selectedHtml = presetTemplates[idx]?.html || '';
        } else if (source.startsWith('user_')) {
            const idx = parseInt(source.split('_')[1], 10);
            selectedHtml = userTemplates[idx]?.html || '';
        }
    }

    pywebview.api.start_sending(loadedEmails, subject.trim(), currentSendMode, plainText, selectedHtml, limitInput, resume).then(res => {
        if (!res.success) {
            showToast(res.message || 'Could not start sending.', true);
            return;
        }

        setSendingButtonsState('sending');
        showToast(res.message || 'Sending started.');

        if (!resume) {
            document.getElementById('prog-bar').style.width = '0%';
            document.getElementById('prog-sent-num').innerText = '0';
            document.getElementById('prog-failed-num').innerText = '0';
            document.getElementById('prog-sent').innerText = '0';
        }

        if (progressInterval) clearInterval(progressInterval);
        progressInterval = setInterval(updateProgress, 600);
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function resumeSending() {
    startSending(true);
}

function recoverState() {
    pywebview.api.get_state().then(state => {
        if (!state || !state.current_emails) return;

        loadedEmails = dedupeEmails(state.current_emails);
        updateRecipientCount();

        document.getElementById('subject').value = state.subject || '';
        if (state.mode) setSendMode(state.mode);
        if (state.plain_text) {
            document.getElementById('plain_text_message').value = state.plain_text;
        }

        document.getElementById('prog-total').innerText = state.total_emails || 0;
        document.getElementById('prog-sent').innerText = state.sent_emails || 0;
        document.getElementById('prog-sent-num').innerText = state.sent_emails || 0;
        document.getElementById('prog-failed-num').innerText = state.failed_emails || 0;

        const total = state.total_emails || 0;
        const sent = state.sent_emails || 0;
        const failed = state.failed_emails || 0;
        const percent = total > 0 ? Math.round(((sent + failed) / total) * 100) : 0;
        document.getElementById('prog-bar').style.width = `${percent}%`;

        const note = document.getElementById('progress-note');
        if (note) {
            note.textContent = state.pause_reason || state.latest_safety_event || '';
        }

        const recoveryBtn = document.getElementById('btn-recovery');
        if (recoveryBtn) {
            recoveryBtn.classList.add('hidden');
            recoveryBtn.classList.remove('flex');
        }

        setSendingButtonsState('paused');
        showToast('Previous session recovered. Press Resume to continue.');
    });
}

function stopSending() {
    pywebview.api.stop_sending(true).then(res => {
        showToast(res.message || 'Sending paused.');
        setSendingButtonsState('paused');
        if (progressInterval) clearInterval(progressInterval);
    });
}

function updateProgress() {
    pywebview.api.get_progress().then(res => {
        const total = res.total || 0;
        const sent = res.sent || 0;
        const failed = res.failed || 0;

        document.getElementById('prog-total').innerText = total;
        document.getElementById('prog-sent').innerText = sent;
        document.getElementById('prog-sent-num').innerText = sent;
        document.getElementById('prog-failed-num').innerText = failed;

        const percent = total > 0 ? Math.round(((sent + failed) / total) * 100) : 0;
        document.getElementById('prog-bar').style.width = `${percent}%`;

        const note = document.getElementById('progress-note');
        if (note) {
            note.textContent = res.pause_reason || res.latest_safety_event || '';
        }

        if (res.latest_safety_event && res.latest_safety_event !== lastSafetyToastMessage) {
            lastSafetyToastMessage = res.latest_safety_event;
            showToast(res.latest_safety_event);
        }

        if (!res.sending) {
            if (progressInterval) clearInterval(progressInterval);

            if (sent + failed >= total && total > 0) {
                setSendingButtonsState('ready');
                pywebview.api.clear_cache().then(() => {
                    loadedEmails = [];
                    updateRecipientCount();
                    const noteEl = document.getElementById('progress-note');
                    if (noteEl) noteEl.textContent = '';
                    showToast('Campaign finished. Queue cache cleared.');
                });
                return;
            }

            if (res.paused) {
                setSendingButtonsState('paused');
                const reason = res.pause_reason || 'Sending paused by safety logic.';
                if (reason !== lastPauseReasonToast) {
                    lastPauseReasonToast = reason;
                    showToast(reason);
                }
            } else {
                setSendingButtonsState('ready');
            }
        }
    });
}

function openQueueModal() {
    pywebview.api.get_queue(loadedEmails).then(q => {
        const modal = document.getElementById('queue-modal');
        const list = document.getElementById('queue-list');
        const label = document.getElementById('queue-total-label');
        if (!modal || !list || !label) return;

        list.innerHTML = '';

        const statuses = q.statuses || {};
        const errors = q.email_errors || {};

        let pendingCount = 0;
        let sentCount = 0;
        let failedCount = 0;

        if (!q.emails || q.emails.length === 0) {
            list.innerHTML = '<div class="text-sm text-slate-500 text-center mt-6">The queue is currently empty.</div>';
        } else {
            q.emails.forEach((email, idx) => {
                const status = statuses[email] || 'pending';
                const err = errors[email] || '';

                const row = document.createElement('div');
                row.className = 'bg-slate-800/50 hover:bg-slate-700/50 p-3 rounded-lg border border-slate-700/50 mb-2 transition-colors';

                const top = document.createElement('div');
                top.className = 'flex justify-between items-center gap-2';

                const left = document.createElement('div');
                left.className = 'flex items-center space-x-3 min-w-0';
                left.innerHTML = `
                    <span class="text-slate-500 text-xs w-6 text-right">${idx + 1}.</span>
                    <span class="text-slate-200 text-sm font-medium truncate">${escapeHtml(email)}</span>
                `;

                const right = document.createElement('div');

                if (status === 'sent') {
                    sentCount++;
                    row.classList.add('border-l-2', 'border-l-emerald-500');
                    right.innerHTML = '<span class="text-xs font-medium bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-full"><i class="fa-solid fa-check mr-1"></i>Sent</span>';
                } else if (status === 'failed') {
                    failedCount++;
                    row.classList.add('border-l-2', 'border-l-rose-500');
                    right.innerHTML = '<span class="text-xs font-medium bg-rose-500/10 text-rose-400 px-2 py-1 rounded-full"><i class="fa-solid fa-xmark mr-1"></i>Failed</span>';
                } else {
                    pendingCount++;
                    row.classList.add('border-l-2', 'border-l-slate-500');

                    const removeBtn = document.createElement('button');
                    removeBtn.className = 'text-rose-400 hover:text-rose-300 mr-3 text-sm';
                    removeBtn.title = 'Remove from queue';
                    removeBtn.innerHTML = '<i class="fa-solid fa-trash"></i>';
                    removeBtn.onclick = () => removeFromQueue(email);

                    const pendingBadge = document.createElement('span');
                    pendingBadge.className = 'text-xs font-medium bg-slate-500/10 text-slate-400 px-2 py-1 rounded-full';
                    pendingBadge.innerHTML = '<i class="fa-solid fa-clock mr-1"></i>Pending';

                    right.appendChild(removeBtn);
                    right.appendChild(pendingBadge);
                }

                top.appendChild(left);
                top.appendChild(right);
                row.appendChild(top);

                if (status === 'failed' && err) {
                    const errEl = document.createElement('div');
                    errEl.className = 'text-xs text-rose-300 mt-2 pl-9';
                    errEl.textContent = `Reason: ${err}`;
                    row.appendChild(errEl);
                }

                list.appendChild(row);
            });
        }

        label.innerText = `Sent: ${sentCount} | Pending: ${pendingCount} | Failed: ${failedCount}`;

        modal.classList.remove('hidden');
        setTimeout(() => modal.classList.remove('opacity-0'), 10);
    });
}

function closeQueueModal() {
    const modal = document.getElementById('queue-modal');
    if (!modal) return;
    modal.classList.add('opacity-0');
    setTimeout(() => modal.classList.add('hidden'), 300);
}

function removeFromQueue(email) {
    pywebview.api.remove_from_queue(email).then(res => {
        if (!res.success) {
            showToast(res.message || 'Could not remove email.', true);
            return;
        }

        loadedEmails = loadedEmails.filter(e => e !== normalizeEmail(email));
        updateRecipientCount();
        openQueueModal();
        showToast(res.message || `${email} removed.`);
    }).catch(err => {
        showToast(err.message || String(err), true);
    });
}

function getTemplateHtmlForPreview(source) {
    if (source === 'editor') {
        return composeTemplateHtmlFromEditor();
    }

    if (source.startsWith('sys_')) {
        const idx = parseInt(source.split('_')[1], 10);
        return presetTemplates[idx]?.html || '';
    }

    if (source.startsWith('user_')) {
        const idx = parseInt(source.split('_')[1], 10);
        return userTemplates[idx]?.html || '';
    }

    return '';
}

function previewSelectedTemplate(forceSource = null) {
    const source = forceSource || document.getElementById('send_template_select')?.value || 'editor';
    const htmlContent = getTemplateHtmlForPreview(source);

    if (!htmlContent) {
        showToast('No template content to preview.', true);
        return;
    }

    const iframe = document.getElementById('preview-iframe');
    const modal = document.getElementById('preview-modal');
    if (!iframe || !modal) return;

    iframe.srcdoc = htmlContent;
    modal.classList.remove('hidden');
    setTimeout(() => modal.classList.remove('opacity-0'), 10);
}

function closePreviewModal() {
    const modal = document.getElementById('preview-modal');
    const iframe = document.getElementById('preview-iframe');
    if (!modal || !iframe) return;

    modal.classList.add('opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        iframe.srcdoc = '';
    }, 300);
}

function triggerEasterEgg() {
    easterEggCount++;
    const heart = document.getElementById('easter-egg-heart');
    if (!heart) return;

    if (easterEggCount === 1) {
        showToast('Hello @xavi52!');
        heart.classList.add('text-rose-500');
        heart.classList.remove('text-rose-500/50');
        heart.style.transform = 'scale(1.2)';
    } else if (easterEggCount === 3) {
        showToast('Builder + safety mode = unstoppable 🚀');
        heart.style.transform = 'scale(1.4)';
    } else if (easterEggCount >= 5) {
        showToast('Easter Egg unlocked.');
        heart.style.transform = 'scale(1.6) rotate(15deg)';
        easterEggCount = 0;
        setTimeout(() => {
            heart.style.transform = 'scale(1) rotate(0deg)';
        }, 1500);
    }
}
