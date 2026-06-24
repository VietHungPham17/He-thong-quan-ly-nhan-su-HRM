/* HRM System - Main JavaScript (Responsive) */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle ─────────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar       = document.getElementById('sidebar');
    const mainContent   = document.getElementById('mainContent');
    const overlay       = document.getElementById('sidebarOverlay');

    const MOBILE_BP = 768;

    function isMobile() {
        return window.innerWidth <= MOBILE_BP;
    }

    function openMobileSidebar() {
        sidebar.classList.add('mobile-open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMobileSidebar() {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    function toggleDesktopSidebar() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('collapsed');
        // Persist state
        const isCollapsed = sidebar.classList.contains('collapsed');
        try { localStorage.setItem('sidebarCollapsed', isCollapsed); } catch(e) {}
    }

    // Restore desktop sidebar state
    if (!isMobile()) {
        try {
            const saved = localStorage.getItem('sidebarCollapsed');
            if (saved === 'true' && sidebar && mainContent) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('collapsed');
            }
        } catch(e) {}
    }

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function () {
            if (isMobile()) {
                if (sidebar.classList.contains('mobile-open')) {
                    closeMobileSidebar();
                } else {
                    openMobileSidebar();
                }
            } else {
                toggleDesktopSidebar();
            }
        });
    }

    // Overlay click closes sidebar
    if (overlay) {
        overlay.addEventListener('click', function () {
            closeMobileSidebar();
        });
    }

    // Handle resize: clean up mobile state when going to desktop
    window.addEventListener('resize', function () {
        if (!isMobile()) {
            closeMobileSidebar();
        }
    });

    // ── Auto-dismiss alerts ─────────────────────────────
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // ── Confirm delete dialogs ──────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm || 'Bạn có chắc chắn muốn xóa?')) {
                e.preventDefault();
            }
        });
    });

    // ── Tooltip initialization ──────────────────────────
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    // ── Avatar preview ──────────────────────────────────
    const avatarInputs = document.querySelectorAll('input[type="file"][name="avatar"]');
    avatarInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    const preview = document.getElementById('avatarPreview');
                    if (preview) preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // ── Number formatting ──────────────────────────────
    function formatVND(amount) {
        return new Intl.NumberFormat('vi-VN').format(amount) + ' ₫';
    }

    // ── Search with delay ──────────────────────────────
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function (input) {
        let timeout;
        input.addEventListener('input', function () {
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                input.closest('form').submit();
            }, 500);
        });
    });

    // ── Touch swipe to open/close sidebar on mobile ────
    let touchStartX = 0;
    let touchEndX   = 0;
    const SWIPE_THRESHOLD = 60;

    document.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });

    document.addEventListener('touchend', function (e) {
        if (!isMobile()) return;
        touchEndX = e.changedTouches[0].clientX;
        const diff = touchEndX - touchStartX;

        // Swipe right from left edge → open sidebar
        if (diff > SWIPE_THRESHOLD && touchStartX < 30) {
            openMobileSidebar();
        }
        // Swipe left when sidebar is open → close
        if (diff < -SWIPE_THRESHOLD && sidebar && sidebar.classList.contains('mobile-open')) {
            closeMobileSidebar();
        }
    }, { passive: true });

});
