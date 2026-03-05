/**
 * 行情页面
 * 展示行情榜单（标签页切换）、标的搜索、添加到自选
 */

import React, { useEffect, useState } from 'react';
import { Card, Tabs, Table, Typography, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useMarketStore } from '@/stores/marketStore';
import SymbolSearch from '@/components/SymbolSearch';
import AddToWatchlistModal from '@/components/AddToWatchlistModal';
import { formatPrice, formatPercent, formatVolume, formatAmount, getPriceColorClass } from '@/utils/format';
import type { StockQuote, SymbolInfo, RankingType } from '@/types';

/** 榜单标签页配置 */
const rankingTabs: { key: RankingType; label: string }[] = [
  { key: 'rise', label: '涨幅榜' },
  { key: 'fall', label: '跌幅榜' },
  { key: 'volume', label: '成交量' },
  { key: 'amount', label: '成交额' },
  { key: 'turnover', label: '换手率' },
];

const MarketPage: React.FC = () => {
  const { rankings, activeRankingType, loading, fetchRankings, startAutoRefresh, stopAutoRefresh } = useMarketStore();
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<SymbolInfo | null>(null);
  const navigate = useNavigate();

  // 初始化加载和自动刷新
  useEffect(() => {
    fetchRankings('rise');
    startAutoRefresh(30000);
    return () => stopAutoRefresh();
  }, [fetchRankings, startAutoRefresh, stopAutoRefresh]);

  /** 切换榜单 */
  const handleTabChange = (key: string) => {
    fetchRankings(key as RankingType);
  };

  /** 打开添加到自选弹窗 */
  const handleAddToWatchlist = (record: StockQuote | SymbolInfo) => {
    setSelectedSymbol({
      symbol: record.symbol,
      name: record.name,
      market: record.market,
      industry: '',
      list_date: '',
    });
    setModalOpen(true);
  };

  /** 表格列定义 */
  const columns = [
    {
      title: '代码',
      dataIndex: 'symbol',
      width: 100,
      render: (text: string) => <Typography.Text style={{ fontSize: 12 }}>{text}</Typography.Text>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      width: 80,
      ellipsis: true,
    },
    {
      title: '最新价',
      dataIndex: 'current_price',
      width: 80,
      align: 'right' as const,
      render: (val: number, record: StockQuote) => (
        <span className={getPriceColorClass(record.change_percent)}>
          {formatPrice(val)}
        </span>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      width: 80,
      align: 'right' as const,
      render: (val: number) => (
        <span className={getPriceColorClass(val)}>{formatPercent(val)}</span>
      ),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      width: 80,
      align: 'right' as const,
      render: (val: number) => formatVolume(val),
    },
    {
      title: '成交额',
      dataIndex: 'amount',
      width: 80,
      align: 'right' as const,
      render: (val: number) => formatAmount(val),
    },
    {
      title: '',
      width: 40,
      render: (_: unknown, record: StockQuote) => (
        <PlusOutlined
          style={{ color: '#1677ff', cursor: 'pointer' }}
          onClick={(e) => { e.stopPropagation(); handleAddToWatchlist(record); }}
          aria-label={`添加 ${record.name} 到自选`}
        />
      ),
    },
  ];

  const currentData = rankings[activeRankingType] || [];

  return (
    <div>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        {/* 搜索栏 */}
        <SymbolSearch onSelect={handleAddToWatchlist} />

        {/* 榜单 */}
        <Card bodyStyle={{ padding: 0 }}>
          <Tabs
            activeKey={activeRankingType}
            onChange={handleTabChange}
            items={rankingTabs.map((tab) => ({
              key: tab.key,
              label: tab.label,
            }))}
            style={{ padding: '0 16px' }}
          />
          <Table<StockQuote>
            columns={columns}
            dataSource={currentData}
            rowKey="symbol"
            loading={loading}
            pagination={false}
            size="small"
            scroll={{ x: 540 }}
            locale={{ emptyText: '暂无数据' }}
            onRow={(record) => ({
              onClick: () => navigate(`/stock/${encodeURIComponent(record.symbol)}`),
              style: { cursor: 'pointer' },
            })}
          />
        </Card>
      </Space>

      {/* 添加到自选弹窗 */}
      <AddToWatchlistModal
        open={modalOpen}
        symbol={selectedSymbol}
        onClose={() => { setModalOpen(false); setSelectedSymbol(null); }}
      />
    </div>
  );
};

export default MarketPage;
