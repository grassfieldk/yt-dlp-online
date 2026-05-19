const API_BASE = '/api';
const form = document.getElementById('downloadForm');
const apiKey = document.getElementById('apiKey');
const videoUrl = document.getElementById('videoUrl');
const quality = document.getElementById('quality');
const fetchBtn = document.getElementById('fetchFormatsBtn');
const formatsDiv = document.getElementById('formatsContainer');
const formatsList = document.getElementById('formatsList');
const dlBtn = document.getElementById('downloadBtn');
const progress = document.getElementById('progress');
const progressFill = document.getElementById('progressFill');
const message = document.getElementById('message');

let selectedFormat = null;

fetchBtn.onclick = async (e) => {
    e.preventDefault();
    if (!apiKey.value.trim() || !videoUrl.value.trim()) {
        showMsg('入力してください', 'error');
        return;
    }
    fetchBtn.disabled = true;
    try {
        const res = await fetch(`${API_BASE}/formats?url=${encodeURIComponent(videoUrl.value)}`, {
            headers: { 'X-Api-Key': apiKey.value }
        });
        if (!res.ok) throw new Error('取得失敗');
        const formats = await res.json();
        formatsList.innerHTML = formats.slice(0, 10).map(f =>
            `<div class="format-item" data-id="${f.format_id}">${f.format_id}: ${f.format}</div>`
        ).join('');
        formatsDiv.style.display = 'block';
        document.querySelectorAll('.format-item').forEach(el => {
            el.onclick = () => selectedFormat = el.dataset.id;
        });
    } catch (e) {
        showMsg('エラー: ' + e.message, 'error');
    } finally {
        fetchBtn.disabled = false;
    }
};

form.onsubmit = async (e) => {
    e.preventDefault();
    if (!apiKey.value.trim() || !videoUrl.value.trim()) {
        showMsg('入力してください', 'error');
        return;
    }
    dlBtn.disabled = true;
    progress.style.display = 'block';
    message.style.display = 'none';
    try {
        const body = {
            url: videoUrl.value,
            ...(quality.value && { quality: parseInt(quality.value) }),
            ...(selectedFormat && { format_id: selectedFormat })
        };
        const res = await fetch(`${API_BASE}/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Api-Key': apiKey.value },
            body: JSON.stringify(body)
        });
        if (!res.ok) throw new Error((await res.json()).detail || '失敗');
        const blob = await res.blob();
        const fn = res.headers.get('Content-Disposition')?.match(/filename[^;=]*=(?:(['"]).*?\1|[^;]*)/)?.[0]?.split('=')[1]?.replace(/['"]/g, '') || 'video.mp4';
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fn;
        a.click();
        URL.revokeObjectURL(url);
        showMsg('✓ ダウンロード完了', 'success');
    } catch (e) {
        showMsg('✗ ' + e.message, 'error');
    } finally {
        dlBtn.disabled = false;
        progress.style.display = 'none';
    }
};

function showMsg(msg, type) {
    message.textContent = msg;
    message.className = 'message ' + type;
    message.style.display = 'block';
    if (type !== 'error') setTimeout(() => message.style.display = 'none', 4000);
}
