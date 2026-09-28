from django.urls import path
from main.views.comanda_views import (
    MenuItemListCreateView, MenuItemDetailView,
    TableListCreateView, TableDetailView,
    ComandaListCreateView, ComandaDetailView,
    ComandaItemListCreateView, ComandaItemDeleteView,
    StaffTokenListCreateView, StaffTokenDetailView,
    WaiterInfoView, WaiterComandaListCreateView,
    WaiterComandaDetailView, WaiterComandaItemView,
)

# Prefixed under /restaurants/<pk>/  (added in restaurant_urls.py)
restaurant_patterns = [
    path('menu/', MenuItemListCreateView.as_view()),
    path('menu/<int:item_pk>/', MenuItemDetailView.as_view()),
    path('tables/', TableListCreateView.as_view()),
    path('tables/<int:table_pk>/', TableDetailView.as_view()),
    path('comandas/', ComandaListCreateView.as_view()),
    path('comandas/<int:comanda_pk>/', ComandaDetailView.as_view()),
    path('comandas/<int:comanda_pk>/items/', ComandaItemListCreateView.as_view()),
    path('comandas/<int:comanda_pk>/items/<int:item_pk>/', ComandaItemDeleteView.as_view()),
    path('staff-tokens/', StaffTokenListCreateView.as_view()),
    path('staff-tokens/<int:tok_pk>/', StaffTokenDetailView.as_view()),
]

# Prefixed under /waiter/  (added in api_urls.py)
waiter_patterns = [
    path('<str:token>/', WaiterInfoView.as_view()),
    path('<str:token>/comandas/', WaiterComandaListCreateView.as_view()),
    path('<str:token>/comandas/<int:comanda_pk>/', WaiterComandaDetailView.as_view()),
    path('<str:token>/comandas/<int:comanda_pk>/items/', WaiterComandaItemView.as_view()),
    path('<str:token>/comandas/<int:comanda_pk>/items/<int:item_pk>/', WaiterComandaItemView.as_view()),
]
