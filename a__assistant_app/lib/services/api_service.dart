import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String _tokenKey = 'auth_token';
  static const String _configuredBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
  );

  static String get baseUrl {
    if (_configuredBaseUrl.isNotEmpty) {
      return _configuredBaseUrl;
    }

    if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:5000';
    }

    return 'http://localhost:5000';
  }

  static Future<Map<String, dynamic>> login(
    String email,
    String password,
  ) async {
    final response = await _send(
      http.post(
        Uri.parse('$baseUrl/login'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      ),
    );

    final data = _decodeMap(response);

    if (!_isSuccess(response.statusCode)) {
      throw ApiException(data['message']?.toString() ?? 'Login failed');
    }

    final token = data['token']?.toString();

    if (token == null || token.isEmpty) {
      throw ApiException('Login token missing from server response');
    }

    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);

    return data;
  }

  static Future<List<Map<String, dynamic>>> getHistory() async {
    final response = await _send(
      http.get(
        Uri.parse('$baseUrl/history'),
        headers: await _authorizedHeaders(),
      ),
    );

    final data = _decodeBody(response);

    if (!_isSuccess(response.statusCode)) {
      throw ApiException(_messageFrom(data, 'Could not load chat history'));
    }

    if (data is! List) {
      throw ApiException('Invalid history response from server');
    }

    return data.map((item) => Map<String, dynamic>.from(item as Map)).toList();
  }

  static Future<String> sendMessage(String message) async {
    final response = await _send(
      http.post(
        Uri.parse('$baseUrl/chat'),
        headers: await _authorizedHeaders(json: true),
        body: jsonEncode({
          'message': message,
        }),
      ),
      timeout: const Duration(seconds: 30),
    );

    final data = _decodeMap(response);

    if (!_isSuccess(response.statusCode)) {
      throw ApiException(data['message']?.toString() ?? 'Message failed');
    }

    return data['reply']?.toString() ?? '';
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  static Future<Map<String, String>> _authorizedHeaders({
    bool json = false,
  }) async {
    final token = await getToken();

    if (token == null || token.isEmpty) {
      throw ApiException('Please login again');
    }

    return {
      if (json) 'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  static bool _isSuccess(int statusCode) {
    return statusCode >= 200 && statusCode < 300;
  }

  static Future<http.Response> _send(
    Future<http.Response> request, {
    Duration timeout = const Duration(seconds: 15),
  }) async {
    try {
      return await request.timeout(timeout);
    } on TimeoutException {
      throw ApiException(
        'Server timed out at $baseUrl. Make sure Flask is running.',
      );
    } on http.ClientException catch (error) {
      throw ApiException(
        'Cannot connect to $baseUrl. Start the Flask backend and check the URL. ${error.message}',
      );
    } catch (error) {
      throw ApiException('Connection failed: $error');
    }
  }

  static Map<String, dynamic> _decodeMap(http.Response response) {
    final data = _decodeBody(response);

    if (data is Map<String, dynamic>) {
      return data;
    }

    if (data is Map) {
      return Map<String, dynamic>.from(data);
    }

    return {
      'message': 'Invalid server response',
    };
  }

  static dynamic _decodeBody(http.Response response) {
    if (response.body.isEmpty) {
      return <String, dynamic>{};
    }

    try {
      return jsonDecode(response.body);
    } catch (_) {
      return {
        'message': 'Invalid server response',
      };
    }
  }

  static String _messageFrom(dynamic data, String fallback) {
    if (data is Map && data['message'] != null) {
      return data['message'].toString();
    }

    return fallback;
  }
}

class ApiException implements Exception {
  const ApiException(this.message);

  final String message;

  @override
  String toString() {
    return message;
  }
}
