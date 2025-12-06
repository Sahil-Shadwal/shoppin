import { NextResponse } from 'next/server';

const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');
  const category = searchParams.get('category');
  const forceFresh = searchParams.get('forceFresh') === 'true';

  // We need at least one of them
  if (!query && !category) {
    return NextResponse.json({ success: false, error: 'Query or Category is required' }, { status: 400 });
  }

  // If query is missing but category exists, use category as query
  const finalQuery = query || category;

  try {
    // 1. Try to fetch from DB Gallery first
    // We use the gallery endpoint which returns ScrapedImage objects
    const galleryResponse = await fetch(`${DJANGO_BACKEND_URL}/api/gallery/?query=${encodeURIComponent(finalQuery!)}&limit=50`);
    
    let pins = [];
    let cached = false;

    if (galleryResponse.ok) {
      const galleryData = await galleryResponse.json();
      if (galleryData.images && galleryData.images.length > 0 && !forceFresh) {
        // Found in DB! Map to Pin format
        pins = galleryData.images.map((img: any) => ({
          id: img.id,
          imageUrl: img.image_url,
          thumbnailUrl: img.thumbnail_url || img.image_url,
          title: img.caption || finalQuery,
          sourceUrl: img.source === 'pinterest' ? `https://pinterest.com/pin/${img.id}` : '',
          query: img.query
        }));
        cached = true;
      }
    }

    // 2. If no pins found or forceFresh is true, trigger scraper
    if (pins.length === 0) {
      console.log(`No pins found for "${finalQuery}", triggering scraper...`);
      
      // Call our own scrape endpoint
      // We need to use the absolute URL for server-side fetch
      const protocol = request.url.split('://')[0];
      const host = request.headers.get('host');
      const scrapeUrl = `${protocol}://${host}/api/scrape?query=${encodeURIComponent(finalQuery!)}&shuffle=${forceFresh}`;
      
      const scrapeResponse = await fetch(scrapeUrl);
      
      if (scrapeResponse.ok) {
        const scrapeData = await scrapeResponse.json();
        if (scrapeData.success && scrapeData.pins) {
          pins = scrapeData.pins;
        }
      } else {
        console.error('Scraper failed:', await scrapeResponse.text());
      }
    }

    return NextResponse.json({
      success: true,
      pins: pins,
      cached: cached,
      query: finalQuery
    });

  } catch (error) {
    console.error('Error fetching pins:', error);
    return NextResponse.json({ success: false, error: 'Failed to fetch pins' }, { status: 500 });
  }
}
