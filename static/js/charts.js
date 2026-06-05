// Chart.js initialization for performance metrics

class PerformanceCharts {
    constructor() {
        this.charts = new Map();
        this.init();
    }
    
    init() {
        this.initEncryptionTimeChart();
        this.initPSNRChart();
        this.initAlgorithmComparisonChart();
        this.initSecurityMetricsChart();
    }
    
    initEncryptionTimeChart() {
        const ctx = document.getElementById('encryptionTimeChart');
        if (!ctx) return;
        
        this.charts.set('encryptionTime', new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['SM4', 'AES-256-GCM', 'Text Embedding', 'Image Embedding'],
                datasets: [{
                    label: 'Time (seconds)',
                    data: [0.045, 0.038, 1.234, 2.567],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(39, 174, 96, 0.8)',
                        'rgba(155, 89, 182, 0.8)',
                        'rgba(241, 196, 15, 0.8)'
                    ],
                    borderColor: [
                        'rgba(52, 152, 219, 1)',
                        'rgba(39, 174, 96, 1)',
                        'rgba(155, 89, 182, 1)',
                        'rgba(241, 196, 15, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Encryption Performance Comparison'
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Time (seconds)'
                        }
                    }
                }
            }
        }));
    }
    
    initPSNRChart() {
        const ctx = document.getElementById('psnrChart');
        if (!ctx) return;
        
        this.charts.set('psnr', new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Image 1', 'Image 2', 'Image 3', 'Image 4', 'Image 5'],
                datasets: [{
                    label: 'PSNR (dB)',
                    data: [45.6, 48.2, 42.8, 47.1, 49.3],
                    borderColor: 'rgba(231, 76, 60, 1)',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Image Quality Metrics (PSNR)'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        title: {
                            display: true,
                            text: 'PSNR (dB)'
                        }
                    }
                }
            }
        }));
    }
    
    initAlgorithmComparisonChart() {
        const ctx = document.getElementById('algorithmComparisonChart');
        if (!ctx) return;
        
        this.charts.set('algorithmComparison', new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Speed', 'Security', 'Image Quality', 'File Size', 'Compatibility'],
                datasets: [{
                    label: 'SM4',
                    data: [85, 80, 90, 75, 95],
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderColor: 'rgba(52, 152, 219, 1)',
                    pointBackgroundColor: 'rgba(52, 152, 219, 1)'
                }, {
                    label: 'AES-256-GCM',
                    data: [75, 95, 85, 80, 90],
                    backgroundColor: 'rgba(39, 174, 96, 0.2)',
                    borderColor: 'rgba(39, 174, 96, 1)',
                    pointBackgroundColor: 'rgba(39, 174, 96, 1)'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Algorithm Comparison'
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                }
            }
        }));
    }
    
    initSecurityMetricsChart() {
        const ctx = document.getElementById('securityMetricsChart');
        if (!ctx) return;
        
        this.charts.set('securityMetrics', new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Successful', 'Failed Attempts', 'Pending'],
                datasets: [{
                    data: [75, 15, 10],
                    backgroundColor: [
                        'rgba(39, 174, 96, 0.8)',
                        'rgba(231, 76, 60, 0.8)',
                        'rgba(241, 196, 15, 0.8)'
                    ],
                    borderColor: [
                        'rgba(39, 174, 96, 1)',
                        'rgba(231, 76, 60, 1)',
                        'rgba(241, 196, 15, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Security Operations'
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        }));
    }
    
    updateChart(chartName, newData) {
        const chart = this.charts.get(chartName);
        if (chart) {
            chart.data.datasets[0].data = newData;
            chart.update();
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        window.performanceCharts = new PerformanceCharts();
    }
});