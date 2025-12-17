const API_URL = 'http://localhost:8000/api';

export const api = {
  // --- AUTHENTICATION ---
  login: async (username, password) => {
    // Mapping username to email field as required by backend schema
    const response = await fetch(`${API_URL}/users/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        email: username, 
        password: password 
      })
    });
    
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Invalid credentials');
    }
    
    // Returning static Admin profile as requested
    return { 
        success: true, 
        user: { 
            name: "System Admin", 
            role: "Admin" 
        } 
    }; 
  },

  // --- DASHBOARD & VALIDATION ---
  getPendingSamples: async () => {
    const response = await fetch(`${API_URL}/samples`);
    if (!response.ok) throw new Error('Failed to fetch samples');
    return response.json();
  },

  getResults: async (barcode) => {
    const response = await fetch(`${API_URL}/results/${barcode}`);
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  approveSample: async (barcode) => {
    const response = await fetch(`${API_URL}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ barcode })
    });
    if (!response.ok) throw new Error('Failed to approve result');
    return response.json();
  },

  // --- MANUAL ORDER ENTRY ---
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
  },

  // --- ADMIN SETTINGS ---
  getTests: async () => {
    const response = await fetch(`${API_URL}/settings/tests`);
    if (!response.ok) throw new Error('Failed to fetch test definitions');
    return response.json();
  },

  addTest: async (testData) => {
    const response = await fetch(`${API_URL}/settings/tests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testData)
    });
    if (!response.ok) throw new Error('Failed to add test');
    return response.json();
  },

  getMachines: async () => {
    const response = await fetch(`${API_URL}/settings/machines`);
    if (!response.ok) throw new Error('Failed to fetch machines');
    return response.json();
  },

  addMachine: async (machineData) => {
    const response = await fetch(`${API_URL}/settings/machines`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(machineData)
    });
    if (!response.ok) throw new Error('Failed to add machine');
    return response.json();
  },

  // --- DASHBOARD ---
  getStats: async () => {
    const response = await fetch(`${API_URL}/dashboard/stats`);
    if (!response.ok) throw new Error('Failed to load stats');
    return response.json();
  },

  // --- SAMPLES LIST ---
  getAllSamples: async (search = '', status = '') => {
    // Build query string like ?search=john&status=PENDING
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status && status !== 'All') params.append('status', status);
    
    const response = await fetch(`${API_URL}/samples/all?${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch samples');
    return response.json();
  },

  // --- QC MODULE ---
  getQCDefinitions: async () => {
    const response = await fetch(`${API_URL}/qc/definitions`);
    if (!response.ok) throw new Error('Failed to load QC definitions');
    return response.json();
  },

  addQCDefinition: async (data) => {
    const response = await fetch(`${API_URL}/qc/definitions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create QC definition');
    return response.json();
  },

  getQCData: async (qcId) => {
    const response = await fetch(`${API_URL}/qc/results/${qcId}`);
    if (!response.ok) throw new Error('Failed to load chart data');
    return response.json();
  },

  addQCResult: async (data) => {
    const response = await fetch(`${API_URL}/qc/results`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to save QC result');
    return response.json();
  },
};