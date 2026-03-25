export interface StationInfo {
  id: string;
  name: string;
  type: string;
  status: 'normal' | 'warning' | 'error';
  voltageLevel: string;
}

export interface PatrolRecord {
  id: string;
  taskName: string;
  type: '例行巡视' | '特殊巡视' | '熄灯巡视' | '全面巡视';
  status: '待执行' | '执行中' | '已完成' | '暂停' | '智巡';
  startTime: string;
  endTime?: string;
  executor: string;
  result?: string;
}

export interface PatrolTask {
  id: string;
  name: string;
  planDate: string;
  status: '待执行' | '执行中' | '已完成';
  deviceCount: number;
  pointCount: number;
  progress: number;
}

export interface AlarmRecord {
  id: string;
  level: '一般' | '重要' | '紧急';
  source: string;
  content: string;
  time: string;
  status: '未处理' | '处理中' | '已处理';
  type: string;
  area: string;
}

export interface DeviceInfo {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'warning';
  location: string;
  lastInspection?: string;
}

export interface PatrolStatItem {
  label: string;
  value: number;
  icon?: string;
  color?: string;
}

export interface DefectStatItem {
  type: string;
  count: number;
  percentage: number;
}

export interface UserInfo {
  id: string;
  username: string;
  name: string;
  role: 'admin' | 'operator' | 'viewer';
  avatar?: string;
}
