# Boardy

**AI-powered Kanban board with MCP integration.**

Boardy is a SaaS Kanban board with a native [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server. Connect any MCP-compatible AI assistant to manage your tasks through natural conversation.

## Features

- **MCP Server**: Standard MCP protocol — works with any compatible client
- **Automatic Task Management**: AI creates and updates cards based on your conversations
- **Real-time Kanban**: Drag-and-drop interface with instant sync
- **Team Collaboration**: Invite team members with role-based permissions
- **OAuth 2.1 Security**: Secure authentication with PKCE support

## Quick Start

### 1. Create Your Account

1. Go to [boardy.alivik.io](https://boardy.alivik.io)
2. Click "Get Started" and create an account
3. Create your first board

### 2. Connect Your AI Assistant

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "boardy": {
      "url": "https://boardy.alivik.io/mcp"
    }
  }
}
```

#### Claude Code (CLI)

```bash
claude mcp add boardy --url https://boardy.alivik.io/mcp
```

#### Any MCP Client

Use these endpoints:

| Endpoint | URL |
|----------|-----|
| MCP Server | `https://boardy.alivik.io/mcp` |
| OAuth Discovery | `https://boardy.alivik.io/.well-known/oauth-authorization-server` |
| Resource Metadata | `https://boardy.alivik.io/.well-known/oauth-protected-resource` |

The server uses OAuth 2.1 with PKCE. Implement the standard authorization flow:
1. Register client via `POST /auth/register`
2. Redirect user to `/auth/authorize` with PKCE challenge
3. Exchange code for token at `/auth/token`

## Usage Examples

Once connected, interact with your board naturally:

### Create a Task

**You**: "I need to implement user authentication for the mobile app"

**AI**: *Creates a card titled "Implement user authentication for mobile app" in your To Do column*

> I've created a new card for the authentication task. Would you like me to add any specific requirements?

### Check Board Status

**You**: "What tasks are currently in progress?"

**AI**: *Reads your board via `get_board`*

> You have 3 cards in the "In Progress" column:
> 1. **Fix login bug** (High priority)
> 2. **Update API documentation**
> 3. **Refactor payment module** - due tomorrow

### Move a Completed Task

**You**: "I just finished the login bug fix"

**AI**: *Moves the card to Done and adds a comment*

> Done! I've moved "Fix login bug" to Done.

### Search Cards

**You**: "Show me all high priority tasks"

**AI**: *Uses `search_cards` with filters*

> Found 2 high priority cards:
> 1. **Security audit** (In Progress) - due in 3 days
> 2. **Performance optimization** (To Do)

## MCP Tools

| Tool | Type | Description |
|------|------|-------------|
| `list_boards` | Read | Get all accessible boards |
| `get_board` | Read | Get full board with columns and cards |
| `search_cards` | Read | Search and filter cards |
| `list_users` | Read | Get board members |
| `create_card` | Write | Create a new card |
| `update_card` | Write | Update card details |
| `move_card` | Write | Move card between columns |
| `add_comment` | Write | Add a comment to a card |
| `close_card` | Write | Mark card as completed |
| `archive_card` | Write | Archive a card |
| `duplicate_card` | Write | Copy a card |
| `delete_card` | Destructive | Permanently delete a card |
| `delete_board` | Destructive | Permanently delete a board |

All tools include MCP annotations (`readOnlyHint`, `destructiveHint`) for client safety controls.

## Security

- **OAuth 2.1 with PKCE**: RFC-compliant authorization
- **Board Isolation**: Each token scoped to single board
- **Rate Limiting**: Protection against abuse
- **GDPR Compliant**: Data stored in EU (Germany)

## Self-Hosting

```bash
git clone https://github.com/alivik/boardy.git
cd boardy
cp .env.prod.example .env.prod
# Edit .env.prod with your secrets
docker compose -f docker-compose.prod.yml up -d
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /mcp` | MCP server (JSON-RPC) |
| `GET /.well-known/oauth-authorization-server` | OAuth 2.0 Discovery (RFC 8414) |
| `GET /.well-known/oauth-protected-resource` | Protected Resource Metadata (RFC 9728) |
| `POST /auth/register` | Dynamic Client Registration (RFC 7591) |
| `GET /auth/authorize` | Authorization endpoint |
| `POST /auth/token` | Token endpoint |
| `POST /auth/revoke` | Token revocation (RFC 7009) |

## Privacy & Terms

- [Privacy Policy](https://boardy.alivik.io/privacy)
- [Terms of Service](https://boardy.alivik.io/terms)
- [Imprint](https://boardy.alivik.io/imprint)

## Support

- **Email**: contact@alivik.io
- **Issues**: [GitHub Issues](https://github.com/alivik/boardy/issues)

## Tech Stack

- **Backend**: Python 3.12, FastAPI, FastMCP, SQLModel, PostgreSQL
- **Frontend**: React 18, TypeScript, TanStack Query, Tailwind CSS
- **Infrastructure**: Hetzner (EU), Cloudflare

## License

AGPL-3.0 — see [LICENSE](LICENSE)

---

Made by [boardy.ALIVIK](https://alivik.io)
