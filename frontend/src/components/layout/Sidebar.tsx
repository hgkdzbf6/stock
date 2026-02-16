import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  LineChartOutlined,
  StockOutlined,
  AppstoreOutlined,
  DownloadOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Sider } = Layout;

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/market',
      icon: <LineChartOutlined />,
      label: '行情',
    },
    {
      key: '/kline',
      icon: <BarChartOutlined />,
      label: 'K线图',
    },
    {
      key: '/strategies',
      icon: <AppstoreOutlined />,
      label: '策略',
    },
    {
      key: '/data-download',
      icon: <DownloadOutlined />,
      label: '数据下载',
    },
    {
      key: '/trading',
      icon: <StockOutlined />,
      label: '交易',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider width={240} theme="dark">
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: '18px',
          fontWeight: 'bold',
        }}
      >
        Stock Platform
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
      />
    </Sider>
  );
};

export default Sidebar;