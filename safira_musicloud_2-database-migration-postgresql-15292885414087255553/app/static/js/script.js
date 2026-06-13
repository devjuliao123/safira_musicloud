// Theme Management
(function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
})();

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Logic
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');

    function updateThemeIcon(theme) {
        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        }
    }

    // Set initial icon
    const currentTheme = document.documentElement.getAttribute('data-theme');
    updateThemeIcon(currentTheme);

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');

    if (menuToggle && sidebar && overlay) {
        // Alternar sidebar e overlay
        menuToggle.addEventListener('click', function() {
            menuToggle.classList.toggle('active');
            sidebar.classList.toggle('active');
            overlay.classList.toggle('active');
        });

        // Fechar ao clicar no overlay
        overlay.addEventListener('click', function() {
            menuToggle.classList.remove('active');
            sidebar.classList.remove('active');
            overlay.classList.remove('active');
        });
    }

    // Destacar link de navegação ativo
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.flash-messages-container .alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Dropdown Stacking Context Fix (Fallback for browsers without :has)
    document.addEventListener('show.bs.dropdown', function (event) {
        const tr = event.target.closest('tr');
        if (tr) {
            tr.style.zIndex = '1070';
            tr.style.position = 'relative';
        }
    });

    document.addEventListener('hide.bs.dropdown', function (event) {
        const tr = event.target.closest('tr');
        if (tr) {
            tr.style.zIndex = '';
            tr.style.position = '';
        }
    });
});
