/**
 * 股票详情页
 * 展示股票实时行情和K线图
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Spin, Typography, Space, Segmented, Descriptions, message } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';
import marketApi from '@/api/market';
import { formatPrice, formatPercent, formatVolume, formatAmount, getPriceColorClass } from '@/utils/format';
import type { StockQuote, KlineData, KlinePeriod } from '@/types';

/** K线周期选项 */
const periodOptions = [
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

  /** 渲染K线图 */
  useEffect(() => {
    if (!chartRef.current || klineData.length === 0) return;

    // 初始化或获取已有实例
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }
    const chart = chartInstance.current;

    // 准备数据
    const dates = klineData.map((d) => d.day);
    const ohlc = klineData.map((d) => [
      parseFloat(d.open),
      parseFloat(d.close),
      parseFloat(d.low),
      parseFloat(d.high),
    ]);
    const volumes = klineData.map((d) => parseFloat(d.volume));
    // 判断涨跌颜色
    const volumeColors = klineData.map((d) =>
      parseFloat(d.close) >= parseFloat(d.open) ? '#ef5350' : '#26a69a'
    );

    const option: echarts.EChartsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      grid: [
        { left: '8%', right: '3%', top: '5%', height: '55%' },
        { left: '8%', right: '3%', top: '68%', height: '22%' },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: true,
          axisLine: { lineStyle: { color: '#999' } },
          axisLabel: { fontSize: 10 },
          gridIndex: 0,
        },
        {
          type: 'category',
          data: dates,
          boundaryGap: true,
          gridIndex: 1,
          axisLabel: { show: false },
          axisLine: { lineStyle: { color: '#999' } },
        },
      ],
      yAxis: [
        {
          type: 'value',
          scale: true,
          splitLine: { lineStyle: { color: '#f0f0f0' } },
          axisLabel: { fontSize: 10 },
          gridIndex: 0,
        },
        {
          type: 'value',
          scale: true,
          splitLine: { show: false },
          axisLabel: { show: false },
          gridIndex: 1,
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 60,
          end: 100,
        },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          bottom: '2%',
          height: 20,
          start: 60,
          end: 100,
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
            color: '#ef5350',
            color0: '#26a69a',
            borderColor: '#ef5350',
            borderColor0: '#26a69a',
          },
        },
        {
          name: '成交量',
          type: 'bar',
          data: volumes.map((v, i) => ({
            value: v,
            itemStyle: { color: volumeColors[i] },
          })),
          xAxisIndex: 1,
          yAxisIndex: 1,
        },
      ],
    };

    chart.setOption(option, true);

    // 响应窗口大小变化
    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [klineData]);

  // 组件卸载时销毁图表
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
    };
  }, []);

  return (
    <div>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 顶部导航 */}
        <Space align="center" style={{ cursor: 'pointer' }} onClick={() => navigate(-1)}>
          <ArrowLeftOutlined />
          <Typography.Text>返回</Typography.Text>
        </Space>

        {/* 行情概览 */}
        {quote && (
          <Card size="small">
            <Space direction="vertical" size={4} style={{ width: '100%' }}>
              <Space align="baseline">
                <Typography.Title level={4} style={{ margin: 0 }}>
                  {quote.name}
                </Typography.Title>
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  {quote.symbol}
                </Typography.Text>
              </Space>
              <Space align="baseline" size="large">
                <Typography.Title
                  level={3}
                  style={{ margin: 0 }}
                  className={getPriceColorClass(quote.change_percent)}
                >
                  {formatPrice(quote.current_price)}
                </Typography.Title>
                <span className={getPriceColorClass(quote.change_percent)}>
                  {formatPercent(quote.change_percent)}
                </span>
                <span className={getPriceColorClass(quote.change_amount)}>
                  {quote.change_amount > 0 ? '+' : ''}{formatPrice(quote.change_amount)}
                </span>
              </Space>
              <Descriptions size="small" column={{ xs: 2, sm: 4 }}>
                <Descriptions.Item label="今开">{formatPrice(quote.open_price)}</Descriptions.Item>
                <Descriptions.Item label="昨收">{formatPrice(quote.pre_close)}</Descriptions.Item>
                <Descriptions.Item label="最高">{formatPrice(quote.high_price)}</Descriptions.Item>
                <Descriptions.Item label="最低">{formatPrice(quote.low_price)}</Descriptions.Item>
                <Descriptions.Item label="成交量">{formatVolume(quote.volume)}</Descriptions.Item>
                <Descriptions.Item label="成交额">{formatAmount(quote.amount)}</Descriptions.Item>
                <Descriptions.Item label="换手率">{formatPercent(quote.turnover_rate)}</Descriptions.Item>
                <Descriptions.Item label="市盈率">{formatPrice(quote.pe_ratio)}</Descriptions.Item>
              </Descriptions>
            </Space>
          </Card>
        )}

        {/* K线图 */}
        <Card
          size="small"
          title="K线图"
          extra={
            <Segmented
              options={periodOptions}
              value={period}
              onChange={(val) => setPeriod(val as KlinePeriod)}
              size="small"
            />
          }
        >
          <Spin spinning={loading}>
            <div
              ref={chartRef}
              style={{ width: '100%', height: 450 }}
              role="img"
              aria-label={`${quote?.name ?? symbol} K线图`}
            />
            {!loading && klineData.length === 0 && (
              <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                暂无K线数据
              </div>
            )}
          </Spin>
        </Card>
      </Space>
    </div>
  );
};

export default StockDetailPage;
