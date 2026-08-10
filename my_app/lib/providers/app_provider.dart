import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/coffee_item.dart';
import '../models/cart_item.dart';

class AppProvider with ChangeNotifier {
  final String baseUrl = 'http://10.0.2.2:8000/api'; // Use 127.0.0.1 if on Windows/Web

  List<CoffeeItem> _coffees = [];
  List<int> _favoriteIds = [];
  List<CartItem> _cartItems = [];
  
  bool _isLoading = false;
  String _searchQuery = '';
  String _selectedCategory = 'All';

  List<CoffeeItem> get coffees => _coffees;
  List<int> get favoriteIds => _favoriteIds;
  List<CartItem> get cartItems => _cartItems;
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
      print("Error fetching coffees: $e");
    }
  }

  Future<void> fetchFavorites() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/favorites'));
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _favoriteIds = data.map<int>((f) => f['coffee_id'] as int).toList();
        notifyListeners();
      }
    } catch (e) {
      print("Error fetching favorites: $e");
    }
  }

  Future<void> fetchCart() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/cart'));
      if (response.statusCode == 200) {
        List data = json.decode(response.body);
        _cartItems = data.map((json) => CartItem.fromJson(json)).toList();
        notifyListeners();
      }
    } catch (e) {
      print("Error fetching cart: $e");
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
      await http.delete(Uri.parse('$baseUrl/favorites/$coffeeId'));
    } else {
      _favoriteIds.add(coffeeId);
      notifyListeners();
      await http.post(
        Uri.parse('$baseUrl/favorites'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'coffee_id': coffeeId}),
      );
    }
  }

  Future<void> addToCart(int coffeeId, String size, int quantity) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/cart'),
        headers: {'Content-Type': 'application/json'},
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
      print("Error adding to cart: $e");
    }
  }

  Future<void> removeFromCart(int cartItemId) async {
    _cartItems.removeWhere((item) => item.id == cartItemId);
    notifyListeners();
    try {
      await http.delete(Uri.parse('$baseUrl/cart/$cartItemId'));
    } catch (e) {
      print("Error removing from cart: $e");
    }
  }
}
