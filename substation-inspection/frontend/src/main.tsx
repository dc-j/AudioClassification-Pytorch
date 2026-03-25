import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import App from './App';
import './styles/global.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#0ea5e9',
          colorBgContainer: 'transparent',
          colorBorderSecondary: 'rgba(32,128,240,0.3)',
          fontFamily: "'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif",
        },
      }}
    >
      <App />
    </ConfigProvider>
  </StrictMode>
);
