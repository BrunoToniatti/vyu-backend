from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main.permissions import IsManager
from main.models.restaurant import Restaurant
from main.models.comanda import MenuItem, RestaurantTable, Comanda, ComandaItem, StaffToken
from main.serializers.comanda_serializers import (
    MenuItemSerializer, MenuItemCreateSerializer,
    RestaurantTableSerializer,
    ComandaSerializer, ComandaCreateSerializer,
    ComandaItemSerializer, ComandaItemCreateSerializer,
    StaffTokenSerializer,
)


def _owned_restaurant(request, pk):
    return get_object_or_404(Restaurant, pk=pk, manager=request.user)


def _waiter_restaurant(token_str):
    tok = get_object_or_404(StaffToken, token=token_str, active=True)
    return tok.restaurant, tok


# ── MENU ──────────────────────────────────────────────────────────────────────

class MenuItemListCreateView(APIView):
    """GET/POST /restaurants/<pk>/menu/"""
    permission_classes = [IsManager]

    def get(self, request, pk):
        r = _owned_restaurant(request, pk)
        items = r.menu_items.all()
        category = request.query_params.get('category')
        if category:
            items = items.filter(category=category)
        return Response({'status': 'success', 'data': MenuItemSerializer(items, many=True).data})

    def post(self, request, pk):
        r = _owned_restaurant(request, pk)
        s = MenuItemCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        item = MenuItem.objects.create(restaurant=r, **s.validated_data)
        return Response({'status': 'success', 'data': MenuItemSerializer(item).data}, status=status.HTTP_201_CREATED)


class MenuItemDetailView(APIView):
    """GET/PUT/PATCH/DELETE /restaurants/<pk>/menu/<item_pk>/"""
    permission_classes = [IsManager]

    def _get(self, request, pk, item_pk):
        r = _owned_restaurant(request, pk)
        return get_object_or_404(MenuItem, pk=item_pk, restaurant=r)

    def get(self, request, pk, item_pk):
        item = self._get(request, pk, item_pk)
        return Response({'status': 'success', 'data': MenuItemSerializer(item).data})

    def put(self, request, pk, item_pk):
        item = self._get(request, pk, item_pk)
        s = MenuItemCreateSerializer(item, data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({'status': 'success', 'data': MenuItemSerializer(item).data})

    def patch(self, request, pk, item_pk):
        item = self._get(request, pk, item_pk)
        s = MenuItemCreateSerializer(item, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({'status': 'success', 'data': MenuItemSerializer(item).data})

    def delete(self, request, pk, item_pk):
        item = self._get(request, pk, item_pk)
        item.delete()
        return Response({'status': 'success'}, status=status.HTTP_204_NO_CONTENT)


# ── TABLES ────────────────────────────────────────────────────────────────────

class TableListCreateView(APIView):
    """GET/POST /restaurants/<pk>/tables/"""
    permission_classes = [IsManager]

    def get(self, request, pk):
        r = _owned_restaurant(request, pk)
        return Response({'status': 'success', 'data': RestaurantTableSerializer(r.tables.all(), many=True).data})

    def post(self, request, pk):
        r = _owned_restaurant(request, pk)
        identifier = request.data.get('identifier', '').strip()
        capacity = request.data.get('capacity')
        if not identifier:
            return Response({'status': 'error', 'message': 'identifier é obrigatório.'}, status=400)
        if r.tables.filter(identifier=identifier).exists():
            return Response({'status': 'error', 'message': 'Mesa já existe.'}, status=400)
        table = RestaurantTable.objects.create(restaurant=r, identifier=identifier, capacity=capacity or None)
        return Response({'status': 'success', 'data': RestaurantTableSerializer(table).data}, status=201)


class TableDetailView(APIView):
    """DELETE /restaurants/<pk>/tables/<table_pk>/"""
    permission_classes = [IsManager]

    def delete(self, request, pk, table_pk):
        r = _owned_restaurant(request, pk)
        table = get_object_or_404(RestaurantTable, pk=table_pk, restaurant=r)
        table.delete()
        return Response({'status': 'success'}, status=204)


# ── COMANDAS ──────────────────────────────────────────────────────────────────

class ComandaListCreateView(APIView):
    """GET/POST /restaurants/<pk>/comandas/"""
    permission_classes = [IsManager]

    def get(self, request, pk):
        r = _owned_restaurant(request, pk)
        qs = r.comandas.prefetch_related('items').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response({'status': 'success', 'data': ComandaSerializer(qs, many=True).data})

    def post(self, request, pk):
        r = _owned_restaurant(request, pk)
        s = ComandaCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        table = None
        table_label = d.get('table_label', '')
        if d.get('table_id'):
            table = get_object_or_404(RestaurantTable, pk=d['table_id'], restaurant=r)
            table_label = table_label or f"Mesa {table.identifier}"
        comanda = Comanda.objects.create(
            restaurant=r, table=table, table_label=table_label,
            opened_by=d.get('opened_by', 'Manager'),
            notes=d.get('notes', ''),
        )
        return Response({'status': 'success', 'data': ComandaSerializer(comanda).data}, status=201)


class ComandaDetailView(APIView):
    """GET/PATCH /restaurants/<pk>/comandas/<comanda_pk>/"""
    permission_classes = [IsManager]

    def _get(self, request, pk, comanda_pk):
        r = _owned_restaurant(request, pk)
        return get_object_or_404(Comanda, pk=comanda_pk, restaurant=r)

    def get(self, request, pk, comanda_pk):
        c = self._get(request, pk, comanda_pk)
        return Response({'status': 'success', 'data': ComandaSerializer(c).data})

    def patch(self, request, pk, comanda_pk):
        c = self._get(request, pk, comanda_pk)
        new_status = request.data.get('status')
        notes = request.data.get('notes')
        if new_status:
            c.status = new_status
            if new_status == Comanda.STATUS_CLOSED and not c.closed_at:
                c.closed_at = timezone.now()
        if notes is not None:
            c.notes = notes
        c.save()
        return Response({'status': 'success', 'data': ComandaSerializer(c).data})


class ComandaItemListCreateView(APIView):
    """POST /restaurants/<pk>/comandas/<comanda_pk>/items/"""
    permission_classes = [IsManager]

    def post(self, request, pk, comanda_pk):
        r = _owned_restaurant(request, pk)
        c = get_object_or_404(Comanda, pk=comanda_pk, restaurant=r, status=Comanda.STATUS_OPEN)
        s = ComandaItemCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        menu_item = None
        item_name = d.get('item_name', '')
        item_price = d.get('item_price', 0)
        if d.get('menu_item_id'):
            menu_item = get_object_or_404(MenuItem, pk=d['menu_item_id'], restaurant=r)
            item_name = item_name or menu_item.name
            item_price = item_price or menu_item.price
        ci = ComandaItem.objects.create(
            comanda=c, menu_item=menu_item,
            item_name=item_name, item_price=item_price,
            quantity=d.get('quantity', 1),
            notes=d.get('notes', ''),
        )
        return Response({'status': 'success', 'data': ComandaItemSerializer(ci).data}, status=201)


class ComandaItemDeleteView(APIView):
    """DELETE /restaurants/<pk>/comandas/<comanda_pk>/items/<item_pk>/"""
    permission_classes = [IsManager]

    def delete(self, request, pk, comanda_pk, item_pk):
        r = _owned_restaurant(request, pk)
        c = get_object_or_404(Comanda, pk=comanda_pk, restaurant=r)
        ci = get_object_or_404(ComandaItem, pk=item_pk, comanda=c)
        ci.delete()
        return Response({'status': 'success'}, status=204)


# ── STAFF TOKENS ──────────────────────────────────────────────────────────────

class StaffTokenListCreateView(APIView):
    """GET/POST /restaurants/<pk>/staff-tokens/"""
    permission_classes = [IsManager]

    def get(self, request, pk):
        r = _owned_restaurant(request, pk)
        return Response({'status': 'success', 'data': StaffTokenSerializer(r.staff_tokens.all(), many=True).data})

    def post(self, request, pk):
        r = _owned_restaurant(request, pk)
        staff_name = request.data.get('staff_name', '').strip()
        if not staff_name:
            return Response({'status': 'error', 'message': 'staff_name é obrigatório.'}, status=400)
        tok = StaffToken.objects.create(restaurant=r, staff_name=staff_name)
        return Response({'status': 'success', 'data': StaffTokenSerializer(tok).data}, status=201)


class StaffTokenDetailView(APIView):
    """PATCH/DELETE /restaurants/<pk>/staff-tokens/<tok_pk>/"""
    permission_classes = [IsManager]

    def patch(self, request, pk, tok_pk):
        r = _owned_restaurant(request, pk)
        tok = get_object_or_404(StaffToken, pk=tok_pk, restaurant=r)
        if 'active' in request.data:
            tok.active = request.data['active']
            tok.save()
        return Response({'status': 'success', 'data': StaffTokenSerializer(tok).data})

    def delete(self, request, pk, tok_pk):
        r = _owned_restaurant(request, pk)
        tok = get_object_or_404(StaffToken, pk=tok_pk, restaurant=r)
        tok.delete()
        return Response({'status': 'success'}, status=204)


# ── WAITER (public, token-based) ──────────────────────────────────────────────

class WaiterInfoView(APIView):
    """GET /waiter/<token>/ — restaurant info + tables + menu"""
    permission_classes = [AllowAny]

    def get(self, request, token):
        restaurant, tok = _waiter_restaurant(token)
        tables = RestaurantTableSerializer(restaurant.tables.all(), many=True).data
        menu   = MenuItemSerializer(restaurant.menu_items.filter(available=True), many=True).data
        return Response({
            'status': 'success',
            'data': {
                'staff_name': tok.staff_name,
                'restaurant': {'id': restaurant.id, 'name': restaurant.name, 'address': restaurant.address},
                'tables': tables,
                'menu': menu,
            }
        })


class WaiterComandaListCreateView(APIView):
    """GET/POST /waiter/<token>/comandas/"""
    permission_classes = [AllowAny]

    def get(self, request, token):
        restaurant, tok = _waiter_restaurant(token)
        qs = restaurant.comandas.filter(status=Comanda.STATUS_OPEN).prefetch_related('items')
        return Response({'status': 'success', 'data': ComandaSerializer(qs, many=True).data})

    def post(self, request, token):
        restaurant, tok = _waiter_restaurant(token)
        s = ComandaCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        table = None
        table_label = d.get('table_label', '')
        if d.get('table_id'):
            table = get_object_or_404(RestaurantTable, pk=d['table_id'], restaurant=restaurant)
            table_label = table_label or f"Mesa {table.identifier}"
        comanda = Comanda.objects.create(
            restaurant=restaurant, table=table, table_label=table_label,
            opened_by=tok.staff_name,
            notes=d.get('notes', ''),
        )
        return Response({'status': 'success', 'data': ComandaSerializer(comanda).data}, status=201)


class WaiterComandaDetailView(APIView):
    """GET/PATCH /waiter/<token>/comandas/<comanda_pk>/"""
    permission_classes = [AllowAny]

    def _get(self, token, comanda_pk):
        restaurant, tok = _waiter_restaurant(token)
        return get_object_or_404(Comanda, pk=comanda_pk, restaurant=restaurant), tok

    def get(self, request, token, comanda_pk):
        c, _ = self._get(token, comanda_pk)
        return Response({'status': 'success', 'data': ComandaSerializer(c).data})

    def patch(self, request, token, comanda_pk):
        c, _ = self._get(token, comanda_pk)
        new_status = request.data.get('status')
        if new_status:
            c.status = new_status
            if new_status == Comanda.STATUS_CLOSED and not c.closed_at:
                c.closed_at = timezone.now()
        c.save()
        return Response({'status': 'success', 'data': ComandaSerializer(c).data})


class WaiterComandaItemView(APIView):
    """POST /waiter/<token>/comandas/<comanda_pk>/items/  — add item
       DELETE /waiter/<token>/comandas/<comanda_pk>/items/<item_pk>/"""
    permission_classes = [AllowAny]

    def post(self, request, token, comanda_pk):
        restaurant, tok = _waiter_restaurant(token)
        c = get_object_or_404(Comanda, pk=comanda_pk, restaurant=restaurant, status=Comanda.STATUS_OPEN)
        s = ComandaItemCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data
        menu_item = None
        item_name = d.get('item_name', '')
        item_price = d.get('item_price', 0)
        if d.get('menu_item_id'):
            menu_item = get_object_or_404(MenuItem, pk=d['menu_item_id'], restaurant=restaurant)
            item_name = item_name or menu_item.name
            item_price = item_price or menu_item.price
        ci = ComandaItem.objects.create(
            comanda=c, menu_item=menu_item,
            item_name=item_name, item_price=item_price,
            quantity=d.get('quantity', 1),
            notes=d.get('notes', ''),
        )
        return Response({'status': 'success', 'data': ComandaItemSerializer(ci).data}, status=201)

    def delete(self, request, token, comanda_pk, item_pk):
        restaurant, _ = _waiter_restaurant(token)
        c = get_object_or_404(Comanda, pk=comanda_pk, restaurant=restaurant)
        ci = get_object_or_404(ComandaItem, pk=item_pk, comanda=c)
        ci.delete()
        return Response({'status': 'success'}, status=204)
