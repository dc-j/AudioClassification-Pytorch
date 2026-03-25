import React from 'react';
import './StatCard.css';

interface StatCardProps {
  label: string;
  value: number | string;
  icon?: React.ReactNode;
  color?: string;
  unit?: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon, color = 'var(--accent-cyan)', unit }) => {
  return (
    <div className="stat-card" style={{ borderColor: color }}>
      {icon && <div className="stat-card-icon" style={{ color }}>{icon}</div>}
      <div className="stat-card-info">
        <div className="stat-card-value" style={{ color }}>
          {value}
          {unit && <span className="stat-card-unit">{unit}</span>}
        </div>
        <div className="stat-card-label">{label}</div>
      </div>
    </div>
  );
};

export default StatCard;
