import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>>? _controller;
  Timer? _reconnectTimer;
  final String _baseUrl;
  bool _isDisposed = false;

  WebSocketService({String baseUrl = 'ws://10.0.2.2:8000'}) : _baseUrl = baseUrl;

  Stream<Map<String, dynamic>> connect(String sessionId) {
    _isDisposed = false;
    _controller ??= StreamController<Map<String, dynamic>>.broadcast();
    
    _connectInternal(sessionId);
    
    return _controller!.stream;
  }

  void _connectInternal(String sessionId) {
    if (_isDisposed) return;
    
    try {
      final wsUrl = Uri.parse('$_baseUrl/ws/session/$sessionId');
      _channel = WebSocketChannel.connect(wsUrl);

      _channel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message as String) as Map<String, dynamic>;
            _controller?.add(data);
          } catch (e) {
            debugPrint('Error parsing WebSocket message: $e');
          }
        },
        onDone: () {
          if (!_isDisposed) {
            _scheduleReconnect(sessionId);
          }
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          if (!_isDisposed) {
            _scheduleReconnect(sessionId);
          }
        },
      );
    } catch (e) {
      debugPrint('WebSocket connection error: $e');
      if (!_isDisposed) {
        _scheduleReconnect(sessionId);
      }
    }
  }

  void _scheduleReconnect(String sessionId) {
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      debugPrint('Attempting to reconnect WebSocket for session: $sessionId');
      _connectInternal(sessionId);
    });
  }

  void dispose() {
    _isDisposed = true;
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _controller?.close();
    _channel = null;
    _controller = null;
  }
}
