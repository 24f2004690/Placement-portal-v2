<script setup>
import { ref, onMounted } from 'vue'
import AdminNavBar from '../../components/AdminNavBar.vue'
// Added LineElement and PointElement for the trend chart
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement, LineElement, PointElement } from 'chart.js'
// Added Line component
import { Doughnut, Bar, Line } from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, LineElement, PointElement)

const isLoading = ref(true)
const funnelData = ref({ labels: [], datasets: [] })
const branchData = ref({ labels: [], datasets: [] })
const trendData = ref({ labels: [], datasets: [] })

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/admin/analytics', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      
      // Funnel (Application Statuses)
      const statuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
      const funnelCounts = statuses.map(s => data.funnel[s] || 0)
      
      funnelData.value = {
        labels: statuses,
        datasets: [{
          backgroundColor: ['#6c757d', '#0dcaf0', '#ffc107', '#198754', '#dc3545'],
          data: funnelCounts,
          borderWidth: 0, hoverOffset: 4
        }]
      }

      // Branch Placements (Selections per Branch)
      const branches = Object.keys(data.branches)
      const branchCounts = Object.values(data.branches)

      branchData.value = {
        labels: branches.length ? branches : ['No Data'],
        datasets: [{
          label: 'Students Selected',
          backgroundColor: '#0d6efd', 
          borderRadius: 6,
          data: branchCounts.length ? branchCounts : [0]
        }]
      }

      // Drive Posting Trends (Timeline)
      const trendDates = data.trends.map(t => t.date)
      const trendCounts = data.trends.map(t => t.count)

      trendData.value = {
        labels: trendDates.length ? trendDates : ['No Data'],
        datasets: [{
          label: 'Drives Posted',
          borderColor: '#fd7e14',
          backgroundColor: 'rgba(253, 126, 20, 0.1)',
          borderWidth: 3,
          pointBackgroundColor: '#fd7e14',
          tension: 0.3, // Adds a slight curve to the line
          fill: true,
          data: trendCounts.length ? trendCounts : [0]
        }]
      }
      
      isLoading.value = false
    }
  } catch (error) { console.error(error) }
})

const funnelOptions = { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom' } } }
const barOptions = { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
const lineOptions = { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } }, plugins: { legend: { display: false } } }
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <AdminNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Placement Reports</h2>
        <p class="text-white-50 mb-0">Visualize hiring funnels, branch statistics, and posting trends.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      <div v-if="isLoading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
      
      <div v-else>
        <!-- Funnel and Branch Charts (Top Row) -->
        <div class="row g-4 mb-4">
          <div class="col-lg-5">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-0 pt-4 px-4"><h6 class="fw-bold text-secondary mb-0">Application Funnel</h6></div>
              <div class="card-body p-4" style="height: 350px;"><Doughnut :data="funnelData" :options="funnelOptions" /></div>
            </div>
          </div>

          <div class="col-lg-7">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-0 pt-4 px-4"><h6 class="fw-bold text-secondary mb-0">Selections by Branch</h6></div>
              <div class="card-body p-4" style="height: 350px;"><Bar :data="branchData" :options="barOptions" /></div>
            </div>
          </div>
        </div>

        <!-- Trend Chart (Bottom Row) -->
        <div class="row g-4 mb-4">
          <div class="col-12">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-0 pt-4 px-4"><h6 class="fw-bold text-secondary mb-0">Drive Posting Trends</h6></div>
              <div class="card-body p-4" style="height: 350px;"><Line :data="trendData" :options="lineOptions" /></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-section { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding-bottom: 4rem !important; }
.mt-n5 { margin-top: -4rem !important; }
</style>