import React, { useState } from 'react';
import { Tabs, Table, Button, Tag } from 'antd';
import { PlusOutlined, SettingOutlined, VideoCameraOutlined, RobotOutlined } from '@ant-design/icons';
import PanelBox from '../components/common/PanelBox';

const cameraData = [
  { id: '1', name: '站区摄像头#1', ip: '192.168.1.101', protocol: 'RTSP', status: '在线', area: '220kV区域' },
  { id: '2', name: '站区摄像头#2', ip: '192.168.1.102', protocol: 'RTSP', status: '在线', area: '110kV区域' },
  { id: '3', name: '红外摄像头#1', ip: '192.168.1.201', protocol: 'RTMP', status: '在线', area: '主变区域' },
  { id: '4', name: '站区摄像头#3', ip: '192.168.1.103', protocol: 'RTSP', status: '离线', area: '站区入口' },
];

const robotData = [
  { id: '1', name: '四足机器人A', model: 'QR-200', status: '在线', battery: '85%', lastMaintenance: '2025-07-15' },
  { id: '2', name: '轨道机器人B', model: 'GR-100', status: '在线', battery: '92%', lastMaintenance: '2025-07-20' },
];

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('cameras');

  const cameraColumns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: 'IP地址', dataIndex: 'ip', key: 'ip', width: 140 },
    { title: '协议', dataIndex: 'protocol', key: 'protocol', width: 80 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 80, render: (s: string) => <Tag color={s === '在线' ? '#10b981' : '#ef4444'}>{s}</Tag> },
    { title: '区域', dataIndex: 'area', key: 'area', width: 120 },
    {
      title: '操作', key: 'action', width: 140,
      render: () => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="link" size="small" style={{ color: 'var(--accent-cyan)', padding: 0 }}>编辑</Button>
          <Button type="link" size="small" style={{ color: 'var(--accent-red)', padding: 0 }}>删除</Button>
        </div>
      ),
    },
  ];

  const robotColumns = [
    { title: '名称', dataIndex: 'name', key: 'name' },
    { title: '型号', dataIndex: 'model', key: 'model', width: 100 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 80, render: (s: string) => <Tag color={s === '在线' ? '#10b981' : '#ef4444'}>{s}</Tag> },
    { title: '电量', dataIndex: 'battery', key: 'battery', width: 80 },
    { title: '上次维护', dataIndex: 'lastMaintenance', key: 'lastMaintenance', width: 120 },
    {
      title: '操作', key: 'action', width: 140,
      render: () => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="link" size="small" style={{ color: 'var(--accent-cyan)', padding: 0 }}>编辑</Button>
          <Button type="link" size="small" style={{ color: 'var(--accent-red)', padding: 0 }}>删除</Button>
        </div>
      ),
    },
  ];

  const tabItems = [
    {
      key: 'cameras',
      label: <span><VideoCameraOutlined /> 摄像头管理</span>,
      children: (
        <Table columns={cameraColumns} dataSource={cameraData} rowKey="id" pagination={false} size="small" className="dark-table" />
      ),
    },
    {
      key: 'robots',
      label: <span><RobotOutlined /> 巡检机器人</span>,
      children: (
        <Table columns={robotColumns} dataSource={robotData} rowKey="id" pagination={false} size="small" className="dark-table" />
      ),
    },
    {
      key: 'system',
      label: <span><SettingOutlined /> 系统配置</span>,
      children: (
        <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: 40 }}>
          系统配置管理（告警阈值、巡检策略、权限管理等）
        </div>
      ),
    },
  ];

  return (
    <div style={{ height: '100%' }}>
      <PanelBox
        title="配置管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} size="small" style={{ background: 'var(--chart-blue)' }}>
            新增设备
          </Button>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          style={{ color: 'var(--text-primary)' }}
        />
      </PanelBox>
    </div>
  );
};

export default Settings;
