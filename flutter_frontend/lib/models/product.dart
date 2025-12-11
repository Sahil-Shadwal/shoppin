class Product {
  final String productId;
  final String title;
  final String imageUrl;
  final double? price;
  final double? visualScore;

  Product({
    required this.productId,
    required this.title,
    required this.imageUrl,
    this.price,
    this.visualScore,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      productId: json['product_id'],
      title: json['title'],
      imageUrl: json['image_url'],
      price: json['price'] != null ? (json['price'] as num).toDouble() : null,
      visualScore: json['visual_score'] != null ? (json['visual_score'] as num).toDouble() : null,
    );
  }
}
