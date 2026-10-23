// Global Pulse & Tech Daily - Client-Side Script

// Trigger instant daily test post generation from sidebar widget
function triggerTestGenerate() {
    const btn = document.getElementById('btnQuickGenerate');
    const statusBox = document.getElementById('genStatus');
    const catSelect = document.getElementById('quickCatSelect');
    const selectedCategory = catSelect ? catSelect.value : '';

    if (!btn || !statusBox) return;

    btn.disabled = true;
    btn.innerHTML = '⏳ Generating bilingual post...';
    statusBox.style.display = 'block';
    statusBox.style.background = '#e0f2fe';
    statusBox.style.color = '#0369a1';
    statusBox.innerHTML = '⚡ Drafting English & Hindi daily post...';

    fetch('/api/generate-test-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: selectedCategory })
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        btn.innerHTML = '🚀 Generate Test Post';
        if (data.success) {
            statusBox.style.background = '#ecfdf5';
            statusBox.style.color = '#065f46';
            statusBox.innerHTML = `
                ✅ <strong>Post Published!</strong><br>
                <a href="/post/${data.post.slug}" style="text-decoration: underline; font-weight: bold; color: #2563eb;">
                    View: ${data.post.title_en.substring(0, 35)}... &rarr;
                </a>
            `;
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        } else {
            statusBox.style.background = '#fef2f2';
            statusBox.style.color = '#991b1b';
            statusBox.innerHTML = '❌ Failed to generate post.';
        }
    })
    .catch(err => {
        btn.disabled = false;
        btn.innerHTML = '🚀 Generate Test Post';
        statusBox.style.background = '#fef2f2';
        statusBox.style.color = '#991b1b';
        statusBox.innerHTML = '❌ Network error: ' + err;
    });
}

// Initialise page
document.addEventListener('DOMContentLoaded', () => {
    // Check if user came from a language switch
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    if (langParam && (langParam === 'en' || langParam === 'hi')) {
        document.cookie = "site_lang=" + langParam + ";path=/;max-age=" + (365*24*60*60);
    }
});
