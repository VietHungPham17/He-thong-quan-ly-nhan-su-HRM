/* HRM System - Main JavaScript */

document.addEventListener('DOMContentLoaded', function () {

    // ── Sidebar Toggle ─────────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('mobile-open');
            } else {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('collapsed');
            }
        });
    }

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

    // ── Active sidebar link ─────────────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(function (link) {
        if (link.href && link.href !== '#' && currentPath.startsWith(new URL(link.href, window.location.origin).pathname)) {
            link.classList.add('active');
        }
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

    // ── Mobile overlay ──────────────────────────────────
    document.addEventListener('click', function (e) {
        if (window.innerWidth <= 768 && sidebar && sidebar.classList.contains('mobile-open')) {
            if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

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

});
