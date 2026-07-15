<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const route = useRoute()
const companies = ref([])
const isLoading = ref(true)

// Compute search term directly from the URL
const searchQuery = computed(() => route.query.search || '')

const fetchCompanies = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/companies', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) companies.value = await response.json()
  } catch (error) { 
    console.error(error) 
  } finally { 
    isLoading.value = false 
  }
}

onMounted(() => fetchCompanies())

const approveCompany = async (id) => {
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/approve_company/${id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) fetchCompanies()
  } catch (error) { 
    alert("Failed to approve.") 
  }
}

const toggleBlacklist = async (company) => {
  const action = company.is_blacklisted ? "restore" : "blacklist"
  if(!confirm(`Are you sure you want to ${action} ${company.name}?`)) return
  
  try {
    const res = await fetch(`http://127.0.0.1:5000/api/admin/blacklist_company/${company.id}`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (res.ok) fetchCompanies()
  } catch (error) { 
    alert("Failed to update status.") 
  }
}

const filteredCompanies = computed(() => {
  if (!searchQuery.value) return companies.value
  
  const q = searchQuery.value.toLowerCase()
  return companies.value.filter(c => 
    c.name.toLowerCase().includes(q) || 
    (c.email && c.email.toLowerCase().includes(q))
  )
})
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Manage Companies</h2>
        <p class="text-white-50 mb-0">Approve registrations and manage recruiter access.</p>
      </div>
    </div>

    <div class="container pt-4 pb-5">
      
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      
      <!-- TABLE VIEW (Simplified to match Student Directory) -->
      <div v-else class="card border-0 shadow-sm">
        <div class="card-body p-0">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th class="ps-4 py-3 text-secondary small border-bottom-0">Company Name</th>
                <th class="py-3 text-secondary small border-bottom-0">Contact Info</th>
                <th class="py-3 text-secondary small border-bottom-0">Status</th>
                <th class="pe-4 text-end text-secondary small border-bottom-0">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in filteredCompanies" :key="company.id" :class="{'opacity-50': company.is_blacklisted}">
                <td class="ps-4 fw-bold">{{ company.name }}</td>
                <td>
                  <div class="small">{{ company.hr_contact }}</div>
                  <div class="small text-muted">{{ company.email }}</div>
                </td>
                <td>
                  <span v-if="!company.is_approved" class="badge bg-warning text-dark">Pending</span>
                  <span v-else-if="company.is_blacklisted" class="badge bg-danger">Blacklisted</span>
                  <span v-else class="badge bg-success">Approved</span>
                </td>
                <td class="text-end pe-4">
                  <button v-if="!company.is_approved" @click="approveCompany(company.id)" class="btn btn-sm btn-primary me-2">Approve</button>
                  <button @click="toggleBlacklist(company)" class="btn btn-sm" :class="company.is_blacklisted ? 'btn-outline-success' : 'btn-outline-danger'">
                    {{ company.is_blacklisted ? 'Restore' : 'Blacklist' }}
                  </button>
                </td>
              </tr>
              
              <tr v-if="filteredCompanies.length === 0">
                <td colspan="4" class="text-center py-5 text-muted">
                  <i class="bi bi-building display-4 opacity-25 d-block mb-3"></i>
                  No companies match your criteria.
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
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);}
</style>