/**
 * 标的搜索组件
 * 输入关键词搜索标的，支持防抖和下拉选择
 */

import React, { useState, useRef, useCallback } from 'react';
import { Input, List, Spin, Empty, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useMarketStore } from '@/stores/marketStore';
import type { SymbolInfo } from '@/types';

interface SymbolSearchProps {
  onSelect: (symbol: SymbolInfo) => void;  // 选中标的回调
  placeholder?: string;
}

const SymbolSearch: React.FC<SymbolSearchProps> = ({
  onSelect,
  placeholder = '搜索标的代码或名称',
}) => {
  const { searchResults, loading, searchSymbols, clearSearchResults } = useMarketStore();
  const [keyword, setKeyword] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceTimer = useRef<ReturnType<typeof setTimeout>>();

  /** 防抖搜索 */
  const handleSearch = useCallback(
    (value: string) => {
      setKeyword(value);
      if (debounceTimer.current) clearTimeout(debounceTimer.current);

      if (!value.trim()) {
        clearSearchResults();
        setShowDropdown(false);
        return;
      }

      debounceTimer.current = setTimeout(() => {
        searchSymbols(value);
        setShowDropdown(true);
      }, 300);
    },
    [searchSymbols, clearSearchResults],
  );

  /** 选中标的 */
  const handleSelect = (item: SymbolInfo) => {
    onSelect(item);
    setKeyword('');
    clearSearchResults();
    setShowDropdown(false);
  };

  return (
    <div style={{ position: 'relative' }}>
      <Input
        prefix={<SearchOutlined />}
        placeholder={placeholder}
        value={keyword}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => searchResults.length > 0 && setShowDropdown(true)}
        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
        allowClear
        aria-label="搜索标的"
      />

      {/* 搜索结果下拉 */}
      {showDropdown && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            zIndex: 1000,
            background: 'var(--bg-color, #fff)',
            border: '1px solid var(--border-color, #f0f0f0)',
            borderRadius: 8,
            boxShadow: '0 6px 16px rgba(0,0,0,0.08)',
            maxHeight: 320,
            overflow: 'auto',
            marginTop: 4,
          }}
        >
          {loading ? (
            <div style={{ padding: 24, textAlign: 'center' }}>
              <Spin size="small" />
            </div>
          ) : searchResults.length === 0 ? (
            <Empty description="未找到相关标的" image={Empty.PRESENTED_IMAGE_SIMPLE} style={{ padding: 16 }} />
          ) : (
            <List
              size="small"
              dataSource={searchResults}
              renderItem={(item) => (
                <List.Item
                  style={{ cursor: 'pointer', padding: '8px 12px' }}
                  onClick={() => handleSelect(item)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                    <span>
                      <Typography.Text strong>{item.name}</Typography.Text>
                      <Typography.Text type="secondary" style={{ marginLeft: 8 }}>
                        {item.symbol}
                      </Typography.Text>
                    </span>
                    <Typography.Text type="secondary">{item.market}</Typography.Text>
                  </div>
                </List.Item>
              )}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default SymbolSearch;
