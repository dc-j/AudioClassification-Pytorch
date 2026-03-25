import React from 'react';
import ReactECharts from 'echarts-for-react';
import PanelBox from '../components/common/PanelBox';

const Analysis: React.FC = () => {
  const trendOption = {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(6,30,65,0.9)', borderColor: 'rgba(32,128,240,0.3)', textStyle: { color: '#e0f0ff' } },
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月'],
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8' },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8' },
      splitLine: { lineStyle: { color: 'rgba(32,128,240,0.1)' } },
    },
    series: [
      {
        name: '告警次数',
        type: 'line',
        smooth: true,
        data: [20, 35, 28, 42, 38, 25, 18],
        lineStyle: { color: '#ef4444' },
        itemStyle: { color: '#ef4444' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(239,68,68,0.3)' }, { offset: 1, color: 'rgba(239,68,68,0)' }] } },
      },
      {
        name: '巡检次数',
        type: 'line',
        smooth: true,
        data: [120, 132, 145, 160, 155, 170, 180],
        lineStyle: { color: '#22d3ee' },
        itemStyle: { color: '#22d3ee' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(34,211,238,0.3)' }, { offset: 1, color: 'rgba(34,211,238,0)' }] } },
      },
    ],
    legend: { textStyle: { color: '#8bb8e8' }, top: 0 },
  };

  const barOption = {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(6,30,65,0.9)', borderColor: 'rgba(32,128,240,0.3)', textStyle: { color: '#e0f0ff' } },
    grid: { top: 30, right: 20, bottom: 30, left: 50 },
    xAxis: {
      type: 'category',
      data: ['变压器', '断路器', '互感器', '避雷器', '母线', '开关柜'],
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8', rotate: 20 },
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8' },
      splitLine: { lineStyle: { color: 'rgba(32,128,240,0.1)' } },
    },
    series: [
      {
        name: '缺陷数',
        type: 'bar',
        data: [12, 8, 5, 3, 6, 11],
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: '#22d3ee' }, { offset: 1, color: 'rgba(34,211,238,0.2)' }],
          },
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: 24,
      },
    ],
  };

  const heatmapOption = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(6,30,65,0.9)', borderColor: 'rgba(32,128,240,0.3)', textStyle: { color: '#e0f0ff' } },
    grid: { top: 10, right: 20, bottom: 30, left: 80 },
    xAxis: {
      type: 'category',
      data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8' },
    },
    yAxis: {
      type: 'category',
      data: ['主变1', '主变2', '220kV母线', '110kV母线'],
      axisLine: { lineStyle: { color: 'rgba(32,128,240,0.3)' } },
      axisLabel: { color: '#8bb8e8' },
    },
    visualMap: { min: 20, max: 90, calculable: true, orient: 'horizontal', left: 'center', bottom: -5, show: false, inRange: { color: ['#0ea5e9', '#f59e0b', '#ef4444'] } },
    series: [
      {
        type: 'heatmap',
        data: [
          [0, 0, 42], [1, 0, 45], [2, 0, 55], [3, 0, 58], [4, 0, 52], [5, 0, 44],
          [0, 1, 38], [1, 1, 40], [2, 1, 50], [3, 1, 62], [4, 1, 48], [5, 1, 41],
          [0, 2, 35], [1, 2, 36], [2, 2, 48], [3, 2, 52], [4, 2, 46], [5, 2, 37],
          [0, 3, 32], [1, 3, 34], [2, 3, 45], [3, 3, 55], [4, 3, 43], [5, 3, 35],
        ],
        label: { show: true, color: '#e0f0ff', fontSize: 11, formatter: (p: { value: number[] }) => p.value[2] + '°C' },
        itemStyle: { borderWidth: 2, borderColor: 'var(--bg-primary)' },
      },
    ],
  };

  return (
    <div style={{ height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 8 }}>
      <PanelBox title="告警与巡检趋势分析">
        <ReactECharts option={trendOption} style={{ height: '100%' }} />
      </PanelBox>
      <PanelBox title="设备缺陷分布">
        <ReactECharts option={barOption} style={{ height: '100%' }} />
      </PanelBox>
      <PanelBox title="红外热成像温度分布">
        <ReactECharts option={heatmapOption} style={{ height: '100%' }} />
      </PanelBox>
      <PanelBox title="能效分析">
        <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>📊</div>
            <div>能效效能分析模块</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>发电指标 · 设备可利用率 · 功率曲线</div>
          </div>
        </div>
      </PanelBox>
    </div>
  );
};

export default Analysis;
