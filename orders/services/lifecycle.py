"""订单生命周期服务：集中处理接单、完成、取消的权限与状态转换。"""

from django.db import transaction
from django.utils import timezone

from ..models import Order


class OrderLifecycleError(Exception):
    """订单状态转换不被允许时抛出。"""
    pass


def accept_order(order_id, user):
    """接单：仅待接单订单可被非发布者接取。"""
    with transaction.atomic():
        order = Order.objects.select_for_update().get(pk=order_id)
        if order.status != 'pending':
            raise OrderLifecycleError('该订单已被接单或已完成')
        if order.publisher == user:
            raise OrderLifecycleError('不能接自己发布的订单')
        order.helper = user
        order.status = 'accepted'
        order.accepted_at = timezone.now()
        order.save()
    return order


def complete_order(order_id, user):
    """确认完成：仅发布者可在已接单状态下确认。"""
    order = Order.objects.get(pk=order_id)
    if order.publisher != user:
        raise OrderLifecycleError('只有发布者可以确认完成')
    if order.status != 'accepted':
        raise OrderLifecycleError('当前状态无法确认完成')
    order.status = 'completed'
    order.save()
    return order


def cancel_order(order_id, user):
    """取消订单：仅发布者可在待接单或已接单状态下取消。"""
    order = Order.objects.get(pk=order_id)
    if order.publisher != user:
        raise OrderLifecycleError('只有发布者可以取消订单')
    if order.status not in ('pending', 'accepted'):
        raise OrderLifecycleError('当前状态无法取消')
    order.status = 'cancelled'
    order.save()
    return order
