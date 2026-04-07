# Boardy

**AI-powered Kanban board with native Claude integration via MCP.**

Boardy is a SaaS Kanban board that connects directly to Claude via the Model Context Protocol (MCP). Once connected, Claude can automatically manage your tasks—creating cards, moving them between columns, and adding comments based on your conversations.

## Features

- **Native Claude Integration**: Connect your board to Claude Desktop with one click
- **Automatic Task Management**: Claude creates and updates cards based on your conversations
- **Real-time Kanban**: Drag-and-drop interface with instant sync
- **Team Collaboration**: Invite team members with role-based permissions
- **OAuth 2.1 Security**: Secure authentication with PKCE support

## Quick Start

### 1. Create Your Account

1. Go to [boardy.alivik.io](https://boardy.alivik.io)
2. Click "Get Started" and create an account
3. Create your first board

### 2. Connect to Claude

1. In Claude Desktop, click "Add Server" in MCP settings
2. Enter the MCP URL: `https://boardy.alivik.io/mcp`
3. Complete the OAuth authorization flow
4. Select which board Claude should manage

That's it! Claude now has access to your Kanban board.

## Usage Examples

Once connected, you can interact with your board naturally through Claude:

### Example 1: Create a New Task

**You**: "I need to implement user authentication for the mobile app"

**Claude**: *Creates a card titled "Implement user authentication for mobile app" in your To Do column*

> I've created a new card for the authentication task. Would you like me to add any specific requirements or acceptance criteria?

### Example 2: Check Board Status

**You**: "What tasks are currently in progress?"

**Claude**: *Reads your board via `get_board`*

> You have 3 cards in the "In Progress" column:
> 1. **Fix login bug** (High priority) - assigned to @alice
> 2. **Update API documentation** - created by Claude
> 3. **Refactor payment module** - due tomorrow
>
> Would you like me to update any of these?

### Example 3: Move a Completed Task

**You**: "I just finished the login bug fix and pushed the PR"

**Claude**: *Moves the card to Done and adds a comment*

> Great work! I've moved "Fix login bug" to Done and added a comment noting the PR was merged. Is there anything blocking the other in-progress tasks?

### Example 4: Search and Filter Cards

**You**: "Show me all high priority tasks assigned to me"

**Claude**: *Uses `search_cards` with filters*

> Found 2 high priority cards assigned to you:
> 1. **Security audit** (In Progress) - due in 3 days
> 2. **Performance optimization** (To Do) - no due date
>
> The security audit is approaching its deadline. Want me to add a reminder comment?

### Example 5: Add Context to a Task

**You**: "Add a note to the API docs card that we need to include the new endpoints from PR #42"

**Claude**: *Adds a comment to the card*

> Done! I've added the following comment to "Update API documentation":
> "Include new endpoints from PR #42: /api/v1/users/export and /api/v1/webhooks"

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `list_boards` | Get all boards you have access to |
| `get_board` | Get full board with columns and cards |
| `create_card` | Create a new card |
| `update_card` | Update card title, description, priority, due date |
| `move_card` | Move card to another column |
| `add_comment` | Add a comment to a card |
| `close_card` | Mark a card as completed |
| `archive_card` | Archive a card |
| `delete_card` | Permanently delete a card |
| `duplicate_card` | Create a copy of a card |
| `search_cards` | Search and filter cards |
| `list_users` | Get board members |

## Security

- **OAuth 2.1 with PKCE**: Secure authorization flow
- **Board Isolation**: Each OAuth token is scoped to a single board
- **Rate Limiting**: Protection against abuse
- **GDPR Compliant**: Data stored in EU (Germany)

## API Documentation

- OAuth Discovery: `GET /.well-known/oauth-authorization-server`
- Protected Resource Metadata: `GET /.well-known/oauth-protected-resource`
- MCP Endpoint: `POST /mcp`

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

---

Made with care by [boardy.ALIVIK](https://alivik.io)
