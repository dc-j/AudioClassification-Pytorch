import type { StationInfo, PatrolRecord, AlarmRecord, PatrolTask } from '../types';

export const stationList: StationInfo[] = [
  { id: '1', name: '润能220kV站', type: '220kV变电站', status: 'normal', voltageLevel: '220kV' },
  { id: '2', name: '润能110kV2号站', type: '110kV变电站', status: 'normal', voltageLevel: '110kV' },
  { id: '3', name: '润能110kV3号站', type: '110kV变电站', status: 'warning', voltageLevel: '110kV' },
];

export const patrolRecords: PatrolRecord[] = [
  { id: '1', taskName: '例行巡视', type: '例行巡视', status: '执行中', startTime: '2025-07-29 08:00', executor: '智能机器人A', result: '' },
  { id: '2', taskName: '特殊巡视', type: '特殊巡视', status: '已完成', startTime: '2025-07-29 06:00', endTime: '2025-07-29 07:30', executor: '巡检人员张三', result: '正常' },
  { id: '3', taskName: '熄灯巡视', type: '熄灯巡视', status: '已完成', startTime: '2025-07-28 22:00', endTime: '2025-07-29 01:00', executor: '智能机器人B', result: '正常' },
  { id: '4', taskName: '全面巡视', type: '全面巡视', status: '待执行', startTime: '2025-07-30 08:00', executor: '巡检人员李四' },
];

export const patrolTasks: PatrolTask[] = [
  { id: '1', name: '220kV设备日常巡检', planDate: '2025-07-29', status: '执行中', deviceCount: 12, pointCount: 86, progress: 65 },
  { id: '2', name: '110kV开关柜巡检', planDate: '2025-07-29', status: '待执行', deviceCount: 8, pointCount: 52, progress: 0 },
  { id: '3', name: '主变压器红外测温', planDate: '2025-07-29', status: '已完成', deviceCount: 3, pointCount: 24, progress: 100 },
];

export const alarmRecords: AlarmRecord[] = [
  { id: '1', level: '紧急', source: '220kV母线PT', content: '温度超过阈值85℃', time: '2025-07-29 15:20:08', status: '未处理', type: '温度告警', area: '220kV区域' },
  { id: '2', level: '重要', source: '110kV开关柜#3', content: 'SF6气压低于告警值', time: '2025-07-29 14:55:32', status: '处理中', type: '气压告警', area: '110kV区域' },
  { id: '3', level: '一般', source: '站区摄像头#12', content: '画面异常抖动', time: '2025-07-29 14:30:15', status: '已处理', type: '设备告警', area: '站区' },
  { id: '4', level: '重要', source: '巡检机器人A', content: '电池电量低于20%', time: '2025-07-29 13:45:00', status: '处理中', type: '设备告警', area: '站区' },
  { id: '5', level: '一般', source: '110kV2号变压器', content: '油温偏高', time: '2025-07-29 12:10:22', status: '已处理', type: '温度告警', area: '110kV区域' },
];

export const patrolSummary = {
  total: { label: '总任务', value: 200 },
  executing: { label: '执行中', value: 35 },
  completed: { label: '已完成', value: 147 },
  paused: { label: '暂停', value: 53 },
  smart: { label: '智巡', value: 0 },
};

export const patrolRecordSummary = {
  all: { label: '全部', count: 200 },
  executing: { label: '执行中', count: 147 },
  paused: { label: '已完成', count: 53 },
  completed: { label: '暂止', count: 0 },
};

export const deviceStatusSummary = {
  robot4wd: { name: '四足机器人', total: 1, online: 1 },
  camera: { name: '摄像头', total: 38, online: 38 },
  infrared: { name: '红外装置', total: 2, online: 2 },
  railRobot: { name: '轨道机器人', total: 2, online: 2 },
};

export const defectStats = {
  total: 45,
  categories: [
    { type: '普通', count: 30, color: '#22d3ee' },
    { type: '严重', count: 10, color: '#f59e0b' },
    { type: '危急', count: 5, color: '#ef4444' },
  ],
};
