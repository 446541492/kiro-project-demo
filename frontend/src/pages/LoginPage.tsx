/**
 * 登录页面
 * 支持用户名密码登录、滑块验证码、2FA 验证
 */

import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Card, Form, Input, Button, Typography, Space, message } from 'antd';
import { UserOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';
import SliderCaptcha from '@/components/SliderCaptcha';

/** 登录失败计数的 sessionStorage 键 */
const FAIL_COUNT_KEY = 'login_fail_count';
/** 需要验证码的失败次数阈值 */
const CAPTCHA_THRESHOLD = 3;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [form] = Form.useForm();
  const { login, verify2FA, is2FARequired, loading } = useAuthStore();

  const [failCount, setFailCount] = useState(() => {
    return parseInt(sessionStorage.getItem(FAIL_COUNT_KEY) || '0', 10);
  });
  const [captchaToken, setCaptchaToken] = useState<string | null>(null);
  const [twoFACode, setTwoFACode] = useState('');

  /** 是否需要显示滑块验证码 */
  const needCaptcha = failCount >= CAPTCHA_THRESHOLD;

  /** 登录成功后的跳转目标 */
  const redirectTo = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  /** 提交登录 */
  const handleLogin = async (values: { username: string; password: string }) => {
    if (needCaptcha && !captchaToken) {
      message.warning('请先完成滑块验证');
      return;
    }

    try {
      await login({
        username: values.username,
        password: values.password,
        captcha_token: captchaToken || undefined,
      });

      // 如果不需要 2FA，直接跳转
      if (!useAuthStore.getState().is2FARequired) {
        sessionStorage.removeItem(FAIL_COUNT_KEY);
        navigate(redirectTo, { replace: true });
      }
    } catch {
      // 递增失败计数
      const newCount = failCount + 1;
      setFailCount(newCount);
      sessionStorage.setItem(FAIL_COUNT_KEY, String(newCount));
      setCaptchaToken(null);
    }
  };

  /** 提交 2FA 验证码 */
  const handle2FAVerify = async () => {
    if (!twoFACode || twoFACode.length !== 6) {
      message.warning('请输入 6 位验证码');
      return;
    }
    try {
      await verify2FA(twoFACode);
      sessionStorage.removeItem(FAIL_COUNT_KEY);
      navigate(redirectTo, { replace: true });
    } catch {
      setTwoFACode('');
    }
  };

  // 2FA 验证码输入界面
  if (is2FARequired) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: 16 }}>
        <Card style={{ width: 400 }}>
          <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
            <SafetyOutlined style={{ fontSize: 48, color: '#1677ff' }} />
            <Typography.Title level={3} style={{ margin: 0 }}>两步验证</Typography.Title>
            <Typography.Paragraph type="secondary">
              请输入验证器应用中的 6 位验证码
            </Typography.Paragraph>
            <Input
              size="large"
              maxLength={6}
              placeholder="000000"
              value={twoFACode}
              onChange={(e) => setTwoFACode(e.target.value.replace(/\D/g, ''))}
              onPressEnter={handle2FAVerify}
              style={{ textAlign: 'center', fontSize: 24, letterSpacing: 8 }}
              aria-label="两步验证码"
            />
            <Button
              type="primary"
              size="large"
              block
              loading={loading}
              onClick={handle2FAVerify}
            >
              验证
            </Button>
          </Space>
        </Card>
      </div>
    );
  }


  // 登录表单界面
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: 16 }}>
      <Card style={{ width: 400 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Typography.Title level={3} style={{ margin: 0 }}>📈 股票助手</Typography.Title>
            <Typography.Paragraph type="secondary">登录你的账号</Typography.Paragraph>
          </div>

          <Form
            form={form}
            onFinish={handleLogin}
            size="large"
            autoComplete="off"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, max: 50, message: '用户名 3-50 个字符' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
                aria-label="用户名"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 8, message: '密码至少 8 位' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
                aria-label="密码"
              />
            </Form.Item>

            {/* 滑块验证码 */}
            {needCaptcha && !captchaToken && (
              <Form.Item>
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <SliderCaptcha
                    onSuccess={(token) => setCaptchaToken(token)}
                  />
                </div>
              </Form.Item>
            )}

            {needCaptcha && captchaToken && (
              <Form.Item>
                <Typography.Text type="success">✓ 验证通过</Typography.Text>
              </Form.Item>
            )}

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                登录
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Link to="/register">还没有账号？去注册</Link>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default LoginPage;
