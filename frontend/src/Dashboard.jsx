import React, { useState, useEffect } from 'react';
import { CRow, CCol, CWidgetStatsB, CCard, CCardBody, CCardHeader } from '@coreui/react';
import CIcon from '@coreui/icons-react';
import { cilBeaker, cilCheckCircle, cilWarning, cilChartLine } from '@coreui/icons';
import { api } from './services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({ total_today: 0, pending: 0, approved: 0, critical: 0 });

  useEffect(() => {
    loadStats();
    // Optional: Poll every 30 seconds for live updates
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error("Dashboard error:", error);
    }
  };

  return (
    <>
      {/* STATS WIDGETS */}
      <CRow className="mb-4">
        <CCol xs={12} sm={6} md={3}>
          <CWidgetStatsB
            className="mb-3"
            progress={{ color: 'info', value: 100 }}
            text="Samples Registered Today"
            title="Total Intake"
            value={stats.total_today}
            icon={<CIcon icon={cilChartLine} size="xl" className="text-white"/>}
            color="info"
            inverse
          />
        </CCol>
        <CCol xs={12} sm={6} md={3}>
          <CWidgetStatsB
            className="mb-3"
            progress={{ color: 'warning', value: 75 }} // Static progress for visual
            text="Waiting for Validation"
            title="Pending"
            value={stats.pending}
            icon={<CIcon icon={cilBeaker} size="xl" className="text-white"/>}
            color="warning"
            inverse
          />
        </CCol>
        <CCol xs={12} sm={6} md={3}>
          <CWidgetStatsB
            className="mb-3"
            progress={{ color: 'success', value: 100 }}
            text="Results Released Today"
            title="Approved"
            value={stats.approved}
            icon={<CIcon icon={cilCheckCircle} size="xl" className="text-white"/>}
            color="success"
            inverse
          />
        </CCol>
        <CCol xs={12} sm={6} md={3}>
          <CWidgetStatsB
            className="mb-3"
            progress={{ color: 'danger', value: 100 }}
            text="Requires Immediate Action"
            title="Critical"
            value={stats.critical}
            icon={<CIcon icon={cilWarning} size="xl" className="text-white"/>}
            color="danger"
            inverse
          />
        </CCol>
      </CRow>

      {/* QUICK ACTIONS / WELCOME AREA */}
      <CRow>
        <CCol xs={12}>
            <CCard className="mb-4">
                <CCardHeader><strong>System Status</strong></CCardHeader>
                <CCardBody>
                    <p className="text-muted">
                        Welcome to <strong>EWC LIS</strong>. The system is currently online and listening for instrument data on port 5001.
                    </p>
                    {/* Placeholder for a chart or recent activity list */}
                    <div style={{ height: '200px', background: '#f8f9fa', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '4px' }}>
                        <span className="text-muted">Activity Graph / Workload Chart will appear here</span>
                    </div>
                </CCardBody>
            </CCard>
        </CCol>
      </CRow>
    </>
  );
}