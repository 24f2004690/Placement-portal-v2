<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import StudentNavBar from '../../components/StudentNavBar.vue'

const route = useRoute()
const userName = ref('Student')
const isLoading = ref(true)
const availableDrives = ref([])
const showModal = ref(false)
const selectedDrive = ref(null)
const isApplying = ref(false)

const searchQuery = computed(() => route.query.search || '')

const fetchDrives = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/drives', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      availableDrives.value = await response.json()
    }
  } catch (error) {
    console.error("Error fetching drives:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  const storedName = localStorage.getItem('name')
  if (storedName) userName.value = storedName.split(' ')[0]
  fetchDrives()
})

const openDriveDetails = (drive) => {
  selectedDrive.value = drive
  showModal.value = true
}

const applyForDrive = async () => {
  isApplying.value = true
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/apply', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ drive_id: selectedDrive.value.id })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || "Failed to apply.")
    }

    alert(data.message)
    showModal.value = false
    // Refresh to show status change locally
    fetchDrives() 
  } catch (error) {
    alert(error.message)
  } finally {
    isApplying.value = false
  }
}

const filteredDrives = computed(() => {
  if (!searchQuery.value) return availableDrives.value
  const q = searchQuery.value.toLowerCase()
  return availableDrives.value.filter(d => 
    d.title.toLowerCase().includes(q) || 
    d.company.toLowerCase().includes(q)
  )
})
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5">
      <StudentNavBar />
      <div class="container pt-4 pb-5">
        <h1 class="display-5 fw-bold text-white">Hello, {{ userName }}!</h1>
        <p class="lead text-white-50">Explore and apply for upcoming placement drives.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      <div class="card border-0 shadow-sm p-4 mb-4 d-flex flex-row justify-content-between align-items-center">
        <h5 class="fw-bold mb-0 text-dark"><i class="bi bi-briefcase-fill text-primary me-2"></i>Active Opportunities</h5>
        <span v-if="searchQuery" class="badge bg-primary-subtle text-primary border border-primary-subtle rounded-pill px-3 py-2 shadow-sm">
          Filtered: {{ searchQuery }}
        </span>
      </div>

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else class="row g-4">
        <div v-for="drive in filteredDrives" :key="drive.id" class="col-md-6 col-lg-4">
          <div class="card border-0 shadow-sm h-100 hover-card cursor-pointer" @click="openDriveDetails(drive)">
            <div class="card-body p-4 d-flex flex-column">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div class="avatar-box bg-primary-subtle text-primary fw-bold fs-4 rounded-3 d-flex align-items-center justify-content-center" style="width: 50px; height: 50px;">
                  {{ drive.company.charAt(0) }}
                </div>
                <span class="badge bg-light border text-secondary"><i class="bi bi-clock me-1"></i>{{ drive.deadline }}</span>
              </div>
              
              <h5 class="fw-bold text-dark mb-1">{{ drive.title }}</h5>
              <h6 class="text-primary fw-bold mb-3">{{ drive.company }}</h6>
              
              <div class="mt-auto bg-light p-2 rounded small text-muted">
                <i class="bi bi-mortarboard me-2"></i>{{ drive.eligibility || 'No specific criteria' }}
              </div>
            </div>
          </div>
        </div>

        <div v-if="filteredDrives.length === 0" class="col-12 text-center text-muted py-5 bg-white rounded shadow-sm">
          <i class="bi bi-folder-x display-4 opacity-25"></i>
          <p class="mt-3">No active placement drives match your criteria.</p>
        </div>
      </div>
    </div>

    <!-- Application Modal -->
    <div v-if="showModal && selectedDrive" class="modal-backdrop-custom d-flex align-items-center justify-content-center" @click.self="showModal = false">
      <div class="modal-content-custom bg-white rounded-4 shadow-lg p-4" style="max-width: 550px; width: 90%;">
        
        <div class="d-flex justify-content-between align-items-center mb-4 pb-3 border-bottom">
          <div class="d-flex align-items-center gap-3">
            <div class="bg-primary text-white rounded d-flex align-items-center justify-content-center fw-bold fs-4" style="width: 45px; height: 45px;">
              {{ selectedDrive.company.charAt(0) }}
            </div>
            <div>
              <h5 class="fw-bold mb-0 text-dark">{{ selectedDrive.title }}</h5>
              <div class="text-primary fw-bold small">{{ selectedDrive.company }}</div>
            </div>
          </div>
          <button @click="showModal = false" class="btn-close"></button>
        </div>

        <div class="mb-4">
          <h6 class="fw-bold text-secondary small text-uppercase">Role Description</h6>
          <p class="text-dark bg-light p-3 rounded border border-light-subtle" style="white-space: pre-wrap;">{{ selectedDrive.desc }}</p>
        </div>

        <div class="row mb-4">
          <div class="col-6">
            <h6 class="fw-bold text-secondary small text-uppercase">Eligibility</h6>
            <div class="fw-medium text-dark">{{ selectedDrive.eligibility || 'N/A' }}</div>
          </div>
          <div class="col-6">
            <h6 class="fw-bold text-secondary small text-uppercase">Apply By</h6>
            <div class="fw-medium text-danger"><i class="bi bi-calendar me-1"></i>{{ selectedDrive.deadline }}</div>
          </div>
        </div>

        <div class="alert alert-info border-0 small d-flex align-items-center mb-4">
          <i class="bi bi-info-circle-fill me-2 fs-5"></i>
          <div>Your profile details (CGPA, Branch, Resumé) will be automatically securely submitted.</div>
        </div>

        <div class="d-flex gap-2">
          <button type="button" @click="showModal = false" class="btn btn-light flex-grow-1 fw-bold rounded-pill py-2">Close</button>
          
          <button v-if="selectedDrive.has_applied" 
                  @click="$router.push('/student-applications')" 
                  class="btn btn-secondary flex-grow-1 fw-bold rounded-pill py-2 shadow-sm">
            View Status
          </button>
          
          <button v-else 
                  @click="applyForDrive" 
                  class="btn btn-primary flex-grow-1 fw-bold rounded-pill py-2 shadow-sm" 
                  :disabled="isApplying">
            {{ isApplying ? 'Submitting Application...' : '1-Click Apply' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem; }
.mt-n5 { margin-top: -4rem; }
.hover-card { transition: transform 0.2s, box-shadow 0.2s; border-radius: 12px; border: 1px solid #f8f9fa; }
.hover-card:hover { transform: translateY(-4px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.08) !important; border-color: #e2e8f0; }
.cursor-pointer { cursor: pointer; }

.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1050; backdrop-filter: blur(2px); }
.modal-content-custom { position: relative; z-index: 1060; animation: scaleIn 0.2s ease-out; }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>