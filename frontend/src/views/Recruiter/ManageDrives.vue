<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import RecruiterNavBar from '../../components/RecruiterNavBar.vue'

const router = useRouter()
const route = useRoute()

// --- STATE ---
const drives = ref([])
const editingId = ref(null) 
const isLoading = ref(false)

const driveForm = ref({ title: '', desc: '', eligibility: '', deadline: '' })

// URL-driven search
const searchQuery = computed(() => route.query.search || '')

// --- FETCH DRIVES ---
const fetchMyDrives = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/recruiter/drives', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) {
      drives.value = await response.json()
    }
  } catch (error) { console.error("Error fetching drives:", error) }
}

onMounted(() => { fetchMyDrives() })

const minDate = new Date().toISOString().split('T')[0]

// Filter Logic
const filteredDrives = computed(() => {
  if (!searchQuery.value) return drives.value
  const q = searchQuery.value.toLowerCase()
  return drives.value.filter(d => 
    d.title.toLowerCase().includes(q) || 
    (d.eligibility && d.eligibility.toLowerCase().includes(q))
  )
})

// --- ACTIONS ---
const submitDrive = async () => {
  if (driveForm.value.deadline < minDate) {
    alert("Application deadline cannot be set in the past.")
    return
  }
  
  isLoading.value = true
  const isEdit = editingId.value !== null
  
  const url = isEdit 
    ? `http://127.0.0.1:5000/api/recruiter/drives/${editingId.value}`
    : 'http://127.0.0.1:5000/api/recruiter/drives'
    
  const method = isEdit ? 'PUT' : 'POST'

  try {
    const response = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(driveForm.value)
    })

    const result = await response.json()
    if (!response.ok) throw new Error(result.error || 'Failed to process request')

    alert(result.message)
    resetForm()
    fetchMyDrives()

  } catch (error) {
    alert(error.message)
  } finally {
    isLoading.value = false
  }
}

const editDrive = (driveData) => {
  editingId.value = driveData.id
  driveForm.value = {
    title: driveData.title,
    desc: driveData.desc,
    eligibility: driveData.eligibility,
    deadline: driveData.deadline
  }
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const deleteDrive = async (id) => {
  if(!confirm("Are you sure you want to delete this drive? All associated applications will be lost.")) return

  try {
    const response = await fetch(`http://127.0.0.1:5000/api/recruiter/drives/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) {
      alert("Drive deleted.")
      fetchMyDrives()
    } else {
      alert("Failed to delete.")
    }
  } catch (error) {
    alert(error.message)
  }
}

const resetForm = () => {
  driveForm.value = { title: '', desc: '', eligibility: '', deadline: '' }
  editingId.value = null
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <RecruiterNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Drive Management</h2>
        <p class="text-white-50 mb-0">Post new opportunities and manage existing listings.</p>
      </div>
    </div>

    <div class="container pt-4 pb-5">
      <div class="row g-4">
        
        <!-- LEFT PANE: Create/Edit Form -->
        <div class="col-lg-5">
          <div class="card border-0 shadow-sm sticky-top" style="top: 20px;">
            <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
              <h5 class="fw-bold text-primary mb-0">
                <i class="bi" :class="editingId ? 'bi-pencil-square' : 'bi-megaphone'"></i>
                {{ editingId ? 'Edit Placement Drive' : 'Post New Drive' }}
              </h5>
              <button v-if="editingId" @click="resetForm" class="btn btn-sm btn-light text-muted">Cancel</button>
            </div>
            <div class="card-body p-4">
              <form @submit.prevent="submitDrive">
                
                <div class="mb-3">
                  <label class="form-label small fw-bold text-muted">Job Title / Role</label>
                  <input type="text" class="form-control" v-model="driveForm.title" placeholder="e.g. Software Engineer" required>
                </div>

                <div class="mb-3">
                  <label class="form-label small fw-bold text-muted">Eligibility Criteria</label>
                  <input type="text" class="form-control" v-model="driveForm.eligibility" placeholder="e.g. B.Tech CS, CGPA > 7.5" required>
                </div>

                <div class="mb-3">
                  <label class="form-label small fw-bold text-muted">Application Deadline</label>
                  <input type="date" class="form-control" v-model="driveForm.deadline" :min="minDate" required>
                </div>

                <div class="mb-4">
                  <label class="form-label small fw-bold text-muted">Job Description & Package Details</label>
                  <textarea class="form-control" v-model="driveForm.desc" rows="5" placeholder="Describe the role, CTC, location..." required></textarea>
                </div>

                <button class="btn w-100 fw-bold py-2 shadow-sm rounded-pill" :class="editingId ? 'btn-warning text-dark' : 'btn-primary'" :disabled="isLoading">
                  {{ isLoading ? 'Processing...' : (editingId ? 'Update Drive' : 'Post Drive') }}
                </button>
              </form>
            </div>
          </div>
        </div>

        <!-- RIGHT PANE: Listed Drives -->
        <div class="col-lg-7">
          <div v-if="searchQuery" class="d-flex justify-content-end mb-3">
            <span class="badge bg-white text-primary border shadow-sm px-3 py-2 rounded-pill d-flex align-items-center gap-2">
              Search: {{ searchQuery }}
            </span>
          </div>

          <div class="card border-0 shadow-sm mb-4">
            <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
              <h5 class="fw-bold text-dark mb-0">My Posted Drives</h5>
            </div>
            
            <div class="card-body p-4">
              <div class="row g-3">
                <div v-for="drive in filteredDrives" :key="drive.id" class="col-12">
                  
                  <div class="card border-0 bg-lightc hover-card">
                    <div class="card-body p-3">
                      <div class="d-flex justify-content-between align-items-start">
                        
                        <div class="flex-grow-1">
                          <h6 class="fw-bold mb-1 text-dark">{{ drive.title }}</h6>
                          <div class="small text-muted mb-2"><i class="bi bi-mortarboard me-1"></i>{{ drive.eligibility }}</div>
                          
                          <div class="d-flex gap-2 align-items-center">
                            <span class="badge border rounded-pill px-3 py-2" :class="drive.status === 'Approved' ? 'bg-success-subtle text-success border-success-subtle' : drive.status === 'Rejected' ? 'bg-danger-subtle text-danger border-danger-subtle' : 'bg-warning-subtle text-warning border-warning-subtle'">
                              {{ drive.status }}
                            </span>
                            <span class="small text-muted"><i class="bi bi-calendar-event me-1"></i>Deadline: {{ drive.deadline }}</span>
                          </div>
                        </div>

                        <div class="d-flex flex-column gap-2 ms-3 border-start ps-3">
                          <button v-if="drive.status !== 'Approved'" @click="editDrive(drive)" class="btn btn-sm btn-light text-primary fw-bold w-100" title="Edit">
                            <i class="bi bi-pencil-square me-1"></i> Edit
                          </button>
                          
                          <button @click="router.push('/drive-applications')" class="btn btn-sm btn-primary fw-bold w-100 shadow-sm" title="View Apps">
                             View Apps
                          </button>

                          <button @click="deleteDrive(drive.id)" class="btn btn-sm btn-link text-danger p-0 mt-1" title="Delete">
                            <i class="bi bi-trash"></i> Delete
                          </button>
                        </div>

                      </div>
                    </div>
                  </div>

                </div>
                
                <div v-if="filteredDrives.length === 0" class="col-12 text-center text-muted py-5">
                  <i class="bi bi-filter-circle display-4 opacity-25 d-block mb-3"></i>
                  <p class="mt-3">No placement drives match your criteria.</p>
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
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); }

.bg-lightc { background-color: #f8f9fa; border: 1px solid #e9ecef !important; }
.hover-card { transition: transform 0.2s, box-shadow 0.2s; border-radius: 12px; }
.hover-card:hover { transform: translateY(-3px); box-shadow: 0 .25rem .75rem rgba(0,0,0,.05) !important; background-color: #ffffff; }
</style>