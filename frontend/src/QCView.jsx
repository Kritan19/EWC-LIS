import React, { useState, useEffect } from 'react';
import {
  CRow, CCol, CCard, CCardBody, CCardHeader, CFormSelect, 
  CButton, CFormInput, CModal, CModalHeader, CModalBody, CModalFooter, CInputGroup, CInputGroupText
} from '@coreui/react';
import { CChartLine } from '@coreui/react-chartjs';
import CIcon from '@coreui/icons-react';
import { cilPlus, cilGraph, cilSearch } from '@coreui/icons';
import { api } from './services/api';

export default function QCView() {
  const [controls, setControls] = useState([]);
  const [filteredControls, setFilteredControls] = useState([]); // For search
  const [searchTerm, setSearchTerm] = useState('');
  
  const [selectedControl, setSelectedControl] = useState('');
  const [chartData, setChartData] = useState(null);
  const [definition, setDefinition] = useState(null);
  
  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [newValue, setNewValue] = useState('');

  useEffect(() => {
    loadControls();
  }, []);

  useEffect(() => {
    // Filter logic
    if (searchTerm === '') {
        setFilteredControls(controls);
    } else {
        const lower = searchTerm.toLowerCase();
        setFilteredControls(controls.filter(c => 
            c.control_name.toLowerCase().includes(lower) || 
            c.test_name.toLowerCase().includes(lower)
        ));
    }
  }, [searchTerm, controls]);

  useEffect(() => {
    if (selectedControl) {
      loadChartData(selectedControl);
    }
  }, [selectedControl]);

  const loadControls = async () => {
    try {
      const data = await api.getQCDefinitions();
      setControls(data);
      setFilteredControls(data);
      if (data.length > 0) setSelectedControl(data[0].id);
    } catch (e) {
      console.error(e);
    }
  };

  const loadChartData = async (id) => {
    try {
      const { definition, data } = await api.getQCData(id);
      setDefinition(definition);
      
      const mean = definition.mean_value;
      const sd = definition.sd_value;
      const labels = data.map(d => d.date);
      const values = data.map(d => d.result_value);
      
      setChartData({
        labels,
        datasets: [
          {
            label: 'Result',
            backgroundColor: 'rgba(50, 31, 219, 0.2)',
            borderColor: 'rgba(50, 31, 219, 1)',
            data: values,
            fill: false
          },
          {
            label: 'Mean',
            data: Array(values.length).fill(mean),
            borderColor: 'green',
            borderDash: [5, 5],
            pointRadius: 0
          },
          {
            label: '+2 SD',
            data: Array(values.length).fill(mean + (2 * sd)),
            borderColor: 'red',
            borderDash: [2, 2],
            pointRadius: 0
          },
          {
            label: '-2 SD',
            data: Array(values.length).fill(mean - (2 * sd)),
            borderColor: 'red',
            borderDash: [2, 2],
            pointRadius: 0
          }
        ]
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddResult = async () => {
    if (!newValue || !selectedControl) return;
    try {
      await api.addQCResult({
        qc_definition_id: parseInt(selectedControl), // <--- FIX: Ensure this is Int
        result_value: parseFloat(newValue),
        performed_by: "Admin",
        status: "OK" 
      });
      setShowModal(false);
      setNewValue('');
      loadChartData(selectedControl);
    } catch (e) {
      alert("Error saving QC: " + e.message);
    }
  };

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader className="d-flex justify-content-between align-items-center">
            <strong><CIcon icon={cilGraph} className="me-2"/>Quality Control Charts</strong>
            <CButton color="primary" size="sm" onClick={() => setShowModal(true)}>
                <CIcon icon={cilPlus}/> Add Run
            </CButton>
          </CCardHeader>
          <CCardBody>
            <div className="d-flex gap-3 mb-4">
                {/* SEARCH FILTER */}
                <CInputGroup className="w-25">
                    <CInputGroupText><CIcon icon={cilSearch}/></CInputGroupText>
                    <CFormInput 
                        placeholder="Filter by Test..." 
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                    />
                </CInputGroup>

                {/* DROPDOWN SELECTOR */}
                <CFormSelect className="w-50" value={selectedControl} onChange={e => setSelectedControl(e.target.value)}>
                    {filteredControls.map(c => (
                        <option key={c.id} value={c.id}>
                            {c.test_name} - {c.control_name} (Lot: {c.lot_number})
                        </option>
                    ))}
                </CFormSelect>
            </div>

            {chartData && (
                <div style={{ height: '400px' }}>
                    <CChartLine 
                        data={chartData}
                        options={{
                            maintainAspectRatio: false,
                            plugins: { legend: { display: true } },
                            scales: {
                                y: {
                                    suggestedMin: definition ? definition.mean_value - (3 * definition.sd_value) : 0,
                                    suggestedMax: definition ? definition.mean_value + (3 * definition.sd_value) : 100
                                }
                            }
                        }}
                    />
                </div>
            )}
          </CCardBody>
        </CCard>
      </CCol>

      {/* ADD RUN MODAL */}
      <CModal visible={showModal} onClose={() => setShowModal(false)}>
        <CModalHeader>Add QC Result</CModalHeader>
        <CModalBody>
            <div className="mb-3">
                <label className="form-label">Result Value</label>
                <CFormInput type="number" step="0.01" value={newValue} onChange={e => setNewValue(e.target.value)} autoFocus/>
            </div>
        </CModalBody>
        <CModalFooter>
            <CButton color="secondary" onClick={() => setShowModal(false)}>Cancel</CButton>
            <CButton color="primary" onClick={handleAddResult}>Save</CButton>
        </CModalFooter>
      </CModal>
    </CRow>
  );
}