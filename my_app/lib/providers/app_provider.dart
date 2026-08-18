import 'package:flutter/material.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/coffee_item.dart';
import '../models/cart_item.dart';
import '../models/order.dart';
import '../models/notification.dart';

class AppProvider with ChangeNotifier {
  final String baseUrl = 'http://10.0.2.2:8000/api'; // Use 127.0.0.1 if on Windows/Web

  List<CoffeeItem> _coffees = [];
  List<int> _favoriteIds = [];
  List<CartItem> _cartItems = [];
  List<Order> _orders = [];
  List<NotificationItem> _notifications = [];
  
  bool _isLoading = false;
  String _searchQuery = '';
  String _selectedCategory = 'All';
  String? _token;

  void updateToken(String? token) {
    final previousToken = _token;
    _token = token;
    if (_token != null && previousToken != _token) {
      fetchAllData();
    } else if (_token == null) {
      _coffees = [];
      _favoriteIds = [];
      _cartItems = [];
      _orders = [];
      _notifications = [];
      notifyListeners();
    }
  }

  Map<String, String> get _headers {
    return {
      'Content-Type': 'application/json',
      if (_token != null) 'Authorization': 'Bearer $_token',
    };
  }

  List<CoffeeItem> get coffees => _coffees;
  List<int> get favoriteIds => _favoriteIds;
  List<CartItem> get cartItems => _cartItems;
  List<Order> get orders => _orders;
  List<NotificationItem> get notifications => _notifications;
  bool get isLoading => _isLoading;
  String get searchQuery => _searchQuery;
  String get selectedCategory => _selectedCategory;
  
  List<CoffeeItem> get favoriteCoffees => _coffees.where((c) => _favoriteIds.contains(c.id)).toList();

  Future<void> fetchAllData() async {
    _isLoading = true;
    notifyListeners();

    await Future.wait([
      fetchCoffees(),
      fetchFavorites(),
      fetchCart(),
      fetchOrders(),
      fetchNotifications(),
    ]);

    _isLoading = false;
    notifyListeners();
  }

  Future<void> fetchCoffees() async {
    String url = '$baseUrl/coffees?';
    if (_selectedCategory != 'All' && _selectedCategory.isNotEmpty) {
      url += 'category=$_selectedCategory&';
    }
    if (_searchQuery.isNotEmpty) {
      url += 'search=$_searchQuery';
    }

    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _coffees = data.map((json) => CoffeeItem.fromJson(json)).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching coffees: $e");
    }
  }

  Future<void> fetchFavorites() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/favorites'), headers: _headers);
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _favoriteIds = data.map<int>((f) => f['coffee_id'] as int).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching favorites: $e");
    }
  }

  Future<void> fetchCart() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/cart'), headers: _headers);
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _cartItems = data.map((json) => CartItem.fromJson(json)).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching cart: $e");
    }
  }

  Future<void> fetchOrders() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/orders'), headers: _headers);
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _orders = data.map((json) => Order.fromJson(json)).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching orders: $e");
    }
  }

  Future<void> fetchNotifications() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/notifications'), headers: _headers);
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _notifications = data.map((json) => NotificationItem.fromJson(json)).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching notifications: $e");
    }
  }

  Future<void> markNotificationRead(int notificationId) async {
    try {
      final response = await http.put(Uri.parse('$baseUrl/notifications/$notificationId/read'), headers: _headers);
      if (response.statusCode == 200) {
        final index = _notifications.indexWhere((n) => n.id == notificationId);
        if (index >= 0) {
          _notifications[index] = NotificationItem.fromJson(json.decode(response.body));
          notifyListeners();
        }
      }
    } catch (e) {
      debugPrint("Error marking notification read: $e");
    }
  }

  void setSearchQuery(String query) {
    _searchQuery = query;
    fetchCoffees();
  }

  void setSelectedCategory(String category) {
    _selectedCategory = category;
    fetchCoffees();
  }

  Future<void> toggleFavorite(int coffeeId) async {
    if (_favoriteIds.contains(coffeeId)) {
      _favoriteIds.remove(coffeeId);
      notifyListeners();
      await http.delete(Uri.parse('$baseUrl/favorites/$coffeeId'), headers: _headers);
    } else {
      _favoriteIds.add(coffeeId);
      notifyListeners();
      await http.post(
        Uri.parse('$baseUrl/favorites'),
        headers: _headers,
        body: json.encode({'coffee_id': coffeeId}),
      );
    }
  }

  Future<void> addToCart(int coffeeId, String size, int quantity) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/cart'),
        headers: _headers,
        body: json.encode({
          'coffee_id': coffeeId,
          'size': size,
          'quantity': quantity,
        }),
      );
      if (response.statusCode == 200) {
        fetchCart(); // Refresh cart to get full item with ID
      }
    } catch (e) {
      debugPrint("Error adding to cart: $e");
    }
  }

  Future<void> removeFromCart(int cartItemId) async {
    _cartItems.removeWhere((item) => item.id == cartItemId);
    notifyListeners();
    try {
      await http.delete(Uri.parse('$baseUrl/cart/$cartItemId'), headers: _headers);
    } catch (e) {
      debugPrint("Error removing from cart: $e");
    }
  }

  Future<void> updateCartItem(int cartItemId, int newQuantity) async {
    if (newQuantity <= 0) {
      await removeFromCart(cartItemId);
      return;
    }
    final index = _cartItems.indexWhere((item) => item.id == cartItemId);
    if (index >= 0) {
      _cartItems[index].quantity = newQuantity;
      notifyListeners();
      try {
        await http.put(
          Uri.parse('$baseUrl/cart/$cartItemId'),
          headers: _headers,
          body: json.encode({'quantity': newQuantity}),
        );
      } catch (e) {
        debugPrint("Error updating cart: $e");
      }
    }
  }

  Future<bool> checkout() async {
    if (_cartItems.isEmpty) return false;
    
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/create-payment-intent'),
        headers: _headers,
      );

      if (response.statusCode != 200) {
        debugPrint("Failed to create payment intent: ${response.body}");
        return false;
      }

      final data = json.decode(response.body);
      final String? clientSecret = data['client_secret'];
      if (clientSecret == null) return false;

      final String paymentIntentId = clientSecret.split('_secret_')[0];

      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          paymentIntentClientSecret: clientSecret,
          merchantDisplayName: 'Coffee Shop',
          style: ThemeMode.light,
        ),
      );

      await Stripe.instance.presentPaymentSheet();

      final checkoutResponse = await http.post(
        Uri.parse('$baseUrl/checkout'),
        headers: _headers,
        body: json.encode({'payment_intent_id': paymentIntentId}),
      );

      if (checkoutResponse.statusCode == 200) {
        _cartItems = [];
        notifyListeners();
        fetchOrders(); // refresh order history
        return true;
      }
      return false;
    } on StripeException catch (e) {
      debugPrint("Stripe error: ${e.error.localizedMessage}");
      rethrow;
    } catch (e) {
      debugPrint("Error checking out: $e");
      return false;
    }
  }
}
