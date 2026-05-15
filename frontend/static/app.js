document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initCountups();
    initSidebarCollapsibles();
    initDashboardFilters();
    initProjectTaskFilters();
    initInteractiveRows();
    initFloatingActionButton();
    initSurfaceTilt();
    ensureSidebarFallback();
});

function initClock() {
    const clockElement = document.getElementById('live-clock');
    if (!clockElement) return;

    const updateClock = () => {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        clockElement.textContent = `${hours}:${minutes}:${seconds}`;
    };

    updateClock();
    const delay = 1000 - new Date().getMilliseconds();
    setTimeout(() => {
        updateClock();
        setInterval(updateClock, 1000);
    }, delay);
}

function initCountups() {
    const counters = document.querySelectorAll('[data-countup]');
    if (!counters.length) return;

    const animateCounter = (element) => {
        if (element.dataset.counted === 'true') return;
        element.dataset.counted = 'true';

        const target = Number(element.dataset.countup || 0);
        const duration = 750;
        const start = performance.now();

        const frame = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            element.textContent = Math.round(target * eased);

            if (progress < 1) {
                requestAnimationFrame(frame);
            } else {
                element.textContent = target;
            }
        };

        requestAnimationFrame(frame);
    };

    if (!('IntersectionObserver' in window)) {
        counters.forEach(animateCounter);
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            animateCounter(entry.target);
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.35 });

    counters.forEach((counter) => observer.observe(counter));
}

function ensureSidebarFallback() {
    // If the server-side template didn't render the sidebar, inject a minimal fallback so users always see navigation.
    if (document.querySelector('.workspace-sidebar')) return;

    const signedInText = Array.from(document.querySelectorAll('.navbar-nav li')).find(li => li.textContent && li.textContent.includes('Signed in'));
    const isSignedIn = Boolean(signedInText);
    if (!isSignedIn) return; // only inject for signed-in users

    const sidebar = document.createElement('aside');
    sidebar.className = 'workspace-sidebar';
    sidebar.innerHTML = `
        <div class="sidebar-panel">
            <div class="sidebar-user">
                <span class="sidebar-user-kicker">Signed in</span>
                <strong>${document.querySelector('.user-pill') ? document.querySelector('.user-pill').textContent.replace('Signed in as', '').trim() : 'You'}</strong>
            </div>
            <div class="sidebar-section">
                <div class="sidebar-section-title">Navigation</div>
                <a href="/dashboard" class="sidebar-link"><i class="fa-solid fa-house"></i><span>Dashboard</span></a>
                <a href="/projects" class="sidebar-link"><i class="fa-solid fa-folder-open"></i><span>Projects</span></a>
                <a href="/tasks" class="sidebar-link"><i class="fa-solid fa-list-check"></i><span>Team Tasks</span></a>
                <a href="/admin" class="sidebar-link"><i class="fa-solid fa-user-shield"></i><span>Admin</span></a>
            </div>
        </div>
    `;

    // Insert before main content if possible
    const appShell = document.querySelector('.app-shell') || document.body;
    appShell.insertBefore(sidebar, appShell.firstChild);
}

function initSidebarCollapsibles() {
    document.querySelectorAll('[data-collapsible]').forEach((section) => {
        const trigger = section.querySelector('[data-collapsible-trigger]');
        const body = section.querySelector('[data-collapsible-body]');
        if (!trigger || !body) return;

        trigger.addEventListener('click', () => {
            const isCollapsed = section.classList.toggle('is-collapsed');
            body.classList.toggle('d-none', isCollapsed);
            trigger.setAttribute('aria-expanded', String(!isCollapsed));
        });
    });
}

function initDashboardFilters() {
    document.querySelectorAll('[data-filter-group]').forEach((group) => {
        const targetSelector = group.dataset.filterTarget;
        const target = targetSelector ? document.querySelector(targetSelector) : null;
        if (!target) return;

        const rows = Array.from(target.querySelectorAll('[data-filterable]'));
        const emptyState = group.dataset.emptyTarget ? document.querySelector(group.dataset.emptyTarget) : target.parentElement?.nextElementSibling;

        group.querySelectorAll('[data-filter]').forEach((button) => {
            button.addEventListener('click', () => {
                group.querySelectorAll('[data-filter]').forEach((item) => item.classList.remove('is-active'));
                button.classList.add('is-active');

                const filter = (button.dataset.filter || 'all').toLowerCase();
                let visibleCount = 0;

                rows.forEach((row) => {
                    const status = (row.dataset.status || '').toLowerCase();
                    const overdue = row.dataset.overdue === 'true';
                    const matches =
                        filter === 'all' ||
                        status === filter ||
                        (filter === 'overdue' && overdue);

                    row.classList.toggle('is-hidden', !matches);
                    if (matches) visibleCount += 1;
                });

                if (emptyState) {
                    emptyState.classList.toggle('d-none', visibleCount !== 0);
                }
            });
        });
    });
}

function initProjectTaskFilters() {
    const searchInput = document.querySelector('[data-task-search]');
    const statusSelect = document.querySelector('[data-task-status-filter]');
    if (!searchInput || !statusSelect) return;

    const targetSelector = searchInput.dataset.taskTarget || statusSelect.dataset.taskTarget;
    const target = targetSelector ? document.querySelector(targetSelector) : null;
    if (!target) return;

    const rows = Array.from(target.querySelectorAll('[data-task-row]'));
    const emptyState = document.querySelector('#project-task-empty');

    const applyFilters = () => {
        const term = searchInput.value.trim().toLowerCase();
        const statusFilter = (statusSelect.value || 'all').toLowerCase();
        let visibleCount = 0;

        rows.forEach((row) => {
            const haystack = (row.dataset.search || '').toLowerCase();
            const status = (row.dataset.status || '').toLowerCase();
            const overdue = row.dataset.overdue === 'true';

            const matchesSearch = !term || haystack.includes(term);
            const matchesStatus =
                statusFilter === 'all' ||
                status === statusFilter ||
                (statusFilter === 'overdue' && overdue);

            const isVisible = matchesSearch && matchesStatus;
            row.classList.toggle('is-hidden', !isVisible);
            if (isVisible) visibleCount += 1;
        });

        if (emptyState) {
            emptyState.classList.toggle('d-none', visibleCount !== 0);
        }
    };

    searchInput.addEventListener('input', applyFilters);
    statusSelect.addEventListener('change', applyFilters);
}

function initInteractiveRows() {
    document.querySelectorAll('.table tbody tr, .list-group-item').forEach((row) => {
        row.addEventListener('click', (event) => {
            if (event.target.closest('a, button, select, input, textarea, label, form')) return;

            const parent = row.parentElement;
            if (!parent) return;

            parent.querySelectorAll('.is-highlighted').forEach((item) => {
                if (item !== row) item.classList.remove('is-highlighted');
            });

            row.classList.toggle('is-highlighted');
        });
    });
}

function initFloatingActionButton() {
    const fab = document.querySelector('[data-fab]');
    const toggle = document.querySelector('[data-fab-toggle]');
    if (!fab || !toggle) return;

    const setOpen = (nextOpen) => {
        fab.classList.toggle('is-open', nextOpen);
        toggle.setAttribute('aria-expanded', String(nextOpen));
    };

    toggle.addEventListener('click', () => {
        setOpen(!fab.classList.contains('is-open'));
    });

    document.addEventListener('click', (event) => {
        if (!fab.contains(event.target)) {
            setOpen(false);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setOpen(false);
        }
    });

    const scrollTopButton = fab.querySelector('[data-scroll-top]');
    if (scrollTopButton) {
        scrollTopButton.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            setOpen(false);
        });
    }

    fab.querySelectorAll('.fab-action-chip').forEach((item) => {
        item.addEventListener('click', () => setOpen(false));
    });
}

function initSurfaceTilt() {
    const surfaces = document.querySelectorAll('.interactive-surface');
    surfaces.forEach((surface) => {
        surface.addEventListener('pointermove', (event) => {
            const rect = surface.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) - 0.5;
            const y = ((event.clientY - rect.top) / rect.height) - 0.5;
            surface.classList.add('is-tilting');
            surface.style.transform = `translateY(-3px) rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 5).toFixed(2)}deg)`;
        });

        surface.addEventListener('pointerleave', () => {
            surface.style.transform = '';
            surface.classList.remove('is-tilting');
        });
    });
}
