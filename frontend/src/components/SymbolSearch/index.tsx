/**
 * 标的搜索组件
 * Webull 风格：紧凑搜索框、简洁下拉结果
 */

import React, { useState, useRef, useCallback } from 'react';
import { Input, Spin, Empty } from 'antd';
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
  const { searchResults, searchLoading, searchSymbols, clearSearchResults } = useMarketStore();
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
        prefix={<SearchOutlined style={{ color: 'var(--text-tertiary)' }} />}
        placeholder={placeholder}
        value={keyword}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => searchResults.length > 0 && setShowDropdown(true)}
        onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
        allowClear
        aria-label="搜索标的"
        style={{
          background: 'var(--bg-input)',
          borderColor: 'var(--border-color)',
          borderRadius: 8,
          height: 36,
          fontSize: 13,
        }}
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
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: 8,
            boxShadow: 'var(--shadow-md)',
            maxHeight: 320,
            overflow: 'auto',
            marginTop: 4,
          }}
        >
          {searchLoading ? (
            <div style={{ padding: 24, textAlign: 'center' }}>
              <Spin size="small" />
            </div>
          ) : searchResults.length === 0 ? (
            <Empty
              description="未找到相关标的"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              style={{ padding: 16 }}
            />
          ) : (
            searchResults.map((item, index) => (
              <div
                key={item.symbol}
                onClick={() => handleSelect(item)}
                role="option"
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && handleSelect(item)}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '10px 14px',
                  cursor: 'pointer',
                  borderBottom: index < searchResults.length - 1 ? '1px solid var(--border-color)' : 'none',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-hover)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <div>
                  <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)' }}>
                    {item.name}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--text-tertiary)', marginLeft: 8 }}>
                    {item.symbol}
                  </span>
                </div>
                <span style={{ fontSize: 11, color: 'var(--text-tertiary)' }}>
                  {item.market}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default SymbolSearch;
