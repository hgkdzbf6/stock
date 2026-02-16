/** K线图仪表板 - 整合市场K线图和板块K线图 */
import { Tabs } from 'antd';
import MarketKLineChart from '@components/charts/MarketKLineChart';
import SectorKLineChart from '@components/charts/SectorKLineChart';

export default function KLineDashboard() {
  const tabItems = [
    {
      key: 'market',
      label: '市场K线',
      children: (
        <div style={{ padding: '16px' }}>
          <MarketKLineChart height="700px" />
        </div>
      )
    },
    {
      key: 'sector',
      label: '板块K线',
      children: (
        <div style={{ padding: '16px' }}>
          <SectorKLineChart height="700px" />
        </div>
      )
    }
  ];

  return (
    <div style={{ padding: '24px', background: '#f0f2f5', minHeight: '100vh' }}>
      <h1 style={{ 
        textAlign: 'center', 
        marginBottom: '24px',
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#333'
      }}>
        K线图仪表板
      </h1>
      
      <Tabs
        defaultActiveKey="market"
        items={tabItems}
        size="large"
        tabBarStyle={{
          marginBottom: '24px',
          background: '#fff',
          padding: '8px 16px',
          borderRadius: '4px'
        }}
      />
    </div>
  );
}