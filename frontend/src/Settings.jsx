import React, { useState, useEffect } from 'react';
import {
  CRow, CCol, CCard, CCardBody, CCardHeader, CNav, CNavItem, CNavLink, 
  CTabContent, CTabPane, CTable, CTableHead, CTableRow, CTableHeaderCell, 
  CTableBody, CTableDataCell, CButton, CModal, CModalHeader, CModalTitle, 
  CModalBody, CModalFooter, CForm, CFormInput, CFormSelect
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilPlus, cilMedicalCross, cilDevices, cilGraph } from '@coreui/icons';
import { api } from './services/api';

export default function Settings() {
  const [activeKey, setActiveKey] = useState(1);
  const [tests, setTests] = useState([]);
  const [machines, setMachines] = useState([]);
  const [qcDefs, setQcDefs] = useState([]); // New QC List
  
  // Modals
  const [showTestModal, setShowTestModal] = useState(false);
  const [showMachineModal, setShowMachineModal] = useState(false);
  const [showQCModal, setShowQCModal] = useState(false); // New QC Modal
  
  // Forms
  const [testForm, setTestForm] = useState({ test_code: '', test_name: '', unit: '', min_male: 0, max_male: 0, min_female: 0, max_female: 0 });
  const [machineForm, setMachineForm] = useState({ machine_name: '', ip_address: '', protocol: 'ASTM', division: 'Hematology' });
  
  // New QC Form
  const [qcForm, setQcForm] = useState({ control_name: '', lot_number: '', test_code: '', mean_value: 0, sd_value: 0, expiration_date: '' });

  useEffect(() => {
    loadData();
  }, [activeKey]); // Reload when tab changes

  const loadData = async () => {
    try {
        const t = await api.getTests();
        setTests(t);
        const m = await api.getMachines();
        setMachines(m);
        const q = await api.getQCDefinitions();
        setQcDefs(q);
    } catch(e) { console.error(e); }
  };

  const handleAddTest = async () => { /* Same as before */ await api.addTest(testForm); setShowTestModal(false); loadData(); };
  const handleAddMachine = async () => { /* Same as before */ await api.addMachine(machineForm); setShowMachineModal(false); loadData(); };

  // New QC Handler
  const handleAddQC = async () => {
    try {
        await api.addQCDefinition(qcForm);
        setShowQCModal(false);
        loadData();
        setQcForm({ control_name: '', lot_number: '', test_code: '', mean_value: 0, sd_value: 0, expiration_date: '' });
    } catch (e) { alert("Error: " + e.message); }
  };

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader><strong>Lab Configuration</strong></CCardHeader>
          <CCardBody>
            <CNav variant="tabs" role="tablist">
              <CNavItem><CNavLink active={activeKey === 1} onClick={() => setActiveKey(1)} style={{cursor:'pointer'}}><CIcon icon={cilMedicalCross} className="me-2"/>Test Definitions</CNavLink></CNavItem>
              <CNavItem><CNavLink active={activeKey === 2} onClick={() => setActiveKey(2)} style={{cursor:'pointer'}}><CIcon icon={cilDevices} className="me-2"/>Machines</CNavLink></CNavItem>
              <CNavItem><CNavLink active={activeKey === 3} onClick={() => setActiveKey(3)} style={{cursor:'pointer'}}><CIcon icon={cilGraph} className="me-2"/>QC Controls</CNavLink></CNavItem>
            </CNav>
            
            <CTabContent className="pt-3">
              {/* TAB 1: TESTS (Keep your existing code here) */}
              <CTabPane visible={activeKey === 1}>
                 {/* ... (Existing Test Table code) ... */}
                 <div className="d-flex justify-content-end mb-3"><CButton color="primary" onClick={() => setShowTestModal(true)}><CIcon icon={cilPlus}/> Add Test Code</CButton></div>
                 <CTable bordered hover><CTableHead color="light"><CTableRow><CTableHeaderCell>Code</CTableHeaderCell><CTableHeaderCell>Name</CTableHeaderCell></CTableRow></CTableHead><CTableBody>{tests.map((t,i)=><CTableRow key={i}><CTableDataCell>{t.test_code}</CTableDataCell><CTableDataCell>{t.test_name}</CTableDataCell></CTableRow>)}</CTableBody></CTable>
              </CTabPane>

              {/* TAB 2: MACHINES (Keep your existing code here) */}
              <CTabPane visible={activeKey === 2}>
                 {/* ... (Existing Machine Table code) ... */}
                 <div className="d-flex justify-content-end mb-3"><CButton color="primary" onClick={() => setShowMachineModal(true)}><CIcon icon={cilPlus}/> Add Machine</CButton></div>
                 <CTable bordered hover><CTableHead color="light"><CTableRow><CTableHeaderCell>Machine</CTableHeaderCell><CTableHeaderCell>IP</CTableHeaderCell></CTableRow></CTableHead><CTableBody>{machines.map((m,i)=><CTableRow key={i}><CTableDataCell>{m.machine_name}</CTableDataCell><CTableDataCell>{m.ip_address}</CTableDataCell></CTableRow>)}</CTableBody></CTable>
              </CTabPane>

              {/* TAB 3: QC DEFINITIONS (NEW) */}
              <CTabPane visible={activeKey === 3}>
                <div className="d-flex justify-content-end mb-3">
                    <CButton color="primary" onClick={() => setShowQCModal(true)}>
                        <CIcon icon={cilPlus}/> Add Control
                    </CButton>
                </div>
                <CTable bordered hover>
                    <CTableHead color="light">
                        <CTableRow>
                            <CTableHeaderCell>Control Name</CTableHeaderCell>
                            <CTableHeaderCell>Test</CTableHeaderCell>
                            <CTableHeaderCell>Lot #</CTableHeaderCell>
                            <CTableHeaderCell>Mean</CTableHeaderCell>
                            <CTableHeaderCell>SD</CTableHeaderCell>
                            <CTableHeaderCell>Expiry</CTableHeaderCell>
                        </CTableRow>
                    </CTableHead>
                    <CTableBody>
                        {qcDefs.map((q, i) => (
                            <CTableRow key={i}>
                                <CTableDataCell className="fw-bold">{q.control_name}</CTableDataCell>
                                <CTableDataCell>{q.test_name || q.test_code}</CTableDataCell>
                                <CTableDataCell>{q.lot_number}</CTableDataCell>
                                <CTableDataCell>{q.mean_value}</CTableDataCell>
                                <CTableDataCell>{q.sd_value}</CTableDataCell>
                                <CTableDataCell>{q.expiration_date}</CTableDataCell>
                            </CTableRow>
                        ))}
                    </CTableBody>
                </CTable>
              </CTabPane>
            </CTabContent>
          </CCardBody>
        </CCard>
      </CCol>

      {/* RE-ADD YOUR TEST/MACHINE MODALS HERE (I'm skipping them for brevity, keep your existing ones) */}
      <CModal visible={showTestModal} onClose={() => setShowTestModal(false)}><CModalHeader>Add Test</CModalHeader><CModalBody><CForm><CFormInput label="Test Code" onChange={e => setTestForm({...testForm, test_code: e.target.value})}/></CForm></CModalBody><CModalFooter><CButton onClick={handleAddTest} color="primary">Save</CButton></CModalFooter></CModal>
      <CModal visible={showMachineModal} onClose={() => setShowMachineModal(false)}><CModalHeader>Add Machine</CModalHeader><CModalBody><CForm><CFormInput label="Name" onChange={e => setMachineForm({...machineForm, machine_name: e.target.value})}/></CForm></CModalBody><CModalFooter><CButton onClick={handleAddMachine} color="primary">Save</CButton></CModalFooter></CModal>

      {/* --- QC MODAL (NEW) --- */}
      <CModal visible={showQCModal} onClose={() => setShowQCModal(false)}>
        <CModalHeader><CModalTitle>Add QC Control</CModalTitle></CModalHeader>
        <CModalBody>
            <CForm>
                <div className="mb-3">
                    <CFormInput label="Control Name" placeholder="e.g. Level 1 Normal" value={qcForm.control_name} onChange={e => setQcForm({...qcForm, control_name: e.target.value})}/>
                </div>
                <div className="mb-3">
                    <label className="form-label">Test</label>
                    <CFormSelect value={qcForm.test_code} onChange={e => setQcForm({...qcForm, test_code: e.target.value})}>
                        <option value="">Select Test...</option>
                        {tests.map(t => <option key={t.id} value={t.test_code}>{t.test_name} ({t.test_code})</option>)}
                    </CFormSelect>
                </div>
                <div className="mb-3">
                    <CFormInput label="Lot Number" value={qcForm.lot_number} onChange={e => setQcForm({...qcForm, lot_number: e.target.value})}/>
                </div>
                <CRow>
                    <CCol><CFormInput label="Mean" type="number" step="0.01" value={qcForm.mean_value} onChange={e => setQcForm({...qcForm, mean_value: e.target.value})}/></CCol>
                    <CCol><CFormInput label="SD" type="number" step="0.01" value={qcForm.sd_value} onChange={e => setQcForm({...qcForm, sd_value: e.target.value})}/></CCol>
                </CRow>
                <div className="mb-3 mt-3">
                    <CFormInput label="Expiration Date" type="date" value={qcForm.expiration_date} onChange={e => setQcForm({...qcForm, expiration_date: e.target.value})}/>
                </div>
            </CForm>
        </CModalBody>
        <CModalFooter>
            <CButton color="secondary" onClick={() => setShowQCModal(false)}>Cancel</CButton>
            <CButton color="primary" onClick={handleAddQC}>Save Control</CButton>
        </CModalFooter>
      </CModal>
    </CRow>
  );
}