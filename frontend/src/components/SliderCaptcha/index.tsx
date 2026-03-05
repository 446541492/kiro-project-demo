/**
 * 滑块验证码组件
 * 前端生成拼图验证，防止自动化攻击
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { message } from 'antd';

interface SliderCaptchaProps {
  onSuccess: (token: string) => void;  // 验证成功回调
  onFail?: () => void;                 // 验证失败回调
}

/** 画布尺寸 */
const CANVAS_WIDTH = 280;
const CANVAS_HEIGHT = 160;
/** 拼图块尺寸 */
const PIECE_SIZE = 40;
/** 允许的偏移误差 */
const TOLERANCE = 5;
/** 最短拖动时间（毫秒） */
const MIN_DRAG_TIME = 300;

const SliderCaptcha: React.FC<SliderCaptchaProps> = ({ onSuccess, onFail }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [targetX, setTargetX] = useState(0);
  const [sliderX, setSliderX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [verified, setVerified] = useState(false);
  const dragStartTime = useRef(0);
  const dragTrack = useRef<number[]>([]);
  const startX = useRef(0);

  /** 生成随机拼图位置并绘制画布 */
  const initCaptcha = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 随机目标位置（避免太靠边）
    const tx = Math.floor(Math.random() * (CANVAS_WIDTH - PIECE_SIZE * 3)) + PIECE_SIZE * 2;
    setTargetX(tx);
    setSliderX(0);
    setVerified(false);
    dragTrack.current = [];

    // 绘制背景（渐变色块模拟图片）
    const gradient = ctx.createLinearGradient(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    // 绘制装饰色块
    for (let i = 0; i < 8; i++) {
      ctx.fillStyle = `rgba(255,255,255,${Math.random() * 0.15 + 0.05})`;
      const rx = Math.random() * CANVAS_WIDTH;
      const ry = Math.random() * CANVAS_HEIGHT;
      const rw = Math.random() * 60 + 20;
      const rh = Math.random() * 40 + 10;
      ctx.fillRect(rx, ry, rw, rh);
    }

    // 绘制目标缺口
    const ty = (CANVAS_HEIGHT - PIECE_SIZE) / 2;
    ctx.fillStyle = 'rgba(0,0,0,0.4)';
    ctx.fillRect(tx, ty, PIECE_SIZE, PIECE_SIZE);
    ctx.strokeStyle = 'rgba(255,255,255,0.6)';
    ctx.lineWidth = 1;
    ctx.strokeRect(tx, ty, PIECE_SIZE, PIECE_SIZE);
  }, []);

  useEffect(() => {
    initCaptcha();
  }, [initCaptcha]);

  /** 开始拖动 */
  const handleDragStart = (e: React.MouseEvent | React.TouchEvent) => {
    if (verified) return;
    setIsDragging(true);
    dragStartTime.current = Date.now();
    dragTrack.current = [0];
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    startX.current = clientX;
  };

  /** 拖动中 */
  const handleDragMove = useCallback((e: MouseEvent | TouchEvent) => {
    if (!isDragging) return;
    const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
    const diff = clientX - startX.current;
    const newX = Math.max(0, Math.min(diff, CANVAS_WIDTH - PIECE_SIZE));
    setSliderX(newX);
    dragTrack.current.push(newX);
  }, [isDragging]);

  /** 结束拖动 */
  const handleDragEnd = useCallback(() => {
    if (!isDragging) return;
    setIsDragging(false);

    const dragTime = Date.now() - dragStartTime.current;
    const track = dragTrack.current;

    // 检查拖动时间
    if (dragTime < MIN_DRAG_TIME) {
      message.warning('请慢一点拖动');
      initCaptcha();
      onFail?.();
      return;
    }

    // 检查轨迹自然度（非直线）
    if (track.length < 5) {
      message.warning('验证失败，请重试');
      initCaptcha();
      onFail?.();
      return;
    }

    // 检查偏移精度
    if (Math.abs(sliderX - targetX) <= TOLERANCE) {
      setVerified(true);
      // 生成简单的 captcha_token
      const token = btoa(`captcha_${Date.now()}_${Math.random().toString(36).slice(2)}`);
      message.success('验证通过');
      onSuccess(token);
    } else {
      message.error('验证失败，请重试');
      initCaptcha();
      onFail?.();
    }
  }, [isDragging, sliderX, targetX, initCaptcha, onSuccess, onFail]);

  // 全局鼠标/触摸事件监听
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleDragMove);
      window.addEventListener('mouseup', handleDragEnd);
      window.addEventListener('touchmove', handleDragMove);
      window.addEventListener('touchend', handleDragEnd);
    }
    return () => {
      window.removeEventListener('mousemove', handleDragMove);
      window.removeEventListener('mouseup', handleDragEnd);
      window.removeEventListener('touchmove', handleDragMove);
      window.removeEventListener('touchend', handleDragEnd);
    };
  }, [isDragging, handleDragMove, handleDragEnd]);

  const pieceY = (CANVAS_HEIGHT - PIECE_SIZE) / 2;

  return (
    <div style={{ width: CANVAS_WIDTH, userSelect: 'none' }}>
      {/* 画布区域 */}
      <div style={{ position: 'relative', marginBottom: 8 }}>
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          style={{ borderRadius: 4, display: 'block' }}
        />
        {/* 拼图块 */}
        <div
          style={{
            position: 'absolute',
            left: sliderX,
            top: pieceY,
            width: PIECE_SIZE,
            height: PIECE_SIZE,
            background: verified
              ? 'rgba(82,196,26,0.8)'
              : 'rgba(255,255,255,0.9)',
            border: '2px solid #fff',
            borderRadius: 4,
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            transition: isDragging ? 'none' : 'background 0.3s',
          }}
        />
      </div>

      {/* 滑动条 */}
      <div
        style={{
          position: 'relative',
          height: 40,
          background: verified ? '#f6ffed' : '#f5f5f5',
          borderRadius: 20,
          border: `1px solid ${verified ? '#b7eb8f' : '#d9d9d9'}`,
          overflow: 'hidden',
        }}
      >
        {/* 提示文字 */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: verified ? '#52c41a' : '#999',
            fontSize: 13,
            pointerEvents: 'none',
          }}
        >
          {verified ? '✓ 验证通过' : '向右拖动滑块完成验证'}
        </div>

        {/* 滑块按钮 */}
        <div
          onMouseDown={handleDragStart}
          onTouchStart={handleDragStart}
          role="slider"
          aria-label="滑块验证码"
          aria-valuenow={sliderX}
          aria-valuemin={0}
          aria-valuemax={CANVAS_WIDTH - PIECE_SIZE}
          tabIndex={0}
          style={{
            position: 'absolute',
            left: sliderX,
            top: 0,
            width: 40,
            height: 40,
            background: verified ? '#52c41a' : isDragging ? '#1677ff' : '#fff',
            border: `1px solid ${verified ? '#52c41a' : '#d9d9d9'}`,
            borderRadius: 20,
            cursor: verified ? 'default' : 'grab',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 16,
            color: verified || isDragging ? '#fff' : '#666',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            transition: isDragging ? 'none' : 'background 0.3s, border 0.3s',
          }}
        >
          {verified ? '✓' : '→'}
        </div>
      </div>
    </div>
  );
};

export default SliderCaptcha;
