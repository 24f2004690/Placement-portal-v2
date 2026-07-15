<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import RecruiterNavBar from '../../components/RecruiterNavBar.vue'

const route = useRoute()
const applications = ref([])
const isLoading = ref(true)

// URL-driven search
const searchQuery = computed(() => route.query.search || '')

// Filter State
const selectedStatuses = ref([])
const availableStatuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
const selectedBranches = ref([])
const selectedCgpa = ref(null)

// Modal State
const showModal = ref(false)
const selectedApp = ref(null)
const isUpdating = ref(false)
const updateForm = ref({ status: '', remarks: '', interview_date: '', interview_time: '' })

const minDate = new Date().toISOString().split('T')[0]

const fetchApplications = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/recruiter/applications', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      applications.value = await response.json()
    }
  } catch (error) { 
    console.error("Error fetching applications:", error) 
  } finally { 
    isLoading.value = false 
  }
}

onMounted(() => fetchApplications())

// Filter Logic
const availableBranches = computed(() => {
  const branches = new Set(applications.value.map(a => a.branch).filter(Boolean))
  return Array.from(branches)
})

const activeFilterCount = computed(() => {
  let count = selectedStatuses.value.length + selectedBranches.value.length
  if (selectedCgpa.value) count++
  return count
})

const clearAllFilters = () => { 
  selectedStatuses.value = []
  selectedBranches.value = []
  selectedCgpa.value = null
}

const filteredApplications = computed(() => {
  return applications.value.filter(app => {
    // 1. Search Query Match
    const matchesSearch = !searchQuery.value || 
      app.student_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
      app.drive_title.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    // 2. Status Match
    const matchesStatus = selectedStatuses.value.length === 0 || selectedStatuses.value.includes(app.status)
    
    // 3. Branch Match
    const matchesBranch = selectedBranches.value.length === 0 || selectedBranches.value.includes(app.branch)
    
    // 4. CGPA Match
    let matchesCgpa = true
    if (selectedCgpa.value) {
      const cgpaVal = parseFloat(app.cgpa) || 0
      matchesCgpa = cgpaVal >= selectedCgpa.value
    }
    
    return matchesSearch && matchesStatus && matchesBranch && matchesCgpa
  })
})

const openAppModal = (app) => {
  selectedApp.value = app
  updateForm.value = { 
    status: app.status, 
    remarks: app.remarks || '', 
    interview_date: '', 
    interview_time: '' 
  }
  showModal.value = true
}

const saveApplicationStatus = async () => {
  if (updateForm.value.status === 'Interview Scheduled' && updateForm.value.interview_date < minDate) {
    alert("Interview date cannot be set in the past.")
    return
  }

  isUpdating.value = true
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/recruiter/applications/${selectedApp.value.id}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` 
      },
      body: JSON.stringify(updateForm.value)
    })
    
    if (response.ok) {
      alert("Application successfully updated!")
      showModal.value = false
      fetchApplications()
    } else {
      alert("Failed to update application.")
    }
  } catch (error) {
    alert(error.message)
  } finally {
    isUpdating.value = false
  }
}

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
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <RecruiterNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Student Applications</h2>
        <p class="text-white-50 mb-0">Review candidates, schedule interviews, and update statuses.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      
      <!-- COMPACT FILTER BAR -->
      <div class="d-flex justify-content-end mb-4">
        <div class="dropdown">
          <button class="btn btn-white bg-white border shadow-sm rounded-pill px-3 py-2 fw-medium text-secondary dropdown-toggle d-flex align-items-center gap-2" 
                  type="button" data-bs-toggle="dropdown" data-bs-auto-close="outside">
            <i class="bi bi-filter text-muted fs-5"></i> 
            Filter
            <span v-if="activeFilterCount > 0" class="badge bg-primary rounded-circle ms-1">{{ activeFilterCount }}</span>
          </button>
          
          <div class="dropdown-menu dropdown-menu-end shadow-lg border-0 p-4 mt-2 rounded-4" style="width: 280px; max-height: 80vh; overflow-y: auto;">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0 fw-bold text-muted small">STATUS</h6>
              <a href="#" @click.prevent="clearAllFilters" class="text-primary small text-decoration-none">Clear all</a>
            </div>
            
            <div class="mb-4">
              <div class="form-check mb-2" v-for="status in availableStatuses" :key="status">
                <input class="form-check-input shadow-none cursor-pointer" type="checkbox" :value="status" :id="'status_' + status.replace(/\s+/g, '')" v-model="selectedStatuses">
                <label class="form-check-label small cursor-pointer" :for="'status_' + status.replace(/\s+/g, '')">{{ status }}</label>
              </div>
            </div>

            <!-- BRANCH FILTER -->
            <h6 class="mb-3 fw-bold text-muted small">BRANCH</h6>
            <div class="mb-4">
              <div class="form-check mb-2" v-for="branch in availableBranches" :key="branch">
                <input class="form-check-input shadow-none cursor-pointer" type="checkbox" :value="branch" :id="'branch_' + branch.replace(/\s+/g, '')" v-model="selectedBranches">
                <label class="form-check-label small cursor-pointer" :for="'branch_' + branch.replace(/\s+/g, '')">{{ branch }}</label>
              </div>
              <div v-if="availableBranches.length === 0" class="small text-muted mb-2">No branches available</div>
            </div>

            <!-- CGPA FILTER -->
            <h6 class="mb-3 fw-bold text-muted small">CGPA</h6>
            <div>
              <div class="form-check mb-2" v-for="val in [8.0, 7.0, 6.0, 5.0]" :key="val">
                <input class="form-check-input shadow-none cursor-pointer" type="radio" name="cgpaFilter" :value="val" :id="'cgpa'+val" v-model="selectedCgpa">
                <label class="form-check-label small cursor-pointer" :for="'cgpa'+val">&gt; {{ val.toFixed(1) }}</label>
              </div>
            </div>

          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm overflow-hidden rounded-4">
        
        <div v-if="isLoading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status"></div>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Candidate</th>
                <th class="py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Resume</th>
                <th class="py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Placement Drive</th>
                <th class="py-3 text-secondary small text-uppercase fw-bold border-bottom-0">Status</th>
                <th class="pe-4 text-end text-secondary small text-uppercase fw-bold border-bottom-0">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filteredApplications" :key="app.id" class="hover-row">
                <td class="ps-4 py-3">
                  <div class="fw-bold text-dark">{{ app.student_name }}</div>
                  <div class="small text-muted"><i class="bi bi-book me-1"></i>{{ app.branch }} | CGPA: <span class="fw-bold text-dark">{{ app.cgpa }}</span></div>
                </td>
                
                <td>
                  <a v-if="app.resume_file" 
                     :href="'http://127.0.0.1:5000/uploads/' + app.resume_file" 
                     target="_blank" 
                     class="btn btn-sm btn-outline-primary rounded-pill fw-bold px-3">
                     <i class="bi bi-file-earmark-pdf-fill me-1"></i> PDF
                  </a>
                  <span v-else class="text-muted small">N/A</span>
                </td>

                <td>
                   <div class="fw-medium text-dark">{{ app.drive_title }}</div>
                   <div class="small text-muted">{{ app.applied_on }}</div>
                </td>
                
                <td>
                  <span class="badge border rounded-pill px-3 py-2" :class="getStatusBadge(app.status)">
                    {{ app.status }}
                  </span>
                </td>
                <td class="text-end pe-4">
                  <button v-if="app.status !== 'Selected' && app.status !== 'Rejected'" 
                          @click="openAppModal(app)" 
                          class="btn btn-sm btn-primary shadow-sm fw-bold px-4 rounded-pill">
                    Process
                  </button>
                  <span v-else class="text-muted small fw-bold">
                    <i class="bi bi-check2-all me-1"></i>Processed
                  </span>
                </td>
              </tr>
              <tr v-if="filteredApplications.length === 0">
                <td colspan="5" class="text-center py-5 text-muted">
                  <i class="bi bi-filter-circle display-4 opacity-25 d-block mb-3"></i>
                  No applications match your criteria.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Process Application Modal -->
    <div v-if="showModal && selectedApp" class="modal-backdrop-custom d-flex align-items-center justify-content-center" @click.self="showModal = false">
      <div class="modal-content-custom bg-white rounded-4 shadow-lg p-4" style="max-width: 550px; width: 90%;">
        
        <div class="d-flex justify-content-between align-items-center mb-4 border-bottom pb-3">
          <div>
            <h5 class="fw-bold mb-0 text-dark">Process Application</h5>
            <small class="text-muted">{{ selectedApp.drive_title }}</small>
          </div>
          <button @click="showModal = false" class="btn-close"></button>
        </div>

        <div class="bg-light p-3 rounded-3 mb-4 border border-light-subtle d-flex justify-content-between align-items-center">
          <div>
            <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">Candidate</small>
            <div class="fw-bold text-dark fs-5">{{ selectedApp.student_name }}</div>
          </div>
          <div class="text-end">
            <small class="text-muted text-uppercase fw-bold" style="font-size: 0.7rem;">CGPA</small>
            <div class="fw-bold text-primary fs-5">{{ selectedApp.cgpa }}</div>
          </div>
        </div>

        <form @submit.prevent="saveApplicationStatus">
          <div class="mb-3">
            <label class="form-label small fw-bold text-muted text-uppercase">Update Status</label>
            <select class="form-select border-primary-subtle bg-light fw-medium" v-model="updateForm.status" required>
              <option value="Applied">Applied (Pending Review)</option>
              <option value="Shortlisted">Shortlist for Interview</option>
              <option value="Interview Scheduled">Interview Scheduled</option>
              <option value="Selected">Selected (Final Offer)</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>

          <div v-if="updateForm.status === 'Interview Scheduled'" class="row mb-3 p-3 bg-warning-subtle rounded-3 mx-0 border border-warning-subtle">
            <div class="col-md-6 mb-2 mb-md-0">
              <label class="form-label small fw-bold text-dark text-uppercase">Interview Date</label>
              <input type="date" class="form-control" v-model="updateForm.interview_date" :min="minDate" required>
            </div>
            <div class="col-md-6">
              <label class="form-label small fw-bold text-dark text-uppercase">Time</label>
              <input type="time" class="form-control" v-model="updateForm.interview_time" required>
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label small fw-bold text-muted text-uppercase">Remarks / Feedback</label>
            <textarea class="form-control" v-model="updateForm.remarks" rows="3" placeholder="Enter interview link, feedback, or internal notes..."></textarea>
          </div>

          <div class="d-flex gap-2">
            <button type="button" @click="showModal = false" class="btn btn-light flex-grow-1 fw-bold rounded-pill border">Cancel</button>
            <button type="submit" class="btn btn-primary flex-grow-1 fw-bold rounded-pill shadow-sm" :disabled="isUpdating">
              {{ isUpdating ? 'Saving...' : 'Save Update' }}
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem; }
.mt-n5 { margin-top: -4rem; }
.hover-row { transition: background-color 0.2s ease; }
.hover-row:hover { background-color: #f8f9fa; }

.modal-backdrop-custom { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1050; backdrop-filter: blur(2px); }
.modal-content-custom { position: relative; z-index: 1060; animation: scaleIn 0.2s ease-out; }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>