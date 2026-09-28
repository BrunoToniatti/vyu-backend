from django.urls import path, include
from main.views.restaurant_views import (
    ManagerRestaurantListCreateView,
    ManagerRestaurantDetailView,
    PublicRestaurantListView,
    PublicRestaurantDetailView,
    AdminRestaurantListView,
    AdminRestaurantTransferView,
)
from main.views.review_views import (
    RestaurantReviewListCreateView,
    ManagerReviewResponseView,
)
from main.views.photo_views import RestaurantPhotoUploadView
from main.views.chat_views import PublicChatListView, AppUserChatView, ManagerChatView
from main.views.reservation_views import (
    ManagerReservationListCreateView,
    ManagerReservationDetailView,
    PublicReservationCreateView,
)
from main.views.comanda_views import (
    MenuItemListCreateView, MenuItemDetailView, MenuItemPhotoUploadView,
    TableListCreateView, TableDetailView,
    ComandaListCreateView, ComandaDetailView,
    ComandaItemListCreateView, ComandaItemDeleteView,
    StaffTokenListCreateView, StaffTokenDetailView,
)

urlpatterns = [
    # Public routes
    path('public/', PublicRestaurantListView.as_view(), name='restaurant-public-list'),
    path('public/<int:pk>/', PublicRestaurantDetailView.as_view(), name='restaurant-public-detail'),
    # Review routes
    path('public/<int:restaurant_pk>/reviews/', RestaurantReviewListCreateView.as_view(), name='restaurant-review-list-create'),
    path('public/<int:restaurant_pk>/reviews/<int:review_pk>/respond/', ManagerReviewResponseView.as_view(), name='manager-review-respond'),
    # Admin routes
    path('admin/', AdminRestaurantListView.as_view(), name='admin-restaurant-list'),
    path('admin/<int:pk>/transfer/', AdminRestaurantTransferView.as_view(), name='admin-restaurant-transfer'),
    # Protected manager routes
    path('', ManagerRestaurantListCreateView.as_view(), name='restaurant-list-create'),
    path('<int:pk>/', ManagerRestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<int:pk>/photo/', RestaurantPhotoUploadView.as_view(), name='restaurant-photo-upload'),
    # Chat routes
    path('public/<int:pk>/chat/', PublicChatListView.as_view(), name='restaurant-chat-list'),
    path('public/<int:pk>/chat/send/', AppUserChatView.as_view(), name='restaurant-chat-send'),
    path('<int:pk>/chat/', ManagerChatView.as_view(), name='restaurant-manager-chat'),
    # Reservation routes
    path('public/<int:pk>/reservations/', PublicReservationCreateView.as_view(), name='restaurant-public-reservations'),
    path('<int:pk>/reservations/', ManagerReservationListCreateView.as_view(), name='restaurant-reservations'),
    path('<int:pk>/reservations/<int:res_pk>/', ManagerReservationDetailView.as_view(), name='restaurant-reservation-detail'),
    # Menu routes
    path('<int:pk>/menu/', MenuItemListCreateView.as_view(), name='restaurant-menu-list'),
    path('<int:pk>/menu/<int:item_pk>/', MenuItemDetailView.as_view(), name='restaurant-menu-detail'),
    path('<int:pk>/menu/<int:item_pk>/photo/', MenuItemPhotoUploadView.as_view(), name='restaurant-menu-photo'),
    # Table routes
    path('<int:pk>/tables/', TableListCreateView.as_view(), name='restaurant-tables-list'),
    path('<int:pk>/tables/<int:table_pk>/', TableDetailView.as_view(), name='restaurant-tables-detail'),
    # Comanda routes
    path('<int:pk>/comandas/', ComandaListCreateView.as_view(), name='restaurant-comandas-list'),
    path('<int:pk>/comandas/<int:comanda_pk>/', ComandaDetailView.as_view(), name='restaurant-comandas-detail'),
    path('<int:pk>/comandas/<int:comanda_pk>/items/', ComandaItemListCreateView.as_view(), name='restaurant-comanda-items'),
    path('<int:pk>/comandas/<int:comanda_pk>/items/<int:item_pk>/', ComandaItemDeleteView.as_view(), name='restaurant-comanda-item-delete'),
    # Staff token routes
    path('<int:pk>/staff-tokens/', StaffTokenListCreateView.as_view(), name='restaurant-staff-tokens'),
    path('<int:pk>/staff-tokens/<int:tok_pk>/', StaffTokenDetailView.as_view(), name='restaurant-staff-token-detail'),
]
