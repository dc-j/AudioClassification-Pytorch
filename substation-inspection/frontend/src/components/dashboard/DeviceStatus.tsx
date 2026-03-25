import React from 'react';
import PanelBox from '../common/PanelBox';
import { deviceStatusSummary } from '../../services/mockData';
import './DeviceStatus.css';

const DeviceStatus: React.FC = () => {
  const devices = Object.values(deviceStatusSummary);

  return (
    <PanelBox title="巡视状态">
      <div className="device-status-grid">
        {devices.map((device) => (
          <div key={device.name} className="device-status-item">
            <div className="device-status-name">{device.name}</div>
            <div className="device-status-row">
              <div className="device-status-cell">
                <span className="device-status-val">{device.total}</span>
                <span className="device-status-lbl">总数</span>
              </div>
              <div className="device-status-cell online">
                <span className="device-status-val">{device.online}</span>
                <span className="device-status-lbl">在线数</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </PanelBox>
  );
};

export default DeviceStatus;
