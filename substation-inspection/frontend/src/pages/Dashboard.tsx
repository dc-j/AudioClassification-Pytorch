import React from 'react';
import StationInfo from '../components/dashboard/StationInfo';
import DeviceStatus from '../components/dashboard/DeviceStatus';
import StationAnalysis from '../components/dashboard/StationAnalysis';
import TopologyView from '../components/dashboard/TopologyView';
import PatrolRecords from '../components/dashboard/PatrolRecords';
import PatrolStats from '../components/dashboard/PatrolStats';
import DefectStats from '../components/dashboard/DefectStats';
import AlarmTable from '../components/dashboard/AlarmTable';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <div className="dashboard-left">
        <StationInfo />
        <DeviceStatus />
        <StationAnalysis />
      </div>
      <div className="dashboard-center">
        <div className="dashboard-center-top">
          <TopologyView />
        </div>
        <div className="dashboard-center-bottom">
          <AlarmTable />
        </div>
      </div>
      <div className="dashboard-right">
        <PatrolRecords />
        <PatrolStats />
        <DefectStats />
      </div>
    </div>
  );
};

export default Dashboard;
