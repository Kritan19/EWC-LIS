import React, { useState } from 'react';
import {
  CCard, CCardBody, CCardHeader, CCol, CRow, CForm, CFormInput,
  CFormSelect, CButton, CFormCheck, CAlert
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilSave, cilUserPlus } from '@coreui/icons';
import { api } from './services/api';

export default function PatientRegistration() {
  const [formData, setFormData] = useState({
    fullName: '',
    patientId: '',
    age: '',
    gender: 'M',
    barcode: '',
    tests: []
  });
  const [msg, setMsg] = useState(null);

  // Auto-generate barcode based on timestamp
  const generateBarcode = () => {
    const code = "BC-" + Math.floor(Date.now() / 1000).toString().slice(-6);
    setFormData(prev => ({ ...prev, barcode: code }));
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTestSelection = (test) => {
    setFormData(prev => {
      const tests = prev.tests.includes(test)
        ? prev.tests.filter(t => t !== test)
        : [...prev.tests, test];
      return { ...prev, tests };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMsg(null);

    if (!formData.barcode || !formData.fullName) {
        setMsg({ type: 'danger', text: 'Name and Barcode are required.' });
        return;
    }

    try {
      await api.createOrder({
        patient_id: formData.patientId || formData.barcode, // Fallback ID
        full_name: formData.fullName,
        age: formData.age,
        gender: formData.gender,
        barcode: formData.barcode,
        tests: formData.tests
      });
      setMsg({ type: 'success', text: 'Patient Registered & Order Created!' });
      // Reset form
      setFormData({ fullName: '', patientId: '', age: '', gender: 'M', barcode: '', tests: [] });
    } catch (err) {
      setMsg({ type: 'danger', text: err.message });
    }
  };

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong><CIcon icon={cilUserPlus} className="me-2"/>New Patient Registration</strong>
          </CCardHeader>
          <CCardBody>
            {msg && <CAlert color={msg.type}>{msg.text}</CAlert>}
            
            <CForm onSubmit={handleSubmit}>
              <CRow className="mb-3">
                <CCol md={6}>
                  <CFormInput 
                    label="Full Name" 
                    name="fullName"
                    value={formData.fullName} 
                    onChange={handleInputChange} 
                    required 
                  />
                </CCol>
                <CCol md={3}>
                  <CFormInput 
                    label="Patient ID (Optional)" 
                    name="patientId"
                    value={formData.patientId} 
                    onChange={handleInputChange} 
                  />
                </CCol>
                <CCol md={3}>
                  <CFormSelect 
                    label="Gender" 
                    name="gender"
                    value={formData.gender} 
                    onChange={handleInputChange}
                  >
                    <option value="M">Male</option>
                    <option value="F">Female</option>
                    <option value="O">Other</option>
                  </CFormSelect>
                </CCol>
              </CRow>

              <CRow className="mb-3">
                <CCol md={6}>
                  <div className="mb-2"><strong>Barcode / Sample ID</strong></div>
                  <div className="d-flex gap-2">
                    <CFormInput 
                      name="barcode"
                      value={formData.barcode} 
                      onChange={handleInputChange} 
                      placeholder="Scan or Generate"
                      required
                    />
                    <CButton color="secondary" variant="outline" onClick={generateBarcode}>
                        Generate
                    </CButton>
                  </div>
                </CCol>
                <CCol md={2}>
                    <CFormInput 
                        label="Age" 
                        name="age"
                        value={formData.age} 
                        onChange={handleInputChange} 
                    />
                </CCol>
              </CRow>

              <div className="mb-3">
                <label className="form-label fw-bold">Select Tests</label>
                <div className="p-3 border rounded bg-light d-flex gap-4 flex-wrap">
                    {['CBC', 'LFT', 'KFT', 'Lipid Profile', 'TFT', 'Urine Routine'].map(test => (
                        <CFormCheck 
                            key={test}
                            label={test}
                            checked={formData.tests.includes(test)}
                            onChange={() => handleTestSelection(test)}
                        />
                    ))}
                </div>
              </div>

              <div className="d-grid gap-2 d-md-flex justify-content-md-end">
                <CButton color="primary" type="submit" size="lg">
                    <CIcon icon={cilSave} className="me-2" /> Register & Create Order
                </CButton>
              </div>
            </CForm>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
}