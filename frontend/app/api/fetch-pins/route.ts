import { NextRequest, NextResponse } from 'next/server';

const DJANGO_BACKEND_URL = process.env.DJANGO_BACKEND_URL || 'http://127.0.0.1:8000';
const SCRAPINGBEE_API_KEY = 'DGQAE9RYPCV7J6C2AMGV1H2OBV3BMAJ8P4NKVH6WBVRAF4RIV38BFVN2WKPFTE707RAAE9NX8DWKCPYN';
 
interface Pin {
  id: string;
  imageUrl: string;
  thumbnailUrl: string;
  title: string;
  sourceUrl: string;
  query: string;
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const query = searchParams.get('query') || 'fashion';
  const shuffle = searchParams.get('shuffle') === 'true';

  try {
    // 🔄 If shuffle/More Ideas: ALWAYS scrape fresh content
    if (shuffle) {
      console.log(`🔄 More Ideas clicked - scraping FRESH content for "${query}"`);
      const scrapedPins = await scrapePinterest(query, true);
      
      // Store scraped images in background (don't wait)
      storeInDatabase(scrapedPins, query).catch(err => 
        console.error('Background storage error:', err)
      );

      return NextResponse.json({
        success: true,
        pins: scrapedPins,
        total: scrapedPins.length,
        query: query,
        shuffled: true,
        cached: false
      });
    }

    // ⚡ First load: Check DB first for instant load
    const dbPins = await fetchFromDatabase(query, false);
    
    // If we have enough cached images, return them immediately
    if (dbPins.length >= 15) {
      console.log(`✅ Returning ${dbPins.length} cached images for "${query}"`);
      return NextResponse.json({
        success: true,
        pins: dbPins,
        total: dbPins.length,
        query: query,
        shuffled: false,
        cached: true
      });
    }

    // Not enough cached images, scrape fresh content
    console.log(`🔍 Not enough cached images - scraping for "${query}"`);
    const scrapedPins = await scrapePinterest(query, false);
    
    // Store scraped images in background (don't wait)
    storeInDatabase(scrapedPins, query).catch(err => 
      console.error('Background storage error:', err)
    );

    return NextResponse.json({
      success: true,
      pins: scrapedPins,
      total: scrapedPins.length,
      query: query,
      shuffled: shuffle,
      cached: false
    });

  } catch (error) {
    console.error('Fetch error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to fetch pins',
        pins: []
      },
      { status: 500 }
    );
  }
}

async function fetchFromDatabase(query: string, shuffle: boolean): Promise<Pin[]> {
  try {
    const response = await fetch(
      `${DJANGO_BACKEND_URL}/api/gallery/?source=pinterest&query=${encodeURIComponent(query)}&limit=50`,
      { cache: 'no-store' }
    );

    if (!response.ok) {
      console.warn('Failed to fetch from database:', response.status);
      return [];
    }

    const data = await response.json();
    
    if (!data.success || !data.images || data.images.length === 0) {
      return [];
    }

    // Convert Django format to frontend Pin format
    const pins: Pin[] = data.images.map((img: any, index: number) => ({
      id: `db-${img.id}`,
      imageUrl: img.image_url,
      thumbnailUrl: img.thumbnail_url || img.image_url,
      title: img.caption || 'Fashion inspiration',
      sourceUrl: `https://in.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`,
      query: query
    }));

    return pins;
  } catch (error) {
    console.error('Database fetch error:', error);
    return [];
  }
}

async function scrapePinterest(query: string, shuffle: boolean): Promise<Pin[]> {
  // Build Pinterest search URL
  let pinterestUrl = `https://in.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`;
  
  // When shuffling, add timestamp to force fresh results
  if (shuffle) {
    pinterestUrl += `&rs=${Date.now()}`;
  }
  
  // Build ScrapingBee API URL with extract rules
  const extractRules = {
    images: {
      selector: 'img',
      type: 'list',
      output: {
        src: 'img@src',
        alt: 'img@alt'
      }
    }
  };

  const scrapingBeeUrl = new URL('https://app.scrapingbee.com/api/v1');
  scrapingBeeUrl.searchParams.append('api_key', SCRAPINGBEE_API_KEY);
  scrapingBeeUrl.searchParams.append('url', pinterestUrl);
  scrapingBeeUrl.searchParams.append('extract_rules', JSON.stringify(extractRules));
  scrapingBeeUrl.searchParams.append('render_js', 'true');

  if (shuffle) {
    // Scroll down to get fresh pins (next page)
    const jsScenario = {
      instructions: [
        { wait: 1000 },
        { scroll_y: 2500 }, // Scroll down significantly to get past initial results
        { wait: 2000 }
      ]
    };
    scrapingBeeUrl.searchParams.append('js_scenario', JSON.stringify(jsScenario));
  } else {
    scrapingBeeUrl.searchParams.append('wait', '2000');
  }

  const response = await fetch(scrapingBeeUrl.toString());
  
  if (!response.ok) {
    throw new Error(`ScrapingBee API error: ${response.status}`);
  }

  const data = await response.json();
  
  // Filter images to only include Pinterest pin images
  let filteredImages = data.images
    .filter((img: any) => {
      return img.src.includes('i.pinimg.com') && 
             (img.src.includes('236x') || img.src.includes('474x') || img.src.includes('736x')) &&
             img.alt && 
             img.alt.length > 10;
    })
    .map((img: any, index: number) => ({
      id: `${query}-${shuffle ? Date.now() : 'static'}-${index}`,
      imageUrl: img.src.replace('236x', '474x'),
      thumbnailUrl: img.src,
      title: img.alt,
      sourceUrl: `https://in.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`,
      query: query
    }));

  // When shuffling, randomize the order
  if (shuffle) {
    filteredImages = filteredImages.sort(() => Math.random() - 0.5);
  }

  return filteredImages;
}

async function storeInDatabase(pins: Pin[], query: string): Promise<void> {
  try {
    const imagesToStore = pins.map(img => ({
      image_url: img.imageUrl,
      thumbnail_url: img.thumbnailUrl,
      source: 'pinterest',
      caption: img.title,
      query: query,
      hashtags: [],
    }));

    const response = await fetch(`${DJANGO_BACKEND_URL}/api/scraped-images/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ images: imagesToStore }),
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`📦 Stored ${data.created_count} images in Django backend`);
    }
  } catch (error) {
    console.error('Failed to store in Django backend:', error);
    // Don't throw - storage is optional
  }
}
