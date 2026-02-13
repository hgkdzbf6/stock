import { Layout } from 'antd';
import Header from './Header';
import Sidebar from './Sidebar';
import { Outlet } from 'react-router-dom';

const { Content, Footer } = Layout;

const LayoutComponent = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout>
        <Header />
        <Content style={{ margin: '24px 16px 0', overflow: 'auto' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: '#fff',
              borderRadius: 8,
            }}
          >
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Stock Platform ©{new Date().getFullYear()} Created by AI Assistant
        </Footer>
      </Layout>
    </Layout>
  );
};

export default LayoutComponent;
