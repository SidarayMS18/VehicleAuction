const { createApp } = Vue;

createApp({
    data() {
        return {
            currentUser: null,
            loginData: { username: '', password: '' },
            registerData: { username: '', password: '', email: '' },
            vehicles: [],
            bidAmounts: {},
            newVehicle: {
                make: '',
                model: '',
                year: new Date().getFullYear(),
                mileage: 0,
                reserve_price: 0,
                end_time: ''
            },
            profile: {},
            showRegister: false,
            showFundsModal: false
        }
    },
    computed: {
        formattedVehicles() {
            return this.vehicles.map(v => ({
                ...v,
                end_time: new Date(v.end_time).toLocaleString()
            }))
        }
    },
    mounted() {
        this.checkAuth();
    },
    methods: {
        async checkAuth() {
            try {
                const res = await axios.get('/api/check-auth');
                this.currentUser = res.data;
                if (this.currentUser) this.loadData();
            } catch (error) {
                this.currentUser = null;
            }
        },
        async loadData() {
            const [vehicles, profile] = await Promise.all([
                axios.get('/api/vehicles'),
                axios.get('/api/profile')
            ]);
            this.vehicles = vehicles.data;
            this.profile = profile.data;
        },
        async login() {
            try {
                const res = await axios.post('/api/login', this.loginData);
                this.currentUser = res.data;
                this.loginData = { username: '', password: '' };
                await this.loadData();
            } catch (error) {
                alert('Login failed');
            }
        },
        async register() {
            try {
                await axios.post('/api/register', this.registerData);
                this.showRegister = false;
                this.registerData = { username: '', password: '', email: '' };
                alert('Registration successful! Please login.');
            } catch (error) {
                alert('Registration failed');
            }
        },
        async logout() {
            await axios.post('/api/logout');
            this.currentUser = null;
            this.vehicles = [];
        },
        async addVehicle() {
            try {
                await axios.post('/api/admin/vehicles', this.newVehicle);
                this.newVehicle = {
                    make: '',
                    model: '',
                    year: new Date().getFullYear(),
                    mileage: 0,
                    reserve_price: 0,
                    end_time: ''
                };
                await this.loadData();
                alert('Vehicle added!');
            } catch (error) {
                alert('Error adding vehicle');
            }
        },
        async placeBid(vehicleId) {
            try {
                await axios.post('/api/bid', {
                    vehicle_id: vehicleId,
                    amount: this.bidAmounts[vehicleId]
                });
                this.bidAmounts[vehicleId] = '';
                await this.loadData();
                alert('Bid placed!');
            } catch (error) {
                alert('Bid failed');
            }
        },
        toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
        }
    }
}).mount('#app');
