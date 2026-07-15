<script setup>
import { ref, onMounted } from 'vue'
import StudentNavBar from '../../components/StudentNavBar.vue'

const profile = ref({
  full_name: '',
  username: '',
  email: '',
  phone: '',
  dob: '',
  branch: '',
  experience: '', // Added here for reactivity
  cgpa: '',
  resume_file: '' // Added here for reactivity
})
const isLoading = ref(false)
const isFetching = ref(true)

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/profile', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      const data = await response.json()
      profile.value = {
        full_name: data.full_name || '',
        username: data.username || '',
        email: data.email || '',
        phone: data.phone || '',
        dob: data.dob || '',
        branch: data.branch || '',
        experience: data.experience || '',
        cgpa: data.cgpa || '',
        resume_file: data.resume_file || ''
      }
      if (data.full_name) localStorage.setItem('name', data.full_name)
    }
  } catch (error) {
    console.error("Error fetching profile:", error)
  } finally {
    isFetching.value = false
  }
})

const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (file.type !== 'application/pdf') {
    alert("Please upload a PDF file.")
    return
  }

  const formData = new FormData()
  formData.append('resume', file)

  isLoading.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/upload_resume', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: formData 
    })
    
    const data = await response.json()
    if (response.ok) {
      alert("Resume uploaded successfully!")
      profile.value.resume_file = data.resume_file
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error("Upload failed", error)
    alert("Failed to upload resume.")
  } finally {
    isLoading.value = false
  }
}

const saveProfile = async () => {
  isLoading.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/profile', {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` 
      },
      body: JSON.stringify(profile.value)
    })
    
    if (response.ok) {
      alert("Profile updated securely! Your 1-Click apply data is up to date.")
      localStorage.setItem('name', profile.value.full_name)
    } else {
      const errorData = await response.json()
      alert(errorData.message || "Failed to update profile.")
    }
  } catch (error) {
    console.error("Error saving profile:", error)
    alert("An error occurred while saving.")
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <StudentNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">My Profile</h2>
        <p class="text-white-50 mb-0">Ensure your details are accurate for 1-Click applications.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5"> 
      
      <div v-if="isFetching" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      
      <div v-else class="row g-4">
        
        <!-- Left Section -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm rounded-4">
            <div class="card-body p-4 text-center">
              
              <div class="mx-auto mb-3 bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center fw-bold display-5 border border-4 border-white shadow-sm" 
                   style="width: 120px; height: 120px; margin-top: -60px;">
                {{ profile.full_name ? profile.full_name.charAt(0) : 'S' }}
              </div>
              
              <h5 class="fw-bold text-dark mb-1">{{ profile.full_name || 'Update your name' }}</h5>
              <p class="text-muted small mb-3">@{{ profile.username || 'username' }}</p>
              <span class="badge bg-primary px-3 py-2 rounded-pill shadow-sm">Verified Student</span>

              <hr class="w-100 my-4 text-muted opacity-25">

              <div class="text-start px-3 bg-light py-3 rounded mt-4 border border-light-subtle">
                <small class="text-uppercase text-muted fw-bold" style="font-size: 0.7rem;">Academic Status</small>
                <div class="d-flex align-items-center mt-3">
                  <i class="bi bi-book text-primary me-3 fs-5"></i>
                  <div class="fw-bold text-dark text-truncate">{{ profile.branch || 'Not set' }}</div>
                </div>
                <div class="d-flex align-items-center mt-3">
                  <i class="bi bi-star text-primary me-3 fs-5"></i>
                  <div>CGPA: <span class="fw-bold text-dark">{{ profile.cgpa || 'Not set' }}</span></div>
                </div>
                <div class="d-flex align-items-center mt-3" v-if="profile.experience">
                  <i class="bi bi-briefcase text-primary me-3 fs-5"></i>
                  <div>Exp: <span class="fw-bold text-dark">{{ profile.experience }}</span></div>
                </div>
              </div>
              
            </div>
          </div>
        </div>

        <!-- Right Section -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm rounded-4 h-100 d-flex flex-column">
            <div class="card-header bg-white border-0 py-4 px-4 pb-0">
              <h5 class="fw-bold text-dark mb-0">Update Details</h5>
            </div>
            <div class="card-body p-4 d-flex flex-column">
              <form @submit.prevent="saveProfile" class="d-flex flex-column h-100">
                
                <h6 class="fw-bold text-secondary mb-3 small text-uppercase">Personal Info</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Full Name</label>
                    <input type="text" class="form-control" v-model="profile.full_name" required>
                  </div>
                  <div class="col-md-6 mt-3 mt-md-0">
                    <label class="form-label small fw-bold text-muted">Username</label>
                    <input type="text" class="form-control bg-light text-muted" v-model="profile.username" disabled>
                  </div>
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Date of Birth</label>
                    <input type="date" class="form-control" v-model="profile.dob" disabled>
                  </div>
                  <div class="col-md-6 mt-3 mt-md-0">
                    <label class="form-label small fw-bold text-muted">Phone Number</label>
                    <input type="tel" class="form-control" v-model="profile.phone" required>
                  </div>
                </div>
                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Email Address</label>
                  <input type="email" class="form-control bg-light text-muted" v-model="profile.email" disabled>
                </div>

                <hr class="text-muted opacity-25 my-4">
                <h6 class="fw-bold text-secondary mb-3 small text-uppercase">Academic Info (Auto-Submitted)</h6>

                <div class="row mb-4">
                   <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Degree / Branch</label>
                    <input type="text" class="form-control" v-model="profile.branch" placeholder="e.g. B.Tech Computer Science" disabled>
                  </div>
                   <div class="col-md-6">
                    <label class="form-label small fw-bold text-muted">Experience</label>
                    <input type="text" class="form-control" v-model="profile.experience" placeholder="e.g. 2 years">
                  </div>
                </div>

               <hr class="text-muted opacity-25 my-4">
               <h6 class="fw-bold text-secondary mb-3 small text-uppercase">Resume Upload (PDF Only)</h6>

               <div class="row align-items-center mb-4">
                  <div class="col-md-8">
                      <input type="file" class="form-control" accept="application/pdf" @change="handleFileUpload">
                      <div class="small text-muted mt-1">Maximum file size: 5MB</div>
                  </div>
                     <div class="col-md-4 mt-3 mt-md-0 text-md-end">
                        <a v-if="profile.resume_file" 
                              :href="'http://127.0.0.1:5000/uploads/' + profile.resume_file" 
                               target="_blank" 
                               class="btn btn-outline-primary btn-sm rounded-pill fw-bold px-3 shadow-sm">
                              <i class="bi bi-file-earmark-pdf-fill me-1"></i> View Resume
                              </a>
                           <span v-else class="badge bg-light text-muted border px-3 py-2">No resume uploaded</span>
                    </div>
                   </div>

                <div class="d-flex justify-content-end gap-2 pt-4 mt-auto border-top">
                  <button type="submit" class="btn btn-primary px-5 py-2 fw-bold rounded-pill shadow-sm" :disabled="isLoading">
                    {{ isLoading ? 'Saving...' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem; }
.mt-n5 { margin-top: -4rem; }
</style>