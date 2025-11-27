// API Configuration - Use relative URL for same-origin requests
const API_BASE_URL = window.location.origin; // Automatically uses current domain

// Fetch stats from backend API
async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    document.getElementById('total-complaints').textContent = data.total || 0;
    document.getElementById('resolved-complaints').textContent = data.resolved || 0;
    document.getElementById('pending-complaints').textContent = data.pending || 0;
    document.getElementById('inprogress-complaints').textContent = data.in_progress || 0;
  } catch (error) {
    console.error('Error fetching stats:', error);
    // Show 0 instead of "Loading..." on error
    document.getElementById('total-complaints').textContent = '0';
    document.getElementById('resolved-complaints').textContent = '0';
    document.getElementById('pending-complaints').textContent = '0';
    document.getElementById('inprogress-complaints').textContent = '0';
  }
}

// Load stats on page load
if (document.getElementById('total-complaints')) {
  fetchStats();
}
