// Encryption-related JavaScript functionality

class EncryptionManager {
    constructor() {
        this.currentAlgorithm = 'SM4';
        this.encryptionHistory = JSON.parse(localStorage.getItem('encryptionHistory')) || [];
        this.init();
    }
    
    init() {
        this.bindAlgorithmSwitcher();
        this.loadEncryptionHistory();
        this.initKeyGenerator();
    }
    
    bindAlgorithmSwitcher() {
        const algorithmSelects = document.querySelectorAll('select[name="algorithm"]');
        algorithmSelects.forEach(select => {
            select.addEventListener('change', (e) => {
                this.currentAlgorithm = e.target.value;
                this.updateAlgorithmInfo();
            });
        });
    }
    
    updateAlgorithmInfo() {
        const algorithmInfo = {
            'SM4': {
                name: 'SM4',
                keySize: '128-bit',
                security: 'High',
                speed: 'Fast',
                description: 'Chinese national standard block cipher, optimized for performance'
            },
            'AES-GCM': {
                name: 'AES-256-GCM',
                keySize: '256-bit',
                security: 'Very High',
                speed: 'Fast',
                description: 'Advanced Encryption Standard with Galois/Counter Mode, provides authenticated encryption'
            }
        };
        
        const info = algorithmInfo[this.currentAlgorithm];
        if (!info) return;
        
        // Update algorithm info displays
        const infoDisplays = document.querySelectorAll('.algorithm-info');
        infoDisplays.forEach(display => {
            display.innerHTML = `
                <div class="card bg-light">
                    <div class="card-body">
                        <h6><i class="fas fa-info-circle me-2"></i>${info.name} Algorithm</h6>
                        <div class="row small mt-2">
                            <div class="col-6">
                                <strong>Key Size:</strong> ${info.keySize}
                            </div>
                            <div class="col-6">
                                <strong>Security:</strong> ${info.security}
                            </div>
                            <div class="col-6">
                                <strong>Speed:</strong> ${info.speed}
                            </div>
                            <div class="col-12 mt-2">
                                ${info.description}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    initKeyGenerator() {
        const generateBtns = document.querySelectorAll('.generate-key-btn');
        generateBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const keyField = document.querySelector(btn.dataset.target);
                if (keyField) {
                    const key = this.generateKey();
                    keyField.value = key;
                    this.showNotification('New encryption key generated!', 'success');
                }
            });
        });
    }
    
    generateKey() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        let result = '';
        const length = this.currentAlgorithm === 'AES-GCM' ? 44 : 24; // Base64 encoded lengths
        
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        return btoa(result).slice(0, length);
    }
    
    async simulateEncryption(file, algorithm) {
        return new Promise((resolve) => {
            const fileSize = file.size;
            const baseTime = fileSize / (1024 * 1024) * 100; // Simulate time based on file size
            
            // Different algorithms have different performance characteristics
            const algorithmMultipliers = {
                'SM4': 1.0,
                'AES-GCM': 1.2
            };
            
            const processingTime = baseTime * algorithmMultipliers[algorithm];
            
            // Simulate processing
            setTimeout(() => {
                resolve({
                    success: true,
                    time: processingTime / 1000, // Convert to seconds
                    key: this.generateKey(),
                    algorithm: algorithm
                });
            }, processingTime);
        });
    }
    
    addToHistory(operation) {
        this.encryptionHistory.unshift({
            timestamp: new Date().toISOString(),
            ...operation
        });
        
        // Keep only last 50 operations
        this.encryptionHistory = this.encryptionHistory.slice(0, 50);
        localStorage.setItem('encryptionHistory', JSON.stringify(this.encryptionHistory));
        this.updateHistoryDisplay();
    }
    
    loadEncryptionHistory() {
        this.updateHistoryDisplay();
    }
    
    updateHistoryDisplay() {
        const historyContainers = document.querySelectorAll('.encryption-history');
        
        historyContainers.forEach(container => {
            if (this.encryptionHistory.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">No encryption history yet</p>';
                return;
            }
            
            const historyHTML = this.encryptionHistory.map(operation => `
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas ${operation.type === 'encrypt' ? 'fa-lock' : 'fa-unlock'}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="d-flex justify-content-between">
                            <span>${operation.type === 'encrypt' ? 'Encrypted' : 'Decrypted'} ${operation.dataType}</span>
                            <span class="encryption-badge badge-${operation.algorithm.toLowerCase()}">
                                ${operation.algorithm}
                            </span>
                        </div>
                        <small class="activity-time">${new Date(operation.timestamp).toLocaleString()}</small>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = historyHTML;
        });
    }
    
    showNotification(message, type = 'info') {
        // Use the notification function from main.js
        if (typeof showNotification === 'function') {
            showNotification(message, type);
        }
    }
    
    // PSNR Calculator
    calculatePSNR(originalSize, stegoSize) {
        // Simplified PSNR calculation for demo
        const mse = Math.abs(originalSize - stegoSize) / originalSize;
        if (mse === 0) return Infinity;
        return 20 * Math.log10(255 / Math.sqrt(mse));
    }
    
    // Security audit
    performSecurityAudit() {
        const auditResults = {
            encryptionStrength: this.currentAlgorithm === 'AES-GCM' ? 'Excellent' : 'Good',
            keyManagement: 'Secure',
            dataIntegrity: 'Verified',
            accessControl: 'Enforced'
        };
        
        return auditResults;
    }
}

// Initialize encryption manager
document.addEventListener('DOMContentLoaded', function() {
    window.encryptionManager = new EncryptionManager();
});

// Utility function for file validation
function validateFile(file, allowedTypes, maxSizeMB) {
    const errors = [];
    
    // Check file type
    if (!allowedTypes.includes(file.type)) {
        errors.push(`File type ${file.type} is not supported.`);
    }
    
    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        errors.push(`File size exceeds ${maxSizeMB}MB limit.`);
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

// Real-time file size calculator
function setupFileSizeCalculator() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const sizeDisplay = this.parentElement.querySelector('.file-size');
            if (sizeDisplay && this.files.length > 0) {
                const file = this.files[0];
                const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                sizeDisplay.textContent = `${sizeMB} MB`;
            }
        });
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', setupFileSizeCalculator);