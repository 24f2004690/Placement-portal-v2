<script setup>
import { ref, onMounted, computed } from 'vue'
import AdminNavBar from '../../components/AdminNavBar.vue'

const drives = ref([])
const isLoading = ref(true)

// Modal State
const showModal = ref(false)
const selectedDrive = ref(null)

const fetchDrives = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/drives', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      drives.value = await response.json()
    }
  } catch (error) { 
    console.error("Error fetching drives:", error) 
  } finally { 
    isLoading.value = false 
  }
}

const approveDrive = async (id) => {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/approve_drive/${id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) fetchDrives()
  } catch (error) { 
    alert("Failed to approve drive.") 
  }
}

const rejectDrive = async (id) => {
  if(!confirm("Are you sure you want to reject this placement drive?")) return
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/reject_drive/${id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) fetchDrives()
  } catch (error) { 
    alert("Failed to reject drive.") 
  }
}

const viewDrive = (drive) => {
  selectedDrive.value = drive
  showModal.value = true
}

const sortedDrives = computed(() => {
  return [...drives.value].sort((a, b) => {
    if (a.status === 'Pending' && b.status !== 'Pending') return -1
    if (a.status !== 'Pending' && b.status === 'Pending') return 1
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

onMounted(() => {
  fetchDrives()
})
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Placement Drives</h2>
        <p class="text-white-50 mb-0">Review and manage active recruitment events from companies.</p>
      </div>
    </div>

    <div class="container pt-4 pb-5">

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 text-secondary small border-bottom-0">Company & Role</th>
                <th class="py-3 text-secondary small border-bottom-0">Deadline</th>
                <th class="py-3 text-secondary small border-bottom-0">Status</th>
                <th class="pe-4 text-end text-secondary small border-bottom-0">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in sortedDrives" :key="drive.id">
                <td class="ps-4 py-3">
                  <div class="fw-bold text-dark">{{ drive.company }}</div>
                  <div class="small text-muted">{{ drive.job_title }}</div>
                </td>
                <td>
                  <span class="fw-medium text-danger">
                    <i class="bi bi-calendar me-1"></i>{{ drive.deadline }}
                  </span>
                </td>
                <td>
                  <span class="badge px-3 py-2 border rounded-pill" 
                        :class="{
                          'bg-success-subtle text-success border-success-subtle': drive.status === 'Approved',
                          'bg-warning-subtle text-warning border-warning-subtle': drive.status === 'Pending',
                          'bg-danger-subtle text-danger border-danger-subtle': drive.status === 'Rejected'
                        }">
                    {{ drive.status }}
                  </span>
                </td>
                <td class="text-end pe-4">
                  <button @click="viewDrive(drive)" class="btn btn-sm btn-light text-primary shadow-sm fw-bold px-3 me-2">
                    View
                  </button>
                  
                  <div v-if="drive.status === 'Pending'" class="d-inline-flex gap-2">
                    <button @click="approveDrive(drive.id)" class="btn btn-sm btn-primary shadow-sm fw-bold px-3">
                      Approve
                    </button>
                    <button @click="rejectDrive(drive.id)" class="btn btn-sm btn-outline-danger shadow-sm fw-bold px-3">
                      Reject
                    </button>
                  </div>
                  
                  <span v-else-if="drive.status === 'Approved'" class="text-muted small">
                    <i class="bi bi-check-circle-fill text-success me-1"></i>Active
                  </span>
                  
                  <span v-else class="text-muted small">
                    <i class="bi bi-x-circle-fill text-danger me-1"></i>Closed
                  </span>
                </td>
              </tr>
              <tr v-if="drives.length === 0">
                <td colspan="4" class="text-center py-5 text-muted">
                  <i class="bi bi-folder-x display-4 opacity-25 d-block mb-3"></i>
                  No placement drives found in the system.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Admin Drive Details Modal -->
    <div v-if="showModal && selectedDrive" class="modal-backdrop-custom d-flex align-items-center justify-content-center">
      <div class="modal-content-custom bg-white rounded-4 shadow-lg p-4" style="max-width: 550px; width: 90%;">
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
          <h5 class="fw-bold mb-0 text-dark">Placement Drive Details</h5>
          <button @click="showModal = false" class="btn-close"></button>
        </div>
        
        <div class="mb-3">
          <label class="small text-muted fw-bold text-uppercase">Company</label>
          <div class="fw-bold fs-5 text-primary">{{ selectedDrive.company }}</div>
        </div>
        
        <div class="mb-3">
          <label class="small text-muted fw-bold text-uppercase">Job Role / Title</label>
          <div class="fw-medium text-dark fs-6">{{ selectedDrive.job_title }}</div>
        </div>
        
        <div class="row mb-3">
          <div class="col-12">
            <label class="small text-muted fw-bold text-uppercase">Eligibility Criteria</label>
            <div class="bg-light p-3 rounded-3 small border border-light-subtle">
              {{ selectedDrive.eligibility || 'Not specified' }}
            </div>
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-12">
            <label class="small text-muted fw-bold text-uppercase">Job Description & Package</label>
            <div class="bg-light p-3 rounded-3 small border border-light-subtle" style="white-space: pre-wrap;">
              {{ selectedDrive.desc || 'Not specified' }}
            </div>
          </div>
        </div>
        
        <div class="d-flex justify-content-end">
          <button @click="showModal = false" class="btn btn-primary fw-bold rounded-pill px-5 shadow-sm">Close</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);}

/* Modal styling */
.modal-backdrop-custom { 
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  background: rgba(0,0,0,0.6); 
  z-index: 1050; 
  backdrop-filter: blur(2px); 
}
.modal-content-custom { 
  position: relative; 
  z-index: 1060; 
  animation: scaleIn 0.2s ease-out; 
}

@keyframes scaleIn { 
  from { transform: scale(0.95); opacity: 0; } 
  to { transform: scale(1); opacity: 1; } 
}
</style>