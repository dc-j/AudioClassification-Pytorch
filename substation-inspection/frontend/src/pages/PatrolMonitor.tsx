import React from 'react';
import PanelBox from '../components/common/PanelBox';

const PatrolMonitor: React.FC = () => {
  return (
    <div style={{ height: '100%', display: 'grid', gridTemplateColumns: '1fr 1fr', gridTemplateRows: '1fr 1fr', gap: 8 }}>
      {[1, 2, 3, 4].map((i) => (
        <PanelBox key={i} title={`监控画面 #${i}`}>
          <div
            style={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-muted)',
              fontSize: 14,
              background: 'rgba(0,0,0,0.3)',
              borderRadius: 4,
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 36, marginBottom: 8 }}>📹</div>
              <div>视频流接入点 #{i}</div>
              <div style={{ fontSize: 12, marginTop: 4 }}>RTSP / RTMP / HLS</div>
            </div>
          </div>
        </PanelBox>
      ))}
    </div>
  );
};

export default PatrolMonitor;
