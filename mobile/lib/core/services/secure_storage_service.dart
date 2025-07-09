import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// A singleton service for secure storage operations.
class SecureStorageService {
  // Private constructor
  SecureStorageService._internal();

  /// Provides access to the singleton instance.
  factory SecureStorageService() => _instance;

  // Singleton instance
  static final SecureStorageService _instance =
      SecureStorageService._internal();

  // The storage instance (static and const for efficiency)
  static const FlutterSecureStorage _storage = FlutterSecureStorage();

  /// Writes a value to secure storage.
  Future<void> write(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  /// Reads a value from secure storage.
  Future<String?> read(String key) async {
    return _storage.read(key: key);
  }

  /// Deletes a value from secure storage.
  Future<void> delete(String key) async {
    await _storage.delete(key: key);
  }

  /// Deletes all values from secure storage.
  Future<void> deleteAll() async {
    await _storage.deleteAll();
  }
}
