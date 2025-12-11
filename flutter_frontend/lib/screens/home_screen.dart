import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_staggered_grid_view/flutter_staggered_grid_view.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/home_provider.dart';
import '../models/pin.dart';

import 'pin_detail_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: _SearchBar(),
        actions: [
          IconButton(
            icon: const Icon(Icons.camera_alt),
            onPressed: () async {
              final ImagePicker picker = ImagePicker();
              final XFile? image = await picker.pickImage(source: ImageSource.gallery);
              if (image != null && context.mounted) {
                Provider.of<HomeProvider>(context, listen: false).searchByImage(image);
              }
            },
          ),
        ],
      ),
      body: Consumer<HomeProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (provider.currentState == HomeState.gallery && provider.pins.isEmpty) {
             return const Center(child: Text('No results found.'));
          }

          if (provider.currentState == HomeState.visualSearch && provider.visualResults.isEmpty) {
             return const Center(child: Text('No visual matches found.'));
          }

          final itemCount = provider.currentState == HomeState.gallery
              ? provider.pins.length
              : provider.visualResults.length;

          return MasonryGridView.count(
            padding: const EdgeInsets.all(8.0),
            crossAxisCount: 2,
            mainAxisSpacing: 8.0,
            crossAxisSpacing: 8.0,
            itemCount: itemCount,
            itemBuilder: (context, index) {
              if (provider.currentState == HomeState.gallery) {
                final pin = provider.pins[index];
                return _PinCard(pin: pin);
              } else {
                final product = provider.visualResults[index];
                // Convert Product to Pin for detail view
                final pin = Pin(
                  id: product.productId,
                  imageUrl: product.imageUrl,
                  caption: product.title,
                  source: product.price != null ? '\$${product.price}' : 'Unknown',
                );
                return _PinCard(pin: pin);
              }
            },
          );
        },
      ),
    );
  }
}

class _SearchBar extends StatefulWidget {
  @override
  State<_SearchBar> createState() => _SearchBarState();
}

class _SearchBarState extends State<_SearchBar> {
  late TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  Widget build(BuildContext context) {
    // Keep internal state but if empty, could sync with provider
    return TextField(
      controller: _controller,
      decoration: InputDecoration(
        hintText: 'Search fashion (e.g. zara, outfit)...',
        border: InputBorder.none,
        suffixIcon: IconButton(
          icon: const Icon(Icons.search),
          onPressed: () {
            if (_controller.text.isNotEmpty) {
              FocusManager.instance.primaryFocus?.unfocus();
              Provider.of<HomeProvider>(context, listen: false)
                  .searchByText(_controller.text);
            }
          },
        ),
      ),
      textInputAction: TextInputAction.search,
      onSubmitted: (value) {
        if (value.isNotEmpty) {
          FocusManager.instance.primaryFocus?.unfocus();
          Provider.of<HomeProvider>(context, listen: false).searchByText(value);
        }
      },
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

class _PinCard extends StatelessWidget {
  final Pin pin;

  const _PinCard({required this.pin});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => PinDetailScreen(pin: pin),
          ),
        );
      },
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CachedNetworkImage(
              imageUrl: pin.imageUrl,
              placeholder: (context, url) => Container(
                color: Colors.grey[200],
                height: 150, // Approximate height for placeholder
              ),
              errorWidget: (context, url, error) => const Icon(Icons.error),
              fit: BoxFit.cover,
            ),
            if (pin.caption != null)
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  pin.caption!,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
