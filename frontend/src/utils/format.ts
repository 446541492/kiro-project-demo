/**
 * 数据格式化工具
 * 价格、涨跌幅、成交量等数据的显示格式化
 */

/**
 * 格式化价格
 * @param price - 原始价格
 * @param decimals - 小数位数，默认 2
 * @returns 格式化后的价格字符串
 */
export function formatPrice(price: number | undefined | null, decimals = 2): string {
  if (price == null || isNaN(price)) return '--';
  return price.toFixed(decimals);
}

/**
 * 格式化涨跌幅
 * @param percent - 涨跌幅百分比
 * @returns 带正负号和 % 的字符串
 */
export function formatPercent(percent: number | undefined | null): string {
  if (percent == null || isNaN(percent)) return '--';
  const sign = percent > 0 ? '+' : '';
  return `${sign}${percent.toFixed(2)}%`;
}

/**
 * 格式化成交量（万/亿单位）
 * @param volume - 原始成交量
 * @returns 带单位的字符串
 */
export function formatVolume(volume: number | undefined | null): string {
  if (volume == null || isNaN(volume)) return '--';
  if (volume >= 100000000) {
    return `${(volume / 100000000).toFixed(2)}亿`;
  }
  if (volume >= 10000) {
    return `${(volume / 10000).toFixed(2)}万`;
  }
  return volume.toFixed(0);
}

/**
 * 格式化金额（万/亿单位）
 * @param amount - 原始金额（单位：千元）
 * @returns 带单位的字符串
 */
export function formatAmount(amount: number | undefined | null): string {
  if (amount == null || isNaN(amount)) return '--';
  // Tushare 金额单位为千元，转换为元
  const yuan = amount * 1000;
  if (yuan >= 100000000) {
    return `${(yuan / 100000000).toFixed(2)}亿`;
  }
  if (yuan >= 10000) {
    return `${(yuan / 10000).toFixed(2)}万`;
  }
  return yuan.toFixed(0);
}

/**
 * 获取涨跌颜色 CSS 类名
 * @param value - 涨跌值
 * @returns CSS 类名
 */
export function getPriceColorClass(value: number | undefined | null): string {
  if (value == null || value === 0) return 'price-flat';
  return value > 0 ? 'price-up' : 'price-down';
}
