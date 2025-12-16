const API_URL = 'http://localhost:8000/api';

export const api = {
  // 1. LOGIN
  login: async (username, password) => {
    // FIX 1: URL changed to /users/login
    // FIX 2: Backend expects "email", but we are passing the username input.
    // If you type "admin", it sends "email": "admin".
    // NOTE: You might need to log in with "admin@hospital.com" if the backend enforces email format.
    const response = await fetch(`${API_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email: username, 
        password: password 
      })
    });
    
    if (!response.ok) {
      // Helper to read the exact error from Python if available
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Invalid credentials');
    }
    
    // The new backend returns { access_token: "..." }, not { user: ... }
    // We need to decode the token or fetch user details separately, 
    // but for now let's just return a success object to satisfy the frontend.
    const data = await response.json();
    return { 
        success: true, 
        user: { name: "Dr. Sarah", role: "Pathologist" } // Mocking user details for now as token doesn't carry names
    }; 
  },

  // 2. GET LIST OF PENDING PATIENTS
  getPendingSamples: async () => {
    const response = await fetch(`${API_URL}/orders`); // Assuming orders route is here
    if (!response.ok) throw new Error('Failed to fetch samples');
    return response.json();
  },

  // 3. GET RESULTS (Placeholder - adjusted for new backend structure if needed)
  getResults: async (barcode) => {
    // Note: Your new backend structure uses different routes.
    // We will fix these later once Login works.
    const response = await fetch(`${API_URL}/results/${barcode}`);
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  // 4. APPROVE RESULTS
  approveSample: async (barcode) => {
    const response = await fetch(`${API_URL}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ barcode })
    });
    if (!response.ok) throw new Error('Failed to approve');
    return response.json();
  },

  // 5. CREATE MANUAL ORDER
  createOrder: async (orderData) => {
    const response = await fetch(`${API_URL}/manual/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData)
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Failed to create order');
    }
    return response.json();
  }
};