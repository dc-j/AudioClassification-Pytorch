import React from 'react';
import './PanelBox.css';

interface PanelBoxProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  extra?: React.ReactNode;
}

const PanelBox: React.FC<PanelBoxProps> = ({ title, children, className = '', style, extra }) => {
  return (
    <div className={`panel-box ${className}`} style={style}>
      <div className="panel-box-header">
        <div className="panel-box-title">
          <span className="panel-box-title-icon" />
          <span>{title}</span>
        </div>
        {extra && <div className="panel-box-extra">{extra}</div>}
      </div>
      <div className="panel-box-body">{children}</div>
    </div>
  );
};

export default PanelBox;
