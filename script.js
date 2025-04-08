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
            },
            deleteVehicleId: '',
            // Data for vehicle editing
            editVehicleId: '',
            showEditVehicle: false,
            editVehicleData: {
                make: '',
                model: '',
                year: '',
                mileage: '',
                reserve_price: '',
                end_time: '',
                description: ''
            },
            // Data for marking a vehicle as sold
            markSoldVehicleId: '',
            // Extra user-specific properties
            profile: null,
            showFundsModal: false,
            addFundsAmount: 0,
            userBids: [],
            // For admin: user management
            users: [],
            isLoading: false
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
            this.isLoading = true;
            await Promise.all([this.loadVehicles(), this.loadNotifications()]);
            if (!this.currentUser.is_admin) {
                this.loadProfile();
                this.loadUserBids();
            }
            this.isLoading = false;
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
            
            const amount = parseFloat(this.bidAmounts[vehicleId]);
            this.bidAmounts[vehicleId] = ''; // Reset early
            try {
                await axios.post('/api/bid', {
                    vehicle_id: vehicleId,
                    amount
                });
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
        },
        async deleteVehicle() {
            if (!this.deleteVehicleId) {
                alert('Please enter a valid Vehicle ID to delete.');
                return;
            }
            try {
                await axios.post(`/api/admin/vehicles/delete/${this.deleteVehicleId}`);
                alert('Vehicle deleted successfully!');
                this.deleteVehicleId = '';
                await this.loadVehicles();
            } catch (error) {
                alert('Failed to delete vehicle: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async editVehicle(vehicleId) {
            try {
                await axios.post(`/api/admin/vehicles/edit/${vehicleId}`, {
                    ...this.editVehicleData
                });
                alert('Vehicle updated successfully!');
                this.showEditVehicle = false;
                this.editVehicleId = '';
                this.editVehicleData = {
                    make: '',
                    model: '',
                    year: '',
                    mileage: '',
                    reserve_price: '',
                    end_time: '',
                    description: ''
                };
                await this.loadVehicles();
            } catch (error) {
                alert('Failed to update vehicle: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async markVehicleSold() {
            if (!this.markSoldVehicleId) {
                alert('Please enter a valid Vehicle ID.');
                return;
            }
            try {
                await axios.post(`/api/admin/vehicles/mark-sold/${this.markSoldVehicleId}`);
                alert('Vehicle marked as sold!');
                this.markSoldVehicleId = '';
                await this.loadVehicles();
            } catch (error) {
                alert('Failed to mark vehicle as sold: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        async loadProfile() {
            try {
                const res = await axios.get('/api/profile');
                this.profile = res.data;
            } catch (error) {
                console.error('Error loading profile:', error);
            }
        },
        async loadUserBids() {
            try {
                const res = await axios.get('/api/profile/bids');
                this.userBids = res.data;
            } catch (error) {
                console.error('Error loading bids:', error);
            }
        },
        async addFunds() {
            try {
                const res = await axios.post('/api/profile/add-funds', { amount: this.addFundsAmount });
                alert('Funds added! New Balance: $' + res.data.new_balance);
                this.profile.balance = res.data.new_balance;
                this.addFundsAmount = 0;
                this.showFundsModal = false;
            } catch (error) {
                alert('Failed to add funds: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        // Admin: Load users for management
        async loadUsers() {
            try {
                const res = await axios.get('/api/admin/users');
                this.users = res.data;
            } catch (error) {
                alert('Failed to load users: ' + (error.response?.data?.error || 'Unknown error'));
            }
        },
        // Toggle dark mode
        toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        },
        // (Optional) Open edit user modal – implementation details depend on your design.
        openEditUser(user) {
            // Example: Implement a modal to edit user details.
            alert(`Edit user ${user.username} (functionality to be implemented)`);
        }
    }
}).mount('#app');
