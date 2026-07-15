<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import StudentNavBar from '../../components/StudentNavBar.vue'

const route = useRoute()
const applications = ref([])
const isLoading = ref(true)
const isExporting = ref(false)
const exportStatus = ref('')

const searchQuery = computed(() => route.query.search || '')

const fetchApplications = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/student/applications', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) applications.value = await response.json()
  } catch (error) {
    console.error("Error fetching applications:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => fetchApplications())

const getStatusBadge = (status) => {
  const map = {
    'Applied': 'bg-secondary-subtle text-secondary border-secondary-subtle',
    'Shortlisted': 'bg-primary-subtle text-primary border-primary-subtle',
    'Interview Scheduled': 'bg-warning-subtle text-warning border-warning-subtle',
    'Selected': 'bg-success text-white',
    'Rejected': 'bg-danger-subtle text-danger border-danger-subtle'
  }
  return map[status] || 'bg-light text-dark'
}

const filteredApplications = computed(() => {
  if (!searchQuery.value) return applications.value
  const q = searchQuery.value.toLowerCase()
  return applications.value.filter(app => 
    app.title.toLowerCase().includes(q) || 
    app.company.toLowerCase().includes(q)
  )
})

// --- ASYNC EXPORT LOGIC ---
const exportApplications = async () => {
  isExporting.value = true
  exportStatus.value = 'Starting background job...'
  
  try {
    // 1. Trigger the job
    const triggerRes = await fetch('http://127.0.0.1:5000/api/student/export_applications', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    const { task_id } = await triggerRes.json()

    // 2. Poll for completion every 1 second
    const pollInterval = setInterval(async () => {
      const statusRes = await fetch(`http://127.0.0.1:5000/api/tasks/${task_id}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      const taskData = await statusRes.json()
      
      exportStatus.value = `Status: ${taskData.state}...`

      if (taskData.state === 'SUCCESS') {
        clearInterval(pollInterval)
        exportStatus.value = 'Download Ready!'
        
        // 3. Trigger automatic download
        const filename = taskData.result.filename
        const downloadUrl = `http://127.0.0.1:5000/uploads/${filename}`
        const link = document.createElement('a')
        link.href = downloadUrl
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        setTimeout(() => { isExporting.value = false; exportStatus.value = '' }, 2000)
      } else if (taskData.state === 'FAILURE') {
        clearInterval(pollInterval)
        alert('Export failed.')
        isExporting.value = false
      }
    }, 1000)
    
  } catch (error) {
    alert("An error occurred while starting the export.")
    isExporting.value = false
  }
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <StudentNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">My Applications</h2>
        <p class="text-white-50 mb-0">Track the status of your placement applications.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      
      <div class="d-flex justify-content-between align-items-end mb-3">
        <!-- Async Export Button -->
        <button @click="exportApplications" class="btn btn-white bg-white border shadow-sm rounded-pill fw-bold text-primary px-4 py-2 d-flex align-items-center gap-2" :disabled="isExporting">
          <i v-if="!isExporting" class="bi bi-cloud-download fs-5"></i>
          <span v-else class="spinner-border spinner-border-sm" role="status"></span>
          {{ isExporting ? exportStatus : 'Export CSV' }}
        </button>

        <span v-if="searchQuery" class="badge bg-white text-primary border shadow-sm px-3 py-2 rounded-pill d-flex align-items-center gap-2">
          Search: {{ searchQuery }}
        </span>
      </div>

      <div class="card border-0 shadow-sm rounded-4 overflow-hidden">
        
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Company & Role</th>
                <th class="py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Applied On</th>
                <th class="pe-4 text-end text-secondary small text-uppercase fw-bold border-bottom-0">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="app.id">
                <td class="ps-4 py-3">
                  <div class="fw-bold text-dark fs-6">{{ app.company }}</div>
                  <div class="small text-muted mb-2">{{ app.title }}</div>
                  <!-- Interview Details (NEW) -->
                  <div v-if="app.status === 'Interview Scheduled' && app.interview_date" class="small mt-2 p-2 bg-warning-subtle rounded border border-warning-subtle text-dark d-inline-block">
                      <i class="bi bi-calendar-check me-1"></i> 
                       <strong>Scheduled:</strong> {{ app.interview_date }}
                  </div>
                  <div v-if="app.remarks" class="small text-dark bg-light p-2 rounded mt-1 border border-light-subtle" style="white-space: pre-wrap;">
                    <i class="bi bi-info-circle text-primary me-1"></i> {{ app.remarks }}
                  </div>
                </td>
                <td><span class="text-muted fw-medium">{{ app.date }}</span></td>
                <td class="text-end pe-4 align-top pt-4">
                  <span class="badge rounded-pill px-3 py-2 border" :class="getStatusBadge(app.status)">
                    {{ app.status }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredApplications.length === 0">
                <td colspan="3" class="text-center py-5 text-muted">
                  <i class="bi bi-inbox display-4 opacity-25 d-block mb-3"></i>
                  <p class="mt-2">No applications found.</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem; }
.mt-n5 { margin-top: -4rem; }
</style>