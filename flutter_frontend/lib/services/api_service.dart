import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../models/pin.dart';
import '../models/product.dart';

class ApiService {
  final Dio _dio = Dio();

  ApiService() {
    // 10.0.2.2 for Android Emulator, localhost for iOS Simulator
    String baseUrl = 'http://127.0.0.1:8000';
    if (!kIsWeb && Platform.isAndroid) {
      baseUrl = 'http://10.0.2.2:8000';
    }
    
    _dio.options.baseUrl = baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 10);
    _dio.options.receiveTimeout = const Duration(seconds: 10);
  }

  Future<List<Pin>> fetchGallery({String query = '', int limit = 20, int offset = 0}) async {
    try {
      final response = await _dio.get(
        '/api/gallery/',
        queryParameters: {
          'query': query,
          'limit': limit,
          'offset': offset,
        },
      );

      if (response.data['success'] == true) {
        final List<dynamic> imagesJson = response.data['images'];
        return imagesJson.map((json) => Pin.fromJson(json)).toList();
      } else {
        return [];
      }
    } catch (e) {
      debugPrint('Error fetching gallery: $e');
      return [];
    }
  }

  Future<List<Product>> searchByImage(XFile imageFile, {int topK = 20, String? queryText}) async {
    try {
      String fileName = imageFile.path.split('/').last;
      
      final Map<String, dynamic> map = {
        'image': await MultipartFile.fromFile(imageFile.path, filename: fileName),
        'top_k': topK,
      };

      if (queryText != null && queryText.isNotEmpty) {
        map['query_text'] = queryText;
      }

      FormData formData = FormData.fromMap(map);

      final response = await _dio.post(
        '/api/search/image/',
        data: formData,
      );

      final List<dynamic> matches = response.data['matches'];
      return matches.map((json) => Product.fromJson(json)).toList();
    } catch (e) {
      debugPrint('Error searching by image: $e');
      rethrow;
    }
  }

  Future<List<Product>> searchByImageUrl(String imageUrl, {int topK = 20}) async {
    try {
      FormData formData = FormData.fromMap({
        'external_image_url': imageUrl,
        'top_k': topK,
      });

      final response = await _dio.post(
        '/api/search/image/',
        data: formData,
      );

      final List<dynamic> matches = response.data['matches'];
      return matches.map((json) => Product.fromJson(json)).toList();
    } catch (e) {
      debugPrint('Error searching by image URL: $e');
      rethrow; // Rethrow to handle in UI
    }
  }
}
