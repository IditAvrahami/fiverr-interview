# Fiverr URL Shortener Service

A URL shortening service for Fiverr sellers to create short, clean, trackable links to their Fiverr gigs. Sellers earn $0.05 in Fiverr credit for each valid click on their links.

## Features

- **Short Link Generation**: Create memorable short links from long Fiverr gig URLs
- **Duplicate Detection**: Same URLs get the same short code to prevent redundancy
- **Fraud Detection**: All clicks pass through fraud validation (simulated with a 100ms delay)
- **Click Tracking**: Record all clicks with IP and user agent information
- **Analytics**: View comprehensive stats with total clicks, valid clicks, earnings, and monthly breakdowns
- **Pagination**: Built-in pagination for viewing analytics of many links
- **Reward System**: Earn $0.05 in Fiverr credit for every valid click

## Tech Stack

- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL 16 with async SQLAlchemy
- **Cache**: Redis 7 (for future scaling)
- **Package manager**: uv (fast, lockfile-based)
- **Code quality**: isort, ruff, pyright, pre-commit
- **Testing**: pytest with async support
- **CI**: GitHub Actions running all checks
- **Docker**: Containerized deployment with Docker Compose

## Architecture

The application follows a clean, layered architecture:

- **Models**: SQLAlchemy models for Link and Click data
- **Schemas**: Pydantic models for request/response validation
- **Services**: Business logic for link generation, click tracking, and fraud detection
- **API**: FastAPI endpoints for link creation, redirection, and analytics
- **Config**: Environment-based configuration via pydantic-settings

### Directory Structure

```
app/                # FastAPI application
  main.py           # App entry, lifespan, root redirect handler
  config.py         # Pydantic settings (env vars)
  api/v1/           # API routes
    links.py        # Link generation and analytics endpoints
    health.py       # Health checks
  db/               # Database connection
  models/           # SQLAlchemy models
    link.py         # Link and Click models
  schemas/          # Pydantic schemas
    link.py         # Link request/response schemas
  services/         # Business logic
    link_service.py # Link generation and analytics
    fraud_service.py # Fraud detection
tests/              # pytest tests
docker-compose.yml  # All services (app, postgres, redis)
```

## API Endpoints

### Generate a Short Link

```
POST /api/v1/link
```

Request:
```json
{
  "original_url": "https://www.fiverr.com/your_username/your-gig"
}
```

Response:
```json
{
  "original_url": "https://www.fiverr.com/your_username/your-gig",
  "short_url": "http://localhost:8000/abc123",
  "short_code": "abc123",
  "created_at": "2023-05-20T15:30:45.123Z"
}
```

### Access a Short Link

```
GET /{short_code}
```

This redirects to the original URL and records the click if it passes fraud validation.

### Get Analytics

```
GET /api/v1/analytics?page=1&page_size=10
```

Response:
```json
{
  "links": [
    {
      "original_url": "https://www.fiverr.com/your_username/your-gig",
      "short_url": "http://localhost:8000/abc123",
      "short_code": "abc123",
      "created_at": "2023-05-20T15:30:45.123Z",
      "total_clicks": 42,
      "valid_clicks": 38,
      "earnings": 1.90,
      "monthly_stats": [
        {
          "month": "2023-05",
          "valid_clicks": 15,
          "earnings": 0.75
        },
        {
          "month": "2023-06",
          "valid_clicks": 23,
          "earnings": 1.15
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

## How to Run

### Option A: Docker (recommended)

```bash
docker compose up --build
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Option B: Local Development

1. Install uv (if not already): see [uv installation](https://docs.astral.sh/uv/getting-started/installation)
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Start Postgres and Redis:
   ```bash
   docker compose up -d postgres redis
   ```
5. Run the app:
   ```bash
   uv run uvicorn app.main:app --reload
   ```
6. In VS Code: select `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Mac/Linux) as interpreter

## Testing

Run all tests:
```bash
uv run pytest tests/ -v
```

Run with coverage:
```bash
uv run pytest tests/ -v --cov=app --cov-report=html
```

Run specific test file:
```bash
uv run pytest tests/api/test_links.py -v
```

## Example Usage

### Creating a Short Link

```bash
curl -X POST -H "Content-Type: application/json" -d '{"original_url":"https://www.fiverr.com/johndoe/design-awesome-logo"}' http://localhost:8000/api/v1/link
```

### Using the Short Link

Just open the short link in a browser:
```
http://localhost:8000/{short_code}
```

### Viewing Analytics

```bash
curl http://localhost:8000/api/v1/analytics
```

## Configuration

The following environment variables can be set in your `.env` file or environment:

- `BASE_URL`: Base URL for generated short links (default: "http://localhost:8000")
- `CREDIT_PER_CLICK`: Amount of credit in cents per valid click (default: 5)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `DEBUG`: Enable debug mode (default: true)
- `APP_ENV`: Environment name (default: "development")

## Testing Edge Cases

The service handles the following edge cases:

1. **Invalid URLs**: Returns a 422 error when trying to create links with invalid URLs
2. **Non-existent short codes**: Returns a 404 error when accessing a non-existent short link
3. **Duplicate URL shortening**: Returns the same short code when shortening the same URL multiple times
4. **Fraud detection**: Only valid clicks (90% in the simulation) earn credits
5. **Pagination limits**: Page size is limited to 100 entries max to prevent overload

## Further Improvements

Future improvements could include:

1. **Rate limiting**: Prevent abuse by limiting requests per IP
2. **Custom short codes**: Allow sellers to choose their own short codes
3. **Expiration dates**: Add expiry dates to links
4. **Click geolocation**: Track geographical data of clicks
5. **User authentication**: Allow sellers to log in and manage their links
6. **Caching**: Implement Redis caching for frequently accessed links
7. **Advanced analytics**: Add charts and visualizations for click data
8. **QR code generation**: Generate QR codes for short links
9. **A/B testing**: Compare performance of different links for the same gig

## Links

- **Extending the app**: See [CLAUDE.md](CLAUDE.md) for stack, patterns, and where to add code.