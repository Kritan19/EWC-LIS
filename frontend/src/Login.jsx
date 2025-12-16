import React, { useState } from 'react';
import { 
  CContainer, CRow, CCol, CCard, CCardBody, CForm, CFormInput, 
  CInputGroup, CInputGroupText, CButton, CAlert 
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilUser, cilLockLocked, cilBeaker } from '@coreui/icons';
import { api } from './services/api';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.login(username, password);
      onLoginSuccess(response.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-light min-vh-100 d-flex flex-row align-items-center">
      <CContainer>
        <CRow className="justify-content-center">
          <CCol md={5}>
            <div className="text-center mb-4">
               <span className="bg-primary text-white p-3 rounded shadow-sm d-inline-block">
                 <CIcon icon={cilBeaker} size="3xl"/>
               </span>
               <h2 className="mt-3 text-dark fw-bold">EWC LIS</h2>
               <p className="text-muted">Laboratory Information System</p>
            </div>
            <CCard className="p-4 shadow-lg border-0">
              <CCardBody>
                <CForm onSubmit={handleLogin}>
                  <h4 className="mb-4 text-secondary">Sign In</h4>
                  
                  {error && <CAlert color="danger">{error}</CAlert>}

                  <CInputGroup className="mb-3">
                    <CInputGroupText><CIcon icon={cilUser} /></CInputGroupText>
                    <CFormInput 
                      placeholder="Email or Username" 
                      autoComplete="username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                    />
                  </CInputGroup>
                  
                  <CInputGroup className="mb-4">
                    <CInputGroupText><CIcon icon={cilLockLocked} /></CInputGroupText>
                    <CFormInput 
                      type="password" 
                      placeholder="Password" 
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </CInputGroup>
                  
                  <CRow>
                    <CCol xs={12}>
                      <CButton color="primary" className="px-4 w-100 fw-bold" type="submit" disabled={loading}>
                        {loading ? 'Verifying...' : 'Login'}
                      </CButton>
                    </CCol>
                  </CRow>
                </CForm>
              </CCardBody>
            </CCard>
            <div className="text-center mt-3 text-muted small">
                &copy; {new Date().getFullYear()} EWC LIS
            </div>
          </CCol>
        </CRow>
      </CContainer>
    </div>
  );
}