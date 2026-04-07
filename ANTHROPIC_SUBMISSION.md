# Anthropic MCP Directory Submission Checklist

## Pre-Deployment Verification

### Code Ready
- [x] MCP Server with 14 tools (all with readOnlyHint/destructiveHint annotations)
- [x] OAuth 2.1 Authorization Server (RFC 8414)
- [x] Dynamic Client Registration (RFC 7591)
- [x] PKCE support (S256)
- [x] RFC 9728 Protected Resource Metadata (`/.well-known/oauth-protected-resource`)
- [x] WWW-Authenticate header middleware for 401 responses
- [x] Rate limiting (PostgreSQL-based)
- [x] Board isolation (token scoped to single board)

### Documentation Ready
- [x] README.md with 5 usage examples
- [x] Privacy Policy page (`/privacy`)
- [x] Terms of Service page (`/terms`)
- [x] Imprint page (`/imprint`)

### Tests Ready
- [x] MCP tool annotations tests (12 passed)
- [x] OAuth discovery tests (2 passed)
- [x] Client registration tests
- [x] Total: 25 tests passing

---

## Deployment Steps

### 1. Server Setup (Hetzner CAX11)
```bash
# SSH to server
ssh root@<server-ip>

# Clone repo
git clone https://github.com/alivik/boardy.git
cd boardy

# Create production env
cp .env.prod.example .env.prod
nano .env.prod  # Fill in secrets
```

### 2. Generate Secrets
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate POSTGRES_PASSWORD
openssl rand -hex 32
```

### 3. Deploy
```bash
# Start services
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create demo account
docker compose -f docker-compose.prod.yml exec backend python scripts/create_demo_account.py
```

### 4. Configure Nginx (if not using Cloudflare)
```nginx
server {
    listen 443 ssl http2;
    server_name boardy.alivik.io;

    ssl_certificate /etc/letsencrypt/live/boardy.alivik.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/boardy.alivik.io/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /mcp {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /auth/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /.well-known/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

---

## Post-Deployment Verification

Run these checks before submitting:

```bash
# 1. Health check
curl https://boardy.alivik.io/health

# 2. OAuth discovery (RFC 8414)
curl https://boardy.alivik.io/.well-known/oauth-authorization-server

# 3. Protected resource metadata (RFC 9728)
curl https://boardy.alivik.io/.well-known/oauth-protected-resource

# 4. Client registration
curl -X POST https://boardy.alivik.io/auth/register \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Test", "redirect_uris": ["https://claude.ai/api/mcp/auth_callback"]}'

# 5. MCP endpoint (should return 401 with WWW-Authenticate)
curl -I https://boardy.alivik.io/mcp/
```

---

## Anthropic Submission Form

**Form URL**: https://support.claude.com/en/articles/12922490-remote-mcp-server-submission-guide

### Required Information

| Field | Value |
|-------|-------|
| **Server Name** | Boardy |
| **Server URL** | `https://boardy.alivik.io/mcp` |
| **Description** | AI-powered Kanban board with native Claude integration. Create, move, and manage tasks through natural conversation. |
| **Category** | Productivity / Project Management |
| **Auth Type** | OAuth 2.1 with PKCE |
| **OAuth Discovery** | `https://boardy.alivik.io/.well-known/oauth-authorization-server` |

### Test Account Credentials
| Field | Value |
|-------|-------|
| **Email** | demo@boardy.alivik.io |
| **Password** | BoardyDemo2026! |
| **Demo Board** | Demo Project Board |

### MCP Tools (14 total)

| Tool | Hint | Description |
|------|------|-------------|
| `list_boards` | readOnly | List accessible boards |
| `get_board` | readOnly | Get board with columns and cards |
| `create_card` | destructive:false | Create a new card |
| `update_card` | destructive:false | Update card details |
| `move_card` | destructive:false | Move card between columns |
| `add_comment` | destructive:false | Add comment to card |
| `close_card` | destructive:false | Mark card as done |
| `archive_card` | destructive:false | Archive a card |
| `duplicate_card` | destructive:false | Copy a card |
| `attach_file` | destructive:false | Attach file to card |
| `search_cards` | readOnly | Search and filter cards |
| `list_users` | readOnly | Get board members |
| `delete_card` | destructive:true | Permanently delete card |
| `delete_board` | destructive:true | Permanently delete board |

### Support Contact
- **Email**: contact@alivik.io
- **Website**: https://boardy.alivik.io

---

## After Submission

1. Monitor email for Anthropic feedback
2. Be ready to make changes within 24-48 hours
3. Keep test account active and demo board populated
