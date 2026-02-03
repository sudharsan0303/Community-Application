/**
 * Theme Switcher for Community Helper Hub
 * Handles toggling between light and dark themes with smooth transitions
 */

class ThemeManager {
    constructor() {
        this.themeSwitch = document.getElementById('theme-switch');
        this.themeCSS = document.getElementById('theme-css');
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.transitions = {
            duration: '0.3s',
            properties: ['background-color', 'color', 'border-color', 'box-shadow']
        };
        this.themes = {
            light: {
                primary: '#ffffff',
                secondary: '#f8f9fa',
                text: '#212529',
                accent: '#4e6bff',
                border: '#dee2e6',
                shadow: 'rgba(0,0,0,0.1)'
            },
            dark: {
                primary: '#121212',
                secondary: '#1e1e1e',
                text: '#e0e0e0',
                accent: '#6979ff',
                border: '#3d3d3d',
                shadow: 'rgba(255,255,255,0.05)'
            }
        };
        
        this.init();
    }

    init() {
        // Prevent flash of wrong theme
        document.documentElement.style.visibility = 'hidden';
        
        this.setupTransitions();
        this.applyTheme(this.currentTheme);
        this.setupListeners();
        
        // Show content once theme is applied
        requestAnimationFrame(() => {
            document.documentElement.style.visibility = '';
        });
    }
    
    setupTransitions() {
        // Add transition styles to head
        const style = document.createElement('style');
        style.textContent = `
            * {
                transition: background-color ${this.transitions.duration} ease,
                           color ${this.transitions.duration} ease,
                           border-color ${this.transitions.duration} ease,
                           box-shadow ${this.transitions.duration} ease;
            }
        `;
        document.head.appendChild(style);
    }
    
    setupListeners() {
        // Add click event to theme toggle button
        this.themeSwitch.addEventListener('click', () => {
            // Toggle theme
            const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            
            // Apply the new theme
            this.applyTheme(newTheme);
            
            // Save theme preference
            localStorage.setItem('theme', newTheme);
            this.currentTheme = newTheme;
            
            // Add animation to the toggle button
            this.themeSwitch.classList.add('theme-switch-rotate');
            setTimeout(() => {
                this.themeSwitch.classList.remove('theme-switch-rotate');
            }, 300);
        });
    }
    
    /**
     * Apply theme to the document
     * @param {string} theme - 'light' or 'dark'
     */
    applyTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark-theme');
            this.themeCSS.setAttribute('href', this.themeCSS.getAttribute('href').replace('theme-light.css', 'theme-dark.css'));
            this.themeSwitch.querySelector('.dark-icon').style.display = 'none';
            this.themeSwitch.querySelector('.light-icon').style.display = 'inline-block';
        } else {
            document.documentElement.classList.remove('dark-theme');
            this.themeCSS.setAttribute('href', this.themeCSS.getAttribute('href').replace('theme-dark.css', 'theme-light.css'));
            this.themeSwitch.querySelector('.dark-icon').style.display = 'inline-block';
            this.themeSwitch.querySelector('.light-icon').style.display = 'none';
        }
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
});