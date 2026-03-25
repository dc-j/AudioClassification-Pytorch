import React from 'react';
import { Table, Button, Tag, Progress } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import PanelBox from '../components/common/PanelBox';
import { patrolTasks } from '../services/mockData';
import type { PatrolTask as PatrolTaskType } from '../types';

const statusColors: Record<string, string> = {
  '待执行': '#8bb8e8',
  '执行中': '#10b981',
  '已完成': '#22d3ee',
};

const columns = [
  { title: '任务名称', dataIndex: 'name', key: 'name' },
  { title: '计划日期', dataIndex: 'planDate', key: 'planDate', width: 120 },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    render: (status: string) => <Tag color={statusColors[status]}>{status}</Tag>,
  },
  { title: '设备数', dataIndex: 'deviceCount', key: 'deviceCount', width: 80 },
  { title: '巡检点', dataIndex: 'pointCount', key: 'pointCount', width: 80 },
  {
    title: '进度',
    dataIndex: 'progress',
    key: 'progress',
    width: 150,
    render: (progress: number) => (
      <Progress percent={progress} size="small" strokeColor="#22d3ee" trailColor="rgba(32,128,240,0.15)" />
    ),
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    render: () => (
      <div style={{ display: 'flex', gap: 8 }}>
        <Button type="link" size="small" style={{ color: 'var(--accent-cyan)', padding: 0 }}>详情</Button>
        <Button type="link" size="small" style={{ color: 'var(--accent-yellow)', padding: 0 }}>编辑</Button>
      </div>
    ),
  },
];

const PatrolTask: React.FC = () => {
  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <PanelBox
        title="巡检任务管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} size="small" style={{ background: 'var(--chart-blue)' }}>
            新建任务
          </Button>
        }
      >
        <Table<PatrolTaskType>
          columns={columns}
          dataSource={patrolTasks}
          rowKey="id"
          pagination={false}
          size="small"
          className="dark-table"
        />
      </PanelBox>
    </div>
  );
};

export default PatrolTask;
