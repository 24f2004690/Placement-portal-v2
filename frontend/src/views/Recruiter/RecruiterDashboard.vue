<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RecruiterNavBar from '../../components/RecruiterNavBar.vue'

const router = useRouter()
const userName = ref('Recruiter')
const isLoading = ref(true)

// Data state
const drives = ref([])
const applications = ref([])

onMounted(async () => {
  const storedName = localStorage.getItem('name')
  if (storedName) userName.value = storedName

  try {
    const [drivesRes, appsRes] = await Promise.all([
      fetch('http://127.0.0.1:5000/api/recruiter/drives', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      }),
      fetch('http://127.0.0.1:5000/api/recruiter/applications', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
    ])

    if (drivesRes.ok) drives.value = await drivesRes.json()
    if (appsRes.ok) applications.value = await appsRes.json()

  } catch (error) {
    console.error("Failed to load dashboard data:", error)
  } finally {
    isLoading.value = false
  }
})

// Dynamic computations for the 4 Stat Boxes
const totalDrives = computed(() => drives.value.length)
const totalApps = computed(() => applications.value.length)
const pendingInterviews = computed(() => applications.value.filter(a => a.status === 'Interview Scheduled').length)
const selectedCandidates = computed(() => applications.value.filter(a => a.status === 'Selected').length)

// Clean logic for upcoming interviews using the new database column
const upcomingInterviews = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0) // Reset time to midnight for accurate day comparison

  return applications.value
    .filter(app => {
      if (app.status !== 'Interview Scheduled' || !app.interview_date) return false
      
      const interviewDate = new Date(app.interview_date)
      return interviewDate >= today 
    })
    // Sort so the soonest interview is at the top
    .sort((a, b) => new Date(a.interview_date) - new Date(b.interview_date))
    .slice(0, 5) // Limit to top 5
})

// Recent applications for the activity table (Top 5)
const recentApplications = computed(() => applications.value.slice(0, 5))

// Formatting Helpers
const getFormattedDate = (isoString) => {
  if (!isoString) return ''
  return new Date(isoString).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

const getFormattedTime = (isoString) => {
  if (!isoString) return ''
  return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="bg-light min-vh-100">
    <div class="header-section pb-5 pt-4">
      <RecruiterNavBar />
      <div class="container pt-3 pb-5">
        <h2 class="fw-bold text-white mb-1">Recruiter Dashboard</h2>
        <p class="text-white-50 mb-0">Overview of your company's recruitment activities.</p>
      </div>
    </div>

    <div class="container mt-n5 pb-5">
      
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status"></div>
      </div>

      <div v-else>
        <!-- 1. QUICK STATS ROW -->
        <div class="row g-4 mb-4">
          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4 d-flex align-items-center gap-3">
                <div class="bg-primary-subtle text-primary rounded p-3 d-flex align-items-center justify-content-center" style="width: 54px; height: 54px;">
                  <i class="bi bi-briefcase-fill fs-4"></i>
                </div>
                <div>
                  <h3 class="fw-bold mb-0 text-dark">{{ totalDrives }}</h3>
                  <div class="small text-muted text-uppercase fw-bold" style="font-size: 0.75rem;">Total Drives</div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4 d-flex align-items-center gap-3">
                <div class="bg-info-subtle text-info rounded p-3 d-flex align-items-center justify-content-center" style="width: 54px; height: 54px;">
                  <i class="bi bi-people-fill fs-4"></i>
                </div>
                <div>
                  <h3 class="fw-bold mb-0 text-dark">{{ totalApps }}</h3>
                  <div class="small text-muted text-uppercase fw-bold" style="font-size: 0.75rem;">Applications</div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4 d-flex align-items-center gap-3">
                <div class="bg-warning-subtle text-warning rounded p-3 d-flex align-items-center justify-content-center" style="width: 54px; height: 54px;">
                  <i class="bi bi-calendar-event-fill fs-4"></i>
                </div>
                <div>
                  <h3 class="fw-bold mb-0 text-dark">{{ pendingInterviews }}</h3>
                  <div class="small text-muted text-uppercase fw-bold" style="font-size: 0.75rem;">Interviews</div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-lg-3">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4 d-flex align-items-center gap-3">
                <div class="bg-success-subtle text-success rounded p-3 d-flex align-items-center justify-content-center" style="width: 54px; height: 54px;">
                  <i class="bi bi-check-circle-fill fs-4"></i>
                </div>
                <div>
                  <h3 class="fw-bold mb-0 text-dark">{{ selectedCandidates }}</h3>
                  <div class="small text-muted text-uppercase fw-bold" style="font-size: 0.75rem;">Hired Students</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- FLEXBOX ROW FOR TWO TABLES -->
        <div class="row g-4 d-flex align-items-stretch">
          
          <!-- 2. UPCOMING INTERVIEWS TABLE -->
          <div class="col-lg-6 d-flex">
            <div class="card border-0 shadow-sm w-100 d-flex flex-column">
              <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
                <h6 class="fw-bold text-secondary mb-0 text-uppercase small">Upcoming Interviews</h6>
                <button @click="router.push('/drive-applications')" class="btn btn-sm btn-link text-primary text-decoration-none fw-bold p-0">View All</button>
              </div>
              <div class="card-body p-0 flex-grow-1 d-flex flex-column">
                <table class="table table-hover align-middle mb-0 flex-grow-1">
                  <tbody>
                    <tr v-for="app in upcomingInterviews" :key="app.id">
                      <td class="ps-4 py-3">
                        <div class="fw-bold text-dark">{{ app.student_name }}</div>
                        <div class="small text-muted">{{ app.drive_title }}</div>
                      </td>
                      <td class="text-end pe-4">
                        <div class="fw-bold text-dark small"><i class="bi bi-calendar me-1"></i>{{ getFormattedDate(app.interview_date) }}</div>
                        <div class="text-primary fw-bold small"><i class="bi bi-clock me-1"></i>{{ getFormattedTime(app.interview_date) }}</div>
                      </td>
                    </tr>
                    <tr v-if="upcomingInterviews.length === 0">
                      <td colspan="2" class="text-center py-5 text-muted h-100 align-middle">
                        <i class="bi bi-calendar-check fs-1 text-light d-block mb-2"></i>
                        No upcoming interviews scheduled.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 3. RECENT APPLICATIONS TABLE -->
          <div class="col-lg-6 d-flex">
            <div class="card border-0 shadow-sm w-100 d-flex flex-column">
              <div class="card-header bg-white border-0 pt-4 px-4 d-flex justify-content-between align-items-center">
                <h6 class="fw-bold text-secondary mb-0 text-uppercase small">Recent Applications</h6>
                <button @click="router.push('drive-applications')" class="btn btn-sm btn-link text-primary text-decoration-none fw-bold p-0">View All</button>
              </div>
              <div class="card-body p-0 flex-grow-1 d-flex flex-column">
                <table class="table table-hover align-middle mb-0 flex-grow-1">
                  <tbody>
                    <tr v-for="app in recentApplications" :key="app.id">
                      <td class="ps-4 py-3">
                        <div class="fw-bold text-dark">{{ app.student_name }}</div>
                        <div class="small text-muted">{{ app.drive_title }}</div>
                      </td>
                      <td class="text-end pe-4">
                        <span class="badge border rounded-pill px-3 py-2 bg-light text-dark shadow-sm">
                          {{ app.status }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="recentApplications.length === 0">
                      <td colspan="2" class="text-center py-5 text-muted h-100 align-middle">
                        No recent applications.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
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