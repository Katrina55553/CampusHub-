"""通用查询过滤构造器：统一处理列表页的分类/状态筛选与关键词搜索。"""

from django.db.models import Q


class QueryFilter:
    """
    根据 GET 参数构建 QuerySet。

    filters: dict
        参数名 -> (字段名, lookup) 或一个可调用对象 (qs, value, meta) -> qs
    search_fields: list
        关键词搜索要匹配的字段名
    search_param: str
        关键词参数名，默认 'q'
    select_related: list | None
        始终应用的 select_related 字段
    default_ordering: str | None
        默认排序字段
    """

    def __init__(
        self,
        model,
        *,
        filters=None,
        search_fields=None,
        search_param='q',
        select_related=None,
        default_ordering=None,
    ):
        self.model = model
        self.filters = filters or {}
        self.search_fields = search_fields or []
        self.search_param = search_param
        self.select_related = select_related
        self.default_ordering = default_ordering

    def apply(self, params):
        qs = self.model.objects.all()

        if self.select_related:
            qs = qs.select_related(*self.select_related)

        meta = {}

        for param, spec in self.filters.items():
            value = params.get(param, '').strip()
            if not value:
                continue
            if callable(spec):
                qs = spec(qs, value, meta)
            else:
                field, lookup = spec
                qs = qs.filter(**{f'{field}__{lookup}': value})
                meta[param] = value

        q = params.get(self.search_param, '').strip()
        if q and self.search_fields:
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f'{field}__icontains': q})
            qs = qs.filter(condition)
            meta[self.search_param] = q

        if self.default_ordering:
            qs = qs.order_by(self.default_ordering)

        return qs, meta
