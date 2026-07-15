<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const route = useRoute()
const students = ref([])
const isLoading = ref(true)

// Filter State (Search is driven by Navbar)
const selectedBranches = ref([])
const selectedCgpa = ref(null)

// Compute search term directly from the URL
const searchQuery = computed(() => route.query.search || '')

onMounted(async () => {
  await fetchStudents()
})

const fetchStudents = async () => {
  isLoading.value = true
  try {
    const res = await fetch('http://127.0.0.1:5000/api/admin/students', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) students.value = await res.json()
  } catch (e) { 
    console.error(e) 
  } finally { 
    isLoading.value = false 
  }
}

const toggleBlacklist = async (student) => {
  const action = student.is_blacklisted ? "restore" : "blacklist"
  if(!confirm(`Are you sure you want to ${action} ${student.full_name}?`)) return
  
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/blacklist_student/${student.id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) fetchStudents()
  } catch (error) { 
    alert("Failed to update status.") 
  }
}

const availableBranches = computed(() => {
  const branches = new Set(students.value.map(s => s.branch).filter(Boolean))
  return Array.from(branches)
})

const activeFilterCount = computed(() => {
  let count = selectedBranches.value.length
  if (selectedCgpa.value) count++
  return count
})

const clearAllFilters = () => {
  selectedBranches.value = []
  selectedCgpa.value = null
}

const filteredStudents = computed(() => {
  return students.value.filter(s => {
    const matchesSearch = !searchQuery.value || 
      s.full_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
      (s.branch && s.branch.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    const matchesBranch = selectedBranches.value.length === 0 || selectedBranches.value.includes(s.branch)
    
    let matchesCgpa = true
    if (selectedCgpa.value) {
      const cgpaVal = parseFloat(s.cgpa) || 0
      matchesCgpa = cgpaVal >= selectedCgpa.value
    }

    return matchesSearch && matchesBranch && matchesCgpa
  })
})
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Student Directory</h2>
        <p class="text-white-50 mb-0">Manage registered candidates and track eligibility.</p>
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
          
          <div class="dropdown-menu dropdown-menu-end shadow-lg border-0 p-4 mt-2 rounded-4" style="width: 280px;">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="mb-0 fw-bold text-muted small">BRANCH</h6>
              <a href="#" @click.prevent="clearAllFilters" class="text-primary small text-decoration-none">Clear all</a>
            </div>
            
            <div class="mb-4">
              <div class="form-check mb-2" v-for="branch in availableBranches" :key="branch">
                <input class="form-check-input shadow-none cursor-pointer" type="checkbox" :value="branch" :id="branch" v-model="selectedBranches">
                <label class="form-check-label small cursor-pointer" :for="branch">{{ branch }}</label>
              </div>
            </div>

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

      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <!-- TABLE VIEW -->
      <div v-else class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 text-secondary small">Student Name</th>
                <th class="py-3 text-secondary small">Email</th>
                <th class="py-3 text-secondary small">Phone</th>
                <th class="py-3 text-secondary small">Academic</th>
                <th class="pe-4 text-end text-secondary small">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in filteredStudents" :key="student.id" :class="{'opacity-50': student.is_blacklisted}">
                <td class="ps-4 fw-bold">{{ student.full_name }}</td>
                <td><div class="small">{{ student.email }}</div></td>
                <td><div class="small text-muted">{{ student.phone || 'N/A' }}</div></td>
                <td>
                  <div class="small fw-medium text-dark">{{ student.branch || 'N/A' }}</div>
                  <div class="small text-muted">CGPA: {{ student.cgpa || 'N/A' }}</div>
                </td>
                <td class="text-end pe-4">
                  <button @click="toggleBlacklist(student)" 
                          class="btn btn-sm"
                          :class="student.is_blacklisted ? 'btn-outline-success' : 'btn-outline-danger'">
                    {{ student.is_blacklisted ? 'Restore' : 'Blacklist' }}
                  </button>
                </td>
              </tr>
              
              <tr v-if="filteredStudents.length === 0">
                <td colspan="5" class="text-center py-4 text-muted">
                  No students match your criteria.
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
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem !important; }
.mt-n5 { margin-top: -4rem !important; }
</style>