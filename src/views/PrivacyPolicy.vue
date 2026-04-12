<template>
  <div class="privacy-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <router-link to="/" class="back-link">← 返回首页</router-link>
        <h1>隐私政策</h1>
        <p class="update-date">更新日期：2026年4月12日</p>
      </div>
    </header>

    <!-- Content -->
    <main class="page-content">
      <section class="policy-section">
        <h2>一、信息收集与使用</h2>
        <p>当我们为您提供服务时，我们会收集以下信息：</p>
        <ul>
          <li><strong>上传的图片</strong>：您主动上传用于分析的图片，仅用于为您提供图片分析服务。</li>
          <li><strong>聊天内容</strong>：您与 AI 对话的内容，用于提供对话服务。</li>
          <li><strong>技术日志</strong>：访问时间、浏览器类型、IP 地址等基础访问信息，用于服务稳定性分析和安全监控。</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>二、信息存储与安全</h2>
        <ul>
          <li>您上传的图片和聊天内容<strong>不会</strong>被永久存储在我们的服务器上。</li>
          <li>图片分析完成后，图片数据会被<strong>立即删除</strong>。</li>
          <li>聊天记录仅在当前会话中可用，关闭页面后不会保留。</li>
          <li>我们会采取合理的安全措施保护您的信息安全。</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>三、第三方服务</h2>
        <p>我们的服务使用以下第三方 AI 服务提供商：</p>
        <ul>
          <li><strong>MiniMax</strong>：提供图片理解和对话生成能力。</li>
        </ul>
        <p>当您使用我们的服务时，您的图片和消息会被发送到这些第三方提供商的服务器进行处理。我们会确保这些服务商具备相应的数据保护能力。</p>
      </section>

      <section class="policy-section">
        <h2>四、Cookie 使用</h2>
        <p>我们的网站可能会使用 Cookie 来：</p>
        <ul>
          <li>记住您的偏好设置（如界面语言、主题等）。</li>
          <li>分析网站访问量和使用情况。</li>
        </ul>
        <p>您可以在浏览器中禁用 Cookie，但这可能会影响部分网站功能。</p>
      </section>

      <section class="policy-section">
        <h2>五、信息共享</h2>
        <p>未经您的同意，我们<strong>不会</strong>与任何第三方共享您的个人信息，除非：</p>
        <ul>
          <li>法律法规要求。</li>
          <li>保护我们的合法权益。</li>
          <li>提供服务和响应您的请求所必需。</li>
        </ul>
      </section>

      <section class="policy-section">
        <h2>六、您的权利</h2>
        <p>根据适用法律，您有权：</p>
        <ul>
          <li>了解我们如何处理您的信息。</li>
          <li>请求删除您的个人信息。</li>
          <li>撤回您的同意（但不影响撤回前基于同意的处理）。</li>
        </ul>
        <p>如需行使上述权利，请通过网站底部的联系方式与我们联系。</p>
      </section>

      <section class="policy-section">
        <h2>七、未成年人保护</h2>
        <p>我们的服务不面向未满 18 周岁的未成年人。如果您是未成年人，请在监护人的陪同下使用我们的服务。</p>
      </section>

      <section class="policy-section">
        <h2>八、隐私政策更新</h2>
        <p>我们可能会不时更新本隐私政策。更新后我们会通过网站公告或弹窗通知您。重大变更时我们会征求您的同意。</p>
      </section>

      <section class="policy-section">
        <h2>九、联系我们</h2>
        <p>如果您对本隐私政策有任何疑问，请通过以下方式联系我们：</p>
        <ul>
          <li>网站：<a href="https://vision.1i.wiki" target="_blank">https://vision.1i.wiki</a></li>
          <li>备案信息：<a href="https://beian.miit.gov.cn/" target="_blank">鲁ICP备2025137668号</a></li>
        </ul>
      </section>
    </main>

    <!-- Footer -->
    <footer class="page-footer">
      <p>Copyright © 2023-2026 六仙云 | 鲁ICP备2025137668号</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
// No additional script needed for this static page
</script>

<style scoped>
.privacy-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #f8fafc;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  padding: 1.5rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
}

.back-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  display: inline-block;
  margin-bottom: 0.75rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: #f8fafc;
}

.page-header h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.update-date {
  color: #64748b;
  font-size: 0.875rem;
  margin: 0;
}

/* Content */
.page-content {
  flex: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

.policy-section {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.policy-section h2 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.policy-section p {
  color: #cbd5e1;
  line-height: 1.7;
  margin: 0 0 1rem 0;
}

.policy-section ul {
  margin: 0;
  padding-left: 1.5rem;
}

.policy-section li {
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 0.5rem;
}

.policy-section li strong {
  color: #f8fafc;
}

.policy-section a {
  color: #60a5fa;
  text-decoration: none;
}

.policy-section a:hover {
  text-decoration: underline;
}

/* Footer */
.page-footer {
  background: rgba(30, 41, 59, 0.4);
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  padding: 1.5rem 2rem;
  text-align: center;
}

.page-footer p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .page-header {
    padding: 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .page-content {
    padding: 1rem;
  }

  .policy-section {
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .policy-section h2 {
    font-size: 1.125rem;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 0.75rem;
  }

  .page-header h1 {
    font-size: 1.25rem;
  }

  .update-date {
    font-size: 0.75rem;
  }

  .page-content {
    padding: 0.75rem;
  }

  .policy-section {
    padding: 0.875rem;
    border-radius: 8px;
  }

  .policy-section h2 {
    font-size: 1rem;
  }

  .policy-section p,
  .policy-section li {
    font-size: 0.875rem;
  }
}
</style>
