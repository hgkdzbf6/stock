import { useParams } from 'react-router-dom';
import { Card, Row, Col } from 'antd';

const StockDetail = () => {
  const { code } = useParams();

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>
        股票详情 - {code}
      </h1>

      <Row gutter={16}>
        <Col span={24}>
          <Card title="基本信息">
            <p>股票代码: {code}</p>
            <p>股票名称: 待加载</p>
            <p>市场: 待加载</p>
            <p>板块: 待加载</p>
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="K线图">
            <div style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              K线图表组件 - 待实现
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StockDetail;
