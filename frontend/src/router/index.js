import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// --- Admin Views ---
import AdminDashboard from '../views/Admin/AdminDashboard.vue'
import ManageCompanies from '../views/Admin/ManageCompanies.vue'
import PlacementDrives from '../views/Admin/PlacementDrives.vue'
import StudentDirectory from '../views/Admin/StudentDirectory.vue'
import PlacementReports from '../views/Admin/PlacementReports.vue'

// --- Recruiter (Company) Views ---
import RecruiterDashboard from '../views/Recruiter/RecruiterDashboard.vue'
import ManageDrives from '../views/Recruiter/ManageDrives.vue'
import DriveApplications from '../views/Recruiter/DriveApplications.vue'

// --- Student Views ---
import StudentDashboard from '../views/Student/StudentDashboard.vue'
import StudentApplications from '../views/Student/StudentApplications.vue'
import StudentProfile from '../views/Student/StudentProfile.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ==========================================
    // PUBLIC ROUTES
    // ==========================================
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { hideNavbar: true }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { hideNavbar: true }
    },

    // ==========================================
    // ADMIN ROUTES
    // ==========================================
    {
      path: '/admin-dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/admin/companies',
      name: 'ManageCompanies',
      component: ManageCompanies,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/admin/drives',
      name: 'PlacementDrives',
      component: PlacementDrives,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/admin/students',
      name: 'StudentDirectory',
      component: StudentDirectory,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },
    {
      path: '/admin/reports',
      name: 'PlacementReports',
      component: PlacementReports,
      meta: { requiresAuth: true, role: 'admin', hideNavbar: true }
    },

    // ==========================================
    // RECRUITER (COMPANY) ROUTES
    // ==========================================
    {
      path: '/recruiter-dashboard',
      name: 'RecruiterDashboard',
      component: RecruiterDashboard,
      meta: { requiresAuth: true, role: 'company', hideNavbar: true }
    },
    {
      path: '/manage-drives',
      name: 'ManageDrives',
      component: ManageDrives,
      meta: { requiresAuth: true, role: 'company', hideNavbar: true }
    },
    {
      path: '/drive-applications',
      name: 'DriveApplications',
      component: DriveApplications,
      meta: { requiresAuth: true, role: 'company', hideNavbar: true }
    },

    // ==========================================
    // STUDENT ROUTES
    // ==========================================
    {
      path: '/student-dashboard',
      name: 'StudentDashboard',
      component: StudentDashboard,
      meta: { requiresAuth: true, role: 'student', hideNavbar: true }
    },
    {
      path: '/student-applications',
      name: 'StudentApplications',
      component: StudentApplications,
      meta: { requiresAuth: true, role: 'student', hideNavbar: true }
    },
    {
      path: '/student-profile',
      name: 'StudentProfile',
      component: StudentProfile,
      meta: { requiresAuth: true, role: 'student', hideNavbar: true }
    }
  ]
})

// ==========================================
// GLOBAL SECURITY GUARD
// ==========================================
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  // 1. Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!token) {
      alert("Please log in to access this page.")
      return next('/login')
    }

    // 2. Check if route requires a specific role
    if (to.meta.role && to.meta.role !== role) {
      alert(`Unauthorized Access! You are logged in as a ${role}.`)
      
      // Redirect them to their proper dashboard based on their role
      if (role === 'admin') return next('/admin-dashboard')
      if (role === 'company') return next('/recruiter-dashboard')
      if (role === 'student') return next('/student-dashboard')
      
      return next('/login') // Fallback
    }
  }

  // 3. Prevent logged-in users from visiting Login/Register pages
  if ((to.path === '/login' || to.path === '/register') && token) {
    if (role === 'admin') return next('/admin-dashboard')
    if (role === 'company') return next('/recruiter-dashboard')
    if (role === 'student') return next('/student-dashboard')
  }

  next() 
})

export default router