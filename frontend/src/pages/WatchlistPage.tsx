/**
 * 自选页面
 * Webull 风格：紧凑组合标签、精简数据行
 * 支持轮询刷新行情数据，数字变化时有闪烁特效
 */

import React, { useEffect, useState, useRef } from 'react';
import {
  Modal,
  Input,
  Spin,
  Dropdown,
  message,
  Popconfirm,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { usePortfolioStore } from '@/stores/portfolioStore';
import { formatPrice, formatPercent, formatVolume, formatAmount, getPriceColorClass } from '@/utils/format';
import type { WatchlistItem } from '@/types';

/** 获取涨跌幅标签样式类名 */
const getPriceTagClass = (val: number | undefined | null): string => {
  if (val == null || val === 0) return 'price-tag-flat';
  return val > 0 ? 'price-tag-up' : 'price-tag-down';
};

/**
 * 数字变化闪烁 Hook
 * 对比前后数据，返回每个 symbol 对应的闪烁 CSS 类名
 */
function useFlashMap(items: WatchlistItem[]): Record<string, string> {
  // 上一次的价格快照 { symbol: price }
  const prevPricesRef = useRef<Record<string, number>>({});
  // 当前闪烁状态
  const [flashMap, setFlashMap] = useState<Record<string, string>>({});
  // 清除定时器引用
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const prev = prevPricesRef.current;
    const newFlash: Record<string, string> = {};
    let hasChange = false;

    for (const item of items) {
      const price = item.quote?.current_price;
      if (price == null) continue;
      const oldPrice = prev[item.symbol];
      if (oldPrice != null && oldPrice !== price) {
        newFlash[item.symbol] = price > oldPrice ? 'flash-up' : 'flash-down';
        hasChange = true;
      }
    }

    // 更新价格快照
    const snapshot: Record<string, number> = {};
    for (const item of items) {
      if (item.quote?.current_price != null) {
        snapshot[item.symbol] = item.quote.current_price;
      }
    }
    prevPricesRef.current = snapshot;

    if (hasChange) {
      setFlashMap(newFlash);
      // 动画结束后清除 class
      if (timerRef.current) clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setFlashMap({}), 1300);
    }
  }, [items]);

  return flashMap;
}

const WatchlistPage: React.FC = () => {
  const {
    portfolios,
    activePortfolioId,
    items,
    loading,
    fetchPortfolios,
    createPortfolio,
    updatePortfolio,
    deletePortfolio,
    setActivePortfolio,
    removeItem,
    startAutoRefresh,
    stopAutoRefresh,
  } = usePortfolioStore();

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [inputName, setInputName] = useState('');
  const [renameId, setRenameId] = useState<number | null>(null);
  const navigate = useNavigate();

  // 数字变化闪烁
  const flashMap = useFlashMap(items);

  // 初始化加载 + 启动轮询
  useEffect(() => {
    fetchPortfolios();
    startAutoRefresh(15000);
    return () => stopAutoRefresh();
  }, [fetchPortfolios, startAutoRefresh, stopAutoRefresh]);

  /** 创建组合 */
  const handleCreate = async () => {
    if (!inputName.trim()) {
      message.warning('请输入组合名称');
      return;
    }
    try {
      await createPortfolio(inputName.trim());
      message.success('组合创建成功');
      setCreateModalOpen(false);
      setInputName('');
    } catch {
      // 错误已在拦截器中处理
    }
  };

  /** 打开重命名弹窗 */
  const openRename = (id: number, currentName: string) => {
    setRenameId(id);
    setInputName(currentName);
    setRenameModalOpen(true);
  };

  /** 重命名组合 */
  const handleRename = async () => {
    if (!renameId || !inputName.trim()) return;
    try {
      await updatePortfolio(renameId, inputName.trim());
      message.success('重命名成功');
      setRenameModalOpen(false);
      setInputName('');
      setRenameId(null);
    } catch {
      // 错误已在拦截器中处理
    }
  };

  /** 删除组合 */
  const handleDelete = async (id: number) => {
    try {
      await deletePortfolio(id);
      message.success('组合已删除');
    } catch {
      // 错误已在拦截器中处理
    }
  };

  /** 移除标的 */
  const handleRemoveItem = async (itemId: number) => {
    if (!activePortfolioId) return;
    try {
      await removeItem(activePortfolioId, itemId);
      message.success('标的已移除');
    } catch {
      // 错误已在拦截器中处理
    }
  };


  // 空状态
  if (portfolios.length === 0 && !loading) {
    return (
      <>
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '80px 20px',
          color: 'var(--text-tertiary)',
        }}>
          <StarOutlined style={{ fontSize: 48, marginBottom: 16, opacity: 0.3 }} />
          <div style={{ fontSize: 14, marginBottom: 16 }}>还没有自选组合</div>
          <div
            onClick={() => setCreateModalOpen(true)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && setCreateModalOpen(true)}
            style={{
              padding: '8px 24px',
              background: 'var(--accent-color)',
              color: '#fff',
              borderRadius: 6,
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            创建第一个组合
          </div>
        </div>
        <Modal
          title="创建组合"
          open={createModalOpen}
          onOk={handleCreate}
          onCancel={() => { setCreateModalOpen(false); setInputName(''); }}
          okText="创建"
          cancelText="取消"
        >
          <Input
            placeholder="输入组合名称"
            value={inputName}
            onChange={(e) => setInputName(e.target.value)}
            onPressEnter={handleCreate}
            maxLength={50}
            aria-label="组合名称"
          />
        </Modal>
      </>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* 组合卡片 */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 8,
        overflow: 'hidden',
      }}>
        {/* 组合标签栏 */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          borderBottom: '1px solid var(--border-color)',
          padding: '0 4px',
        }}>
          <div style={{ display: 'flex', gap: 0, flex: 1, overflow: 'auto' }}>
            {portfolios.map((p) => {
              const isActive = activePortfolioId === p.id;
              return (
                <Dropdown
                  key={p.id}
                  trigger={['contextMenu']}
                  menu={{
                    items: [
                      { key: 'rename', icon: <EditOutlined />, label: '重命名', onClick: () => openRename(p.id, p.name) },
                      ...(!p.is_default
                        ? [{ key: 'delete', icon: <DeleteOutlined />, label: '删除', danger: true as const, onClick: () => handleDelete(p.id) }]
                        : []),
                    ],
                  }}
                >
                  <div
                    onClick={() => setActivePortfolio(p.id)}
                    role="tab"
                    tabIndex={0}
                    aria-selected={isActive}
                    onKeyDown={(e) => e.key === 'Enter' && setActivePortfolio(p.id)}
                    style={{
                      padding: '10px 16px',
                      fontSize: 13,
                      cursor: 'pointer',
                      color: isActive ? 'var(--accent-color)' : 'var(--text-secondary)',
                      fontWeight: isActive ? 500 : 400,
                      borderBottom: isActive ? '2px solid var(--accent-color)' : '2px solid transparent',
                      whiteSpace: 'nowrap',
                      transition: 'all 0.2s',
                      userSelect: 'none',
                    }}
                  >
                    {p.name}
                    <span style={{ fontSize: 11, marginLeft: 4, opacity: 0.6 }}>
                      {p.item_count}
                    </span>
                  </div>
                </Dropdown>
              );
            })}
          </div>

          {/* 新建 + 管理 */}
          <div style={{ display: 'flex', gap: 4, padding: '0 8px', flexShrink: 0 }}>
            <div
              onClick={() => setCreateModalOpen(true)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setCreateModalOpen(true)}
              style={{
                padding: '4px 8px',
                cursor: 'pointer',
                color: 'var(--accent-color)',
                fontSize: 13,
                borderRadius: 4,
                display: 'flex',
                alignItems: 'center',
                gap: 2,
              }}
              aria-label="创建组合"
            >
              <PlusOutlined style={{ fontSize: 12 }} />
              <span>新建</span>
            </div>
            {activePortfolioId && (
              <Dropdown
                menu={{
                  items: [
                    {
                      key: 'rename',
                      icon: <EditOutlined />,
                      label: '重命名',
                      onClick: () => {
                        const p = portfolios.find((p) => p.id === activePortfolioId);
                        if (p) openRename(p.id, p.name);
                      },
                    },
                    ...(!portfolios.find((p) => p.id === activePortfolioId)?.is_default
                      ? [{
                          key: 'delete',
                          icon: <DeleteOutlined />,
                          label: '删除组合',
                          danger: true as const,
                          onClick: () => activePortfolioId && handleDelete(activePortfolioId),
                        }]
                      : []),
                  ],
                }}
              >
                <div
                  role="button"
                  tabIndex={0}
                  style={{
                    padding: '4px 6px',
                    cursor: 'pointer',
                    color: 'var(--text-secondary)',
                    borderRadius: 4,
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  <MoreOutlined style={{ fontSize: 14 }} />
                </div>
              </Dropdown>
            )}
          </div>
        </div>

        {/* 表头 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1.2fr 0.7fr 0.7fr 0.7fr 0.8fr 0.8fr 36px',
          padding: '8px 12px',
          background: 'var(--bg-elevated)',
          fontSize: 11,
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
        {loading && items.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center' }}>
            <Spin size="small" />
          </div>
        ) : items.length === 0 ? (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: 'var(--text-tertiary)',
            fontSize: 13,
          }}>
            <div>组合内暂无标的</div>
            <div style={{ fontSize: 12, marginTop: 4, opacity: 0.7 }}>
              从行情页搜索或榜单中添加标的
            </div>
          </div>
        ) : (
          items.map((item: WatchlistItem, index: number) => {
            const flash = flashMap[item.symbol] || '';
            return (
              <div
                key={item.id}
                onClick={() => navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                role="row"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && navigate(`/stock/${encodeURIComponent(item.symbol)}`)}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1.2fr 0.7fr 0.7fr 0.7fr 0.8fr 0.8fr 36px',
                  padding: '9px 12px',
                  cursor: 'pointer',
                  borderBottom: index < items.length - 1 ? '1px solid var(--border-color)' : 'none',
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
                {/* 最新价 — 变化时闪烁 */}
                <div className={`num-font ${getPriceColorClass(item.quote?.change_percent ?? null)} ${flash}`}
                  style={{ textAlign: 'right', fontSize: 13, fontWeight: 500, padding: '2px 4px' }}>
                  {formatPrice(item.quote?.current_price)}
                </div>
                {/* 涨跌幅 — 变化时闪烁 */}
                <div style={{ textAlign: 'right', padding: '2px 0' }} className={flash}>
                  <span className={`num-font ${getPriceTagClass(item.quote?.change_percent)}`}
                    style={{ fontSize: 12 }}>
                    {formatPercent(item.quote?.change_percent)}
                  </span>
                </div>
                {/* 涨跌额 — 变化时闪烁 */}
                <div className={`num-font ${getPriceColorClass(item.quote?.change_amount ?? null)} ${flash}`}
                  style={{ textAlign: 'right', fontSize: 12, padding: '2px 4px' }}>
                  {item.quote?.change_amount != null && item.quote.change_amount > 0 ? '+' : ''}
                  {formatPrice(item.quote?.change_amount)}
                </div>
                {/* 成交量 */}
                <div className="num-font" style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-secondary)' }}>
                  {formatVolume(item.quote?.volume)}
                </div>
                {/* 成交额 */}
                <div className="num-font" style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-secondary)' }}>
                  {formatAmount(item.quote?.amount)}
                </div>
                {/* 删除 */}
                <div style={{ textAlign: 'center' }} onClick={(e) => e.stopPropagation()}>
                  <Popconfirm
                    title="确定移除该标的？"
                    onConfirm={() => handleRemoveItem(item.id)}
                    okText="移除"
                    cancelText="取消"
                  >
                    <DeleteOutlined
                      style={{ color: 'var(--text-tertiary)', cursor: 'pointer', fontSize: 12 }}
                      aria-label={`移除 ${item.name}`}
                    />
                  </Popconfirm>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 创建组合弹窗 */}
      <Modal
        title="创建组合"
        open={createModalOpen}
        onOk={handleCreate}
        onCancel={() => { setCreateModalOpen(false); setInputName(''); }}
        okText="创建"
        cancelText="取消"
      >
        <Input
          placeholder="输入组合名称"
          value={inputName}
          onChange={(e) => setInputName(e.target.value)}
          onPressEnter={handleCreate}
          maxLength={50}
          aria-label="组合名称"
        />
      </Modal>

      {/* 重命名弹窗 */}
      <Modal
        title="重命名组合"
        open={renameModalOpen}
        onOk={handleRename}
        onCancel={() => { setRenameModalOpen(false); setInputName(''); setRenameId(null); }}
        okText="确认"
        cancelText="取消"
      >
        <Input
          placeholder="输入新名称"
          value={inputName}
          onChange={(e) => setInputName(e.target.value)}
          onPressEnter={handleRename}
          maxLength={50}
          aria-label="新组合名称"
        />
      </Modal>
    </div>
  );
};

export default WatchlistPage;
