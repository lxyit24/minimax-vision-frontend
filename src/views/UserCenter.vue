<template>
  <div class="user-center">
    <!-- 顶部导航 -->
    <header class="top-nav">
      <div class="nav-brand">
        <span class="brand-icon">🔮</span>
        <span class="brand-name">慧眼</span>
        <span class="brand-badge">AI 助手</span>
      </div>
      <div class="nav-actions">
        <router-link to="/" class="nav-link">
          🏠 返回首页
        </router-link>
      </div>
    </header>

    <!-- 主体区域：侧边栏 + 内容 -->
    <div class="main-layout">
      <!-- 左侧导航栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <span class="sidebar-icon">👤</span>
          <span class="sidebar-title">用户中心</span>
        </div>
        <nav class="sidebar-nav">
          <button 
            class="nav-item" 
            :class="{ active: activeMenu === 'tokens' }"
            @click="activeMenu = 'tokens'"
          >
            <span class="nav-icon">🔑</span>
            <span class="nav-text">令牌管理</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeMenu === 'usage' }"
            @click="activeMenu = 'usage'"
          >
            <span class="nav-icon">📊</span>
            <span class="nav-text">使用日志</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeMenu === 'drawing' }"
            @click="activeMenu = 'drawing'"
          >
            <span class="nav-icon">🎨</span>
            <span class="nav-text">绘图日志</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeMenu === 'wallet' }"
            @click="activeMenu = 'wallet'"
          >
            <span class="nav-icon">💰</span>
            <span class="nav-text">钱包管理</span>
          </button>
          <button 
            class="nav-item" 
            :class="{ active: activeMenu === 'settings' }"
            @click="activeMenu = 'settings'"
          >
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">个人设置</span>
          </button>
        </nav>
        <div class="sidebar-footer">
          <button class="nav-item logout-btn" @click="handleLogout">
            <span class="nav-icon">🚪</span>
            <span class="nav-text">退出登录</span>
          </button>
        </div>
      </aside>

      <!-- 右侧内容区 -->
      <main class="content-area">
        <!-- 令牌管理 -->
        <div v-if="activeMenu === 'tokens'" class="content-panel">
          <div class="panel-header">
            <h2>🔑 令牌管理</h2>
            <button class="btn-primary">+ 创建令牌</button>
          </div>
          <div class="panel-body">
            <div class="empty-state">
              <span class="empty-icon">🔑</span>
              <p>暂无令牌</p>
              <p class="empty-hint">创建您的第一个 API 令牌</p>
            </div>
          </div>
        </div>

        <!-- 使用日志 -->
        <div v-else-if="activeMenu === 'usage'" class="content-panel">
          <div class="panel-header">
            <h2>📊 使用日志</h2>
          </div>
          <div class="panel-body">
            <div class="empty-state">
              <span class="empty-icon">📊</span>
              <p>暂无使用记录</p>
              <p class="empty-hint">开始使用 AI 服务后将显示使用日志</p>
            </div>
          </div>
        </div>

        <!-- 绘图日志 -->
        <div v-else-if="activeMenu === 'drawing'" class="content-panel">
          <div class="panel-header">
            <h2>🎨 绘图日志</h2>
          </div>
          <div class="panel-body">
            <div class="empty-state">
              <span class="empty-icon">🎨</span>
              <p>暂无绘图记录</p>
              <p class="empty-hint">使用绘图功能后将显示绘图日志</p>
            </div>
          </div>
        </div>

        <!-- 钱包管理 -->
        <div v-else-if="activeMenu === 'wallet'" class="content-panel">
          <div class="panel-header">
            <h2>💰 钱包管理</h2>
          </div>
          <div class="panel-body">
            <!-- 余额显示 -->
            <div class="balance-display">
              <span class="balance-label">当前余额</span>
              <span class="balance-value">¥{{ formatYuan(currentUser?.quota || 0) }}</span>
            </div>

            <!-- 统计信息 -->
            <div class="usage-stats">
              <div class="stat-item">
                <span class="stat-label">累计已用</span>
                <span class="stat-value">¥{{ formatYuan(currentUser?.used_quota || 0) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">API请求</span>
                <span class="stat-value">{{ walletInfo?.request_count?.toLocaleString() || 0 }}</span>
              </div>
            </div>

            <!-- 快速操作 -->
            <div class="quick-actions">
              <button class="action-btn primary" @click="openRechargeModal">
                <span class="action-icon">💎</span>
                <span class="action-text">充值</span>
              </button>
              <button class="action-btn" @click="openHistoryModal">
                <span class="action-icon">📜</span>
                <span class="action-text">充值记录</span>
              </button>
              <button class="action-btn" @click="openRedeemModal">
                <span class="action-icon">🎫</span>
                <span class="action-text">兑换码</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 个人设置 -->
        <div v-else-if="activeMenu === 'settings'" class="content-panel">
          <div class="panel-header">
            <h2>⚙️ 个人设置</h2>
          </div>
          <div class="panel-body">
            <div class="settings-section">
              <h3>📋 账户信息</h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">用户ID</span>
                  <span class="info-value">{{ currentUser?.id }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">用户名</span>
                  <span class="info-value">{{ currentUser?.username }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">显示名称</span>
                  <span class="info-value">{{ currentUser?.display_name || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">邮箱</span>
                  <span class="info-value">{{ currentUser?.email || '-' }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">角色</span>
                  <span class="info-value">{{ roleText }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">账户状态</span>
                  <span class="info-value" :class="statusClass">{{ statusText }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="showLogoutToast" class="toast">
        ✅ 已退出登录
      </div>
    </Transition>

    <!-- 充值弹窗 -->
    <Transition name="modal">
      <div v-if="showRechargeModal" class="modal-overlay" @click.self="showRechargeModal = false">
        <div class="modal-content recharge-modal">
          <div class="modal-header">
            <h3>💎 充值配额</h3>
            <button class="modal-close" @click="showRechargeModal = false">✕</button>
          </div>
          <div class="modal-body">
            <!-- 预设金额 -->
            <div class="form-section">
              <label class="form-label">选择金额</label>
              <div class="preset-grid">
                <button
                  v-for="amount in topupInfo?.amount_options"
                  :key="amount"
                  class="preset-btn"
                  :class="{ active: selectedPreset === amount }"
                  @click="selectPreset(amount)"
                >
                  <span class="preset-amount">{{ formatQuota(amount) }}</span>
                  <span class="preset-price">{{ formatMoney(amount) }}</span>
                  <span v-if="getDiscountPercent(amount)" class="preset-badge">{{ getDiscountPercent(amount) }}</span>
                </button>
              </div>
            </div>

            <!-- 自定义金额 -->
            <div class="form-section">
              <label class="form-label">自定义金额</label>
              <div class="custom-input-wrap">
                <input
                  v-model="customAmount"
                  type="number"
                  class="custom-input"
                  placeholder="最低 {{ formatQuota(topupInfo?.min_topup || 100000) }}"
                  :min="topupInfo?.min_topup || 100000"
                  step="100000"
                  @input="onCustomAmountChange"
                />
                <span class="custom-suffix">配额</span>
              </div>
            </div>

            <!-- 支付方式 -->
            <div class="form-section">
              <label class="form-label">支付方式</label>
              <div class="payment-methods">
                <button
                  v-for="method in topupInfo?.pay_methods"
                  :key="method.type"
                  class="payment-btn"
                  :class="{ active: selectedPaymentMethod === method.type }"
                  :style="{ '--method-color': method.color }"
                  @click="selectedPaymentMethod = method.type"
                >
                  <span class="payment-name">{{ method.name }}</span>
                </button>
              </div>
            </div>

            <!-- 订单摘要 -->
            <div v-if="selectedAmount > 0" class="order-summary">
              <div class="summary-row">
                <span>充值配额</span>
                <span>{{ formatQuota(selectedAmount) }}</span>
              </div>
              <div v-if="getDiscountPercent(selectedAmount)" class="summary-row discount">
                <span>优惠</span>
                <span>+{{ getDiscountPercent(selectedAmount) }}</span>
              </div>
              <div class="summary-row total">
                <span>实际到账</span>
                <span class="highlight">{{ formatQuota(actualQuota) }}</span>
              </div>
              <div class="summary-row">
                <span>支付金额</span>
                <span class="money">{{ formatMoney(actualQuota / 100) }}</span>
              </div>
            </div>

            <!-- 充值按钮 -->
            <button
              class="recharge-submit-btn"
              :disabled="selectedAmount <= 0 || isRecharging"
              @click="handleRecharge"
            >
              <span v-if="isRecharging">处理中...</span>
              <span v-else>确认充值 {{ selectedAmount > 0 ? formatMoney(actualQuota / 100) : '' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 充值记录弹窗 -->
    <Transition name="modal">
      <div v-if="showHistoryModal" class="modal-overlay" @click.self="showHistoryModal = false">
        <div class="modal-content history-modal">
          <div class="modal-header">
            <h3>📜 充值记录</h3>
            <button class="modal-close" @click="showHistoryModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div v-if="topupHistory.length === 0" class="empty-history">
              <span class="empty-icon">📜</span>
              <p>暂无充值记录</p>
            </div>
            <div v-else class="history-list">
              <div v-for="record in topupHistory" :key="record.id" class="history-item">
                <div class="history-info">
                  <span class="history-no">订单号: {{ record.trade_no }}</span>
                  <span class="history-time">{{ formatTime(record.create_time) }}</span>
                </div>
                <div class="history-details">
                  <span class="history-amount">+{{ formatQuota(record.amount) }}</span>
                  <span class="history-money">{{ formatMoney(record.money) }}</span>
                  <span class="history-status" :class="record.status">{{ record.status === 'success' ? '成功' : record.status }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 兑换码弹窗 -->
    <Transition name="modal">
      <div v-if="showRedeemModal" class="modal-overlay" @click.self="showRedeemModal = false">
        <div class="modal-content redeem-modal">
          <div class="modal-header">
            <h3>🎫 兑换码充值</h3>
            <button class="modal-close" @click="showRedeemModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="redeem-hint">
              <p>输入您获得的兑换码，即可充值配额</p>
              <p class="redeem-example">格式示例: CARD_1000000_ABC123</p>
            </div>
            <div class="redeem-input-wrap">
              <input
                v-model="redeemCode"
                type="text"
                class="redeem-input"
                placeholder="请输入兑换码"
              />
            </div>
            <button
              class="redeem-submit-btn"
              :disabled="!redeemCode.trim() || isRedeeming"
              @click="handleRedeem"
            >
              <span v-if="isRedeeming">兑换中...</span>
              <span v-else>立即兑换</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface UserInfo {
  id: number
  username: string
  display_name: string
  quota: number
  used_quota: number
  role: number
  email: string
  status: number
}

interface WalletInfo {
  id: number
  username: string
  quota: number
  used_quota: number
  request_count: number
  aff_quota: number
  aff_history_quota: number
  aff_count: number
  group: string
}

interface TopupInfo {
  enable_online_topup: boolean
  enable_stripe_topup: boolean
  pay_methods: { name: string; type: string; color?: string }[]
  min_topup: number
  amount_options: number[]
  discount: Record<number, number>
}

interface TopupRecord {
  id: number
  user_id: number
  amount: number
  money: number
  trade_no: string
  payment_method: string
  create_time: number
  complete_time?: number
  status: string
}

const router = useRouter()
const TOKEN_KEY = 'minimax-vision-auth-token'

const activeMenu = ref('wallet') // 默认显示钱包管理
const currentUser = ref<UserInfo | null>(null)
const showLogoutToast = ref(false)

// 钱包相关状态
const walletInfo = ref<WalletInfo | null>(null)
const topupInfo = ref<TopupInfo | null>(null)
const topupHistory = ref<TopupRecord[]>([])
const showRechargeModal = ref(false)
const showHistoryModal = ref(false)
const showRedeemModal = ref(false)

// 充值表单状态
const selectedPreset = ref<number | null>(null)
const customAmount = ref('')
const selectedPaymentMethod = ref('wechat')
const isRecharging = ref(false)

// 兑换码状态
const redeemCode = ref('')
const isRedeeming = ref(false)

// 格式化配额
const formatQuota = (quota: number): string => {
  if (quota >= 100000000) return (quota / 100000000).toFixed(1) + ' 亿'
  if (quota >= 10000) return (quota / 10000).toFixed(1) + ' 万'
  return quota.toLocaleString()
}

// 配额转换为元 (1元 = 50万配额)
const formatYuan = (quota: number): string => {
  return (quota / 500000).toFixed(2)
}

// 格式化金额
const formatMoney = (money: number): string => {
  return '¥' + money.toFixed(2)
}

// 格式化时间
const formatTime = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算实际充值配额（含折扣）
const getActualQuota = (amount: number): number => {
  if (!topupInfo.value) return amount
  const discount = topupInfo.value.discount[amount] || 0
  return Math.floor(amount * (1 + discount))
}

// 计算折扣百分比
const getDiscountPercent = (amount: number): string => {
  if (!topupInfo.value) return ''
  const discount = topupInfo.value.discount[amount]
  if (!discount) return ''
  return '送' + (discount * 100).toFixed(0) + '%'
}

// 当前选择的充值金额
const selectedAmount = computed((): number => {
  if (selectedPreset.value) return selectedPreset.value
  const amt = parseInt(customAmount.value) || 0
  return amt >= (topupInfo.value?.min_topup || 100000) ? amt : 0
})

// 实际到账配额
const actualQuota = computed((): number => {
  return getActualQuota(selectedAmount.value)
})

// 角色文本
const roleText = computed(() => {
  const roles: Record<number, string> = {
    0: '超级管理员',
    1: '普通用户',
    2: 'VIP用户',
    3: '企业用户'
  }
  return roles[currentUser.value?.role || 1] || '普通用户'
})

// 状态文本
const statusText = computed(() => {
  return currentUser.value?.status === 1 ? '正常' : '已禁用'
})

// 状态样式
const statusClass = computed(() => {
  return currentUser.value?.status === 1 ? 'status-active' : 'status-disabled'
})

// 获取 token
const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

// 获取用户信息
const fetchUserInfo = async () => {
  const token = getToken()
  if (!token) {
    router.push('/')
    return
  }

  try {
    const response = await fetch('/api/userinfo', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    if (data.success) {
      currentUser.value = data.user
    } else {
      localStorage.removeItem(TOKEN_KEY)
      router.push('/')
    }
  } catch (e) {
    localStorage.removeItem(TOKEN_KEY)
    router.push('/')
  }
}

// 获取钱包信息
const fetchWalletInfo = async () => {
  const token = getToken()
  if (!token) return

  try {
    const response = await fetch('/api/wallet/info', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    if (data.success) {
      walletInfo.value = data.data
    }
  } catch (e) {
    console.error('Failed to fetch wallet info:', e)
  }
}

// 获取充值配置
const fetchTopupInfo = async () => {
  const token = getToken()
  if (!token) return

  try {
    const response = await fetch('/api/wallet/topup-info', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    if (data.success) {
      topupInfo.value = data.data
    }
  } catch (e) {
    console.error('Failed to fetch topup info:', e)
  }
}

// 获取充值历史
const fetchTopupHistory = async () => {
  const token = getToken()
  if (!token) return

  try {
    const response = await fetch('/api/wallet/history?page=1&page_size=50', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    if (data.success) {
      topupHistory.value = data.data.items
    }
  } catch (e) {
    console.error('Failed to fetch topup history:', e)
  }
}

// 选择预设金额
const selectPreset = (amount: number) => {
  selectedPreset.value = amount
  customAmount.value = ''
}

// 自定义金额输入
const onCustomAmountChange = () => {
  selectedPreset.value = null
}

// 充值
const handleRecharge = async () => {
  if (selectedAmount.value <= 0) {
    alert('请选择或输入有效的充值金额')
    return
  }

  const token = getToken()
  if (!token) return

  isRecharging.value = true

  try {
    const response = await fetch('/api/wallet/topup', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        amount: selectedAmount.value,
        payment_method: selectedPaymentMethod.value
      })
    })
    const data = await response.json()

    if (data.success && data.data.pay_url) {
      // 跳转到易支付完成支付
      window.location.href = data.data.pay_url
    } else if (data.success) {
      // 如果没有 pay_url（其他支付方式），显示成功
      alert(`充值成功！\n交易号：${data.data.trade_no}\n获得配额：${formatQuota(data.data.amount)}`)
      showRechargeModal.value = false
      // 刷新用户信息
      await fetchUserInfo()
      await fetchWalletInfo()
      await fetchTopupHistory()
      // 重置选择
      selectedPreset.value = null
      customAmount.value = ''
    } else {
      alert('充值失败：' + (data.error || '未知错误'))
    }
  } catch (e) {
    alert('充值请求失败')
  } finally {
    isRecharging.value = false
  }
}

// 兑换码充值
const handleRedeem = async () => {
  const code = redeemCode.value.trim()
  if (!code) {
    alert('请输入兑换码')
    return
  }

  const token = getToken()
  if (!token) return

  isRedeeming.value = true

  try {
    const response = await fetch('/api/wallet/redeem', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ key: code })
    })
    const data = await response.json()

    if (data.success) {
      alert(`兑换成功！\n${data.message}`)
      showRedeemModal.value = false
      redeemCode.value = ''
      // 刷新用户信息
      await fetchUserInfo()
      await fetchWalletInfo()
    } else {
      alert('兑换失败：' + (data.error || '无效的兑换码'))
    }
  } catch (e) {
    alert('兑换请求失败')
  } finally {
    isRedeeming.value = false
  }
}

// 登出
const handleLogout = async () => {
  const token = getToken()
  if (token) {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
    } catch (e) {
      // ignore
    }
  }

  localStorage.removeItem(TOKEN_KEY)
  showLogoutToast.value = true

  setTimeout(() => {
    router.push('/')
  }, 1500)
}

// 打开充值弹窗
const openRechargeModal = () => {
  showRechargeModal.value = true
  selectedPreset.value = null
  customAmount.value = ''
}

// 打开历史弹窗
const openHistoryModal = async () => {
  showHistoryModal.value = true
  await fetchTopupHistory()
}

// 打开兑换弹窗
const openRedeemModal = () => {
  showRedeemModal.value = true
  redeemCode.value = ''
}

onMounted(async () => {
  await fetchUserInfo()
  await fetchWalletInfo()
  await fetchTopupInfo()
})
</script>

<style scoped>
.user-center {
  --primary: #6366f1;
  --primary-dark: #4f46e5;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --bg-code: #0d1117;
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border: #334155;
  --sidebar-width: 240px;

  min-height: 100vh;
  background: var(--bg-dark);
}

/* 顶部导航 */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 2rem;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  font-size: 1.5rem;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.brand-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  background: var(--primary);
  border-radius: 9999px;
  color: white;
}

.nav-actions {
  display: flex;
  gap: 1rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-card);
}

/* 主体布局 */
.main-layout {
  display: flex;
  min-height: calc(100vh - 57px);
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width);
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 57px;
  height: calc(100vh - 57px);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.sidebar-icon {
  font-size: 1.25rem;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid var(--border);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  font-size: 0.9375rem;
}

.nav-item:hover {
  background: rgba(99, 102, 241, 0.1);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary);
  color: white;
}

.nav-icon {
  font-size: 1.125rem;
  width: 1.5rem;
  text-align: center;
}

.nav-text {
  flex: 1;
}

.logout-btn {
  color: var(--danger);
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* 内容区 */
.content-area {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

.content-panel {
  max-width: 900px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.panel-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.btn-primary {
  padding: 0.625rem 1.25rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: var(--primary-dark);
}

.panel-body {
  background: var(--bg-card);
  border-radius: 0.75rem;
  border: 1px solid var(--border);
  padding: 2rem;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin: 0 0 0.5rem 0;
}

.empty-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* 配额卡片 */
.quota-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(99, 102, 241, 0.05));
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.quota-header {
  margin-bottom: 1.25rem;
}

.quota-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.quota-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.25rem;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-value.primary {
  color: var(--primary);
}

.stat-value.warning {
  color: var(--warning);
}

.stat-value.success {
  color: var(--success);
}

.quota-bar {
  height: 8px;
  background: var(--bg-dark);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.75rem;
}

.quota-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--success));
  border-radius: 4px;
  transition: width 0.3s ease;
}

.quota-fill.danger {
  background: linear-gradient(90deg, var(--warning), var(--danger));
}

.quota-hint {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 0;
}

/* 设置页面 */
.settings-section {
  margin-bottom: 2rem;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.settings-section h3 {
  font-size: 1.125rem;
  color: var(--text-primary);
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--bg-dark);
  border-radius: 0.5rem;
}

.info-label {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

.info-value.status-active {
  color: var(--success);
}

.info-value.status-disabled {
  color: var(--danger);
}

/* Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.875rem 1.5rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  color: var(--text-primary);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(1rem);
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 72px;
  }
  
  .sidebar-header {
    padding: 1rem 0.5rem;
    justify-content: center;
  }
  
  .sidebar-title {
    display: none;
  }
  
  .nav-item {
    padding: 0.75rem;
    justify-content: center;
  }
  
  .nav-text {
    display: none;
  }
  
  .content-area {
    padding: 1rem;
  }
  
  .quota-stats {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

/* 余额卡片 */
.balance-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
}

.balance-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.balance-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
}

.balance-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
}

.balance-unit {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.btn-recharge {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #6366f1;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-recharge:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* 充值弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 1rem;
  width: 90%;
  max-width: 480px;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

.modal-close:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 1.5rem;
}

.recharge-hint {
  text-align: center;
  color: var(--text-secondary);
  margin: 0 0 1.25rem 0;
}

.recharge-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.recharge-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.recharge-option:hover {
  border-color: var(--primary);
  background: rgba(99, 102, 241, 0.1);
}

.recharge-amount {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.recharge-price {
  font-size: 0.875rem;
  color: var(--primary);
}

.recharge-note {
  text-align: center;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin: 1.25rem 0 0 0;
}

/* 钱包统计卡片 */
.wallet-stats-card {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
}

.wallet-stats-card .stat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-align: left;
}

.wallet-stats-card .stat-icon {
  font-size: 1.5rem;
}

.wallet-stats-card .stat-content {
  flex: 1;
}

.wallet-stats-card .stat-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.25rem;
}

.wallet-stats-card .stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.wallet-stats-card .stat-unit {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 余额显示 */
.balance-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
}

.balance-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 0.5rem;
}

.balance-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
}

/* 统计信息 */
.usage-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.usage-stats .stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
}

.usage-stats .stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.usage-stats .stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

/* 快速操作按钮 */
.quick-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.action-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.25rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--primary);
  background: rgba(99, 102, 241, 0.1);
}

.action-btn.primary {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.5);
}

.action-icon {
  font-size: 1.5rem;
}

.action-text {
  font-size: 0.875rem;
  color: var(--text-primary);
}

/* 充值弹窗新样式 */
.recharge-modal .modal-body {
  padding: 1.25rem;
}

.form-section {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.75rem;
}

/* 预设金额网格 */
.preset-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.preset-btn {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.875rem 0.5rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: var(--primary);
}

.preset-btn.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--primary);
}

.preset-amount {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.preset-price {
  font-size: 0.75rem;
  color: var(--primary);
}

.preset-badge {
  position: absolute;
  top: -0.375rem;
  right: -0.375rem;
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  background: var(--danger);
  color: white;
  border-radius: 9999px;
}

/* 自定义金额输入 */
.custom-input-wrap {
  display: flex;
  align-items: center;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  overflow: hidden;
}

.custom-input {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 1rem;
  outline: none;
}

.custom-input::placeholder {
  color: var(--text-muted);
}

.custom-suffix {
  padding: 0 1rem;
  color: var(--text-muted);
  font-size: 0.875rem;
}

/* 支付方式 */
.payment-methods {
  display: flex;
  gap: 0.75rem;
}

.payment-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.payment-btn:hover {
  border-color: var(--method-color, var(--primary));
}

.payment-btn.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--method-color, var(--primary));
}

.payment-name {
  font-size: 0.875rem;
  color: var(--text-primary);
}

/* 订单摘要 */
.order-summary {
  background: var(--bg-dark);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.375rem 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.summary-row.discount {
  color: var(--success);
}

.summary-row.total {
  padding-top: 0.75rem;
  margin-top: 0.5rem;
  border-top: 1px solid var(--border);
  font-weight: 600;
  color: var(--text-primary);
}

.summary-row .highlight {
  font-size: 1.125rem;
  color: var(--primary);
}

.summary-row .money {
  color: var(--warning);
  font-weight: 600;
}

/* 充值提交按钮 */
.recharge-submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.recharge-submit-btn:hover:not(:disabled) {
  background: var(--primary-dark);
}

.recharge-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 历史记录弹窗 */
.history-modal .modal-body {
  max-height: 60vh;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 2rem;
}

.empty-history .empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.75rem;
}

.empty-history p {
  color: var(--text-muted);
  margin: 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--bg-dark);
  border-radius: 0.5rem;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.history-no {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-family: monospace;
}

.history-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.history-details {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.history-amount {
  font-size: 1rem;
  font-weight: 600;
  color: var(--success);
}

.history-money {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.history-status {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.history-status.pending {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

/* 兑换码弹窗 */
.redeem-hint {
  text-align: center;
  margin-bottom: 1.25rem;
}

.redeem-hint p {
  margin: 0 0 0.5rem 0;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.redeem-example {
  font-family: monospace;
  color: var(--text-muted) !important;
  font-size: 0.75rem !important;
}

.redeem-input-wrap {
  margin-bottom: 1rem;
}

.redeem-input {
  width: 100%;
  padding: 0.875rem 1rem;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  color: var(--text-primary);
  font-size: 1rem;
  font-family: monospace;
  text-align: center;
  outline: none;
  transition: border-color 0.2s;
}

.redeem-input:focus {
  border-color: var(--primary);
}

.redeem-input::placeholder {
  color: var(--text-muted);
}

.redeem-submit-btn {
  width: 100%;
  padding: 0.875rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.redeem-submit-btn:hover:not(:disabled) {
  background: var(--primary-dark);
}

.redeem-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95);
}
</style>
