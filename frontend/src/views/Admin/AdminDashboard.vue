<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminNavBar from '../../components/AdminNavBar.vue'

const router = useRouter()
const stats = ref({ students: 0, companies: 0, pending_companies: 0, active_drives: 0 })
const isLoading = ref(true)

const quickAccess = [
  { title: 'Manage Companies', desc: 'Approve & blacklist recruiters', icon: 'bi-building', color: 'text-primary', bg: 'bg-primary-subtle', route: '/admin/companies' },
  { title: 'Placement Drives', desc: 'Review & approve job postings', icon: 'bi-briefcase-fill', color: 'text-success', bg: 'bg-success-subtle', route: '/admin/drives' },
  { title: 'Student Directory', desc: 'Manage registered students', icon: 'bi-mortarboard-fill', color: 'text-warning', bg: 'bg-warning-subtle', route: '/admin/students' },
  { title: 'Placement Reports', desc: 'View hiring statistics', icon: 'bi-graph-up-arrow', color: 'text-danger', bg: 'bg-danger-subtle', route: '/admin/reports' },
]

const fetchStats = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/stats', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    if (response.ok) stats.value = await response.json()
  } catch (error) { console.error("Error loading stats:", error) } 
  finally { isLoading.value = false }
}

onMounted(() => { fetchStats() })
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5">
      <AdminNavBar />
      <div class="container pb-5 mb-5 pt-4">
        <h1 class="display-5 text-white fw-bold">Placement Cell Dashboard</h1>
        <p class="lead text-white opacity-75">Manage companies, students, and recruitment drives.</p>
      </div>
    </div>

    <div class="container mt-n5">
      <div class="row g-4 mb-5">
        
        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-warning">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Registered Students</h6>
                <h3 class="fw-bold mb-0">{{ isLoading ? '...' : stats.students }}</h3>
              </div>
              <div class="icon-box bg-warning-subtle text-warning"><i class="bi bi-mortarboard fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-primary">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Registered Companies</h6>
                <h3 class="fw-bold mb-0">{{ isLoading ? '...' : stats.companies }}</h3>
              </div>
              <div class="icon-box bg-primary-subtle text-primary"><i class="bi bi-building fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-danger">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Pending Approvals</h6>
                <h3 class="fw-bold mb-0 text-danger">{{ isLoading ? '...' : stats.pending_companies }}</h3>
              </div>
              <div class="icon-box bg-danger-subtle text-danger"><i class="bi bi-exclamation-circle fs-4"></i></div>
            </div>
          </div>
        </div>

        <div class="col-md-3">
          <div class="card border-0 shadow-sm h-100 border-start border-4 border-success">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-muted mb-1">Active Drives</h6>
                <h3 class="fw-bold mb-0">{{ isLoading ? '...' : stats.active_drives }}</h3>
              </div>
              <div class="icon-box bg-success-subtle text-success"><i class="bi bi-briefcase fs-4"></i></div>
            </div>
          </div>
        </div>

      </div>

      <h4 class="fw-bold mb-4">Quick Actions</h4>
      <div class="row g-4 pb-5">
        <div v-for="item in quickAccess" :key="item.title" class="col-md-3">
          <div @click="router.push(item.route)" class="card border-0 shadow-sm h-100 hover-card text-center py-4 cursor-pointer">
            <div class="card-body">
              <div class="mb-3 rounded-circle d-inline-flex align-items-center justify-content-center" :class="item.bg" style="width: 60px; height: 60px;">
                <i :class="['bi fs-4', item.icon, item.color]"></i>
              </div>
              <h6 class="fw-bold text-dark mt-2">{{ item.title }}</h6>
              <p class="text-muted mb-0 small">{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); }
.mt-n5 { margin-top: -80px; }
.icon-box { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.hover-card:hover { transform: translateY(-5px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
.cursor-pointer { cursor: pointer; }
</style>