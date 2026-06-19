import statistics
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.views.decorators.http import require_POST

from .models import Order, LOCATIONS
from .services.lifecycle import (
    accept_order as accept_order_service,
    complete_order as complete_order_service,
    cancel_order as cancel_order_service,
    OrderLifecycleError,
)
from .services.stats import OrderStats
from utils.filters import QueryFilter


# ==================== 用户系统 ====================

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            messages.error(request, '用户名和密码不能为空')
        elif password != password2:
            messages.error(request, '两次密码不一致')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            try:
                validate_password(password)
            except Exception as e:
                for msg in e.messages:
                    messages.error(request, msg)
                return render(request, 'orders/register.html')

            User.objects.create_user(username=username, password=password)
            messages.success(request, '注册成功，请登录')
            return redirect('login')

    return render(request, 'orders/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'欢迎回来，{user.username}')
            return redirect('orders_index')
        else:
            messages.error(request, '用户名或密码错误')

    return render(request, 'orders/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, '已退出登录')
    return redirect('orders_index')


# ==================== 订单系统 ====================

# 通用查询过滤器
_ORDER_FILTER = QueryFilter(
    Order,
    filters={
        'status': lambda qs, value, meta: (
            qs.filter(status=value) if value in ('pending', 'accepted', 'completed', 'cancelled') else qs
        ),
    },
    search_fields=['title', 'description'],
    search_param='q',
    select_related=['publisher', 'helper'],
    default_ordering='-created_at',
)


def index(request):
    """首页：订单列表，支持按状态筛选"""
    orders, meta = _ORDER_FILTER.apply(request.GET)
    current_status = request.GET.get('status', '')

    stats = Order.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=Q(status='pending')),
        accepted=Count('id', filter=Q(status='accepted')),
        completed=Count('id', filter=Q(status='completed')),
    )

    return render(request, 'orders/index.html', {
        'orders': orders,
        'current_status': current_status,
        'stats': stats,
    })


def orders_search(request):
    """搜索订单"""
    orders, meta = _ORDER_FILTER.apply(request.GET)
    return render(request, 'orders/search.html', {
        'orders': orders,
        'keyword': meta.get('q', ''),
    })


@login_required
def order_detail(request, order_id):
    """订单详情（需登录，防止敏感信息泄露）"""
    order = get_object_or_404(Order.objects.select_related('publisher', 'helper'), pk=order_id)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def create_order(request):
    """发布代取需求"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '')
        pickup_code = request.POST.get('pickup_code', '').strip()
        reward = request.POST.get('reward', '')
        contact = request.POST.get('contact', '').strip()

        if not title or not location or not reward or not contact:
            messages.error(request, '请填写所有必填项')
            return render(request, 'orders/create.html', {
                'locations': LOCATIONS,
                'form_data': request.POST,
            })

        try:
            reward = Decimal(reward)
            if reward < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            messages.error(request, '报酬金额必须为非负数字')
            return render(request, 'orders/create.html', {
                'locations': LOCATIONS,
                'form_data': request.POST,
            })

        Order.objects.create(
            title=title,
            description=description,
            location=location,
            pickup_code=pickup_code,
            reward=reward,
            contact=contact,
            publisher=request.user,
        )
        OrderStats.invalidate()
        messages.success(request, '订单发布成功')
        return redirect('orders_index')

    return render(request, 'orders/create.html', {'locations': LOCATIONS})


@login_required
@require_POST
def accept_order(request, order_id):
    """接单（仅 POST）"""
    try:
        accept_order_service(order_id, request.user)
        OrderStats.invalidate()
        messages.success(request, '接单成功')
    except OrderLifecycleError as e:
        messages.error(request, str(e))
    except Order.DoesNotExist:
        messages.error(request, '订单不存在')
    return redirect('order_detail', order_id=order_id)


@login_required
@require_POST
def complete_order(request, order_id):
    """确认完成（仅 POST）"""
    try:
        complete_order_service(order_id, request.user)
        OrderStats.invalidate()
        messages.success(request, '订单已完成')
    except OrderLifecycleError as e:
        messages.error(request, str(e))
    except Order.DoesNotExist:
        messages.error(request, '订单不存在')
    return redirect('order_detail', order_id=order_id)


@login_required
@require_POST
def cancel_order(request, order_id):
    """取消订单（仅 POST）"""
    try:
        cancel_order_service(order_id, request.user)
        OrderStats.invalidate()
        messages.success(request, '订单已取消')
    except OrderLifecycleError as e:
        messages.error(request, str(e))
    except Order.DoesNotExist:
        messages.error(request, '订单不存在')
    return redirect('order_detail', order_id=order_id)


@login_required
def my_orders(request):
    """我的订单：我发布的 + 我接的"""
    published = Order.objects.filter(publisher=request.user).select_related('helper')
    helped = Order.objects.filter(helper=request.user).select_related('publisher')
    return render(request, 'orders/my_orders.html', {
        'published_orders': published,
        'helped_orders': helped,
    })


def stats(request):
    """数据统计页面：统计描述 + 可视化"""
    data = OrderStats.snapshot()
    rewards = data['rewards']
    reward_stats = data['reward_stats']
    status_counts = data['status_counts']
    location_data = data['location_data']

    location_map = dict(LOCATIONS)
    location_labels = [location_map.get(d['location'], d['location']) for d in location_data]
    location_counts = [d['count'] for d in location_data]
    location_avg_rewards = [round(float(d['avg_reward']), 2) for d in location_data]

    location_table = [
        {'label': l, 'count': c, 'avg': a}
        for l, c, a in zip(location_labels, location_counts, location_avg_rewards)
    ]

    status_labels = ['待接单', '已接单', '已完成', '已取消']
    status_values = [
        status_counts.get('pending', 0),
        status_counts.get('accepted', 0),
        status_counts.get('completed', 0),
        status_counts.get('cancelled', 0),
    ]

    reward_distribution = {}
    if rewards:
        bins = [0, 2, 4, 6, 8, 10, 100]
        bin_labels = ['0-2', '2-4', '4-6', '6-8', '8-10', '10+']
        for i in range(len(bins) - 1):
            label = bin_labels[i]
            count = sum(1 for r in rewards if bins[i] <= r < bins[i + 1])
            reward_distribution[label] = count

    return render(request, 'orders/stats.html', {
        'reward_stats': reward_stats,
        'status_labels': status_labels,
        'status_values': status_values,
        'location_labels': location_labels,
        'location_counts': location_counts,
        'location_avg_rewards': location_avg_rewards,
        'location_table': location_table,
        'reward_dist_labels': list(reward_distribution.keys()),
        'reward_dist_values': list(reward_distribution.values()),
        'total_orders': data['total_orders'],
    })


def predict(request):
    """接单时间预测：基于历史数据的线性回归分析"""
    accepted_orders = Order.objects.filter(
        accepted_at__isnull=False
    ).values('reward', 'accepted_at', 'created_at', 'location')

    data = []
    location_map = dict(LOCATIONS)
    for o in accepted_orders:
        delta = (o['accepted_at'] - o['created_at']).total_seconds() / 60.0
        data.append({
            'reward': float(o['reward']),
            'minutes': round(delta, 1),
            'location': o['location'],
            'location_label': location_map.get(o['location'], o['location']),
        })

    input_reward = request.GET.get('reward', '')
    input_location = request.GET.get('location', '')
    prediction = None

    rewards = [d['reward'] for d in data]
    minutes = [d['minutes'] for d in data]
    n = len(data)

    regression = None
    if n >= 2:
        x_mean = sum(rewards) / n
        y_mean = sum(minutes) / n
        ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(rewards, minutes))
        ss_xx = sum((x - x_mean) ** 2 for x in rewards)
        if ss_xx > 0:
            b = ss_xy / ss_xx
            a = y_mean - b * x_mean
            ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(rewards, minutes))
            ss_tot = sum((y - y_mean) ** 2 for y in minutes)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            regression = {
                'a': round(a, 2),
                'b': round(b, 2),
                'r_squared': round(r_squared, 4),
                'formula': f'y = {round(a, 2)} + ({round(b, 2)}) × 报酬',
            }

    location_stats = {}
    for d in data:
        loc = d['location_label']
        if loc not in location_stats:
            location_stats[loc] = []
        location_stats[loc].append(d['minutes'])

    location_avg = [
        {'label': k, 'avg': round(statistics.mean(v), 1), 'count': len(v)}
        for k, v in location_stats.items()
    ]
    location_avg.sort(key=lambda x: x['avg'])

    overall_avg = round(statistics.mean(minutes), 1) if minutes else 0
    overall_median = round(statistics.median(minutes), 1) if minutes else 0

    if input_reward:
        try:
            r = float(input_reward)
            if regression:
                predicted = regression['a'] + regression['b'] * r
                predicted = max(1, round(predicted, 1))

                if input_location and input_location in location_stats:
                    loc_avg = statistics.mean(location_stats[location_map.get(input_location, input_location)])
                    overall = statistics.mean(minutes)
                    bias = loc_avg - overall
                    predicted = max(1, round(predicted + bias, 1))

                prediction = {
                    'minutes': predicted,
                    'reward': r,
                    'location': location_map.get(input_location, '全部') if input_location else '全部',
                }
        except ValueError:
            pass

    scatter_data = [{'x': d['reward'], 'y': d['minutes']} for d in data]
    regression_line = []
    if regression and rewards:
        min_r = min(rewards)
        max_r = max(rewards)
        regression_line = [
            {'x': min_r, 'y': round(regression['a'] + regression['b'] * min_r, 1)},
            {'x': max_r, 'y': round(regression['a'] + regression['b'] * max_r, 1)},
        ]

    return render(request, 'orders/predict.html', {
        'locations': LOCATIONS,
        'input_reward': input_reward,
        'input_location': input_location,
        'prediction': prediction,
        'regression': regression,
        'location_avg': location_avg,
        'overall_avg': overall_avg,
        'overall_median': overall_median,
        'data_count': n,
        'scatter_data': scatter_data,
        'regression_line': regression_line,
    })
