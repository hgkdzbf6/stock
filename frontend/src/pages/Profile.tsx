import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  message,
  Avatar,
  Descriptions,
  Tabs,
  Space,
  Divider,
  Upload,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  PhoneOutlined,
  EditOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

const { TabPane } = Tabs;

interface ProfileForm {
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
}

interface PasswordForm {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

const Profile: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);
  const [form] = Form.useForm<ProfileForm>();
  const [passwordForm] = Form.useForm<PasswordForm>();
  const navigate = useNavigate();
  const user = authService.getCurrentUserFromStorage();

  // 加载用户信息
  useEffect(() => {
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      setProfileLoading(true);
      const userData = await authService.getCurrentUser();
      form.setFieldsValue({
        username: userData.username,
        email: userData.email,
        full_name: userData.full_name,
        phone: userData.phone,
      });
    } catch (error) {
      console.error('加载用户信息失败:', error);
      message.error('加载用户信息失败');
    } finally {
      setProfileLoading(false);
    }
  };

  const handleProfileUpdate = async (values: ProfileForm) => {
    setLoading(true);
    try {
      await authService.updateProfile({
        full_name: values.full_name,
        phone: values.phone,
        email: values.email,
      });
      message.success('个人信息更新成功');
      
      // 更新本地存储的用户信息
      const updatedUser = {
        ...user,
        full_name: values.full_name,
        phone: values.phone,
        email: values.email,
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      
      // 重新加载用户信息
      await loadUserProfile();
    } catch (error: any) {
      message.error(error?.response?.data?.detail || '更新失败');
      console.error('更新失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: PasswordForm) => {
    setLoading(true);
    try {
      await authService.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      });
      message.success('密码修改成功，请重新登录');
      passwordForm.resetFields();
      
      // 退出登录
      await authService.logout();
      navigate('/login');
    } catch (error: any) {
      message.error(error?.response?.data?.detail || '密码修改失败');
      console.error('密码修改失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    action: '/api/auth/avatar', // TODO: 替换为实际的头像上传接口
    showUploadList: false,
    beforeUpload: (file) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png';
      if (!isJpgOrPng) {
        message.error('只能上传 JPG/PNG 格式的图片!');
        return false;
      }
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB!');
        return false;
      }
      return true;
    },
    onChange: (info) => {
      if (info.file.status === 'done') {
        message.success('头像上传成功');
        loadUserProfile();
      } else if (info.file.status === 'error') {
        message.error('头像上传失败');
      }
    },
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Card loading={profileLoading}>
        {/* 用户信息概览 */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
          <Upload {...uploadProps}>
            <Avatar
              size={80}
              icon={<UserOutlined />}
              style={{ cursor: 'pointer', backgroundColor: '#1890ff' }}
            />
          </Upload>
          <div style={{ marginLeft: '24px' }}>
            <h2 style={{ margin: '0 0 8px 0' }}>{user?.full_name || user?.username}</h2>
            <p style={{ margin: '0', color: '#8c8c8c' }}>@{user?.username}</p>
            <p style={{ margin: '4px 0 0 0', color: '#8c8c8c' }}>{user?.email}</p>
          </div>
        </div>

        <Divider />

        {/* 标签页 */}
        <Tabs defaultActiveKey="info">
          {/* 基本信息 */}
          <TabPane tab="基本信息" key="info">
            <Form
              form={form}
              layout="vertical"
              onFinish={handleProfileUpdate}
              initialValues={{
                username: user?.username,
                email: user?.email,
                full_name: user?.full_name,
                phone: user?.phone,
              }}
            >
              <Form.Item
                label="用户名"
                name="username"
                rules={[{ required: true, message: '请输入用户名!' }]}
              >
                <Input
                  prefix={<UserOutlined />}
                  disabled
                  placeholder="用户名不可修改"
                />
              </Form.Item>

              <Form.Item
                label="姓名"
                name="full_name"
              >
                <Input prefix={<EditOutlined />} placeholder="请输入姓名" />
              </Form.Item>

              <Form.Item
                label="邮箱"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱!' },
                  { type: 'email', message: '请输入有效的邮箱地址!' },
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
              </Form.Item>

              <Form.Item
                label="手机号"
                name="phone"
                rules={[
                  { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码' },
                ]}
              >
                <Input prefix={<PhoneOutlined />} placeholder="请输入手机号" />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                >
                  保存修改
                </Button>
              </Form.Item>
            </Form>
          </TabPane>

          {/* 修改密码 */}
          <TabPane tab="修改密码" key="password">
            <Form
              form={passwordForm}
              layout="vertical"
              onFinish={handlePasswordChange}
            >
              <Form.Item
                label="当前密码"
                name="old_password"
                rules={[{ required: true, message: '请输入当前密码!' }]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请输入当前密码"
                />
              </Form.Item>

              <Form.Item
                label="新密码"
                name="new_password"
                rules={[
                  { required: true, message: '请输入新密码!' },
                  { min: 6, message: '密码至少6个字符' },
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请输入新密码（至少6个字符）"
                />
              </Form.Item>

              <Form.Item
                label="确认新密码"
                name="confirm_password"
                dependencies={['new_password']}
                hasFeedback
                rules={[
                  { required: true, message: '请确认新密码!' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('new_password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('两次输入的密码不一致!'));
                    },
                  }),
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="请再次输入新密码"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SaveOutlined />}
                  loading={loading}
                  danger
                >
                  修改密码
                </Button>
              </Form.Item>

              <div style={{ marginTop: '16px', padding: '16px', background: '#fffbe6', borderRadius: '4px', border: '1px solid #ffe58f' }}>
                <p style={{ margin: '0', color: '#faad14' }}>
                  <strong>提示：</strong>修改密码后，您需要重新登录。
                </p>
              </div>
            </Form>
          </TabPane>

          {/* 账号信息 */}
          <TabPane tab="账号信息" key="account">
            <Descriptions bordered column={1}>
              <Descriptions.Item label="用户ID">{user?.id}</Descriptions.Item>
              <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{user?.email}</Descriptions.Item>
              <Descriptions.Item label="姓名">{user?.full_name || '-'}</Descriptions.Item>
              <Descriptions.Item label="手机号">{user?.phone || '-'}</Descriptions.Item>
              <Descriptions.Item label="注册时间">-</Descriptions.Item>
              <Descriptions.Item label="最后登录">-</Descriptions.Item>
            </Descriptions>

            <Divider />

            <Space direction="vertical" style={{ width: '100%' }}>
              <h3>安全设置</h3>
              <div style={{ padding: '16px', background: '#f5f5f5', borderRadius: '4px' }}>
                <p style={{ margin: '0 0 8px 0' }}>
                  <strong>密码强度：</strong>
                </p>
                <p style={{ margin: '0', color: '#52c41a' }}>强</p>
              </div>
              <div style={{ padding: '16px', background: '#f5f5f5', borderRadius: '4px' }}>
                <p style={{ margin: '0 0 8px 0' }}>
                  <strong>两步验证：</strong>
                </p>
                <p style={{ margin: '0', color: '#8c8c8c' }}>未开启（暂不支持）</p>
              </div>
            </Space>
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default Profile;