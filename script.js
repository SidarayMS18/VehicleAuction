// static/js/script.js
const { createApp } = Vue;

createApp({
    data() {
        return {
            currentUser: null,
            showRegister: false,
            loginData: { username: '', password: '' },
            registerData: { username: '', password: '', email: '' },
            vehicles: [],
            notifications: [],
            bidAmounts: {},
            newVehicle: {
                make: '',
                model: '',
                year: new Date().getFullYear(),
                mileage: 0,
                reserve_price: 0,
                end_time: '',
                description: ''
            }
        }
    },
    computed: {
        formattedVehicles() {
            return this.vehicles.map(vehicle => ({
                ...vehicle,
                formattedMileage: this.formatNumber(vehicle.mileage) + ' miles',
                formattedPrice: '$' + this.formatNumber(vehicle.reserve_price),
                formattedBid: vehicle.highest_bid ? 
                    '$' + this.formatNumber(vehicle.highest_bid) : 
                    'No bids',
                formattedEndTime: this.formatTime(vehicle.end_time)
            }));
        }
    },
    mounted() {
        this.checkAuth();
    },
    methods: {
        formatNumber(num) {
            return num?.toLocaleString('en-US') || '0';
        },
        formatTime(dateString) {
            if (!dateString) return '';
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            return new Date(dateString).toLocaleString('en-US', options);
        },
        async checkAuth() {
            try {
                const response = await axios.get('/api/check-auth');
                this.currentUser = response.data;
                if (this.currentUser) this.loadData();
            } catch (error) {
                this.currentUser = null;
            }
        },
        async loadData() {
            await Promise.all([this.loadVehicles(), this.loadNotifications()]);
        },
        async loadVehicles() {
            try {
                const response = await axios.get('/api/vehicles');
                this.vehicles = response.data;
            } catch (error) {
                console.error('Failed to load vehicles:', error);
            }
        },
        async loadNotifications() {
            if (!this.currentUser) return;
            try {
                const response = await axios.get('/api/notifications');
                this.notifications = response.data;
            } catch (error) {
                console.error('Failed to load notifications:', error);
            }
        },
        async login() {
            try {
                const response = await axios.post('/api/login', this.loginData);
                this.currentUser = response.data;
                this.loginData = { username: '', password: '' };
                await this.loadData();
            } catch (error) {
                alert('Login failed: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async register() {
            try {
                await axios.post('/api/register', this.registerData);
                this.showRegister = false;
                this.registerData = { username: '', password: '', email: '' };
                alert('Registration successful! Please login.');
            } catch (error) {
                alert('Registration failed: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async logout() {
            try {
                await axios.post('/api/logout');
                this.currentUser = null;
                this.vehicles = [];
                this.notifications = [];
            } catch (error) {
                console.error('Logout failed:', error);
            }
        },
        async markNotificationRead(notificationId) {
            try {
                await axios.post(`/api/notifications/mark-read/${notificationId}`);
                this.notifications = this.notifications.filter(n => n.id !== notificationId);
            } catch (error) {
                console.error('Failed to mark notification as read:', error);
            }
        },
        async placeBid(vehicleId) {
            if (!this.bidAmounts[vehicleId] || this.bidAmounts[vehicleId] <= 0) {
                alert('Please enter a valid bid amount');
                return;
            }
            
            try {
                await axios.post('/api/bid', {
                    vehicle_id: vehicleId,
                    amount: parseFloat(this.bidAmounts[vehicleId])
                });
                this.bidAmounts[vehicleId] = '';
                alert('Bid placed successfully!');
                await this.loadVehicles();
            } catch (error) {
                alert('Failed to place bid: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async addVehicle() {
            try {
                await axios.post('/api/admin/vehicles', {
                    ...this.newVehicle
                });
                alert('Vehicle added successfully!');
                this.newVehicle = {
                    make: '',
                    model: '',
                    year: new Date().getFullYear(),
                    mileage: 0,
                    reserve_price: 0,
                    end_time: '',
                    description: ''
                };
                await this.loadVehicles();
            } catch (error) {
                alert('Failed to add vehicle: ' + (error.response?.data?.error || 'Unknown error'));
            }
        }
    }
}).mount('#app');
