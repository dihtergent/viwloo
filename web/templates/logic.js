/* ============================================================
   VIWLOO — UNIFIED MASTER LOGIC (logic.js)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
    initAuthTabs();
    initModalsAndFab();
    initCardEntranceAnimation();
    initAutoDismissToasts();
    initFormSubmissions();
    initAvatarPreview();
    initPasswordToggles();
});

/* ------------------------------------------------------------
   1. AUTH TAB SWITCHING (Index / Login / Register)
   ------------------------------------------------------------ */
function initAuthTabs() {
    const tabs = document.querySelectorAll('.auth-tab');
    const forms = document.querySelectorAll('.auth-form');

    if (!tabs.length) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            forms.forEach(f => f.classList.remove('active'));
            tab.classList.add('active');
            const target = document.getElementById(tab.dataset.target);
            if (target) target.classList.add('active');
        });
    });
}

/* ------------------------------------------------------------
   2. LIKE BUTTON AJAX TOGGLE
   ------------------------------------------------------------ */
function toggleLike(event, postId, btn) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!csrf) return;

    fetch(`/post/${postId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(r => r.json())
    .then(data => {
        const countSpan = btn.querySelector('.like-count') || document.getElementById('detail-like-count');
        const svg = btn.querySelector('svg');

        if (data.liked) {
            btn.classList.add('liked');
            if (svg) svg.setAttribute('fill', 'currentColor');
        } else {
            btn.classList.remove('liked');
            if (svg) svg.setAttribute('fill', 'none');
        }
        if (countSpan) countSpan.textContent = data.likes_count;
    })
    .catch(e => console.error('Like error:', e));
}

/* ------------------------------------------------------------
   3. MODAL & FAB CONTROLS
   ------------------------------------------------------------ */
function initModalsAndFab() {
    const fab = document.getElementById('fab-add');
    const modal = document.getElementById('modal-create');
    const closeBtn = document.getElementById('modal-close');

    if (fab && modal) {
        fab.addEventListener('click', () => modal.classList.add('active'));
    }
    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.remove('active');
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (modal) modal.classList.remove('active');
            closeDeleteModal();
        }
    });
}

function openDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.add('active');
}

function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    if (modal) modal.classList.remove('active');
}

/* ------------------------------------------------------------
   4. CARD ENTRANCE & TOAST AUTO-DISMISS
   ------------------------------------------------------------ */
function initCardEntranceAnimation() {
    const cards = document.querySelectorAll('.card, .comment-item');
    cards.forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        card.style.transition = `opacity 0.35s ease ${i * 0.04}s, transform 0.35s ease ${i * 0.04}s`;
        requestAnimationFrame(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        });
    });
}

function initAutoDismissToasts() {
    document.querySelectorAll('.toast, .toast-msg').forEach(t => {
        setTimeout(() => {
            t.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            t.style.opacity = '0';
            t.style.transform = 'translateX(30px)';
            setTimeout(() => t.remove(), 400);
        }, 4000);
    });
}

/* ------------------------------------------------------------
   5. FORM SUBMISSION SAFETY (DOUBLE-SUBMIT PREVENTION)
   ------------------------------------------------------------ */
function initFormSubmissions() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        if (form.id === 'delete-form' || form.getAttribute('on-delete') === 'true') return;

        form.addEventListener('submit', function() {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.dataset.noDisable) {
                btn.disabled = true;
                const origText = btn.innerText;
                btn.dataset.origText = origText;
                btn.innerText = 'Processing…';
            }
        });
    });
}

/* ------------------------------------------------------------
   6. LIVE AVATAR PREVIEW
   ------------------------------------------------------------ */
function initAvatarPreview() {
    const avatarInput = document.getElementById('avatar-file');
    const avatarImg = document.getElementById('avatar-img');

    if (!avatarInput || !avatarImg) return;

    avatarInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                if (avatarImg.tagName === 'IMG') {
                    avatarImg.src = e.target.result;
                } else {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.id = 'avatar-img';
                    img.alt = 'Avatar preview';
                    img.className = 'avatar';
                    avatarImg.replaceWith(img);
                }
            };
            reader.readAsDataURL(file);
        }
    });
}

/* ------------------------------------------------------------
   7. PASSWORD VISIBILITY TOGGLE
   ------------------------------------------------------------ */
function initPasswordToggles() {
    const toggleBtn = document.getElementById('togglePasswordBtn');
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleEyeIcon');

    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            if (toggleIcon) {
                toggleIcon.setAttribute('data-lucide', isPassword ? 'eye-off' : 'eye');
                if (window.lucide) window.lucide.createIcons();
            }
        });
    }
}

/* ------------------------------------------------------------
   8. MOBILE COMPATIBLE GPS GEOLOCATION (Android & iOS Safari)
   ------------------------------------------------------------ */
function getGPSLocation() {
    const btn = document.getElementById('gps-btn');
    const btnText = document.getElementById('gps-btn-text');
    const latInput = document.getElementById('post-latitude');
    const lngInput = document.getElementById('post-longitude');
    const coordsDiv = document.getElementById('location-coords');
    const coordDisplay = document.getElementById('coord-display');
    const nameInput = document.getElementById('location-name');

    if (!btn || !btnText) return;

    // Check HTTPS / Secure Context requirement for iOS Safari & Android Chrome
    if (!window.isSecureContext && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        alert('Notice: Mobile browsers (iOS & Android) require a secure HTTPS connection for GPS geolocation.');
    }

    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }

    btn.classList.add('loading');
    btnText.textContent = 'Acquiring GPS…';

    // Success Callback
    function onPosSuccess(position) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        if (latInput) latInput.value = lat;
        if (lngInput) lngInput.value = lng;

        if (coordDisplay) coordDisplay.textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        if (coordsDiv) coordsDiv.classList.add('visible');

        btn.classList.remove('loading');
        btn.classList.add('active');
        btnText.textContent = 'Located ✓';

        // Reverse Geocoding to get location name if empty
        if (nameInput && !nameInput.value.trim()) {
            fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`, {
                headers: {
                    'Accept-Language': 'en'
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data && data.display_name) {
                    const parts = data.display_name.split(',');
                    nameInput.value = parts.slice(0, 3).join(',').trim();
                }
            })
            .catch(() => {
                // Silently fallback if Nominatim is rate limited
            });
        }
    }

    // Stage 1: Try High Accuracy GPS (8s timeout for quick response)
    navigator.geolocation.getCurrentPosition(
        onPosSuccess,
        (error) => {
            // If user explicitly denied permission, stop immediately
            if (error.code === 1) { // PERMISSION_DENIED
                btn.classList.remove('loading');
                btnText.textContent = 'Use GPS';
                alert('Location permission was denied. Please allow location access in your device settings.');
                return;
            }

            // Stage 2 Fallback for iOS/Android (indoors or weak satellite signal):
            // Retry with low accuracy (Cellular/Wi-Fi positioning), which resolves fast on mobile devices!
            btnText.textContent = 'Retrying (Network)…';
            navigator.geolocation.getCurrentPosition(
                onPosSuccess,
                (err2) => {
                    btn.classList.remove('loading');
                    btnText.textContent = 'Use GPS';
                    let msg = 'Unable to get location.';
                    if (err2.code === 1) msg = 'Location permission denied.';
                    else if (err2.code === 2) msg = 'Location unavailable. Please check GPS signal.';
                    else if (err2.code === 3) msg = 'Location request timed out. Please try again.';
                    alert(msg);
                },
                { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
            );
        },
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
    );
}
