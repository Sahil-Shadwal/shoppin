import { NextRequest, NextResponse } from 'next/server';

const SCRAPINGBEE_API_KEY = 'LO2AZHTXFTWM383O0SHXU9EGZG86OZFGI6RIMLRPFXM4I7W0AKQKWK2ASO0CC3IPYJH7W607060YPW89';

interface PinterestImage {
  src: string;
  alt: string;
}

interface ScrapingBeeResponse {
  images: PinterestImage[];
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const query = searchParams.get('query') || 'fashion';
  const shuffle = searchParams.get('shuffle') === 'true';

  try {
    // Build Pinterest search URL
    // Add random parameter to get different results each time when shuffling
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
    scrapingBeeUrl.searchParams.append('wait', '2000');


    // Make request to ScrapingBee
    const response = await fetch(scrapingBeeUrl.toString());
    
    if (!response.ok) {
      throw new Error(`ScrapingBee API error: ${response.status}`);
    }

    const data: ScrapingBeeResponse = await response.json();
    
    // Filter images to only include Pinterest pin images (exclude UI elements, icons, etc.)
    let filteredImages = data.images
      .filter(img => {
        // Filter for actual pin images (usually contain 236x or higher resolution)
        return img.src.includes('i.pinimg.com') && 
               (img.src.includes('236x') || img.src.includes('474x') || img.src.includes('736x')) &&
               img.alt && 
               img.alt.length > 10; // Ensure it has a meaningful description
      })
      .map((img, index) => ({
        id: `${query}-${shuffle ? Date.now() : 'static'}-${index}`,
        imageUrl: img.src.replace('236x', '474x'), // Get higher resolution version
        thumbnailUrl: img.src,
        title: img.alt,
        sourceUrl: `https://in.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`,
        query: query
      }));

    // When shuffling, randomize the order
    if (shuffle) {
      filteredImages = filteredImages.sort(() => Math.random() - 0.5);
    }

    return NextResponse.json({
      success: true,
      pins: filteredImages,
      total: filteredImages.length,
      query: query,
      shuffled: shuffle
    });

  } catch (error) {
    console.error('Scraping error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Failed to scrape Pinterest',
        pins: []
      },
      { status: 500 }
    );
  }
}

