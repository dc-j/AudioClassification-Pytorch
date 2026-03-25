import React from 'react';
import ReactECharts from 'echarts-for-react';
import PanelBox from '../common/PanelBox';
import { defectStats } from '../../services/mockData';
import './DefectStats.css';

const DefectStats: React.FC = () => {
  const option = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(6,30,65,0.9)', borderColor: 'rgba(32,128,240,0.3)', textStyle: { color: '#e0f0ff' } },
    series: [
      {
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['50%', '50%'],
        startAngle: 90,
        label: { show: false },
        data: defectStats.categories.map((c) => ({
          value: c.count,
          name: c.type,
          itemStyle: { color: c.color },
        })),
      },
    ],
  };

  return (
    <PanelBox title="缺陷统计">
      <div className="defect-stats-content">
        <div className="defect-chart-wrap">
          <ReactECharts option={option} style={{ height: 130, width: 130 }} />
          <div className="defect-center-text">
            <span className="defect-total-val">{defectStats.total}</span>
          </div>
        </div>
        <div className="defect-legend">
          {defectStats.categories.map((c) => (
            <div key={c.type} className="defect-legend-item">
              <span className="defect-dot" style={{ background: c.color }} />
              <span className="defect-type">{c.type}</span>
              <span className="defect-count" style={{ color: c.color }}>{c.count}</span>
            </div>
          ))}
        </div>
      </div>
    </PanelBox>
  );
};

export default DefectStats;
