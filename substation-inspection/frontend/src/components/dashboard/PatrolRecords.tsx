import React from 'react';
import { Table, Tag } from 'antd';
import PanelBox from '../common/PanelBox';
import './PatrolRecords.css';

const statusColors: Record<string, string> = {
  '全部': '#2080f0',
  '执行中': '#10b981',
  '已完成': '#22d3ee',
  '暂止': '#8bb8e8',
};

const columns = [
  { title: '', dataIndex: 'label', key: 'label', width: 60 },
  { title: '总数量', dataIndex: 'total', key: 'total', width: 60, render: (v: number) => <span style={{ color: '#e0f0ff' }}>{v}</span> },
  { title: '执行中', dataIndex: 'executing', key: 'executing', width: 60, render: (v: number) => <span style={{ color: '#10b981' }}>{v}</span> },
  { title: '已完成', dataIndex: 'completed', key: 'completed', width: 60, render: (v: number) => <span style={{ color: '#22d3ee' }}>{v}</span> },
  { title: '暂止', dataIndex: 'paused', key: 'paused', width: 50, render: (v: number) => <span style={{ color: '#8bb8e8' }}>{v}</span> },
];

const data = [
  { key: '1', label: <Tag color={statusColors['全部']}>全部</Tag>, total: 200, executing: 147, completed: 53, paused: 0 },
  { key: '2', label: <Tag color={statusColors['执行中']}>例行</Tag>, total: 147, executing: 100, completed: 47, paused: 0 },
  { key: '3', label: <Tag color={statusColors['已完成']}>特殊巡视</Tag>, total: 30, executing: 25, completed: 5, paused: 0 },
  { key: '4', label: <Tag color={statusColors['暂止']}>四足</Tag>, total: 23, executing: 22, completed: 1, paused: 0 },
];

const PatrolRecords: React.FC = () => {
  return (
    <PanelBox title="巡视记录">
      <Table
        columns={columns}
        dataSource={data}
        pagination={false}
        size="small"
        bordered={false}
        className="dark-table"
      />
    </PanelBox>
  );
};

export default PatrolRecords;
