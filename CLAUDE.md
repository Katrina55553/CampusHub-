# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

CampusBite（校园美食评价系统）—— 一个基于 Django 的校园美食店铺展示与评价平台。

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
python manage.py test food
```

## 技术栈

- **后端**: Django + SQLite
- **前端**: Bootstrap 5 + Django Template（无 SPA 框架）
- **图标**: Bootstrap Icons
- **语言/时区**: zh-hans / Asia/Shanghai

## 架构

单 Django 项目，单应用 `food`，项目配置在 `config/` 目录。

### 核心模型（`food/models.py`）

- **Category** — 美食分类（食堂、奶茶、小吃等），带 Bootstrap 图标字段
- **Shop** — 店铺，FK 到 Category，含图片、位置、人均价格；`avg_rating()` 和 `review_count()` 为计算属性
- **Review** — 用户评价，FK 到 Shop 和 User，评分 1-5 星

### 视图（`food/views.py`）

函数视图，无 CBV：
- `home` — 首页：分类导航 + 高分推荐（annotate + Avg）+ 最新店铺
- `shop_list` — 全部店铺，支持 `?category=` 筛选
- `shop_by_category` — 重定向到 shop_list 带筛选参数
- `shop_detail` — 店铺详情 + 评价列表
- `search` — 按名称/描述/位置模糊搜索（Q 对象）
- `add_review` — 需登录，POST 提交评价

### 模板结构

```
food/templates/
├── includes/base.html    # 基模板（导航栏、搜索框、消息提示、页脚）
└── food/
    ├── home.html
    ├── shop_list.html
    ├── shop_detail.html
    └── search.html
```

### 静态/媒体文件

- `static/css/style.css` — 卡片悬停动画等自定义样式
- `media/shops/` — 店铺图片上传目录，需预置 `default.jpg`

## 注意事项

- 用户认证复用 Django Admin 的登录/登出（`admin:login` / `admin:logout`），未自建 auth 视图
- 模板中使用 `{% csrf_token %}` 保护 POST 表单
- 店铺图片使用 `ImageField`，需确保 Pillow 已安装
