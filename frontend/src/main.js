import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

// GLOBAL FETCH INTERCEPTOR

const originalFetch = window.fetch

window.fetch = async (...args) => {
  const response = await originalFetch(...args)
  
  // If the backend says the token is expired or user is deleted

  const requestUrl = typeof args[0] === 'string' ? args[0] : args[0].url

  // 1. Ignore the interceptor if the request is going to the login endpoint
  if (requestUrl.includes('/login')) {
    return response
  }
  
  if (response.status === 401) {
    // A 401 from flask_jwt_extended always means the JWT was missing,
    // invalid, or expired. If THIS request never sent a token in the
    // first place, that's a bug in the request (forgot the header),
    // not proof the session is dead, don't log the user out for it.
    const opts = args[1] || {}
    const headers = opts.headers instanceof Headers
      ? Object.fromEntries(opts.headers.entries())
      : (opts.headers || {})
    const sentToken = headers['Authorization'] || headers['authorization']

    if (sentToken) {
      console.warn("Session expired or invalid. Logging out...")
      localStorage.clear()

      // We use window.location to force a hard reload and clear all Vue state
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else {
      console.error(`401 on ${requestUrl} with no Authorization header sent - this looks like a bug in that request, not an expired session.`)
    }
  }
  
  return response
}

const app = createApp(App)

app.use(router)

app.mount('#app')