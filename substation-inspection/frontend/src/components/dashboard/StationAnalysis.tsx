import React from 'react';
import ReactECharts from 'echarts-for-react';
import PanelBox from '../common/PanelBox';
import './StationAnalysis.css';

const StationAnalysis: React.FC = () => {
  const gaugeOption = (title: string, value: number, color: string) => ({
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        radius: '90%',
        center: ['50%', '55%'],
        min: 0,
        max: 100,
        progress: { show: true, width: 8, itemStyle: { color } },
        axisLine: { lineStyle: { width: 8, color: [[1, 'rgba(32,128,240,0.15)']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        title: { show: true, offsetCenter: [0, '70%'], fontSize: 11, color: '#8bb8e8' },
        detail: {
          valueAnimation: true,
          fontSize: 18,
          fontWeight: 700,
          color,
          offsetCenter: [0, '30%'],
          formatter: '{value}%',
        },
        data: [{ value, name: title }],
      },
    ],
  });

  return (
    <PanelBox title="场站分析">
      <div className="station-analysis-grid">
        <div className="gauge-item">
          <ReactECharts option={gaugeOption('未执行率', 15, '#ef4444')} style={{ height: 100 }} />
        </div>
        <div className="gauge-item">
          <ReactECharts option={gaugeOption('完成率', 85, '#10b981')} style={{ height: 100 }} />
        </div>
        <div className="analysis-tags">
          <span className="tag tag-blue">智能分析</span>
          <span className="tag tag-green">振动分析</span>
          <span className="tag tag-cyan">来源功率</span>
        </div>
      </div>
    </PanelBox>
  );
};

export default StationAnalysis;
