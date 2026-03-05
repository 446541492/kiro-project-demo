/**
 * 个人中心页面
 * 用户信息展示、密码修改、2FA 管理、设备列表、退出登录
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  List,
  Typography,
  Button,
  Modal,
  Form,
  Input,
  message,
  Tag,
  Space,
  Divider,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  SafetyOutlined,
  MobileOutlined,
  LogoutOutlined,
  SkinOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';
import authApi, { type ChangePasswordRequest } from '@/api/auth';
import ThemeSwitch from '@/components/ThemeSwitch';
import type { DeviceInfo } from '@/types';

/** 密码强度正则 */
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/;

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const [passwordModalOpen, setPasswordModalOpen] = useState(false);
  const [devicesModalOpen, setDevicesModalOpen] = useState(false);
  const [devices, setDevices] = useState<DeviceInfo[]>([]);
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordForm] = Form.useForm();

  /** 加载设备列表 */
  const loadDevices = async () => {
    try {
      const resp = await authApi.getDevices();
      setDevices(resp.data);
    } catch {
      // 错误已在拦截器中处理
    }
  };

  /** 修改密码 */
  const handleChangePassword = async (values: ChangePasswordRequest & { confirm_password: string }) => {
    setChangingPassword(true);
    try {
      await authApi.changePassword({
        old_password: values.old_password,
        new_password: values.new_password,
      });
      message.success('密码修改成功');
      setPasswordModalOpen(false);
      passwordForm.resetFields();
    } catch {
      // 错误已在拦截器中处理
    } finally {
      setChangingPassword(false);
    }
  };

  /** 退出登录 */
  const handleLogout = () => {
    Modal.confirm({
      title: '确认退出',
      content: '确定要退出登录吗？',
      okText: '退出',
      cancelText: '取消',
      onOk: async () => {
        await logout();
        navigate('/login', { replace: true });
      },
    });
  };

  if (!user) return null;


  /** 功能菜单项 */
  const menuItems = [
    {
      icon: <UserOutlined />,
      title: '用户信息',
      description: `用户名: ${user.username}`,
      extra: (
        <Space direction="vertical" size={0} style={{ textAlign: 'right', fontSize: 12, color: '#999' }}>
          {user.email && <span>{user.email}</span>}
          {user.phone && <span>{user.phone}</span>}
        </Space>
      ),
    },
    {
      icon: <LockOutlined />,
      title: '修改密码',
      description: '更新你的登录密码',
      onClick: () => setPasswordModalOpen(true),
    },
    {
      icon: <SafetyOutlined />,
      title: '两步验证',
      description: user.is_2fa_enabled ? '已启用' : '未启用',
      extra: (
        <Tag color={user.is_2fa_enabled ? 'green' : 'default'}>
          {user.is_2fa_enabled ? '已启用' : '未启用'}
        </Tag>
      ),
      onClick: () => navigate('/2fa/setup'),
    },
    {
      icon: <MobileOutlined />,
      title: '登录设备',
      description: '查看登录过的设备',
      onClick: () => {
        loadDevices();
        setDevicesModalOpen(true);
      },
    },
    {
      icon: <SkinOutlined />,
      title: '主题设置',
      description: '切换明暗主题',
      extra: <ThemeSwitch />,
    },
  ];

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <Typography.Title level={4}>个人中心</Typography.Title>

      <Card>
        <List
          itemLayout="horizontal"
          dataSource={menuItems}
          renderItem={(item) => (
            <List.Item
              style={{ cursor: item.onClick ? 'pointer' : 'default' }}
              onClick={item.onClick}
              extra={item.extra}
            >
              <List.Item.Meta
                avatar={<span style={{ fontSize: 20, color: '#1677ff' }}>{item.icon}</span>}
                title={item.title}
                description={item.description}
              />
            </List.Item>
          )}
        />

        <Divider />

        <Button
          danger
          block
          icon={<LogoutOutlined />}
          onClick={handleLogout}
        >
          退出登录
        </Button>
      </Card>

      {/* 修改密码弹窗 */}
      <Modal
        title="修改密码"
        open={passwordModalOpen}
        onCancel={() => {
          setPasswordModalOpen(false);
          passwordForm.resetFields();
        }}
        footer={null}
      >
        <Form form={passwordForm} onFinish={handleChangePassword} layout="vertical">
          <Form.Item
            name="old_password"
            label="当前密码"
            rules={[{ required: true, message: '请输入当前密码' }]}
          >
            <Input.Password aria-label="当前密码" />
          </Form.Item>
          <Form.Item
            name="new_password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { pattern: PASSWORD_REGEX, message: '至少 8 位，包含大写、小写、数字和特殊字符' },
            ]}
          >
            <Input.Password aria-label="新密码" />
          </Form.Item>
          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password aria-label="确认新密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={changingPassword}>
              确认修改
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 设备列表弹窗 */}
      <Modal
        title="登录设备"
        open={devicesModalOpen}
        onCancel={() => setDevicesModalOpen(false)}
        footer={null}
      >
        <List
          dataSource={devices}
          locale={{ emptyText: '暂无设备记录' }}
          renderItem={(device) => (
            <List.Item>
              <List.Item.Meta
                avatar={<MobileOutlined style={{ fontSize: 20 }} />}
                title={device.device_name || '未知设备'}
                description={
                  <Space direction="vertical" size={0}>
                    {device.ip_address && <span>IP: {device.ip_address}</span>}
                    <span>最后登录: {new Date(device.last_login_at).toLocaleString('zh-CN')}</span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  );
};

export default ProfilePage;
