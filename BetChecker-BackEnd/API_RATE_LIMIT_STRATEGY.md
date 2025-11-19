# API Rate Limit Strategy

## Current Limits

- **Free Plan**: 100 requests per day
- **Rate Limit**: 10 requests per minute
- **Base URLs**: 
  - RapidAPI: `https://api-afl.p.rapidapi.com/`
  - API-Sports: `https://v1.afl.api-sports.io/`

## Strategy for Finding Game Statistics Endpoint

Since we have limited requests, let's be strategic:

1. **Check PDF documentation first** - Get exact endpoint URL before testing
2. **Test one endpoint at a time** - Don't waste requests on guesses
3. **Cache responses** - Save successful responses for reference
4. **Plan requests carefully** - Batch operations when possible

## Efficient API Usage Plan

### Phase 1: Discovery (Use sparingly)
- Test exact endpoint from PDF documentation
- Verify endpoint structure
- Document response format

### Phase 2: Scraping Strategy (Optimize requests)

**For Teams** (One-time, ~18 requests):
- `/teams` - Get all teams once
- Store in database
- **Total: 1 request**

**For Players** (Per season, ~18 teams × 1 request):
- `/players?team={id}&season={year}` - Get players per team per season
- **Total: 18 requests per season**

**For Games** (Per season, 1 request):
- `/games?season={year}&league=1` - Get all games for season
- **Total: 1 request per season**

**For Player Statistics** (TBD - depends on endpoint):
- Need to find the exact endpoint first
- May need multiple requests per game or per player

**Daily Budget**: 100 requests
- Teams: 1 request (one-time)
- Players: 18 requests per season
- Games: 1 request per season
- **Remaining: ~80 requests per day for statistics**

## Rate Limiting Best Practices

1. **Add delays**: Wait 6+ seconds between requests (10/minute = 6 seconds)
2. **Batch when possible**: Use `ids` parameter if available (up to 10 IDs at once)
3. **Cache responses**: Don't re-fetch data we already have
4. **Track usage**: Log requests to monitor daily limit
5. **Prioritize**: Test endpoints first, then scrape systematically

## Next Steps

1. **Get exact endpoint URL** from PDF documentation
2. **Test endpoint once** with sample game ID
3. **Document response structure**
4. **Plan scraping approach** based on endpoint capabilities
5. **Build scraper** with rate limiting built-in

