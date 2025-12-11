import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import '../models/pin.dart';
import '../models/product.dart';
import '../services/api_service.dart';

class PinDetailScreen extends StatefulWidget {
  final Pin pin;

  const PinDetailScreen({Key? key, required this.pin}) : super(key: key);

  @override
  State<PinDetailScreen> createState() => _PinDetailScreenState();
}

class _PinDetailScreenState extends State<PinDetailScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoadingSimilar = false;
  List<Product> _similarProducts = [];

  void _shopSimilar() async {
    setState(() {
      _isLoadingSimilar = true;
    });

    try {
      final products = await _apiService.searchByImageUrl(widget.pin.imageUrl);
      setState(() {
        _similarProducts = products;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load similar items: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoadingSimilar = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pin Detail'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Hero(
              tag: 'pin_${widget.pin.id}',
              child: CachedNetworkImage(
                imageUrl: widget.pin.imageUrl,
                fit: BoxFit.cover,
                placeholder: (context, url) => Container(
                  height: 300,
                  color: Colors.grey[200],
                  child: const Center(child: CircularProgressIndicator()),
                ),
                errorWidget: (context, url, error) => const Icon(Icons.error),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (widget.pin.caption != null)
                    Text(
                      widget.pin.caption!,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                  const SizedBox(height: 8),
                  if (widget.pin.source != null)
                    Text(
                      'Source: ${widget.pin.source}',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey,
                          ),
                    ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _isLoadingSimilar ? null : _shopSimilar,
                    icon: _isLoadingSimilar
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.shopping_bag_outlined),
                    label: const Text('Shop Similar'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                    ),
                  ),
                  if (_similarProducts.isNotEmpty) ...[
                    const SizedBox(height: 24),
                    Text(
                      'Similar Products',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _similarProducts.length,
                      itemBuilder: (context, index) {
                        final product = _similarProducts[index];
                        return ListTile(
                          leading: CachedNetworkImage(
                            imageUrl: product.imageUrl,
                            width: 50,
                            height: 50,
                            fit: BoxFit.cover,
                          ),
                          title: Text(product.title),
                          subtitle: product.price != null
                              ? Text('\$${product.price!.toStringAsFixed(2)}')
                              : null,
                          trailing: product.visualScore != null
                              ? Text(
                                  '${(product.visualScore! * 100).toStringAsFixed(0)}%',
                                  style: const TextStyle(color: Colors.green),
                                )
                              : null,
                        );
                      },
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
