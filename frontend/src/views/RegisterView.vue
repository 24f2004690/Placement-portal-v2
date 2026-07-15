<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoading = ref(false)
const errorMessage = ref('')

// Date picker shouldn't offer future dates
const maxDob = computed(() => new Date().toISOString().split('T')[0])

// Toggle between 'student' and 'company'
const registerRole = ref('student')

// Combined state for both roles
const form = ref({
  name: '',
  username: '',
  email: '',
  password: '',
  // Student specific
  phone: '',
  dob: '',
  branch: '',
  cgpa: '',
  // Company specific
  hr_contact: '',
  website: ''
})

const handleRegister = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  // Determine the endpoint based on selected role
  const endpoint = registerRole.value === 'company' 
    ? 'http://127.0.0.1:5000/api/register/company' 
    : 'http://127.0.0.1:5000/api/register/student'

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed')
    }

    if (registerRole.value === 'company') {
      alert('Company profile created! Please wait for Admin approval before logging in.')
    } else {
      alert('Student account created successfully! You can now log in.')
    }
    
    router.push('/login')

  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="brand-gradient min-vh-100 d-flex align-items-center justify-content-center position-relative py-5"> 
    
    <button 
      @click="$router.push('/')" 
      class="btn btn-link text-white text-decoration-none position-absolute top-0 start-0 m-4 fw-bold opacity-75"
      style="z-index: 10;"
    >
      <i class="bi bi-arrow-left me-1"></i> Back
    </button>

    <div class="container">
      <div class="row justify-content-center">
        
        <div class="col-12 col-md-8 col-lg-6 col-xl-6">
          
          <div class="card border-0 shadow-lg rounded-4 p-4 p-md-5">
            
            <div class="text-center mb-3">
              <div class="d-inline-flex align-items-center gap-2 mb-2">
                <span class="bg-primary text-white rounded px-2 py-1 fw-bold">CPMS</span>
                <span class="h5 mb-0 text-dark fw-bold">PlacementCell</span>
              </div>
              <h2 class="fw-bold text-dark fs-3">Create Account</h2>
              <p class="text-muted small">Join us to manage recruitment and placements.</p>
            </div>

            <!-- ROLE TOGGLE -->
            <div class="d-flex justify-content-center mb-4">
              <div class="btn-group bg-light p-1 rounded-pill border" role="group">
                <input type="radio" class="btn-check" name="role" id="role-student" value="student" v-model="registerRole">
                <label class="btn rounded-pill px-4" :class="registerRole === 'student' ? 'btn-primary shadow-sm fw-bold' : 'btn-light text-muted'" for="role-student">I am a Student</label>

                <input type="radio" class="btn-check" name="role" id="role-company" value="company" v-model="registerRole">
                <label class="btn rounded-pill px-4" :class="registerRole === 'company' ? 'btn-primary shadow-sm fw-bold' : 'btn-light text-muted'" for="role-company">I am a Company</label>
              </div>
            </div>

            <div v-if="errorMessage" class="alert alert-danger d-flex align-items-center small py-2" role="alert">
              <i class="bi bi-exclamation-circle-fill me-2"></i>
              <div>{{ errorMessage }}</div>
            </div>
            
            <form @submit.prevent="handleRegister">
              
              <!-- COMMON FIELDS -->
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">{{ registerRole === 'company' ? 'Company Name' : 'Full Name' }}</label>
                  <input type="text" class="form-control form-control-lg bg-light fs-6" v-model="form.name" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label small text-muted fw-bold">Username</label>
                  <input type="text" class="form-control form-control-lg bg-light fs-6" v-model="form.username" required>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label small text-muted fw-bold">Email Address</label>
                <input type="email" class="form-control form-control-lg bg-light fs-6" v-model="form.email" placeholder="name@example.com" required>
              </div>

              <!-- STUDENT SPECIFIC FIELDS -->
              <template v-if="registerRole === 'student'">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="form-label small text-muted fw-bold">Phone</label>
                    <input type="tel" class="form-control form-control-lg bg-light fs-6" v-model="form.phone" required>
                  </div>
                  <div class="col-md-6 mb-3">
                    <label class="form-label small text-muted fw-bold">Date of Birth</label>
                    <input type="date" class="form-control form-control-lg bg-light fs-6" v-model="form.dob" :max="maxDob" required>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-8 mb-3">
                    <label class="form-label small text-muted fw-bold">Branch / Degree</label>
                    <input type="text" class="form-control form-control-lg bg-light fs-6" v-model="form.branch" placeholder="e.g. B.Tech CS" required>
                  </div>
                  <div class="col-md-4 mb-3">
                    <label class="form-label small text-muted fw-bold">CGPA</label>
                    <input type="number" step="0.01" class="form-control form-control-lg bg-light fs-6" v-model="form.cgpa" placeholder="e.g. 8.5" required>
                  </div>
                </div>
              </template>

              <!-- COMPANY SPECIFIC FIELDS -->
              <template v-if="registerRole === 'company'">
                <div class="mb-3">
                  <label class="form-label small text-muted fw-bold">HR Contact Name</label>
                  <input type="text" class="form-control form-control-lg bg-light fs-6" v-model="form.hr_contact" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small text-muted fw-bold">Company Website (Optional)</label>
                  <input type="text" class="form-control form-control-lg bg-light fs-6" v-model="form.website" placeholder="www.example.com">
                </div>
              </template>

              <!-- COMMON PASSWORD -->
              <div class="mb-4">
                <label class="form-label small text-muted fw-bold">Password</label>
                <input type="password" class="form-control form-control-lg bg-light fs-6" v-model="form.password" placeholder="******" required>
              </div>

              <button type="submit" class="btn btn-primary w-100 py-2 fw-bold rounded-pill" :disabled="isLoading">
                {{ isLoading ? 'Processing...' : 'Sign Up' }}
              </button>

              <div class="text-center mt-3">
                <p class="text-muted small mb-0">
                  Already have an account? 
                  <router-link to="/login" class="text-primary text-decoration-none fw-bold">Log in</router-link>
                </p>
              </div>

            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.brand-gradient { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); }
.form-control { border: 1px solid #e2e8f0; }
.form-control:focus { box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.1); border-color: #0d6efd; background-color: #fff; }
.btn-primary { background-color: #0d6efd; border: none; transition: transform 0.3s ease, box-shadow 0.2s ease; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3); }
.card { animation: slideUp 0.5s ease-out; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>