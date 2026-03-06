/**
 * 项目总结分享页面
 * 展示项目功能范围、技术架构、部署方案、踩坑记录
 */

import React from 'react';

/** 技术栈标签 */
const TechBadge: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <span style={{
    display: 'inline-block',
    padding: '3px 10px',
    borderRadius: 12,
    fontSize: 12,
    fontWeight: 500,
    background: 'var(--tab-active-bg)',
    color: 'var(--accent-color)',
    margin: '3px 4px',
  }}>
    {children}
  </span>
);

/** 卡片容器 */
const SectionCard: React.FC<{ icon: string; title: string; children: React.ReactNode }> = ({ icon, title, children }) => (
  <div style={{
    background: 'var(--bg-card)',
    border: '1px solid var(--border-color)',
    borderRadius: 10,
    padding: '20px 24px',
    marginBottom: 16,
  }}>
    <div style={{
      fontSize: 15,
      fontWeight: 600,
      color: 'var(--text-primary)',
      marginBottom: 14,
      display: 'flex',
      alignItems: 'center',
      gap: 8,
    }}>
      <span style={{ fontSize: 18 }}>{icon}</span>
      {title}
    </div>
    {children}
  </div>
);

/** 问题卡片 */
const ProblemCard: React.FC<{
  index: number;
  title: string;
  problem: string;
  solution: string;
}> = ({ index, title, problem, solution }) => (
  <div style={{
    background: 'var(--bg-elevated)',
    borderRadius: 8,
    padding: '14px 16px',
    marginBottom: 10,
    borderLeft: '3px solid var(--accent-color)',
  }}>
    <div style={{
      fontSize: 13,
      fontWeight: 600,
      color: 'var(--text-primary)',
      marginBottom: 8,
      display: 'flex',
      alignItems: 'center',
      gap: 6,
    }}>
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 20,
        height: 20,
        borderRadius: '50%',
        background: 'var(--accent-color)',
        color: '#fff',
        fontSize: 11,
        fontWeight: 700,
        flexShrink: 0,
      }}>{index}</span>
      {title}
    </div>
    <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>
      <span style={{ color: 'var(--price-up)', fontWeight: 500 }}>问题：</span>{problem}
    </div>
    <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
      <span style={{ color: 'var(--price-down)', fontWeight: 500 }}>方案：</span>{solution}
    </div>
  </div>
);

/** 功能模块数据 */
const features = [
  {
    icon: '🔐',
    name: '用户认证',
    items: ['注册 / 登录 / 登出', '密码强度校验（大小写+数字+特殊字符）', '滑块验证码（连续失败后触发）', 'JWT Token 双令牌（Access + Refresh）', '两步验证 2FA（TOTP + 恢复码）', '设备管理'],
  },
  {
    icon: '📊',
    name: '行情数据',
    items: ['五大榜单（涨幅/跌幅/成交量/成交额/换手率）', '标的搜索（本地 A 股列表匹配）', '个股详情（实时行情 + K线图）', 'K线图表（日K/周K/月K，ECharts 渲染）', '30 秒自动轮询刷新'],
  },
  {
    icon: '⭐',
    name: '自选管理',
    items: ['多组合管理（创建/重命名/删除）', '标的添加/移除/排序', '实时行情合并展示', '数字变化闪烁特效（红涨绿跌）', '自选数据嵌入 JWT 持久化'],
  },
  {
    icon: '🎨',
    name: '界面体验',
    items: ['Webull 风格金融终端 UI', '明暗主题切换', '移动端响应式适配', '底部标签栏导航（移动端）', '红涨绿跌配色体系'],
  },
];

/** 架构层数据 */
const archLayers = [
  { label: '前端', color: '#3b82f6', items: ['React 18 + TypeScript', 'Zustand 状态管理', 'Ant Design 组件库', 'ECharts K线图表', 'Axios HTTP 客户端'] },
  { label: '后端', color: '#22c55e', items: ['FastAPI (Python)', 'JWT 认证 (PyJWT + bcrypt)', '内存存储 (MemoryStore)', '新浪财经 API (行情)', 'Yahoo Finance (搜索)'] },
  { label: '部署', color: '#f59e0b', items: ['Vercel Serverless', 'Python Runtime @4.5.0', 'Vite 构建前端', 'SPA 路由重写', '/tmp 文件持久化'] },
];

/** 踩坑记录 */
const problems = [
  {
    title: 'Vercel 部署后 SQLite 无法使用',
    problem: 'Vercel Serverless 函数是无状态的，不支持 SQLite 文件数据库，且 FastAPI lifespan 事件不会触发。',
    solution: '放弃 SQLAlchemy + SQLite，改用纯 Python 字典 + dataclass 的 MemoryStore 内存存储方案，数据序列化到 /tmp/memory_store.json 做同实例持久化。',
  },
  {
    title: '冷启动 / 实例切换导致 401',
    problem: 'Vercel 不同 Lambda 实例间内存不共享，冷启动后用户数据丢失，所有请求返回 401。',
    solution: '将自选数据快照嵌入 JWT Token（wl 字段），请求到达时自动从 Token 恢复用户和自选数据到内存。固定 JWT_SECRET_KEY 保证跨实例一致。',
  },
  {
    title: '自选数据刷新后丢失或重复',
    problem: '刷新页面后自选组合丢失，或恢复时产生重复数据。组合 ID 不一致导致前端找不到对应数据。',
    solution: '恢复前检查用户是否已有组合数据（有则跳过）。add_portfolio 支持 restore_id 参数，恢复时使用 Token 中记录的原始 ID，保持前后端一致。',
  },
  {
    title: '刷新页面闪烁到登录页',
    problem: 'authStore 初始 isAuthenticated 为 false，刷新时路由守卫立即重定向到登录页，等 Token 验证完成后又跳回来。',
    solution: '初始化 isAuthenticated 为 !!localStorage.getItem("access_token")。AppInitializer 中如果 access_token 存在则直接 fetchUser，不调用 refreshToken 避免旧快照覆盖。',
  },
  {
    title: '新浪 API 403 / 并发请求被封',
    problem: '轮询刷新时如果上一次请求未完成就发起新请求，高频并发触发新浪 API 的 403 封禁。',
    solution: '在 portfolioStore 和 marketStore 中加入 _refreshing 标记，轮询时如果上一次请求还在进行中则跳过本次。',
  },
  {
    title: '搜索接口 Vercel 上 504 超时',
    problem: '原搜索使用新浪接口，在 Vercel 海外节点访问新浪 API 超时（504）。',
    solution: '搜索改用本地内置 A 股列表（50 只热门股票）做关键词匹配，不依赖外部 API。行情/K线 仍用新浪（单次请求，不会超时）。',
  },
  {
    title: 'Yahoo Finance API 429 限流',
    problem: '尝试用 Yahoo Finance 替代新浪获取行情，但免费 API 限流严格，Vercel 上频繁 429。',
    solution: '放弃 Yahoo 行情方案，回退到新浪。Yahoo 仅用于搜索（本地匹配，不实际调用 API）。控制轮询频率（30 秒间隔）避免触发限流。',
  },
];

const ProjectSummaryPage: React.FC = () => {
  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '8px 0' }}>
      {/* 标题 */}
      <div style={{
        textAlign: 'center',
        marginBottom: 24,
        padding: '24px 16px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 10,
      }}>
        <div style={{ fontSize: 32, marginBottom: 8 }}>📈</div>
        <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 6 }}>
          股票助手 — 项目总结
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          一个使用 Kiro AI IDE 辅助开发的全栈 Demo 项目
          <br />
          从需求到部署，全程 AI 协作完成
        </div>
      </div>

      {/* 功能范围 */}
      <SectionCard icon="🧩" title="功能范围">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: 12,
        }}>
          {features.map((f) => (
            <div key={f.name} style={{
              background: 'var(--bg-elevated)',
              borderRadius: 8,
              padding: '14px 16px',
            }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>
                {f.icon} {f.name}
              </div>
              {f.items.map((item, i) => (
                <div key={i} style={{
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  padding: '2px 0',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 6,
                }}>
                  <span style={{ color: 'var(--accent-color)', flexShrink: 0 }}>•</span>
                  {item}
                </div>
              ))}
            </div>
          ))}
        </div>
      </SectionCard>

      {/* 技术架构 */}
      <SectionCard icon="🏗️" title="技术架构">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 12,
          marginBottom: 16,
        }}>
          {archLayers.map((layer) => (
            <div key={layer.label} style={{
              background: 'var(--bg-elevated)',
              borderRadius: 8,
              padding: '14px 16px',
              borderTop: `3px solid ${layer.color}`,
            }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: layer.color, marginBottom: 8 }}>
                {layer.label}
              </div>
              {layer.items.map((item, i) => (
                <div key={i} style={{ fontSize: 12, color: 'var(--text-secondary)', padding: '2px 0' }}>
                  {item}
                </div>
              ))}
            </div>
          ))}
        </div>

        <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 8 }}>
          核心技术栈
        </div>
        <div>
          {['React 18', 'TypeScript', 'Zustand', 'Ant Design', 'ECharts', 'FastAPI', 'Python 3.12', 'JWT', 'bcrypt', 'Vercel', 'Vite'].map((t) => (
            <TechBadge key={t}>{t}</TechBadge>
          ))}
        </div>
      </SectionCard>

      {/* 部署方案 */}
      <SectionCard icon="🚀" title="部署方案">
        <div style={{
          background: 'var(--bg-elevated)',
          borderRadius: 8,
          padding: '16px',
          fontSize: 12,
          color: 'var(--text-secondary)',
          lineHeight: 2,
        }}>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>平台：</span>Vercel Serverless（免费额度）</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>前端：</span>Vite 构建 → 静态文件托管，SPA 路由通过 rewrites 规则处理</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>后端：</span>FastAPI 挂载为 Serverless Function（api/index.py 入口），Python Runtime @4.5.0</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>数据：</span>内存存储 + /tmp JSON 持久化 + JWT 自选快照（无需数据库）</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>行情：</span>新浪财经 API（榜单/行情/K线），本地 A 股列表（搜索）</div>
          <div style={{ marginTop: 8, padding: '8px 12px', background: 'var(--bg-card)', borderRadius: 6, border: '1px solid var(--border-color)' }}>
            <span style={{ fontWeight: 500, color: 'var(--accent-color)' }}>💡 关键设计：</span>
            自选数据嵌入 JWT Token，解决 Serverless 无状态问题。每次自选变更后返回新 Token（X-New-Token 响应头），前端自动更新。
          </div>
        </div>
      </SectionCard>

      {/* 踩坑记录 */}
      <SectionCard icon="🔧" title="踩坑与解决方案">
        {problems.map((p, i) => (
          <ProblemCard key={i} index={i + 1} title={p.title} problem={p.problem} solution={p.solution} />
        ))}
      </SectionCard>

      {/* AI 协作 */}
      <SectionCard icon="🤖" title="AI 协作开发">
        <div style={{
          background: 'var(--bg-elevated)',
          borderRadius: 8,
          padding: '16px',
          fontSize: 12,
          color: 'var(--text-secondary)',
          lineHeight: 2,
        }}>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>开发工具：</span>Kiro AI IDE</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>开发流程：</span>需求分析 → 架构设计 → 功能实现 → 部署调试，全程 AI 辅助</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>迭代方式：</span>对话式迭代，遇到问题实时调整方案（如数据源切换、存储方案变更）</div>
          <div><span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>协作特点：</span>AI 负责代码生成和问题排查，人工负责需求决策和方向把控</div>
        </div>
      </SectionCard>

      {/* 底部 */}
      <div style={{
        textAlign: 'center',
        padding: '16px 0 24px',
        fontSize: 12,
        color: 'var(--text-tertiary)',
      }}>
        Built with Kiro AI IDE · 2025
      </div>
    </div>
  );
};

export default ProjectSummaryPage;
