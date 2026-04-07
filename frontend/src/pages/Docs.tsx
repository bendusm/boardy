import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  ArrowLeft,
  Plug,
  Settings,
  Shield,
  Zap,
  Terminal,
  BookOpen,
  Copy,
  Check,
} from "lucide-react";
import { useState } from "react";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="absolute top-3 right-3 p-2 rounded-lg bg-landing-surface-container-low hover:bg-landing-surface-container text-landing-secondary hover:text-landing-primary transition-all"
      title="Copy to clipboard"
    >
      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
    </button>
  );
}

function CodeBlock({ children, copyText }: { children: string; copyText?: string }) {
  return (
    <div className="relative">
      <pre className="bg-gray-900 text-gray-100 rounded-xl p-4 pr-12 overflow-x-auto text-sm">
        <code>{children}</code>
      </pre>
      <CopyButton text={copyText || children} />
    </div>
  );
}

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-landing-background font-body">
      {/* Header */}
      <header className="w-full border-b border-landing-outline-variant/20 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="flex justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-5">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-landing-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div className="font-headline italic text-2xl font-bold text-landing-on-background">
              Boardy
            </div>
          </Link>
          <Link
            to="/"
            className="flex items-center gap-2 text-landing-secondary hover:text-landing-primary transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </nav>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-16">
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-8 h-8 text-landing-primary" />
          <h1 className="font-headline italic text-4xl md:text-5xl">
            Documentation
          </h1>
        </div>
        <p className="text-landing-secondary text-lg mb-12">
          Learn how to connect Boardy with your AI assistant using MCP.
        </p>

        {/* Table of Contents */}
        <nav className="bg-white rounded-2xl p-6 mb-12 border border-landing-outline-variant/20">
          <h2 className="font-bold text-sm uppercase text-landing-secondary mb-4">
            On this page
          </h2>
          <ul className="space-y-2">
            <li>
              <a href="#quick-start" className="text-landing-primary hover:underline">
                Quick Start
              </a>
            </li>
            <li>
              <a href="#mcp-setup" className="text-landing-primary hover:underline">
                MCP Setup
              </a>
            </li>
            <li>
              <a href="#available-tools" className="text-landing-primary hover:underline">
                Available Tools
              </a>
            </li>
            <li>
              <a href="#security" className="text-landing-primary hover:underline">
                Security & Privacy
              </a>
            </li>
          </ul>
        </nav>

        {/* Quick Start */}
        <section id="quick-start" className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-landing-primary-container/30 flex items-center justify-center">
              <Zap className="w-5 h-5 text-landing-primary" />
            </div>
            <h2 className="text-2xl font-bold">Quick Start</h2>
          </div>

          <div className="prose prose-lg max-w-none text-landing-secondary">
            <ol className="space-y-4">
              <li>
                <strong className="text-landing-on-background">Create an account</strong>
                <p>
                  <Link to="/register" className="text-landing-primary hover:underline">
                    Sign up for free
                  </Link>{" "}
                  and create your first board.
                </p>
              </li>
              <li>
                <strong className="text-landing-on-background">Get your MCP URL</strong>
                <p>
                  Open your board, click the <strong>Settings</strong> icon (gear) in the header,
                  and copy the MCP URL from the "Connect AI Assistant" section.
                </p>
              </li>
              <li>
                <strong className="text-landing-on-background">Connect your AI assistant</strong>
                <p>
                  Add the MCP URL to your AI assistant's configuration. Claude Desktop,
                  Claude Code, and other MCP-compatible clients are supported.
                </p>
              </li>
              <li>
                <strong className="text-landing-on-background">Authorize access</strong>
                <p>
                  When your AI first connects, you'll be prompted to authorize access
                  to a specific board. Each authorization is scoped to one board for security.
                </p>
              </li>
            </ol>
          </div>
        </section>

        {/* MCP Setup */}
        <section id="mcp-setup" className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-landing-primary-container/30 flex items-center justify-center">
              <Plug className="w-5 h-5 text-landing-primary" />
            </div>
            <h2 className="text-2xl font-bold">MCP Setup</h2>
          </div>

          <div className="space-y-8">
            {/* Claude Desktop */}
            <div className="bg-white rounded-2xl p-6 border border-landing-outline-variant/20">
              <div className="flex items-center gap-2 mb-4">
                <Terminal className="w-5 h-5 text-landing-primary" />
                <h3 className="text-lg font-bold">Claude Desktop</h3>
              </div>
              <p className="text-landing-secondary mb-4">
                Add Boardy to your Claude Desktop configuration file:
              </p>
              <p className="text-sm text-landing-secondary mb-2">
                <strong>macOS:</strong> ~/Library/Application Support/Claude/claude_desktop_config.json
              </p>
              <p className="text-sm text-landing-secondary mb-4">
                <strong>Windows:</strong> %APPDATA%\Claude\claude_desktop_config.json
              </p>
              <CodeBlock copyText={`{
  "mcpServers": {
    "boardy": {
      "url": "https://boardy.alivik.io/mcp"
    }
  }
}`}>
{`{
  "mcpServers": {
    "boardy": {
      "url": "https://boardy.alivik.io/mcp"
    }
  }
}`}
              </CodeBlock>
              <p className="text-sm text-landing-secondary mt-4">
                After saving, restart Claude Desktop. You'll be prompted to authorize
                access to your board.
              </p>
            </div>

            {/* Claude Code */}
            <div className="bg-white rounded-2xl p-6 border border-landing-outline-variant/20">
              <div className="flex items-center gap-2 mb-4">
                <Settings className="w-5 h-5 text-landing-primary" />
                <h3 className="text-lg font-bold">Claude Code (CLI)</h3>
              </div>
              <p className="text-landing-secondary mb-4">
                Add Boardy via the Claude Code settings or directly in your config:
              </p>
              <CodeBlock>
{`claude mcp add boardy --url https://boardy.alivik.io/mcp`}
              </CodeBlock>
              <p className="text-sm text-landing-secondary mt-4">
                Or add to your ~/.claude/settings.json manually.
              </p>
            </div>

            {/* Any MCP Client */}
            <div className="bg-white rounded-2xl p-6 border border-landing-outline-variant/20">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5 text-landing-primary" />
                <h3 className="text-lg font-bold">Any MCP Client</h3>
              </div>
              <p className="text-landing-secondary mb-4">
                Boardy implements the standard Model Context Protocol. Connect any MCP-compatible client using these endpoints:
              </p>
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between bg-landing-surface-container-low rounded-lg p-3">
                  <span className="text-sm font-medium">MCP Server</span>
                  <code className="text-xs text-landing-primary">https://boardy.alivik.io/mcp</code>
                </div>
                <div className="flex items-center justify-between bg-landing-surface-container-low rounded-lg p-3">
                  <span className="text-sm font-medium">OAuth Discovery</span>
                  <code className="text-xs text-landing-primary">/.well-known/oauth-authorization-server</code>
                </div>
                <div className="flex items-center justify-between bg-landing-surface-container-low rounded-lg p-3">
                  <span className="text-sm font-medium">Resource Metadata</span>
                  <code className="text-xs text-landing-primary">/.well-known/oauth-protected-resource</code>
                </div>
              </div>
              <p className="text-sm text-landing-secondary">
                Authentication uses OAuth 2.1 with PKCE. See the{" "}
                <a href="https://github.com/alivik/boardy" className="text-landing-primary hover:underline">
                  GitHub repository
                </a>{" "}
                for implementation details.
              </p>
            </div>
          </div>
        </section>

        {/* Available Tools */}
        <section id="available-tools" className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-landing-primary-container/30 flex items-center justify-center">
              <Terminal className="w-5 h-5 text-landing-primary" />
            </div>
            <h2 className="text-2xl font-bold">Available Tools</h2>
          </div>

          <p className="text-landing-secondary mb-6">
            When connected, your AI assistant has access to the following tools:
          </p>

          <div className="grid gap-4">
            {[
              {
                name: "get_board",
                description: "Get the full board with all columns and cards",
                hint: "Read-only",
              },
              {
                name: "list_boards",
                description: "List all boards you have access to",
                hint: "Read-only",
              },
              {
                name: "create_card",
                description: "Create a new card in a specific column",
                hint: "Creates content",
              },
              {
                name: "update_card",
                description: "Update card title, description, or priority",
                hint: "Modifies content",
              },
              {
                name: "move_card",
                description: "Move a card to a different column or position",
                hint: "Modifies content",
              },
              {
                name: "add_comment",
                description: "Add a comment to a card",
                hint: "Creates content",
              },
            ].map((tool) => (
              <div
                key={tool.name}
                className="bg-white rounded-xl p-4 border border-landing-outline-variant/20 flex items-start justify-between"
              >
                <div>
                  <code className="text-landing-primary font-mono font-bold">
                    {tool.name}
                  </code>
                  <p className="text-sm text-landing-secondary mt-1">
                    {tool.description}
                  </p>
                </div>
                <span className="text-xs px-2 py-1 rounded-full bg-landing-surface-container-low text-landing-secondary">
                  {tool.hint}
                </span>
              </div>
            ))}
          </div>

          <p className="text-sm text-landing-secondary mt-6">
            All actions performed by AI assistants are marked with "created by claude"
            in the card history for full transparency.
          </p>
        </section>

        {/* Security */}
        <section id="security" className="mb-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-landing-primary-container/30 flex items-center justify-center">
              <Shield className="w-5 h-5 text-landing-primary" />
            </div>
            <h2 className="text-2xl font-bold">Security & Privacy</h2>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-landing-outline-variant/20">
            <ul className="space-y-4 text-landing-secondary">
              <li className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <strong className="text-landing-on-background">OAuth 2.1 with PKCE</strong>
                  <p className="text-sm">
                    Secure authorization flow - your credentials are never shared with AI clients.
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <strong className="text-landing-on-background">Board-scoped tokens</strong>
                  <p className="text-sm">
                    Each MCP connection is limited to a single board. AI assistants cannot
                    access other boards without explicit authorization.
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <strong className="text-landing-on-background">EU data residency</strong>
                  <p className="text-sm">
                    All data is stored in Germany (EU). We comply with GDPR requirements.
                  </p>
                </div>
              </li>
              <li className="flex gap-3">
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Check className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <strong className="text-landing-on-background">Revocable access</strong>
                  <p className="text-sm">
                    You can revoke AI access at any time from your board settings.
                  </p>
                </div>
              </li>
            </ul>
          </div>

          <p className="text-sm text-landing-secondary mt-6">
            Read our{" "}
            <Link to="/privacy" className="text-landing-primary hover:underline">
              Privacy Policy
            </Link>{" "}
            for complete details on how we handle your data.
          </p>
        </section>

        {/* Help */}
        <section className="bg-landing-primary-container/20 rounded-2xl p-8 text-center">
          <h2 className="text-xl font-bold mb-2">Need help?</h2>
          <p className="text-landing-secondary mb-4">
            Have questions or run into issues? We're here to help.
          </p>
          <a
            href="mailto:contact@alivik.io"
            className="inline-flex items-center gap-2 bg-landing-primary text-white px-6 py-3 rounded-full font-bold hover:shadow-lg transition-all"
          >
            Contact Support
          </a>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full bg-white border-t border-landing-outline-variant/10 mt-16">
        <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-12">
          <div className="flex items-center gap-2 mb-8 md:mb-0">
            <div className="w-6 h-6 bg-landing-primary rounded flex items-center justify-center">
              <LayoutDashboard className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="font-headline italic text-lg font-bold">Boardy</div>
          </div>
          <div className="text-xs font-medium text-landing-secondary/60">
            © {new Date().getFullYear()} boardy.ALIVIK. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
