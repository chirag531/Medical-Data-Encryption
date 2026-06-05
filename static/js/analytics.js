// Analytics and real-time updates for MedSecure

class AnalyticsManager {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.init();
    }
    
    init() {
        this.startRealTimeUpdates();
        this.initCharts();
    }
    
    startRealTimeUpdates() {
        setInterval(() => {
            this.updateDashboardStats();
            this.updateAccessHistory();
        }, this.updateInterval);
    }
    
    async updateDashboardStats() {
        try {
            // This would typically fetch from an API endpoint
            console.log('Updating dashboard statistics...');
        } catch (error) {
            console.error('Error updating dashboard stats:', error);
        }
    }
    
    async updateAccessHistory() {
        if (document.querySelector('.access-history-table')) {
            try {
                // Refresh access history table
                location.reload();
            } catch (error) {
                console.error('Error updating access history:', error);
            }
        }
    }
    
    initCharts() {
        // Initialize any additional charts for analytics
        this.initUserActivityChart();
        this.initPerformanceTrendsChart();
    }
    
    initUserActivityChart() {
        const ctx = document.getElementById('userActivityChart');
        if (!ctx) return;
        
        // User activity over time chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Admin Operations',
                    data: [12, 19, 8, 15, 22, 18, 25],
                    borderColor: 'rgba(255, 193, 7, 1)',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4
                }, {
                    label: 'User Operations',
                    data: [8, 12, 6, 9, 15, 11, 18],
                    borderColor: 'rgba(23, 162, 184, 1)',
                    backgroundColor: 'rgba(23, 162, 184, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'User Activity Over Time'
                    }
                }
            }
        });
    }
    
    initPerformanceTrendsChart() {
        const ctx = document.getElementById('performanceTrendsChart');
        if (!ctx) return;
        
        // Performance trends chart
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['SM4 Encrypt', 'SM4 Decrypt', 'AES Encrypt', 'AES Decrypt'],
                datasets: [{
                    label: 'Average Time (seconds)',
                    data: [0.045, 0.038, 0.052, 0.041],
                    backgroundColor: [
                        'rgba(52, 152, 219, 0.8)',
                        'rgba(52, 152, 219, 0.6)',
                        'rgba(39, 174, 96, 0.8)',
                        'rgba(39, 174, 96, 0.6)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Algorithm Performance Comparison'
                    }
                }
            }
        });
    }
    
    // Export analytics data
    exportAnalyticsData() {
        const data = {
            timestamp: new Date().toISOString(),
            userStats: this.getUserStats(),
            performanceMetrics: this.getPerformanceMetrics()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medsecure-analytics-${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.analyticsManager = new AnalyticsManager();
});