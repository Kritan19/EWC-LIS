import React, { useState } from 'react';
import { 
  CSidebar, CSidebarBrand, CSidebarNav, CNavItem, CContainer, 
  CHeader, CHeaderBrand, CHeaderNav, CHeaderToggler, CAvatar
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { 
  cilSpeedometer, cilBeaker, cilSettings, cilMenu, 
  cilAccountLogout, cilUserPlus, cilGraph, cilList 
} from '@coreui/icons';

// --- IMPORT REAL PAGES ---
import Login from './Login';
import Dashboard from './Dashboard';
import ValidationScreen from './ValidationScreen';
import PatientRegistration from './PatientRegistration';
import Settings from './Settings';
import SamplesList from './SamplesList';
import QCView from './QCView';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [sidebarShow, setSidebarShow] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard');

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
    setCurrentView('dashboard');
  };

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  return (
    <div className="min-vh-100 bg-light d-flex">
      {/* SIDEBAR */}
      <CSidebar position="fixed" visible={sidebarShow}>
        <CSidebarBrand className="d-none d-md-flex bg-dark text-white p-3">
          <CIcon icon={cilBeaker} size="xl" className="me-2"/>
          <strong>EWC LIS</strong>
        </CSidebarBrand>
        <CSidebarNav>
          {/* A. DASHBOARD */}
          <CNavItem 
            href="#" 
            onClick={() => setCurrentView('dashboard')} 
            className={currentView === 'dashboard' ? 'active' : ''}
          >
            <CIcon icon={cilSpeedometer} className="nav-icon" /> Dashboard
          </CNavItem>
          
          {/* B. SAMPLES (NOW WORKING) */}
          <CNavItem 
            href="#" 
            onClick={() => setCurrentView('samples')} 
            className={currentView === 'samples' ? 'active' : ''}
          >
            <CIcon icon={cilList} className="nav-icon" /> Samples
          </CNavItem>

          {/* C. VALIDATION */}
          <CNavItem 
            href="#" 
            onClick={() => setCurrentView('validation')} 
            className={currentView === 'validation' ? 'active' : ''}
          >
            <CIcon icon={cilBeaker} className="nav-icon" /> Validation
          </CNavItem>

          {/* E. QC */}
          <CNavItem 
            href="#" 
            onClick={() => setCurrentView('qc')} 
            className={currentView === 'qc' ? 'active' : ''}
          >
            <CIcon icon={cilGraph} className="nav-icon" /> QC
          </CNavItem>

          {/* F. REGISTRATION */}
          <CNavItem 
            href="#" 
            onClick={() => setCurrentView('registration')} 
            className={currentView === 'registration' ? 'active' : ''}
          >
            <CIcon icon={cilUserPlus} className="nav-icon" /> Registration
          </CNavItem>
          
          {/* D. SETTINGS (Only for Admin) */}
          {currentUser?.role === 'Admin' || currentUser?.role === 'Pathologist' ? (
             <CNavItem 
               href="#" 
               onClick={() => setCurrentView('settings')} 
               className={currentView === 'settings' ? 'active' : ''}
             >
               <CIcon icon={cilSettings} className="nav-icon" /> Settings
             </CNavItem>
          ) : null}
          
          <CNavItem href="#" onClick={handleLogout} className="mt-auto text-danger">
            <CIcon icon={cilAccountLogout} className="nav-icon" /> Logout
          </CNavItem>
          
          {/* Attribution */}
          <div className="mt-2 pb-3 text-center">
            <small className="text-secondary" style={{ fontSize: '0.65rem', opacity: 0.5 }}>
                v1.1.0 | Dev: Kritan Nepal
            </small>
          </div>
        </CSidebarNav>
      </CSidebar>

      {/* MAIN CONTENT WRAPPER */}
      <div className="wrapper d-flex flex-column min-vh-100 bg-light flex-grow-1" 
           style={{ paddingLeft: sidebarShow ? '256px' : '0', transition: 'padding 0.3s' }}>
        
        {/* HEADER */}
        <CHeader position="sticky" className="mb-4 p-3 border-bottom bg-white">
          <CContainer fluid>
            <CHeaderToggler onClick={() => setSidebarShow(!sidebarShow)}>
              <CIcon icon={cilMenu} size="lg" />
            </CHeaderToggler>
            <CHeaderNav className="ms-auto">
                <div className="d-flex align-items-center">
                    <div className="me-2 text-end">
                        <div className="fw-bold">{currentUser?.name}</div>
                        <small className="text-muted">{currentUser?.role}</small>
                    </div>
                    <CAvatar color="primary" textColor="white">
                        {currentUser?.name ? currentUser.name.charAt(0) : 'U'}
                    </CAvatar>
                </div>
            </CHeaderNav>
          </CContainer>
        </CHeader>

        {/* DYNAMIC CONTENT AREA */}
        <CContainer fluid className="px-4 pb-4 h-100">
           {currentView === 'dashboard' && <Dashboard />}
           {currentView === 'samples' && <SamplesList />}
           {currentView === 'validation' && <ValidationScreen />}
           {currentView === 'qc' && <QCView />}
           {currentView === 'registration' && <PatientRegistration />}
           {currentView === 'settings' && <Settings />}
        </CContainer>
      </div>
    </div>
  );
}