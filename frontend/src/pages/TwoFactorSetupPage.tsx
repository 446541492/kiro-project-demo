/**
 * 两步验证设置页面
 * 支持启用/禁用 2FA，展示二维码和恢复码
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Typography,
  Button,
  Input,
  Space,
  Alert,
  Steps,
  message,
  Modal,
} from 'antd';
import { SafetyOutlined, QrcodeOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useAuthStore } from '@/stores/authStore';
import authApi, { type TwoFactorSetupResponse } from '@/api/auth';

const TwoFactorSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, fetchUser } = useAuthStore();

  // 启用流程状态
  const [step, setStep] = useState(0);
  const [setupData, setSetupData] = useState<TwoFactorSetupResponse | null>(null);
  const [verifyCode, setVerifyCode] = useState('');
  const [recoveryCodes, setRecoveryCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // 禁用流程状态
  const [disableCode, setDisableCode] = useState('');
  const [disableModalOpen, setDisableModalOpen] = useState(false);

  if (!user) return null;

  /** 启用 2FA - 第一步：获取二维码 */
  const handleEnable = async () => {
    setLoading(true);
    try {
      const resp = await authApi.enable2FA();
      setSetupData(resp.data);
      setStep(1);
    } catch {
      // 错误已在拦截器中处理
    } finally {
      setLoading(false);
    }
  };

  /** 启用 2FA - 第二步：验证码确认 */
  const handleVerify = async () => {
    if (!verifyCode || verifyCode.length !== 6) {
      message.warning('请输入 6 位验证码');
      return;
    }
    setLoading(true);
    try {
      await authApi.verify2FA(verifyCode);
      // 获取恢复码
      const codesResp = await authApi.getRecoveryCodes();
      setRecoveryCodes(codesResp.data.recovery_codes || []);
      setStep(2);
      await fetchUser();
      message.success('两步验证已启用');
    } catch {
      setVerifyCode('');
    } finally {
      setLoading(false);
    }
  };

  /** 禁用 2FA */
  const handleDisable = async () => {
    if (!disableCode || disableCode.length !== 6) {
      message.warning('请输入 6 位验证码');
      return;
    }
    setLoading(true);
    try {
      await authApi.disable2FA(disableCode);
      await fetchUser();
      message.success('两步验证已禁用');
      setDisableModalOpen(false);
      setDisableCode('');
    } catch {
      setDisableCode('');
    } finally {
      setLoading(false);
    }
  };

  // 已启用状态
  if (user.is_2fa_enabled && step === 0) {
    return (
      <div style={{ maxWidth: 500, margin: '0 auto' }}>
        <Card>
          <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
            <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            <Typography.Title level={4} style={{ margin: 0 }}>两步验证已启用</Typography.Title>
            <Typography.Paragraph type="secondary">
              你的账号已受到两步验证保护
            </Typography.Paragraph>
            <Space>
              <Button danger onClick={() => setDisableModalOpen(true)}>
                禁用两步验证
              </Button>
              <Button onClick={() => navigate('/profile')}>返回</Button>
            </Space>
          </Space>
        </Card>

        {/* 禁用确认弹窗 */}
        <Modal
          title="禁用两步验证"
          open={disableModalOpen}
          onCancel={() => { setDisableModalOpen(false); setDisableCode(''); }}
          footer={null}
        >
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Typography.Paragraph>请输入当前验证码以确认禁用：</Typography.Paragraph>
            <Input
              size="large"
              maxLength={6}
              placeholder="000000"
              value={disableCode}
              onChange={(e) => setDisableCode(e.target.value.replace(/\D/g, ''))}
              onPressEnter={handleDisable}
              style={{ textAlign: 'center', fontSize: 20, letterSpacing: 8 }}
              aria-label="验证码"
            />
            <Button type="primary" danger block loading={loading} onClick={handleDisable}>
              确认禁用
            </Button>
          </Space>
        </Modal>
      </div>
    );
  }


  // 启用流程
  return (
    <div style={{ maxWidth: 500, margin: '0 auto' }}>
      <Card>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <SafetyOutlined style={{ fontSize: 48, color: '#1677ff' }} />
            <Typography.Title level={4}>设置两步验证</Typography.Title>
          </div>

          <Steps
            current={step}
            items={[
              { title: '开始' },
              { title: '扫码' },
              { title: '完成' },
            ]}
          />

          {/* 第 0 步：开始 */}
          {step === 0 && (
            <Space direction="vertical" size="middle" style={{ width: '100%', textAlign: 'center' }}>
              <Typography.Paragraph>
                两步验证为你的账号增加额外的安全保护。启用后，登录时需要输入验证器应用生成的验证码。
              </Typography.Paragraph>
              <Typography.Paragraph type="secondary">
                推荐使用 Google Authenticator 或 Microsoft Authenticator
              </Typography.Paragraph>
              <Button type="primary" size="large" loading={loading} onClick={handleEnable}>
                开始设置
              </Button>
            </Space>
          )}

          {/* 第 1 步：扫码验证 */}
          {step === 1 && setupData && (
            <Space direction="vertical" size="middle" style={{ width: '100%', textAlign: 'center' }}>
              <Typography.Paragraph>
                使用验证器应用扫描下方二维码：
              </Typography.Paragraph>
              <div>
                <img
                  src={`data:image/png;base64,${setupData.qr_code}`}
                  alt="两步验证二维码"
                  style={{ width: 200, height: 200 }}
                />
              </div>
              <Alert
                type="info"
                message="无法扫码？手动输入密钥："
                description={
                  <Typography.Text code copyable style={{ fontSize: 14 }}>
                    {setupData.secret}
                  </Typography.Text>
                }
              />
              <Typography.Paragraph>输入验证器显示的 6 位验证码：</Typography.Paragraph>
              <Input
                size="large"
                maxLength={6}
                placeholder="000000"
                value={verifyCode}
                onChange={(e) => setVerifyCode(e.target.value.replace(/\D/g, ''))}
                onPressEnter={handleVerify}
                style={{ textAlign: 'center', fontSize: 24, letterSpacing: 8, maxWidth: 200, margin: '0 auto' }}
                aria-label="验证码"
              />
              <Button type="primary" size="large" loading={loading} onClick={handleVerify}>
                验证并启用
              </Button>
            </Space>
          )}

          {/* 第 2 步：完成，展示恢复码 */}
          {step === 2 && (
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Alert
                type="success"
                message="两步验证已成功启用"
                showIcon
              />
              {recoveryCodes.length > 0 && (
                <>
                  <Alert
                    type="warning"
                    message="请妥善保存以下恢复码"
                    description="如果你无法使用验证器应用，可以使用恢复码登录。每个恢复码只能使用一次。"
                  />
                  <Card
                    size="small"
                    style={{
                      background: '#fafafa',
                      fontFamily: 'monospace',
                      textAlign: 'center',
                    }}
                  >
                    <Space direction="vertical" size={4}>
                      {recoveryCodes.map((code, i) => (
                        <Typography.Text key={i} copyable style={{ fontSize: 16 }}>
                          {code}
                        </Typography.Text>
                      ))}
                    </Space>
                  </Card>
                </>
              )}
              <Button type="primary" block onClick={() => navigate('/profile')}>
                返回个人中心
              </Button>
            </Space>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default TwoFactorSetupPage;
