<script setup>
import { ref, onMounted } from 'vue'

const isLoggedIn = ref(false)
const userRole = ref('')
const userName = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  
  if (token) {
    try {
      // Ping the backend to ensure the user hasn't been deleted and token hasn't expired
      const response = await fetch('http://127.0.0.1:5000/api/verify_session', {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        // Only set them as logged in if the backend approves
        isLoggedIn.value = true
        userRole.value = localStorage.getItem('role')
        userName.value = localStorage.getItem('name') 
      }
      // Note: If response is 401, the global fetch interceptor in main.js 
      // will automatically handle wiping localStorage and refreshing!
    } catch (error) {
      console.error("Session verification failed:", error)
    }
  }
})

// Helper to determine where the dashboard button points based on CPMS roles
const getDashboardLink = () => {
  if (userRole.value === 'admin') return '/admin-dashboard'
  if (userRole.value === 'company') return '/recruiter-dashboard'
  return '/student-dashboard'
}

// Logic to clear session and refresh UI
const handleLogout = () => {
  localStorage.clear()
  window.location.reload() // Reloads page to show "Get Started" state
}
</script>

<template>
  <div>
    <div class="header-section text-white">
      <slot name="navbar"></slot> 
      
      <div class="container pt-5 pb-5 mb-5 text-center">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <h1 class="display-4 fw-bold mb-3">Manage Placements Effortlessly</h1>
            <p class="lead opacity-75 mb-5">Welcome to CPMS PlacementCell. The modern, secure way to manage student applications, placement drives, and recruiter interactions.</p>
          </div>
        </div>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-10">
          <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="row g-0 font-poppins">
              
              <div class="col-md-7 p-5 d-flex flex-column justify-content-center bg-white">
                
                <!-- Skeleton loader while verifying could go here, but fetch is usually instant -->
                <div v-if="isLoggedIn">
                   <h3 class="fw-bold text-primary mb-4">Welcome back, {{ userName }}!</h3>
                   <p class="text-muted mb-5">You are currently signed in as a <strong>{{ userRole }}</strong>. Continue to your dashboard to manage your account.</p>
                   <div class="d-flex gap-2 align-items-center">
                      <router-link :to="getDashboardLink()" class="btn btn-primary btn-lg rounded-pill px-5 fw-bold">
                        Go to Dashboard <i class="bi bi-arrow-right ms-2"></i>
                      </router-link>
                      
                      <button @click="handleLogout" class="btn btn-outline-danger btn-lg rounded-pill px-4 fw-bold ms-2">
                        Logout
                      </button>
                   </div>
                </div>

                <div v-else>
                  <h3 class="fw-bold text-primary mb-4">Get Started Today</h3>
                  <p class="text-muted mb-5">Are you a student looking for career opportunities or a recruiter seeking top talent? Please sign in or create an account to continue.</p>
                  <div class="d-flex gap-3 flex-wrap">
                    <router-link to="/login" class="btn btn-cstmbtn btn-lg rounded-pill px-5 fw-bold d-flex align-items-center gap-2">
                      <i class="bi bi-box-arrow-in-right"></i> Login
                    </router-link>
                    <router-link to="/register" class="btn btn-outline-primary btn-lg rounded-pill px-5 fw-bold d-flex align-items-center gap-2">
                      <i class="bi bi-person-plus"></i> Register
                    </router-link>
                  </div>
                </div>

              </div>

              <div class="col-md-5 bg-primary-subtle d-none d-md-flex align-items-center justify-content-center p-5">
                 <div class="text-center text-primary opacity-50">
                   <i class="bi bi-building display-1"></i>
                   <h5 class="fw-bold mt-3">CPMS PlacementCell</h5>
                 </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.header-section {
  background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
  padding-bottom: 70px;
}

.mt-n5 {
  margin-top: -150px;
}

.rounded-4 {
  border-radius: 1rem !important;
}

.btn-cstmbtn { background-color: #2c629e; color: #fff; }
.btn-cstmbtn:hover { background-color: #649ad1; color: #fff; }
</style>