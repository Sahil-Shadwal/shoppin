import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../models/pin.dart';
import '../models/product.dart';

enum HomeState { gallery, visualSearch }

class HomeProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  List<Pin> _pins = [];
  List<Product> _visualResults = [];
  bool _isLoading = false;
  String _currentQuery = '';
  HomeState _currentState = HomeState.gallery;

  HomeProvider() {
    fetchGallery(query: 'zara');
  }

  List<Pin> get pins => _pins;
  List<Product> get visualResults => _visualResults;
  bool get isLoading => _isLoading;
  HomeState get currentState => _currentState;
  String get currentQuery => _currentQuery;

  Future<void> fetchGallery({String query = ''}) async {
    _isLoading = true;
    _currentQuery = query;
    _currentState = HomeState.gallery;
    notifyListeners();

    try {
      _pins = await _apiService.fetchGallery(query: query);
    } catch (e) {
      debugPrint('Error fetching gallery: $e');
      _pins = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchByText(String query) async {
    fetchGallery(query: query);
  }

  Future<void> searchByImage(XFile imageFile) async {
    _isLoading = true;
    _currentState = HomeState.visualSearch;
    notifyListeners();

    try {
      _visualResults = await _apiService.searchByImage(imageFile);
    } catch (e) {
      debugPrint('Error parsing visual search: $e');
      _visualResults = [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void resetToGallery() {
    _currentState = HomeState.gallery;
    _visualResults = [];
    // Optionally reload gallery or keep existing
    notifyListeners();
  }
}
