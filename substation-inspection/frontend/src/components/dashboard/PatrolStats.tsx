import React from 'react';
import ReactECharts from 'echarts-for-react';
import PanelBox from '../common/PanelBox';
import { PlayCircleOutlined, PauseCircleOutlined, CheckCircleOutlined, RobotOutlined } from '@ant-design/icons';
import './PatrolStats.css';

const PatrolStats: React.FC = () => {
  const pieOption = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(6,30,65,0.9)', borderColor: 'rgba(32,128,240,0.3)', textStyle: { color: '#e0f0ff' } },
    series: [
      {
        type: 'pie',
        radius: ['50%', '70%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: 35, name: '执行中', itemStyle: { color: '#10b981' } },
          { value: 147, name: '已完成', itemStyle: { color: '#22d3ee' } },
          { value: 53, name: '暂停', itemStyle: { color: '#f59e0b' } },
          { value: 0, name: '智巡', itemStyle: { color: '#2080f0' } },
        ],
      },
    ],
  };

  return (
    <PanelBox title="巡视统计">
      <div className="patrol-stats-content">
        <div className="patrol-stats-chart">
          <ReactECharts option={pieOption} style={{ height: 120, width: 120 }} />
        </div>
        <div className="patrol-stats-legend">
          <div className="legend-item">
            <PlayCircleOutlined style={{ color: '#10b981', fontSize: 16 }} />
            <span className="legend-label">执行中</span>
            <span className="legend-value" style={{ color: '#10b981' }}>35</span>
          </div>
          <div className="legend-item">
            <CheckCircleOutlined style={{ color: '#22d3ee', fontSize: 16 }} />
            <span className="legend-label">已完成</span>
            <span className="legend-value" style={{ color: '#22d3ee' }}>147</span>
          </div>
          <div className="legend-item">
            <PauseCircleOutlined style={{ color: '#f59e0b', fontSize: 16 }} />
            <span className="legend-label">暂停</span>
            <span className="legend-value" style={{ color: '#f59e0b' }}>53</span>
          </div>
          <div className="legend-item">
            <RobotOutlined style={{ color: '#2080f0', fontSize: 16 }} />
            <span className="legend-label">智巡</span>
            <span className="legend-value" style={{ color: '#2080f0' }}>0</span>
          </div>
        </div>
      </div>
    </PanelBox>
  );
};

export default PatrolStats;
