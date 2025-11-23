import { NextResponse } from 'next/server';

// Use environment variable for backend URL (Docker: http://backend:8000, Local: http://127.0.0.1:8000)
const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://127.0.0.1:8000';

export async function POST(request: Request) {
  try {
    console.log('📸 Proxying image search to Django backend...');
    
    const formData = await request.formData();
    const imageFile = formData.get('image') as File;

    if (!imageFile) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    // Forward to Django backend
    const backendFormData = new FormData();
    // Ensure we pass the file with a filename, otherwise Django might not recognize it as a file upload
    backendFormData.append('image', imageFile, imageFile.name || 'image.jpg');
    
    // Pass through additional search parameters
    const topK = formData.get('top_k') || '20';
    const maxPrice = formData.get('max_price');
    const negativeQuery = formData.get('negative_query');
    const queryText = formData.get('query_text');
    const category = formData.get('category');
    
    backendFormData.append('top_k', topK.toString());
    if (maxPrice) backendFormData.append('max_price', maxPrice.toString());
    if (negativeQuery) backendFormData.append('negative_query', negativeQuery.toString());
    if (queryText) backendFormData.append('query_text', queryText.toString());
    if (category) backendFormData.append('category', category.toString());

    console.log(`Proxying image search to Django: ${imageFile.name}, size: ${imageFile.size}`);

    const response = await fetch(`${DJANGO_BACKEND_URL}/api/search/image/`, {
      method: 'POST',
      body: backendFormData,
      // Do NOT set Content-Type header, let fetch set it with boundary
    });

    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      console.error('Backend returned non-JSON response:', text);
      throw new Error(`Backend error: ${response.status} ${response.statusText}`);
    }

    if (!response.ok) {
      console.error('Backend returned error:', data);
      return NextResponse.json(
        { error: data.error || 'Failed to search image' },
        { status: response.status }
      );
    }

    // Transform response to match frontend Pin interface
    const pins = data.matches.map((match: any) => ({
      id: match.product_id,
      imageUrl: match.image_url,
      thumbnailUrl: match.image_url,
      title: match.title,
      sourceUrl: match.pdp_url,
      query: 'visual_search',
      price: match.price,
      brand: match.brand,
      score: match.visual_score
    }));

    return NextResponse.json({
      success: true,
      pins: pins
    });

  } catch (error) {
    console.error('Error in search-image route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
