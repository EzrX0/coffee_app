import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthProvider with ChangeNotifier {
  final String baseUrl = 'http://10.0.2.2:8000/api';
  final _storage = const FlutterSecureStorage();
  
  String? _token;
  String? _refreshToken;
  String? _username;
  bool _isLoading = false;
  String _error = '';

  bool get isAuthenticated => _token != null;
  bool get isLoading => _isLoading;
  String get error => _error;
  String? get token => _token;
  String? get refreshTokenStr => _refreshToken;
  String? get username => _username;

  Future<void> fetchUser() async {
    if (_token == null) return;
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/me'),
        headers: {'Authorization': 'Bearer $_token'},
      );
      if (response.statusCode == 200) {
        _username = json.decode(response.body)['username'];
        notifyListeners();
      }
    } catch (e) {
      debugPrint("Error fetching user: $e");
    }
  }

  Future<void> initAuth() async {
    _token = await _storage.read(key: 'jwt');
    _refreshToken = await _storage.read(key: 'refresh_token');
    if (_token != null) {
      await fetchUser();
    }
    notifyListeners();
  }

  Future<bool> refreshToken() async {
    if (_refreshToken == null) return false;
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'refresh_token': _refreshToken}),
      );
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access_token'];
        _refreshToken = data['refresh_token'];
        await _storage.write(key: 'jwt', value: _token);
        if (_refreshToken != null) {
          await _storage.write(key: 'refresh_token', value: _refreshToken);
        }
        notifyListeners();
        return true;
      }
    } catch (e) {
      debugPrint("Error refreshing token: $e");
    }
    await logout();
    return false;
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'username': username,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['access_token'];
        _refreshToken = data['refresh_token'];
        await _storage.write(key: 'jwt', value: _token);
        if (_refreshToken != null) {
          await _storage.write(key: 'refresh_token', value: _refreshToken);
        }
        await fetchUser();
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        final data = json.decode(response.body);
        _error = data['detail'] ?? 'Login failed';
      }
    } catch (e) {
      _error = 'Network error occurred';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> signup(String username, String password) async {
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/signup'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        // Automatically login after signup
        return await login(username, password);
      } else {
        final data = json.decode(response.body);
        _error = data['detail'] ?? 'Signup failed';
      }
    } catch (e) {
      _error = 'Network error occurred';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<void> logout() async {
    _token = null;
    _refreshToken = null;
    _username = null;
    await _storage.delete(key: 'jwt');
    await _storage.delete(key: 'refresh_token');
    notifyListeners();
  }

  Future<bool> updatePassword(String currentPassword, String newPassword) async {
    if (_token == null) return false;
    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      final response = await http.put(
        Uri.parse('$baseUrl/password'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $_token',
        },
        body: json.encode({
          'current_password': currentPassword,
          'new_password': newPassword,
        }),
      );

      if (response.statusCode == 200) {
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        final data = json.decode(response.body);
        _error = data['detail'] ?? 'Update failed';
      }
    } catch (e) {
      _error = 'Network error occurred';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }
}
