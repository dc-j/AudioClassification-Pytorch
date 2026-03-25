import React from 'react';
import PanelBox from '../common/PanelBox';
import './TopologyView.css';

const equipmentNodes = [
  { id: 'bus220', label: '润能220kV母线', x: '50%', y: '8%', type: 'bus' },
  { id: 'breaker1', label: '断路器', x: '20%', y: '22%', type: 'breaker' },
  { id: 'breaker2', label: '断路器', x: '40%', y: '22%', type: 'breaker' },
  { id: 'breaker3', label: '断路器', x: '60%', y: '22%', type: 'breaker' },
  { id: 'breaker4', label: '断路器', x: '80%', y: '22%', type: 'breaker' },
  { id: 'transformer1', label: '1号主变', x: '20%', y: '45%', type: 'transformer' },
  { id: 'transformer2', label: '2号主变', x: '40%', y: '45%', type: 'transformer' },
  { id: 'compensator', label: '无功补偿', x: '60%', y: '45%', type: 'compensator' },
  { id: 'pt', label: 'PT/CT', x: '80%', y: '45%', type: 'pt' },
  { id: 'bus110', label: '110kV母线', x: '50%', y: '65%', type: 'bus' },
];

const TopologyView: React.FC = () => {
  return (
    <PanelBox title="润能220KV变电站" className="topology-panel" extra={<span>PMT 主线</span>}>
      <div className="topology-container">
        <svg className="topology-lines" viewBox="0 0 600 300" preserveAspectRatio="none">
          <line x1="300" y1="24" x2="120" y2="66" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="300" y1="24" x2="240" y2="66" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="300" y1="24" x2="360" y2="66" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="300" y1="24" x2="480" y2="66" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="120" y1="66" x2="120" y2="135" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="240" y1="66" x2="240" y2="135" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="360" y1="66" x2="360" y2="135" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="480" y1="66" x2="480" y2="135" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="120" y1="135" x2="300" y2="195" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="240" y1="135" x2="300" y2="195" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="360" y1="135" x2="300" y2="195" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
          <line x1="480" y1="135" x2="300" y2="195" stroke="rgba(32,160,255,0.4)" strokeWidth="1" />
        </svg>
        <div className="topology-nodes">
          {equipmentNodes.map((node) => (
            <div
              key={node.id}
              className={`topology-node node-${node.type}`}
              style={{ left: node.x, top: node.y }}
              title={node.label}
            >
              <div className="node-icon">
                {node.type === 'bus' && <div className="icon-bus" />}
                {node.type === 'breaker' && <div className="icon-breaker" />}
                {node.type === 'transformer' && <div className="icon-transformer">T</div>}
                {node.type === 'compensator' && <div className="icon-compensator">C</div>}
                {node.type === 'pt' && <div className="icon-pt">PT</div>}
              </div>
              <div className="node-label">{node.label}</div>
            </div>
          ))}
        </div>
        <div className="topology-progress">
          <div className="progress-label">遍体设备</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '65%' }} />
          </div>
        </div>
      </div>
    </PanelBox>
  );
};

export default TopologyView;
