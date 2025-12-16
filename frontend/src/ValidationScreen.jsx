import React, { useState, useEffect } from 'react';
import {
  CCard, CCardBody, CCardHeader, CCol, CRow, CListGroup, CListGroupItem, 
  CBadge, CTable, CTableHead, CTableRow, CTableHeaderCell, CTableBody, CTableDataCell, CButton, CSpinner, CAlert
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilCheckCircle, cilPrint, cilWarning } from '@coreui/icons';
import { api } from './services/api'; // Import our new API logic

export default function ValidationScreen() {
  // --- STATE ---
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 1. LOAD PATIENTS ON STARTUP
  useEffect(() => {
    loadPendingPatients();
  }, []);

  const loadPendingPatients = async () => {
    try {
      const data = await api.getPendingSamples();
      setPatients(data);
      // If we have patients, select the first one automatically
      if (data.length > 0 && !selectedPatient) {
        handleSelectPatient(data[0]);
      }
    } catch (err) {
      setError("Could not load patients. Is the backend running?");
    }
  };

  // 2. LOAD RESULTS WHEN CLICKING A PATIENT
  const handleSelectPatient = async (patient) => {
    setSelectedPatient(patient);
    setLoading(true);
    try {
      const data = await api.getResults(patient.barcode);
      setResults(data.results);
    } catch (err) {
      console.error(err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // 3. HANDLE APPROVE BUTTON
  const handleApprove = async () => {
    if (!selectedPatient) return;
    
    if(!window.confirm(`Are you sure you want to approve results for ${selectedPatient.name}?`)) return;

    try {
      await api.approveSample(selectedPatient.barcode);
      alert("Approved Successfully!");
      
      // Remove the approved patient from the list locally
      const remainingPatients = patients.filter(p => p.barcode !== selectedPatient.barcode);
      setPatients(remainingPatients);
      setResults([]);
      setSelectedPatient(null);
      
      // Select next patient if available
      if (remainingPatients.length > 0) {
        handleSelectPatient(remainingPatients[0]);
      }

    } catch (err) {
      alert("Error approving sample");
    }
  };

  return (
    <CRow>
      {/* LEFT COLUMN: Patient List */}
      <CCol md={4} className="mb-4">
        <CCard className="h-100 shadow-sm">
          <CCardHeader>
            <strong>Pending Samples</strong>
          </CCardHeader>
          <CListGroup flush>
            {patients.length === 0 && <div className="p-3 text-muted text-center">No pending samples</div>}
            
            {patients.map((patient) => (
              <CListGroupItem 
                key={patient.id} 
                component="button" 
                active={selectedPatient?.barcode === patient.barcode}
                onClick={() => handleSelectPatient(patient)}
                className="d-flex justify-content-between align-items-center"
              >
                <div>
                  <div className="fw-bold">{patient.name}</div>
                  <small className="text-muted">#{patient.barcode}</small>
                </div>
                {patient.critical && <CBadge color="danger" shape="rounded-pill">CRITICAL</CBadge>}
              </CListGroupItem>
            ))}
          </CListGroup>
        </CCard>
      </CCol>

      {/* RIGHT COLUMN: Results Area */}
      <CCol md={8}>
        {error && <CAlert color="danger">{error}</CAlert>}

        {selectedPatient ? (
          <CCard className="mb-4 shadow-sm">
            <CCardHeader className="d-flex justify-content-between align-items-center bg-white">
              <div>
                  <strong>{selectedPatient.name}</strong> 
                  <span className="ms-2 text-muted">#{selectedPatient.barcode}</span>
              </div>
              <CBadge color="warning">PENDING APPROVAL</CBadge>
            </CCardHeader>
            <CCardBody>
              {loading ? (
                <div className="text-center p-5"><CSpinner color="primary"/></div>
              ) : (
                <>
                <CTable hover responsive bordered>
                  <CTableHead color="light">
                    <CTableRow>
                      <CTableHeaderCell>Test Name</CTableHeaderCell>
                      <CTableHeaderCell>Result</CTableHeaderCell>
                      <CTableHeaderCell>Unit</CTableHeaderCell>
                      <CTableHeaderCell>Ref. Range</CTableHeaderCell>
                      <CTableHeaderCell>Flag</CTableHeaderCell>
                    </CTableRow>
                  </CTableHead>
                  <CTableBody>
                    {results.length === 0 && (
                        <CTableRow><CTableDataCell colSpan="5" className="text-center">No results received from machine yet.</CTableDataCell></CTableRow>
                    )}
                    {results.map((res, index) => (
                      <CTableRow key={index} color={res.flag === 'HIGH' || res.flag === 'LOW' ? 'danger' : ''} style={{'--cui-table-bg-type': res.flag !== 'NORMAL' ? 'rgba(255,0,0,0.05)' : ''}}>
                        <CTableDataCell>{res.test_name}</CTableDataCell>
                        <CTableDataCell className="fw-bold">{res.result_value}</CTableDataCell>
                        <CTableDataCell>{res.unit}</CTableDataCell>
                        <CTableDataCell>{res.ref_range}</CTableDataCell>
                        <CTableDataCell>
                            {res.flag === 'HIGH' && <CBadge color="danger">HIGH</CBadge>}
                            {res.flag === 'LOW' && <CBadge color="warning">LOW</CBadge>}
                        </CTableDataCell>
                      </CTableRow>
                    ))}
                  </CTableBody>
                </CTable>

                <div className="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
                    <CButton color="secondary" variant="outline">
                        <CIcon icon={cilPrint} className="me-2" /> Print Preview
                    </CButton>
                    <CButton color="primary" onClick={handleApprove} disabled={results.length === 0}>
                        <CIcon icon={cilCheckCircle} className="me-2" /> APPROVE RESULTS
                    </CButton>
                </div>
                </>
              )}
            </CCardBody>
          </CCard>
        ) : (
            <div className="text-center p-5 text-muted">Select a patient to view results</div>
        )}
      </CCol>
    </CRow>
  );
}