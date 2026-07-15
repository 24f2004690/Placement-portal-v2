<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const adminName = ref('Admin')
const searchQuery = ref('')
const searchResults = ref({})
const showResults = ref(false)
let debounceTimer = null

onMounted(() => {
  const storedName = localStorage.getItem('name')
  if (storedName) adminName.value = storedName
  
  // Populate the search bar if there's a search in the URL
  if (route.query.search) {
    searchQuery.value = route.query.search
  }
})

// Keep it synced if navigating around
watch(() => route.query.search, (newSearch) => {
  searchQuery.value = newSearch || ''
})

const handleSearch = () => {
  clearTimeout(debounceTimer)
  
  if (searchQuery.value.length < 2) {
    searchResults.value = {}
    showResults.value = false
    
    // If the user clears the search bar, remove the filter from the URL
    if (searchQuery.value === '' && route.query.search) {
      router.replace({ query: {} })
    }
    return
  }

  debounceTimer = setTimeout(async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/admin/global_search?q=${searchQuery.value}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (response.ok) {
        searchResults.value = await response.json()
        showResults.value = true
      }
    } catch (error) {
      console.error("Search failed", error)
    }
  }, 300)
}

const closeSearch = () => {
  setTimeout(() => { showResults.value = false }, 200)
}

const navigateToResult = (item) => {
  router.push({ path: item.route, query: { search: item.title } })
  searchQuery.value = ''
  showResults.value = false
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-transparent px-4 py-3">
    <div class="container-fluid">
      <router-link class="navbar-brand fw-bold d-flex align-items-center gap-2" to="/admin-dashboard">
        <span class="bg-white text-primary rounded px-2 py-0 fw-bolder">CPMS</span>
        PlacementCell <span class="badge bg-white text-primary ms-2 small" style="font-size: 0.7rem;">ADMIN</span>
      </router-link>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#adminNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="adminNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-4 gap-3">
          <li class="nav-item">
            <router-link class="nav-link fw-bold" to="/admin-dashboard" active-class="active">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/companies" active-class="fw-bold active">Manage Companies</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/drives" active-class="fw-bold active">Placement Drives</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/students" active-class="fw-bold active">Manage Students</router-link>
          </li>
        </ul>

        <!-- Global Search Bar -->
        <div class="position-relative ms-auto me-4 d-none d-lg-block" style="width: 300px;">
          <div class="input-group input-group-sm bg-white bg-opacity-25 rounded-pill overflow-hidden shadow-sm border border-white border-opacity-25">
            <span class="input-group-text bg-transparent border-0 pe-1 text-white"><i class="bi bi-search"></i></span>
            <input type="text" class="form-control border-0 shadow-none py-2 bg-transparent text-white custom-placeholder" 
                   placeholder="Search..." 
                   v-model="searchQuery" 
                   @input="handleSearch" 
                   @blur="closeSearch" 
                   @focus="handleSearch">
          </div>

          <!-- Dropdown Results -->
          <div v-if="showResults" class="position-absolute w-100 bg-white rounded-3 shadow-lg mt-2 overflow-hidden z-3" style="max-height: 400px; overflow-y: auto; text-align: left;">
            <template v-for="(items, category) in searchResults" :key="category">
              <div v-if="items.length > 0">
                <div class="bg-light px-3 py-2 small fw-bold text-muted text-uppercase" style="font-size: 0.7rem;">
                  {{ category }}
                </div>
                <div v-for="item in items" :key="item.id" 
                     @mousedown.prevent="navigateToResult(item)" 
                     class="px-3 py-2 border-bottom hover-result cursor-pointer text-decoration-none">
                  <div class="fw-bold text-dark small mb-0">{{ item.title }}</div>
                  <div class="text-muted" style="font-size: 0.75rem;">{{ item.subtitle }}</div>
                </div>
              </div>
            </template>
            
            <div v-if="Object.keys(searchResults).length === 0 || Object.values(searchResults).every(arr => arr.length === 0)" class="p-3 text-center text-muted small">
              No results found.
            </div>
          </div>
        </div>

        <div class="d-flex align-items-center gap-3 mt-3 mt-lg-0">
          <div class="dropdown">
            <a class="nav-link dropdown-toggle text-white d-flex align-items-center gap-2" href="#" role="button" data-bs-toggle="dropdown">
              <div class="bg-white text-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 32px; height: 32px;">
                <i class="bi bi-shield-lock-fill"></i>
              </div>
              <span class="d-none d-md-block text-white small fw-bold">{{ adminName }}</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow border-0 mt-2">
              <li><button class="dropdown-item text-danger fw-bold" @click="logout"><i class="bi bi-box-arrow-right me-2"></i>Logout</button></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.router-link-active { color: white !important; opacity: 1 !important; }
.hover-result { transition: background-color 0.2s ease; }
.hover-result:hover { background-color: #f8f9fa; }
.z-3 { z-index: 1050; }
.custom-placeholder::placeholder { color: rgba(255, 255, 255, 0.7) !important; }
.custom-placeholder:focus { color: white !important; }
</style>