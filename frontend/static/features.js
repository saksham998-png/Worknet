document.addEventListener('DOMContentLoaded', () => {
    initThemeToggle();
    initRealtime();
});

function initThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    const apply = (dark) => {
        document.body.classList.toggle('theme-dark', dark);
        document.body.dataset.darkMode = dark ? 'true' : 'false';
        const icon = btn.querySelector('i');
        if (icon) {
            icon.className = dark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    };

    apply(document.body.dataset.darkMode === 'true');

    btn.addEventListener('click', async () => {
        const next = !document.body.classList.contains('theme-dark');
        apply(next);
        try {
            await fetch('/settings/theme', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dark_mode: next }),
            });
        } catch (e) {
            console.warn('Theme save failed', e);
        }
    });
}

function initRealtime() {
    if (typeof io === 'undefined' || !document.body.classList.contains('authenticated-app')) return;

    const socket = io();
    const projectId = document.body.dataset.projectId;

    socket.on('connect', () => {
        if (projectId) {
            socket.emit('join_project', { project_id: parseInt(projectId, 10) });
        }
    });

    socket.on('task_updated', (payload) => {
        showLiveToast('Task updated', payload.title || 'A task was changed');
        if (typeof loadActivityFeed === 'function') loadActivityFeed();
    });

    socket.on('new_activity', () => {
        if (typeof loadActivityFeed === 'function') loadActivityFeed();
    });
}

function showLiveToast(title, message) {
    const existing = document.querySelector('.live-toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'live-toast';
    toast.innerHTML = `<strong>${escapeHtml(title)}</strong><div class="text-muted small">${escapeHtml(message)}</div>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text || '';
    return d.innerHTML;
}

function initKanban(projectId) {
    if (typeof Sortable === 'undefined') return;

    document.querySelectorAll('[data-kanban-column]').forEach((column) => {
        Sortable.create(column, {
            group: 'kanban',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: async (evt) => {
                const status = evt.to.dataset.status;
                const items = [...evt.to.querySelectorAll('[data-task-id]')].map((el, idx) => ({
                    id: parseInt(el.dataset.taskId, 10),
                    status,
                    sort_order: idx,
                }));
                await fetch(`/api/projects/${projectId}/tasks/reorder`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ items }),
                });
            },
        });
    });
}

function initReportCharts(statusData, priorityData, healthData) {
    if (typeof Chart === 'undefined') return;

    const statusEl = document.getElementById('statusChart');
    if (statusEl) {
        new Chart(statusEl, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData),
                datasets: [{
                    data: Object.values(statusData),
                    backgroundColor: ['#64748b', '#1c8b7c', '#2b8f67'],
                }],
            },
            options: { plugins: { legend: { position: 'bottom' } } },
        });
    }

    const priorityEl = document.getElementById('priorityChart');
    if (priorityEl) {
        new Chart(priorityEl, {
            type: 'bar',
            data: {
                labels: Object.keys(priorityData),
                datasets: [{
                    label: 'Tasks',
                    data: Object.values(priorityData),
                    backgroundColor: ['#64748b', '#f59e0b', '#ec4899', '#ef4444'],
                }],
            },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
        });
    }

    const healthEl = document.getElementById('healthChart');
    if (healthEl && healthData.length) {
        new Chart(healthEl, {
            type: 'bar',
            data: {
                labels: healthData.map((p) => p.name),
                datasets: [{
                    label: 'Completion %',
                    data: healthData.map((p) => p.completion),
                    backgroundColor: healthData.map((p) => p.color || '#1c8b7c'),
                }],
            },
            options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { max: 100 } } },
        });
    }
}

window.initKanban = initKanban;
window.initReportCharts = initReportCharts;
window.showLiveToast = showLiveToast;
