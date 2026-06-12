# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

CampusBite — 校园生活综合平台，包含两个核心模块：
- **美食评价系统**（food）：店铺展示、用户评价、数据分析、口味分析
- **快递代取平台**（orders）：发布代取需求、接单互助、订单跟踪、数据统计

## 常用命令

```bash
# 激活虚拟环境
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 安装依赖
pip install django

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员账号
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
# 访问 http://127.0.0.1:8000/
# Admin 后台 http://127.0.0.1:8000/admin/

# 运行测试
python manage.py test food orders
```

## 技术栈

- **后端**: Django + SQLite
- **前端**: Bootstrap 5 + Django Template（无 SPA 框架）
- **图标**: Bootstrap Icons
- **图表**: Chart.js
- **语言/时区**: zh-hans / Asia/Shanghai

## 架构

Django 项目，双应用 `food` + `orders`，项目配置在 `config/` 目录。

### 应用结构

```
CampusBite/
├── config/                  # 项目配置（settings, urls, wsgi）
├── food/                    # 美食评价模块
│   ├── models.py            # Category, Shop, Review 模型
│   ├── views.py             # 首页、店铺列表、详情、搜索、评价、分析
│   ├── urls.py
│   └── templates/food/
├── orders/                  # 快递代取模块
│   ├── models.py            # Order 模型（状态机）
│   ├── views.py             # 用户认证、订单 CRUD、统计、预测
│   ├── urls.py
│   └── templates/orders/
├── static/
│   ├── css/style.css        # 美食模块样式
│   └── css/orders.css       # 快递模块样式
└── media/shops/             # 店铺图片上传
```

### 核心模型

**food 应用**：
- **Category** — 美食分类（食堂、奶茶、小吃等），带 Bootstrap 图标字段
- **Shop** — 店铺，FK 到 Category，含图片、位置、人均价格
- **Review** — 用户评价，FK 到 Shop 和 User，评分 1-5 星

**orders 应用**：
- **Order** — 快递代取订单，关联发布者和接单者
  - 状态机：pending → accepted → completed / cancelled
  - 包含：快递点、取件码、报酬、联系方式

### URL 路由

| 路由 | 功能 |
|------|------|
| `/` | 美食首页（分类导航 + 高分推荐 + 最新店铺） |
| `/shops/` | 店铺列表（支持分类筛选） |
| `/shop/<id>/` | 店铺详情 + 评价 |
| `/search/` | 美食搜索 |
| `/analytics/` | 美食数据统计 |
| `/taste/` | 口味分析 |
| `/orders/` | 快递代取首页（订单列表 + 状态筛选） |
| `/orders/<id>/` | 订单详情 |
| `/orders/create/` | 发布代取需求 |
| `/orders/my-orders/` | 我的订单 |
| `/orders/search/` | 订单搜索 |
| `/orders/stats/` | 快递数据统计 |
| `/orders/predict/` | 接单时间预测 |
| `/orders/login/` | 用户登录 |
| `/orders/register/` | 用户注册 |

### 用户认证

- 自定义登录/注册页面（`/orders/login/`、`/orders/register/`）
- 使用 `@login_required` 装饰器保护需登录的视图
- `LOGIN_URL = '/orders/login/'`

### 模板结构

```
templates/
├── includes/base.html       # 统一基模板（导航栏、搜索框、消息提示、页脚）
├── food/                    # 美食模块模板
│   ├── home.html
│   ├── shop_list.html
│   ├── shop_detail.html
│   ├── search.html
│   ├── analytics.html
│   └── taste_analysis.html
└── orders/                  # 快递模块模板
    ├── base.html            # 继承基模板，引入 orders.css
    ├── index.html
    ├── detail.html
    ├── create.html
    ├── my_orders.html
    ├── search.html
    ├── stats.html
    ├── predict.html
    ├── login.html
    └── register.html
```

## 注意事项

- 两个模块共享同一用户系统（Django Auth）
- 导航栏统一在 `includes/base.html`，包含美食和快递入口
- 快递模块使用独立 CSS 文件（`orders.css`），避免样式冲突
- 模板中使用 `{% csrf_token %}` 保护 POST 表单
- 店铺图片使用 `ImageField`，需确保 Pillow 已安装
- 安全配置使用环境变量（SECRET_KEY, DEBUG, ALLOWED_HOSTS）
