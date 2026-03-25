import React from 'react';
import { Table, Tag } from 'antd';
import PanelBox from '../common/PanelBox';
import { alarmRecords } from '../../services/mockData';
import type { AlarmRecord } from '../../types';
import './AlarmTable.css';

const levelColors: Record<string, string> = {
  '紧急': '#ef4444',
  '重要': '#f59e0b',
  '一般': '#22d3ee',
};

const statusColors: Record<string, string> = {
  '未处理': '#ef4444',
  '处理中': '#f59e0b',
  '已处理': '#10b981',
};

const columns = [
  {
    title: '告警级别',
    dataIndex: 'level',
    key: 'level',
    width: 80,
    render: (level: string) => <Tag color={levelColors[level]}>{level}</Tag>,
  },
  { title: '告警源', dataIndex: 'source', key: 'source', width: 120 },
  { title: '告警内容', dataIndex: 'content', key: 'content', ellipsis: true },
  {
    title: '告警状态',
    dataIndex: 'status',
    key: 'status',
    width: 80,
    render: (status: string) => <Tag color={statusColors[status]}>{status}</Tag>,
  },
  { title: '告警类型', dataIndex: 'type', key: 'type', width: 80 },
  { title: '告警区域', dataIndex: 'area', key: 'area', width: 100 },
  { title: '告警时间', dataIndex: 'time', key: 'time', width: 150 },
];

const AlarmTable: React.FC = () => {
  return (
    <PanelBox title="告警记录" extra={<span style={{ cursor: 'pointer', color: 'var(--accent-cyan)' }}>暂无新告警</span>}>
      <Table<AlarmRecord>
        columns={columns}
        dataSource={alarmRecords}
        rowKey="id"
        pagination={false}
        size="small"
        scroll={{ y: 120 }}
        className="dark-table alarm-table"
      />
    </PanelBox>
  );
};

export default AlarmTable;
