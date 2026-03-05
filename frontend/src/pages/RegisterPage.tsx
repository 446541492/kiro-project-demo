/**
 * 注册页面
 * 支持用户名、密码、邮箱、手机号注册，含滑块验证码
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Typography, Space, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';
import SliderCaptcha from '@/components/SliderCaptcha';

/** 密码强度正则：大写 + 小写 + 数字 + 特殊字符 */
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/;
/** 用户名正则：字母数字下划线 */
const USERNAME_REGEX = /^[a-zA-Z0-9_]{3,50}$/;

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const { register, loading } = useAuthStore();
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);

  /** 提交注册 */
  const handleRegister = async (values: {
    username: string;
    password: string;
    email?: string;
    phone?: string;
  }) => {
    if (!captchaToken) {
      message.warning('请先完成滑块验证');
      return;
    }

    try {
      await register({
        username: values.username,
        password: values.password,
        email: values.email || undefined,
        phone: values.phone || undefined,
      });
      message.success('注册成功');
      navigate('/', { replace: true });
    } catch {
      // 错误已在 apiClient 拦截器中处理
      setCaptchaToken(null);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: 16 }}>
      <Card style={{ width: 420 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Typography.Title level={3} style={{ margin: 0 }}>📈 股票助手</Typography.Title>
            <Typography.Paragraph type="secondary">创建新账号</Typography.Paragraph>
          </div>

          <Form form={form} onFinish={handleRegister} size="large" autoComplete="off">
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { pattern: USERNAME_REGEX, message: '3-50 个字符，仅允许字母、数字、下划线' },
              ]}
            >
              <Input prefix={<UserOutlined />} placeholder="用户名" aria-label="用户名" />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                {
                  pattern: PASSWORD_REGEX,
                  message: '至少 8 位，包含大写、小写、数字和特殊字符',
                },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="密码" aria-label="密码" />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="确认密码" aria-label="确认密码" />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[{ type: 'email', message: '请输入有效的邮箱地址' }]}
            >
              <Input prefix={<MailOutlined />} placeholder="邮箱（可选）" aria-label="邮箱" />
            </Form.Item>

            <Form.Item
              name="phone"
              rules={[{ pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号' }]}
            >
              <Input prefix={<PhoneOutlined />} placeholder="手机号（可选）" aria-label="手机号" />
            </Form.Item>

            {/* 滑块验证码 */}
            {!captchaToken ? (
              <Form.Item>
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <SliderCaptcha onSuccess={(token) => setCaptchaToken(token)} />
                </div>
              </Form.Item>
            ) : (
              <Form.Item>
                <Typography.Text type="success">✓ 验证通过</Typography.Text>
              </Form.Item>
            )}

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                注册
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Link to="/login">已有账号？去登录</Link>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default RegisterPage;
