# Boardy MCP Skill

Boardy is a Kanban board that Claude can manage through natural conversation.

## What Claude Can Do

### Task Management
- **Create cards** from conversations — "I need to implement user auth"
- **Update cards** — change title, description, priority, status, color, due date
- **Move cards** between columns (Backlog → In Progress → Review → Done)
- **Close cards** when tasks are completed
- **Search cards** by assignee, priority, status, color, or label

### Collaboration
- **Assign tasks** to team members or AI Assistant (`ai-agent`)
- **Add comments** to cards for context and updates
- **Attach files** via URL

### Board Operations
- **List boards** accessible to the user
- **Get full board** with all columns and cards
- **Archive cards** (soft delete)
- **Duplicate cards** for similar tasks

## Workflow Rules

Claude follows these rules automatically:

| When... | Claude will... |
|---------|----------------|
| A task is discussed | Check if card exists, create if not |
| A task is completed | Mark as done and move to Done column |
| A blocker is found | Add comment and set status to "blocked" |
| Git push/merge mentioned | Close the related card |

## Column Structure

Standard Kanban columns (in order):
1. **Backlog** — new tasks
2. **In Progress** — active work
3. **Review** — awaiting review
4. **Done** — completed

## Example Prompts

### Create a Task
> "I need to fix the login bug on mobile"

Claude creates a card titled "Fix login bug on mobile" in Backlog.

### Check Progress
> "What tasks are in progress?"

Claude lists all cards in the In Progress column.

### Complete a Task
> "I just finished the API refactoring"

Claude marks the card as done and moves it to Done.

### Assign to AI
> "AI, take the documentation task"

Claude assigns the card to `ai-agent` (AI Assistant).

### Search by Priority
> "Show me all critical tasks"

Claude searches cards with `priority: critical`.

## Card Properties

| Property | Values |
|----------|--------|
| Priority | `low`, `medium`, `high`, `critical` |
| Status | `open`, `in_progress`, `blocked`, `done` |
| Color | `gray`, `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink` |
| Assignee | User ID or `ai-agent` for AI Assistant |
| Due Date | ISO format `YYYY-MM-DD` |
| Labels | Array of strings |

## Privacy & Security

- OAuth 2.1 with PKCE — secure authentication
- Board isolation — each token scoped to specific boards
- Data stored in EU (Germany) — GDPR compliant
- No conversation data collected — only board content

## Support

- Email: contact@alivik.io
- Privacy Policy: https://boardy.alivik.io/privacy
- Terms of Service: https://boardy.alivik.io/terms
