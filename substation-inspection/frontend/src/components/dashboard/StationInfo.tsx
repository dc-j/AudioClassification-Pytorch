import React from 'react';
import PanelBox from '../common/PanelBox';
import { stationList } from '../../services/mockData';
import './StationInfo.css';

const StationInfo: React.FC = () => {
  return (
    <PanelBox title="场站信息">
      <div className="station-info">
        <div className="station-count">
          <div className="station-count-number">{stationList.length}</div>
          <div className="station-count-label">变电站总数</div>
        </div>
        <div className="station-list">
          {stationList.map((station) => (
            <div key={station.id} className="station-item">
              <span className={`station-dot ${station.status}`} />
              <span className="station-name">{station.name}</span>
            </div>
          ))}
        </div>
      </div>
    </PanelBox>
  );
};

export default StationInfo;
