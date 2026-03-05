/**
 * 自选页面
 * 展示自选组合列表、组合内标的列表、组合管理
 */

import React, { useEffect, useState } from 'react';
import {
  Card,
  Tabs,
  Table,
  Button,
  Space,
  Typography,
  Modal,
  Input,
  Empty,
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
import { usePortfolioStore } from '@/stores/portfolioStore';
import { formatPrice, formatPercent, getPriceColorClass } from '@/utils/format';
import type { WatchlistItem } from '@/types';

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
  } = usePortfolioStore();

  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [renameModalOpen, setRenameModalOpen] = useState(false);
  const [inputName, setInputName] = useState('');
  const [renameId, setRenameId] = useState<number | null>(null);

  // 初始化加载
  useEffect(() => {
    fetchPortfolios();
  }, [fetchPortfolios]);

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

  /** 标的列表列定义 */
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
      key: 'price',
      width: 80,
      align: 'right' as const,
      render: (_: unknown, record: WatchlistItem) => {
        const price = record.quote?.current_price;
        const change = record.quote?.change_percent;
        return (
          <span className={getPriceColorClass(change ?? null)}>
            {formatPrice(price)}
          </span>
        );
      },
    },
    {
      title: '涨跌幅',
      key: 'change',
      width: 80,
      align: 'right' as const,
      render: (_: unknown, record: WatchlistItem) => {
        const val = record.quote?.change_percent;
        return (
          <span className={getPriceColorClass(val ?? null)}>
            {formatPercent(val)}
          </span>
        );
      },
    },
    {
      title: '',
      width: 40,
      render: (_: unknown, record: WatchlistItem) => (
        <Popconfirm
          title="确定移除该标的？"
          onConfirm={() => handleRemoveItem(record.id)}
          okText="移除"
          cancelText="取消"
        >
          <DeleteOutlined
            style={{ color: '#ff4d4f', cursor: 'pointer' }}
            aria-label={`移除 ${record.name}`}
          />
        </Popconfirm>
      ),
    },
  ];

  /** 组合标签页配置 */
  const tabItems = portfolios.map((p) => ({
    key: String(p.id),
    label: (
      <Dropdown
        trigger={['contextMenu']}
        menu={{
          items: [
            { key: 'rename', icon: <EditOutlined />, label: '重命名', onClick: () => openRename(p.id, p.name) },
            ...(!p.is_default
              ? [{ key: 'delete', icon: <DeleteOutlined />, label: '删除', danger: true, onClick: () => handleDelete(p.id) }]
              : []),
          ],
        }}
      >
        <span>{p.name} ({p.item_count})</span>
      </Dropdown>
    ),
  }));


  // 空状态
  if (portfolios.length === 0 && !loading) {
    return (
      <>
        <Card>
          <Empty
            image={<StarOutlined style={{ fontSize: 48, color: '#d9d9d9' }} />}
            description="还没有自选组合"
          >
            <Button type="primary" onClick={() => setCreateModalOpen(true)}>
              创建第一个组合
            </Button>
          </Empty>
        </Card>

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
      </>
    );
  }

  return (
    <div>
      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <Card bodyStyle={{ padding: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', padding: '0 16px' }}>
            <Tabs
              activeKey={activePortfolioId ? String(activePortfolioId) : undefined}
              onChange={(key) => setActivePortfolio(Number(key))}
              items={tabItems}
              style={{ flex: 1 }}
              tabBarExtraContent={
                <Button
                  type="text"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateModalOpen(true)}
                  aria-label="创建组合"
                >
                  新建
                </Button>
              }
            />
          </div>

          {/* 组合管理按钮（移动端） */}
          {activePortfolioId && (
            <div style={{ padding: '0 16px 8px', display: 'flex', gap: 8 }}>
              {portfolios.find((p) => p.id === activePortfolioId) && (
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
                  <Button size="small" icon={<MoreOutlined />}>管理</Button>
                </Dropdown>
              )}
            </div>
          )}

          {/* 标的列表 */}
          <Table<WatchlistItem>
            columns={columns}
            dataSource={items}
            rowKey="id"
            loading={loading}
            pagination={false}
            size="small"
            scroll={{ x: 380 }}
            locale={{
              emptyText: (
                <Empty
                  description="组合内暂无标的"
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                >
                  <Typography.Text type="secondary">
                    从行情页搜索或榜单中添加标的
                  </Typography.Text>
                </Empty>
              ),
            }}
          />
        </Card>
      </Space>

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
