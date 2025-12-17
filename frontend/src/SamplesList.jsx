import React, { useState, useEffect } from 'react';
import {
  CCard, CCardBody, CCardHeader, CCol, CRow, CTable, CTableHead, CTableRow, 
  CTableHeaderCell, CTableBody, CTableDataCell, CBadge, CFormInput, CFormSelect, 
  CButton, CSpinner
} from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilSearch, cilList } from '@coreui/icons';
import { api } from './services/api';

export default function SamplesList() {
  const [samples, setSamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({ search: '', status: 'All' });

  useEffect(() => {
    fetchSamples();
  }, []); // Load on mount

  const fetchSamples = async () => {
    setLoading(true);
    try {
      const data = await api.getAllSamples(filters.search, filters.status);
      setSamples(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Trigger search when pressing Enter or clicking button
  const handleSearch = (e) => {
    e.preventDefault();
    fetchSamples();
  };

  return (
    <CRow>
      <CCol xs={12}>
        <CCard className="mb-4">
          <CCardHeader>
            <strong><CIcon icon={cilList} className="me-2"/>Sample History</strong>
          </CCardHeader>
          <CCardBody>
            {/* SEARCH & FILTER BAR */}
            <form onSubmit={handleSearch} className="row g-3 mb-4">
              <CCol md={6}>
                <CFormInput 
                  placeholder="Search by Patient Name or Barcode" 
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                />
              </CCol>
              <CCol md={3}>
                <CFormSelect 
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                >
                  <option value="All">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="APPROVED">Approved</option>
                </CFormSelect>
              </CCol>
              <CCol md={3}>
                <CButton color="primary" type="submit" className="w-100" disabled={loading}>
                  <CIcon icon={cilSearch} className="me-2"/>
                  {loading ? 'Searching...' : 'Search'}
                </CButton>
              </CCol>
            </form>

            {/* DATA TABLE */}
            <CTable hover responsive bordered>
              <CTableHead color="light">
                <CTableRow>
                  <CTableHeaderCell>Date</CTableHeaderCell>
                  <CTableHeaderCell>Barcode</CTableHeaderCell>
                  <CTableHeaderCell>Patient Name</CTableHeaderCell>
                  <CTableHeaderCell>Status</CTableHeaderCell>
                  <CTableHeaderCell>Actions</CTableHeaderCell>
                </CTableRow>
              </CTableHead>
              <CTableBody>
                {samples.length === 0 && !loading && (
                    <CTableRow>
                        <CTableDataCell colSpan="5" className="text-center text-muted">
                            No samples found matching criteria.
                        </CTableDataCell>
                    </CTableRow>
                )}
                
                {samples.map((item) => (
                  <CTableRow key={item.id}>
                    <CTableDataCell>{item.collection_time}</CTableDataCell>
                    <CTableDataCell className="font-monospace">{item.barcode}</CTableDataCell>
                    <CTableDataCell className="fw-bold">{item.patient_name}</CTableDataCell>
                    <CTableDataCell>
                        <CBadge color={item.status === 'APPROVED' ? 'success' : 'warning'}>
                            {item.status}
                        </CBadge>
                    </CTableDataCell>
                    <CTableDataCell>
                        <CButton size="sm" color="info" variant="ghost">View Details</CButton>
                    </CTableDataCell>
                  </CTableRow>
                ))}
              </CTableBody>
            </CTable>
          </CCardBody>
        </CCard>
      </CCol>
    </CRow>
  );
}