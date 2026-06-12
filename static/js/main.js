document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. CLOCK & DATES (Gregorian & Hijri)
    // ==========================================
    const updateTimeAndDates = () => {
        const now = new Date();
        
        const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true };
        document.getElementById('clock-time').textContent = now.toLocaleTimeString('en-US', timeOptions);
        
        const gregOptions = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        document.getElementById('clock-gregorian').textContent = now.toLocaleDateString('en-US', gregOptions);
        
        const hijriOptions = { day: 'numeric', month: 'long', year: 'numeric' };
        const hijriDate = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', hijriOptions).format(now);
        document.getElementById('clock-hijri').textContent = hijriDate + ' AH';
    };

    updateTimeAndDates();
    setInterval(updateTimeAndDates, 1000);


    // ==========================================
    // 2. SIDEBAR TOGGLE LOGIC
    // ==========================================
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');

    const toggleSidebar = () => {
        if (sidebar) {
            sidebar.classList.toggle('collapsed');
        }
    };

    if (sidebarToggle) sidebarToggle.addEventListener('click', toggleSidebar);
    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', toggleSidebar);


    // ==========================================
    // 3. MENU SHUTTER / ACCORDION LOGIC
    // ==========================================
    const dropdownBtns = document.querySelectorAll('.tools-dropdown-btn');

    dropdownBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.toggle('active');
            const targetId = this.getAttribute('data-menu-target');
            if (targetId) {
                const targetMenu = document.getElementById(targetId);
                if (targetMenu) {
                    targetMenu.classList.toggle('expanded');
                }
            }
        });
    });

    // ==========================================
    // 4. IFRAME NAVIGATION LOGIC (NEW)
    // ==========================================
    const navLinks = document.querySelectorAll('.nav-link');
    const iframe = document.getElementById('module-container');

    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            
            if (url) {
                // Iframe में URL लोड करें और उसे दिखाएं
                iframe.src = url;
                iframe.style.display = 'block';

                // सारे लिंक्स से active क्लास हटाएं
                navLinks.forEach(l => l.classList.remove('active'));
                
                // जिस लिंक पर क्लिक किया है, उसे active करें
                this.classList.add('active');
            }
        });
    });

});