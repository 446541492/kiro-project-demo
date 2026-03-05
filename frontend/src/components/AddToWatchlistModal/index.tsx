/**
 * 添加到自选弹窗
 * 选择目标组合，将标的添加到自选
 */

import React, { useEffect, useState } from 'react';
import { Modal, List, Typography, message, Spin } from 'antd';
import { FolderOutlined, CheckCircleFilled } from '@ant-design/icons';
import { usePortfolioStore } from '@/stores/portfolioStore';
import type { SymbolInfo } from '@/types';

interface AddToWatchlistModalProps {
  open: boolean;
  symbol: SymbolInfo | null;
  onClose: () => void;
}

const AddToWatchlistModal: React.FC<AddToWatchlistModalProps> = ({
  open,
  symbol,
  onClose,
}) => {
  const { portfolios, fetchPortfolios, addItem } = usePortfolioStore();
  const [adding, setAdding] = useState<number | null>(null);

  useEffect(() => {
    if (open) {
      fetchPortfolios();
    }
  }, [open, fetchPortfolios]);

  /** 添加到指定组合 */
  const handleAdd = async (portfolioId: number, portfolioName: string) => {
    if (!symbol || adding) return;
    setAdding(portfolioId);
    try {
      await addItem(portfolioId, symbol);
      message.success(`已添加到「${portfolioName}」`);
      onClose();
    } catch (err: unknown) {
      // 如果是 409 冲突（已存在），显示提示
      const error = err as { response?: { status?: number } };
      if (error?.response?.status === 409) {
        message.info('该标的已在组合中');
      }
    } finally {
      setAdding(null);
    }
  };

  return (
    <Modal
      title={
        symbol
          ? `添加「${symbol.name}」到自选`
          : '添加到自选'
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={360}
    >
      {portfolios.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 24 }}>
          <Spin />
        </div>
      ) : (
        <List
          dataSource={portfolios}
          renderItem={(portfolio) => (
            <List.Item
              style={{ cursor: 'pointer', padding: '12px 8px' }}
              onClick={() => handleAdd(portfolio.id, portfolio.name)}
            >
              <List.Item.Meta
                avatar={
                  adding === portfolio.id ? (
                    <Spin size="small" />
                  ) : (
                    <FolderOutlined style={{ fontSize: 20, color: '#1677ff' }} />
                  )
                }
                title={portfolio.name}
                description={`${portfolio.item_count} 个标的`}
              />
              {portfolio.is_default && (
                <CheckCircleFilled style={{ color: '#52c41a' }} />
              )}
            </List.Item>
          )}
        />
      )}

      {portfolios.length > 0 && (
        <Typography.Paragraph
          type="secondary"
          style={{ textAlign: 'center', marginTop: 8, marginBottom: 0, fontSize: 12 }}
        >
          点击组合即可添加
        </Typography.Paragraph>
      )}
    </Modal>
  );
};

export default AddToWatchlistModal;
