class Pin {
  final dynamic id; // Can be int or String
  final String imageUrl;
  final String? caption;
  final String? source;

  Pin({
    required this.id,
    required this.imageUrl,
    this.caption,
    this.source,
  });

  factory Pin.fromJson(Map<String, dynamic> json) {
    return Pin(
      id: json['id'],
      imageUrl: json['image_url'],
      caption: json['caption'],
      source: json['source'],
    );
  }
}
