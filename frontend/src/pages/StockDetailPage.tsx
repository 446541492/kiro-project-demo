/**
 * 股票详情页
 * Webull 风格：深色K线图、紧凑行情概览、专业数据展示
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Spin, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';
import marketApi from '@/api/market';
import { formatPrice, formatPercent, formatVolume, formatAmount, getPriceColorClass } from '@/utils/format';
import type { StockQuote, KlineData, KlinePeriod } from '@/types';

/** K线周期选项 */
const periodOptions: { label: string; value: KlinePeriod }[] = [
  { label: '日K', value: 'daily' },
  { label: '周K', value: 'weekly' },
  { label: '月K', value: 'monthly' },
];

const StockDetailPage: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  const [quote, setQuote] = useState<StockQuote | null>(null);
  const [klineData, setKlineData] = useState<KlineData[]>([]);
  const [period, setPeriod] = useState<KlinePeriod>('daily');
  const [loading, setLoading] = useState(true);

  /** 加载行情数据 */
  const fetchQuote = useCallback(async () => {
    if (!symbol) return;
    try {
      const resp = await marketApi.getQuote(symbol);
      setQuote(resp.data);
    } catch {
      message.error('获取行情数据失败');
    }
  }, [symbol]);

  /** 加载K线数据 */
  const fetchKline = useCallback(async () => {
    if (!symbol) return;
    setLoading(true);
    try {
      const resp = await marketApi.getKline(symbol, period);
      setKlineData(resp.data);
    } catch {
      message.error('获取K线数据失败');
    } finally {
      setLoading(false);
    }
  }, [symbol, period]);

  // 初始化加载
  useEffect(() => {
    fetchQuote();
    fetchKline();
  }, [fetchQuote, fetchKline]);

  /** 获取主题相关颜色 */
  const getThemeColors = () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
      bg: isDark ? '#1a1d26' : '#ffffff',
      gridLine: isDark ? '#2a2e39' : '#f0f0f0',
      textColor: isDark ? '#8b8fa3' : '#6b7280',
      crosshair: isDark ? '#5d6175' : '#9ca3af',
      tooltipBg: isDark ? '#22262f' : '#ffffff',
      tooltipBorder: isDark ? '#2a2e39' : '#e8eaef',
    };
  };

  /** 渲染K线图 */
  useEffect(() => {
    if (!chartRef.current || klineData.length === 0) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }
    const chart = chartInstance.current;
    const colors = getThemeColors();

    // 准备数据
    const dates = klineData.map((d) => d.day);
    const ohlc = klineData.map((d) => [
      parseFloat(d.open),
      parseFloat(d.close),
      parseFloat(d.low),
      parseFloat(d.high),
    ]);
    const volumes = klineData.map((d) => parseFloat(d.volume));
    const volumeColors = klineData.map((d) =>
      parseFloat(d.close) >= parseFloat(d.open) ? '#ef4444' : '#22c55e'
    );

    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          crossStyle: { color: colors.crosshair },
        },
        backgroundColor: colors.tooltipBg,
        borderColor: colors.tooltipBorder,
        textStyle: { color: colors.textColor, fontSize: 12 },
      },
      grid: [
        { left: '8%', right: '3%', top: '4%', height: '58%' },
        { left: '8%', right: '3%', top: '68%', height: '20%' },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: true,
          axisLine: { lineStyle: { color: colors.gridLine } },
          axisLabel: { fontSize: 10, color: colors.textColor },
          gridIndex: 0,
        },
        {
          type: 'category',
          data: dates,
          boundaryGap: true,
          gridIndex: 1,
          axisLabel: { show: false },
          axisLine: { lineStyle: { color: colors.gridLine } },
        },
      ],
      yAxis: [
        {
          type: 'value',
          scale: true,
          splitLine: { lineStyle: { color: colors.gridLine, type: 'dashed' } },
          axisLabel: { fontSize: 10, color: colors.textColor },
          axisLine: { show: false },
          gridIndex: 0,
        },
        {
          type: 'value',
          scale: true,
          splitLine: { show: false },
          axisLabel: { show: false },
          axisLine: { show: false },
          gridIndex: 1,
        },
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          bottom: '2%',
          height: 16,
          start: 50,
          end: 100,
          borderColor: colors.gridLine,
          backgroundColor: 'transparent',
          fillerColor: 'rgba(59, 130, 246, 0.1)',
          handleStyle: { color: '#3b82f6' },
          textStyle: { color: colors.textColor, fontSize: 10 },
        },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: ohlc,
          xAxisIndex: 0,
          yAxisIndex: 0,
          itemStyle: {
            color: '#ef4444',
            color0: '#22c55e',
            borderColor: '#ef4444',
            borderColor0: '#22c55e',
          },
        },
        {
          name: '成交量',
          type: 'bar',
          data: volumes.map((v, i) => ({
            value: v,
            itemStyle: { color: volumeColors[i], opacity: 0.6 },
          })),
          xAxisIndex: 1,
          yAxisIndex: 1,
        },
      ],
    };

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [klineData]);

  // 组件卸载时销毁图表
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
    };
  }, []);

  /** 行情指标项 */
  const QuoteItem = ({ label, value, colored }: { label: string; value: string; colored?: boolean }) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0' }}>
      <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>{label}</span>
      <span className={colored ? `num-font ${getPriceColorClass(quote?.change_percent ?? null)}` : 'num-font'}
        style={{ fontSize: 12, color: colored ? undefined : 'var(--text-primary)' }}>
        {value}
      </span>
    </div>
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* 顶部导航 */}
      <div
        onClick={() => navigate(-1)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && navigate(-1)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          cursor: 'pointer',
          color: 'var(--text-secondary)',
          fontSize: 13,
          padding: '4px 0',
        }}
      >
        <ArrowLeftOutlined style={{ fontSize: 14 }} />
        <span>返回</span>
      </div>

      {/* 行情概览 */}
      {quote && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 8,
          padding: 16,
        }}>
          {/* 标题行 */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginBottom: 12 }}>
            <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)' }}>
              {quote.name}
            </span>
            <span style={{ fontSize: 12, color: 'var(--text-tertiary)' }}>
              {quote.symbol}
            </span>
          </div>

          {/* 价格行 */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 16, marginBottom: 16 }}>
            <span
              className={`num-font ${getPriceColorClass(quote.change_percent)}`}
              style={{ fontSize: 28, fontWeight: 600 }}
            >
              {formatPrice(quote.current_price)}
            </span>
            <span className={`num-font ${quote.change_percent >= 0 ? 'price-tag-up' : 'price-tag-down'}`}
              style={{ fontSize: 14 }}>
              {formatPercent(quote.change_percent)}
            </span>
            <span className={`num-font ${getPriceColorClass(quote.change_amount)}`}
              style={{ fontSize: 13 }}>
              {quote.change_amount > 0 ? '+' : ''}{formatPrice(quote.change_amount)}
            </span>
          </div>

          {/* 指标网格 */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '0 24px',
            borderTop: '1px solid var(--border-color)',
            paddingTop: 12,
          }}>
            <QuoteItem label="今开" value={formatPrice(quote.open_price)} />
            <QuoteItem label="昨收" value={formatPrice(quote.pre_close)} />
            <QuoteItem label="最高" value={formatPrice(quote.high_price)} />
            <QuoteItem label="最低" value={formatPrice(quote.low_price)} />
            <QuoteItem label="成交量" value={formatVolume(quote.volume)} />
            <QuoteItem label="成交额" value={formatAmount(quote.amount)} />
            <QuoteItem label="换手率" value={formatPercent(quote.turnover_rate)} />
            <QuoteItem label="市盈率" value={formatPrice(quote.pe_ratio)} />
          </div>
        </div>
      )}

      {/* K线图 */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        {/* K线图头部 */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '10px 16px',
          borderBottom: '1px solid var(--border-color)',
        }}>
          <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
            K线图
          </span>
          <div style={{ display: 'flex', gap: 2, background: 'var(--bg-input)', borderRadius: 6, padding: 2 }}>
            {periodOptions.map((opt) => (
              <div
                key={opt.value}
                onClick={() => setPeriod(opt.value)}
                role="tab"
                tabIndex={0}
                aria-selected={period === opt.value}
                onKeyDown={(e) => e.key === 'Enter' && setPeriod(opt.value)}
                style={{
                  padding: '4px 12px',
                  fontSize: 12,
                  cursor: 'pointer',
                  borderRadius: 4,
                  fontWeight: period === opt.value ? 500 : 400,
                  color: period === opt.value ? '#fff' : 'var(--text-secondary)',
                  background: period === opt.value ? 'var(--accent-color)' : 'transparent',
                  transition: 'all 0.2s',
                  userSelect: 'none',
                }}
              >
                {opt.label}
              </div>
            ))}
          </div>
        </div>

        {/* 图表区域 */}
        <Spin spinning={loading}>
          <div
            ref={chartRef}
            style={{ width: '100%', height: 480, padding: '8px 0' }}
            role="img"
            aria-label={`${quote?.name ?? symbol} K线图`}
          />
          {!loading && klineData.length === 0 && (
            <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-tertiary)', fontSize: 13 }}>
              暂无K线数据
            </div>
          )}
        </Spin>
      </div>
    </div>
  );
};

export default StockDetailPage;
