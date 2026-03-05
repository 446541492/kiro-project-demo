/**
 * 行情页面
 * Webull 风格：紧凑数据表格、红涨绿跌标签、专业金融终端感
 */

import React, { useEffect, useState } from 'react';
import { Spin } from 'antd';
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

/** 获取涨跌幅标签样式类名 */
const getPriceTagClass = (val: number | undefined | null): string => {
  if (val == null || val === 0) return 'price-tag-flat';
  return val > 0 ? 'price-tag-up' : 'price-tag-down';
};

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
  const handleTabChange = (key: RankingType) => {
    fetchRankings(key);
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

  const currentData = rankings[activeRankingType] || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* 搜索栏 */}
      <div className="wb-search">
        <SymbolSearch onSelect={handleAddToWatchlist} />
      </div>

      {/* 榜单卡片 */}
      <div className="wb-card" style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        {/* 标签页 */}
        <div style={{
          display: 'flex',
          gap: 0,
          borderBottom: '1px solid var(--border-color)',
          padding: '0 4px',
        }}>
          {rankingTabs.map((tab) => {
            const isActive = activeRankingType === tab.key;
            return (
              <div
                key={tab.key}
                onClick={() => handleTabChange(tab.key)}
                role="tab"
                tabIndex={0}
                aria-selected={isActive}
                onKeyDown={(e) => e.key === 'Enter' && handleTabChange(tab.key)}
                style={{
                  padding: '10px 16px',
                  fontSize: 13,
                  cursor: 'pointer',
                  color: isActive ? 'var(--accent-color)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 500 : 400,
                  borderBottom: isActive ? '2px solid var(--accent-color)' : '2px solid transparent',
                  transition: 'all 0.2s',
                  userSelect: 'none',
                }}
              >
                {tab.label}
              </div>
            );
          })}
        </div>

        {/* 表头 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 40px',
          padding: '8px 16px',
          background: 'var(--bg-elevated)',
          fontSize: 12,
          color: 'var(--text-tertiary)',
          fontWeight: 500,
        }}>
          <span>名称/代码</span>
          <span style={{ textAlign: 'right' }}>最新价</span>
          <span style={{ textAlign: 'right' }}>涨跌幅</span>
          <span style={{ textAlign: 'right' }}>涨跌额</span>
          <span style={{ textAlign: 'right' }}>成交量</span>
          <span style={{ textAlign: 'right' }}>成交额</span>
          <span />
        </div>

        {/* 数据行 */}
        {loading && currentData.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <Spin size="small" />
          </div>
        ) : currentData.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-tertiary)' }}>
            暂无数据
          </div>
        ) : (
          currentData.map((item, index) => (
            <div
              key={item.symbol}
              onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
              role="row"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
              style={{
                display: 'grid',
                gridTemplateColumns: '1fr 0.8fr 0.8fr 0.8fr 0.8fr 0.8fr 40px',
                padding: '10px 16px',
                cursor: 'pointer',
                borderBottom: index < currentData.length - 1 ? '1px solid var(--border-color)' : 'none',
                transition: 'background 0.15s',
                alignItems: 'center',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              {/* 名称/代码 */}
              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
                  {item.name}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-tertiary)', marginTop: 1 }}>
                  {item.symbol}
                </div>
              </div>
              {/* 最新价 */}
              <div className={`num-font ${getPriceColorClass(item.change_percent)}`}
                style={{ textAlign: 'right', fontSize: 13, fontWeight: 500 }}>
                {formatPrice(item.current_price)}
              </div>
              {/* 涨跌幅 */}
              <div style={{ textAlign: 'right' }}>
                <span className={`num-font ${getPriceTagClass(item.change_percent)}`}
                  style={{ fontSize: 12 }}>
                  {formatPercent(item.change_percent)}
                </span>
              </div>
              {/* 涨跌额 */}
              <div className={`num-font ${getPriceColorClass(item.change_amount)}`}
                style={{ textAlign: 'right', fontSize: 12 }}>
                {item.change_amount > 0 ? '+' : ''}{formatPrice(item.change_amount)}
              </div>
              {/* 成交量 */}
              <div className="num-font" style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-secondary)' }}>
                {formatVolume(item.volume)}
              </div>
              {/* 成交额 */}
              <div className="num-font" style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-secondary)' }}>
                {formatAmount(item.amount)}
              </div>
              {/* 添加自选 */}
              <div style={{ textAlign: 'center' }}>
                <PlusOutlined
                  style={{ color: 'var(--accent-color)', cursor: 'pointer', fontSize: 14 }}
                  onClick={(e) => { e.stopPropagation(); handleAddToWatchlist(item); }}
                  aria-label={`添加 ${item.name} 到自选`}
                />
              </div>
            </div>
          ))
        )}
      </div>

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
