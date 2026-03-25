import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { UserOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import './Header.css';

const navItems = [
  { key: '/', label: '信息总览' },
  { key: '/patrol-task', label: '巡报任务' },
  { key: '/patrol-monitor', label: '巡视监控' },
  { key: '/analysis', label: '分析决策' },
  { key: '/settings', label: '配置管理' },
];

const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [time, setTime] = useState(dayjs());

  useEffect(() => {
    const timer = setInterval(() => setTime(dayjs()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="app-header">
      <div className="header-title">变电站智能巡检系统</div>
      <nav className="header-nav">
        {navItems.map((item) => (
          <div
            key={item.key}
            className={`header-nav-item ${location.pathname === item.key ? 'active' : ''}`}
            onClick={() => navigate(item.key)}
          >
            {item.label}
          </div>
        ))}
      </nav>
      <div className="header-right">
        <div className="header-time">
          <div className="header-clock">{time.format('HH:mm:ss')}</div>
          <div className="header-date">
            <span>{time.format('ddd')}</span>
            <span>{time.format('YYYY-MM-DD')}</span>
          </div>
        </div>
        <div className="header-user">
          <UserOutlined />
          <span>管理员</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
