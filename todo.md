# CampusBite 优化与扩展清单

## 优先级说明
- 🔴 高优先级（影响安全/性能）
- 🟡 中优先级（改善体验）
- 🟢 低优先级（锦上添花）

---

## 一、安全性优化 🔴

- [ ] 添加 CSRF_TRUSTED_ORIGINS 配置
- [ ] 设置 SECURE_BROWSER_XSS_FILTER 和 SECURE_CONTENT_TYPE_NOSNIFF
- [ ] 配置 SESSION_COOKIE_SECURE 和 CSRF_COOKIE_SECURE（生产环境）
- [ ] 添加文件上传大小限制（DATA_UPLOAD_MAX_MEMORY_SIZE）
- [ ] 实现密码强度验证和登录失败限制
- [ ] 使用 HTTPS 强制跳转（SECURE_SSL_REDIRECT）

## 二、性能优化 🔴

- [ ] 添加分页功能（Paginator）：
  - 店铺列表页
  - 搜索结果页
  - 评价列表
- [ ] 实现缓存机制：
  - 首页热门推荐缓存（@cache_page）
  - 分类数据缓存
  - 使用 Redis 作为缓存后端
- [ ] 优化查询：
  - 首页 top_shops 添加 select_related('category')
  - analytics 页面使用单次聚合查询替代循环
- [ ] 静态文件压缩（django-compressor）
- [ ] 图片懒加载和缩略图生成（sorl-thumbnail / easy-thumbnails）

## 三、功能扩展 🟡

### 用户系统
- [ ] 自定义用户注册/登录页面（替代 Admin 登录）
- [ ] 用户个人中心（头像、评价历史、收藏店铺）
- [ ] 用户头像上传
- [ ] 密码找回功能

### 评价系统
- [ ] 评价点赞/踩功能
- [ ] 评价图片上传
- [ ] 评价回复功能（评论嵌套）
- [ ] 评价举报机制
- [ ] 评价排序（最新、最热、评分高/低）

### 店铺功能
- [ ] 店铺收藏/点赞
- [ ] 店铺营业时间字段
- [ ] 店铺联系方式（电话、微信）
- [ ] 店铺地图定位（接入高德/百度地图 API）
- [ ] 相似店铺推荐

### 搜索增强
- [ ] 搜索高亮显示
- [ ] 搜索历史记录
- [ ] 热门搜索词
- [ ] 搜索自动补全（AJAX）

### 数据分析
- [ ] 用户评价趋势图（按月/季度）
- [ ] 分类热度排行
- [ ] 词云图（评价内容分析）
- [ ] 导出报表（CSV/Excel）

## 四、前端优化 🟡

- [ ] 添加面包屑导航
- [ ] 无限滚动加载（店铺列表）
- [ ] 图片加载占位符（骨架屏）
- [ ] 深色模式支持
- [ ] PWA 支持（离线访问）
- [ ] 移动端底部导航栏
- [ ] Toast 通知替代 alert 弹窗

## 五、代码质量 🟢

- [ ] 编写单元测试：
  - 模型方法测试
  - 视图功能测试
  - 表单验证测试
- [ ] 添加 Flake8 / Black 代码格式化
- [ ] 配置 pre-commit hooks
- [ ] 添加 CI/CD（GitHub Actions）
- [ ] 编写 API 文档（DRF / drf-spectacular）

## 六、部署相关 🟢

- [ ] Docker 容器化
- [ ] Nginx + Gunicorn 配置
- [ ] PostgreSQL 替换 SQLite
- [ ] 环境变量管理（python-decouple / django-environ）
- [ ] 日志配置（LOGGING 设置）
- [ ] 健康检查端点
- [ ] 数据库备份策略

## 七、其他扩展 🟢

- [ ] 多语言支持（i18n）
- [ ] WebSocket 实时通知（新评价提醒）
- [ ] 邮件通知系统
- [ ] SEO 优化（meta 标签、sitemap）
- [ ] 社交分享功能
- [ ] 店铺入驻申请流程

---

**最后更新**: 2026-06-13
**维护者**: CampusBite Team
