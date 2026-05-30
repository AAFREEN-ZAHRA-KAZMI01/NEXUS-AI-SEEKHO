// Local demo auth only — not for production use

import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';

class AuthService {
  static const String _usersKey = 'demo_users_list';
  static const String _currentUserKey = 'current_logged_in_user';

  // Hash password using SHA-256
  String _hashPassword(String password) {
    return sha256.convert(utf8.encode(password)).toString();
  }

  // Get all registered users from shared preferences
  Future<List<UserModel>> getUsers() async {
    final prefs = await SharedPreferences.getInstance();
    final String? usersRaw = prefs.getString(_usersKey);
    if (usersRaw == null) return [];
    try {
      final List<dynamic> decoded = jsonDecode(usersRaw);
      return decoded.map((e) => UserModel.fromJson(Map<String, dynamic>.from(e))).toList();
    } catch (e) {
      return [];
    }
  }

  // Register a new user
  Future<bool> registerUser(String name, String email, String password) async {
    final users = await getUsers();
    // Check if user already exists
    if (users.any((u) => u.email.toLowerCase() == email.toLowerCase())) {
      throw Exception('User with this email already exists.');
    }
    
    final newUser = UserModel(
      id: 'usr_${DateTime.now().millisecondsSinceEpoch}',
      name: name,
      email: email,
      password: _hashPassword(password),
      createdAt: DateTime.now(),
    );

    users.add(newUser);
    final prefs = await SharedPreferences.getInstance();
    final serialized = jsonEncode(users.map((e) => e.toJson()).toList());
    await prefs.setString(_usersKey, serialized);
    return true;
  }

  // Login verification
  Future<UserModel> loginUser(String email, String password) async {
    final users = await getUsers();
    final hashedPassword = _hashPassword(password);
    final userIndex = users.indexWhere(
      (u) => u.email.toLowerCase() == email.toLowerCase() && u.password == hashedPassword
    );

    if (userIndex == -1) {
      throw Exception('Invalid email or password.');
    }

    final user = users[userIndex];
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_currentUserKey, jsonEncode(user.toJson()));
    return user;
  }

  // Get current logged-in user
  Future<UserModel?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final String? userRaw = prefs.getString(_currentUserKey);
    if (userRaw == null) return null;
    try {
      return UserModel.fromJson(jsonDecode(userRaw));
    } catch (e) {
      return null;
    }
  }

  // Logout
  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_currentUserKey);
  }
}
