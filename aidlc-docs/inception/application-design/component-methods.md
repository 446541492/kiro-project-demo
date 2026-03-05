# 组件方法文档 - Stocks Assist

## 一、后端组件方法

### 1. AuthService（认证服务）

```python
class AuthService:
    async def register(self, data: RegisterRequest) -> UserResponse
    """注册新用户，创建默认自选组合"""

    async def login(self, data: LoginRequest) -> TokenResponse
    """用户登录，验证密码，生成 JWT Token"""

    async def logout(self, user_id: int) -> None
    """用户登出，使 Token 失效"""

    async def refresh_token(self, refresh_token: str) -> TokenResponse
    """刷新 Access Token"""

    async def get_current_user(self, token: str) -> UserResponse
    """根据 Token 获取当前用户信息"""

    async def change_password(self, user_id: int, data: ChangePasswordRequest) -> None
    """修改用户密码"""
```

### 2. TwoFactorService（两步验证服务）

```python
class TwoFactorService:
    def generate_secret(self) -> str
    """生成 TOTP 密钥"""

    def generate_qr_code(self, secret: str, username: str) -> str
    """生成 2FA 二维码（Base64 图片）"""

    def verify_totp(self, secret: str, code: str) -> bool
    """验证 TOTP 验证码"""

    def generate_recovery_codes(self, count: int = 8) -> list[str]
    """生成备用恢复码"""

    async def enable_2fa(self, user_id: int) -> TwoFactorSetupResponse
    """启用 2FA，返回密钥和二维码"""

    async def disable_2fa(self, user_id: int, code: str) -> None
    """禁用 2FA，需要验证当前验证码"""
```

### 3. MarketService（行情服务）

```python
class MarketService:
    async def get_rankings(self, ranking_type: str, market: str, limit: int = 20) -> list[StockQuote]
    """获取行情榜单（涨幅榜/跌幅榜/成交量榜等）"""

    async def search_symbols(self, keyword: str, market: str = None) -> list[SymbolInfo]
    """搜索标的（支持代码/名称/拼音）"""

    async def get_quote(self, symbol: str) -> StockQuote
    """获取单个标的详细行情"""

    async def get_batch_quotes(self, symbols: list[str]) -> list[StockQuote]
    """批量获取标的行情"""
```

### 4. PortfolioService（自选组合服务）

```python
class PortfolioService:
    async def get_portfolios(self, user_id: int) -> list[PortfolioResponse]
    """获取用户所有自选组合"""

    async def create_portfolio(self, user_id: int, data: CreatePortfolioRequest) -> PortfolioResponse
    """创建新自选组合"""

    async def update_portfolio(self, portfolio_id: int, user_id: int, data: UpdatePortfolioRequest) -> PortfolioResponse
    """更新组合信息（重命名）"""

    async def delete_portfolio(self, portfolio_id: int, user_id: int) -> None
    """删除组合（默认组合不可删除）"""

    async def reorder_portfolios(self, user_id: int, data: ReorderRequest) -> None
    """调整组合排序"""

    async def create_default_portfolio(self, user_id: int) -> PortfolioResponse
    """创建默认自选组合（注册时自动调用）"""
```

### 5. WatchlistService（自选标的服务）

```python
class WatchlistService:
    async def get_items(self, portfolio_id: int, user_id: int) -> list[WatchlistItemResponse]
    """获取组合内所有标的（含实时行情）"""

    async def add_item(self, portfolio_id: int, user_id: int, data: AddItemRequest) -> WatchlistItemResponse
    """添加标的到组合"""

    async def add_items_batch(self, portfolio_id: int, user_id: int, data: AddItemsBatchRequest) -> list[WatchlistItemResponse]
    """批量添加标的到组合"""

    async def remove_item(self, portfolio_id: int, item_id: int, user_id: int) -> None
    """从组合移除标的"""

    async def reorder_items(self, portfolio_id: int, user_id: int, data: ReorderRequest) -> None
    """调整标的排序"""
```

### 6. SecurityUtils（安全工具）

```python
class SecurityUtils:
    @staticmethod
    def hash_password(password: str) -> str
    """使用 bcrypt 加密密码"""

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool
    """验证密码"""

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str
    """创建 JWT Access Token"""

    @staticmethod
    def create_refresh_token(data: dict) -> str
    """创建 JWT Refresh Token"""

    @staticmethod
    def decode_token(token: str) -> dict
    """解码 JWT Token"""
```

### 7. TushareClient（Tushare API 客户端）

```python
class TushareClient:
    def __init__(self, token: str)
    """初始化 Tushare 客户端"""

    async def get_daily_quotes(self, trade_date: str = None) -> pd.DataFrame
    """获取日线行情数据"""

    async def get_stock_basic(self, market: str = None) -> pd.DataFrame
    """获取股票基础信息"""

    async def search_stock(self, keyword: str) -> list[dict]
    """搜索股票"""

    async def get_top_list(self, trade_date: str = None) -> pd.DataFrame
    """获取龙虎榜数据"""
```

---

## 二、前端组件方法

### 1. 状态管理 Store

#### 1.1 useAuthStore

```typescript
interface AuthStore {
  // 状态
  token: string | null;           // JWT Token
  user: User | null;              // 用户信息
  isAuthenticated: boolean;       // 是否已登录
  is2FARequired: boolean;         // 是否需要 2FA 验证
  loading: boolean;               // 加载状态

  // 方法
  login(data: LoginRequest): Promise<void>;       // 登录
  register(data: RegisterRequest): Promise<void>;  // 注册
  logout(): Promise<void>;                          // 登出
  refreshToken(): Promise<void>;                    // 刷新 Token
  fetchUser(): Promise<void>;                       // 获取用户信息
  verify2FA(code: string): Promise<void>;           // 验证 2FA
}
```

#### 1.2 useMarketStore

```typescript
interface MarketStore {
  // 状态
  rankings: Record<string, StockQuote[]>;  // 各类榜单数据
  searchResults: SymbolInfo[];              // 搜索结果
  activeRankingType: string;               // 当前榜单类型
  loading: boolean;                         // 加载状态
  refreshTimer: number | null;             // 刷新定时器

  // 方法
  fetchRankings(type: string): Promise<void>;       // 获取榜单
  searchSymbols(keyword: string): Promise<void>;    // 搜索标的
  startAutoRefresh(interval?: number): void;        // 开始自动刷新
  stopAutoRefresh(): void;                           // 停止自动刷新
  clearSearchResults(): void;                        // 清空搜索结果
}
```

#### 1.3 usePortfolioStore

```typescript
interface PortfolioStore {
  // 状态
  portfolios: Portfolio[];                  // 组合列表
  activePortfolioId: number | null;        // 当前选中组合 ID
  items: WatchlistItem[];                  // 当前组合内标的
  loading: boolean;                         // 加载状态

  // 方法
  fetchPortfolios(): Promise<void>;                              // 获取组合列表
  createPortfolio(name: string): Promise<void>;                  // 创建组合
  updatePortfolio(id: number, name: string): Promise<void>;      // 更新组合
  deletePortfolio(id: number): Promise<void>;                    // 删除组合
  reorderPortfolios(ids: number[]): Promise<void>;               // 排序组合
  setActivePortfolio(id: number): void;                          // 切换组合
  fetchItems(portfolioId: number): Promise<void>;                // 获取标的
  addItem(portfolioId: number, symbol: SymbolInfo): Promise<void>;  // 添加标的
  removeItem(portfolioId: number, itemId: number): Promise<void>;   // 移除标的
  reorderItems(portfolioId: number, ids: number[]): Promise<void>;  // 排序标的
}
```

#### 1.4 useThemeStore

```typescript
interface ThemeStore {
  // 状态
  theme: 'light' | 'dark';    // 当前主题

  // 方法
  toggleTheme(): void;         // 切换主题
  setTheme(theme: 'light' | 'dark'): void;  // 设置主题
}
```

### 2. API 服务层

#### 2.1 apiClient

```typescript
// Axios 实例配置
const apiClient: AxiosInstance
  // 请求拦截器: 自动注入 JWT Token
  // 响应拦截器: 统一错误处理、Token 过期自动刷新
```

#### 2.2 authApi

```typescript
const authApi = {
  register(data: RegisterRequest): Promise<UserResponse>;
  login(data: LoginRequest): Promise<TokenResponse>;
  logout(): Promise<void>;
  refreshToken(refreshToken: string): Promise<TokenResponse>;
  getMe(): Promise<UserResponse>;
  enable2FA(): Promise<TwoFactorSetupResponse>;
  verify2FA(code: string): Promise<void>;
  disable2FA(code: string): Promise<void>;
}
```

#### 2.3 marketApi

```typescript
const marketApi = {
  getRankings(type: string, market?: string): Promise<StockQuote[]>;
  searchSymbols(keyword: string): Promise<SymbolInfo[]>;
  getQuote(symbol: string): Promise<StockQuote>;
}
```

#### 2.4 portfolioApi

```typescript
const portfolioApi = {
  getPortfolios(): Promise<Portfolio[]>;
  createPortfolio(name: string): Promise<Portfolio>;
  updatePortfolio(id: number, name: string): Promise<Portfolio>;
  deletePortfolio(id: number): Promise<void>;
  reorderPortfolios(ids: number[]): Promise<void>;
  getItems(portfolioId: number): Promise<WatchlistItem[]>;
  addItem(portfolioId: number, data: AddItemRequest): Promise<WatchlistItem>;
  removeItem(portfolioId: number, itemId: number): Promise<void>;
  reorderItems(portfolioId: number, ids: number[]): Promise<void>;
}
```

---

**注意**: 详细的业务逻辑规则将在构建阶段的功能设计中定义。
