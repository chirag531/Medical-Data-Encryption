// Main JavaScript for MedSecure Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload drag and drop
    initFileUpload();
    
    // Encryption form handling
    initEncryptionForms();
    
    // Performance charts
    initPerformanceCharts();
    
    // Real-time updates
    initRealTimeUpdates();
    
    // Security features
    initSecurityFeatures();
});

function initFileUpload() {
    const fileUploadAreas = document.querySelectorAll('.file-upload-area');
    
    fileUploadAreas.forEach(area => {
        const input = area.querySelector('input[type="file"]');
        const label = area.querySelector('.file-upload-label');
        
        if (!input || !label) return;
        
        // Click event
        area.addEventListener('click', () => input.click());
        
        // Drag and drop events
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                input.files = e.dataTransfer.files;
                updateFileLabel(label, e.dataTransfer.files[0]);
            }
        });
        
        // Change event for regular file input
        input.addEventListener('change', () => {
            if (input.files.length) {
                updateFileLabel(label, input.files[0]);
            }
        });
    });
}

function updateFileLabel(label, file) {
    const fileName = file.name;
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    
    label.innerHTML = `
        <i class="fas fa-file-upload fa-2x mb-2 text-success"></i>
        <div><strong>${fileName}</strong></div>
        <small class="text-muted">${fileSize} MB</small>
    `;
}

function initEncryptionForms() {
    const encryptionForms = document.querySelectorAll('form[data-encryption-form]');
    
    encryptionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
            
            // Simulate processing for demo
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 2000);
        });
    });
}

function initPerformanceCharts() {
    // This would be replaced with actual chart initialization
    // For now, we'll just log that charts are ready
    console.log('Performance charts initialized');
}

function initRealTimeUpdates() {
    // Update dashboard stats in real-time
    if (document.querySelector('.quick-stats')) {
        setInterval(updateDashboardStats, 5000);
    }
}

function updateDashboardStats() {
    // Simulate real-time updates
    const statNumbers = document.querySelectorAll('.quick-stat-number');
    statNumbers.forEach(stat => {
        const current = parseInt(stat.textContent);
        const change = Math.floor(Math.random() * 10) - 2; // Random change between -2 and +7
        const newValue = Math.max(0, current + change);
        
        // Animate the number change
        animateValue(stat, current, newValue, 1000);
    });
}

function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value;
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function initSecurityFeatures() {
    // Auto-logout after 30 minutes of inactivity
    let inactivityTime = function() {
        let time;
        window.onload = resetTimer;
        document.onmousemove = resetTimer;
        document.onkeypress = resetTimer;
        
        function logout() {
            // Show logout warning
            showLogoutWarning();
        }
        
        function resetTimer() {
            clearTimeout(time);
            time = setTimeout(logout, 30 * 60 * 1000); // 30 minutes
        }
    };
    
    inactivityTime();
}

function showLogoutWarning() {
    const warningModal = `
        <div class="modal fade" id="logoutWarning" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title"><i class="fas fa-exclamation-triangle me-2"></i>Session Timeout Warning</h5>
                    </div>
                    <div class="modal-body">
                        <p>Your session will expire due to inactivity. Would you like to continue?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Logout</button>
                        <button type="button" class="btn btn-primary" id="continueSession">Continue Session</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', warningModal);
    const modal = new bootstrap.Modal(document.getElementById('logoutWarning'));
    modal.show();
    
    document.getElementById('continueSession').addEventListener('click', () => {
        modal.hide();
        // Reset inactivity timer
        initSecurityFeatures();
    });
}

// Utility functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Key copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy key', 'error');
    });
}

function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type];
    
    const notification = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert.position-fixed');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Encryption key generator
function generateEncryptionKey(length = 32) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return btoa(result).slice(0, length);
}

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
    if (password.match(/\d/)) strength++;
    if (password.match(/[^a-zA-Z\d]/)) strength++;
    
    return strength;
}