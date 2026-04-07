import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  Bot,
  PlayCircle,
  ClipboardList,
  Link2,
  Zap,
  Sparkles,
  GitCommit,
  Terminal,
  Users,
  Heart,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-landing-background text-landing-on-background font-body">
      {/* Header */}
      <header className="w-full border-b border-landing-outline-variant/20 bg-white/70 backdrop-blur-md sticky top-0 z-50">
        <nav className="flex justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-landing-primary rounded-lg flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div className="font-headline italic text-2xl font-bold text-landing-on-background">
              Boardy
            </div>
          </div>
          <div className="hidden md:flex items-center space-x-10">
            <a
              className="text-landing-on-background font-medium text-sm hover:text-landing-primary transition-colors"
              href="#features"
            >
              Features
            </a>
            <a
              className="text-landing-secondary font-medium text-sm hover:text-landing-primary transition-colors"
              href="#process"
            >
              Process
            </a>
            <a
              className="text-landing-secondary font-medium text-sm hover:text-landing-primary transition-colors"
              href="#"
            >
              Documentation
            </a>
          </div>
          <div className="flex items-center gap-4">
            <Link
              to="/login"
              className="text-landing-secondary font-medium text-sm px-4 py-2 hover:text-landing-primary hidden sm:block"
            >
              Log in
            </Link>
            <Link
              to="/register"
              className="bg-landing-primary text-white px-5 py-2.5 rounded-full text-sm font-semibold hover:shadow-lg hover:shadow-landing-primary/20 transition-all"
            >
              Start for free
            </Link>
          </div>
        </nav>
      </header>

      <main>
        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-6 md:px-12 pt-20 pb-32 grid grid-cols-1 lg:grid-cols-12 gap-16 items-center relative overflow-hidden">
          <div className="lg:col-span-7 z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-landing-primary-fixed text-landing-on-primary-fixed-variant text-xs font-bold mb-6 tracking-wide uppercase">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-landing-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-landing-primary"></span>
              </span>
              New: MCP Integration v2
            </div>
            <h1 className="font-headline italic text-6xl md:text-7xl lg:text-[5.5rem] leading-[1.05] tracking-tight mb-8">
              Your AI manages the board.{" "}
              <span className="text-landing-primary block not-italic font-body font-bold text-5xl md:text-6xl mt-2">
                You just ship.
              </span>
            </h1>
            <p className="text-landing-secondary text-lg md:text-xl leading-relaxed mb-10 max-w-xl">
              Connect Boardy to your favorite AI assistant in one URL. It
              creates cards, tracks progress, and closes tasks automatically as
              you work.
            </p>
            <div className="flex flex-wrap gap-4 items-center">
              <Link
                to="/register"
                className="bg-landing-primary text-white px-8 py-4 rounded-full text-lg font-bold hover:scale-[1.02] active:scale-[0.98] transition-all shadow-xl shadow-landing-primary/20"
              >
                Get started free
              </Link>
              <button className="flex items-center gap-2 px-6 py-4 rounded-full border border-landing-outline-variant hover:bg-landing-surface-container-low transition-all font-semibold text-landing-secondary">
                <PlayCircle className="w-5 h-5 text-landing-primary" />
                Watch demo
              </button>
            </div>
          </div>
          <div className="lg:col-span-5 relative">
            <div className="absolute -top-12 -right-12 w-64 h-64 bg-landing-primary-container/10 rounded-full blur-3xl"></div>
            <div className="relative bg-white rounded-[2rem] p-6 shadow-startup border border-landing-outline-variant/10 rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="w-full h-full border border-landing-outline-variant/20 rounded-xl flex flex-col p-6 bg-landing-background/30">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-10 h-10 rounded-full bg-landing-primary-container/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-landing-primary" />
                  </div>
                  <div className="space-y-1.5">
                    <div className="w-24 h-2 bg-landing-secondary/20 rounded-full"></div>
                    <div className="w-16 h-1.5 bg-landing-secondary/10 rounded-full"></div>
                  </div>
                </div>
                <div className="w-full space-y-4">
                  <div className="h-16 w-full bg-white rounded-xl shadow-sm border border-landing-outline-variant/20 p-4 transform -translate-x-4">
                    <div className="flex gap-3">
                      <div className="w-2 h-2 rounded-full bg-green-500"></div>
                      <div className="space-y-2 flex-1">
                        <div className="w-1/3 h-2 bg-landing-outline-variant/40 rounded"></div>
                        <div className="w-full h-1.5 bg-landing-surface-variant/40 rounded"></div>
                      </div>
                    </div>
                  </div>
                  <div className="h-20 w-full bg-white rounded-xl shadow-md border-l-4 border-l-landing-primary p-4 z-10 scale-105">
                    <div className="flex gap-3">
                      <div className="w-2 h-2 rounded-full bg-landing-primary"></div>
                      <div className="space-y-2 flex-1">
                        <div className="w-1/2 h-2 bg-landing-primary/20 rounded"></div>
                        <div className="w-3/4 h-1.5 bg-landing-surface-variant/40 rounded"></div>
                      </div>
                    </div>
                  </div>
                  <div className="h-16 w-full bg-white rounded-xl shadow-sm border border-landing-outline-variant/20 p-4 transform translate-x-4">
                    <div className="flex gap-3">
                      <div className="w-2 h-2 rounded-full bg-gray-300"></div>
                      <div className="space-y-2 flex-1">
                        <div className="w-1/4 h-2 bg-landing-outline-variant/40 rounded"></div>
                        <div className="w-2/3 h-1.5 bg-landing-surface-variant/40 rounded"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="process" className="py-32 bg-white relative">
          <div className="max-w-7xl mx-auto px-6 md:px-12">
            <div className="text-center mb-20">
              <h2 className="font-headline italic text-4xl md:text-5xl mb-4">
                Ship faster, manage less.
              </h2>
              <p className="text-landing-secondary max-w-xl mx-auto">
                Three simple steps to automate your project management workflow
                with AI.
              </p>
            </div>
            <div className="relative grid grid-cols-1 md:grid-cols-3 gap-12 lg:gap-24">
              <div className="hidden md:block absolute top-12 left-[15%] right-[15%] h-0.5 border-t-2 border-dashed border-landing-outline-variant/30"></div>

              <div className="relative flex flex-col items-center text-center group">
                <div className="w-24 h-24 rounded-2xl bg-landing-surface-container-low flex items-center justify-center mb-8 shadow-startup group-hover:bg-landing-primary transition-all duration-300 group-hover:-translate-y-2">
                  <ClipboardList className="w-10 h-10 text-landing-primary group-hover:text-white" />
                </div>
                <div className="absolute -top-4 right-1/2 translate-x-12 bg-white px-2 py-1 border border-landing-outline-variant rounded-full text-[10px] font-bold text-landing-primary uppercase">
                  Step 01
                </div>
                <h3 className="text-xl font-bold mb-4">Setup Board</h3>
                <p className="text-landing-secondary leading-relaxed text-sm">
                  Create your workspace in seconds. Define your columns and
                  invite your team.
                </p>
              </div>

              <div className="relative flex flex-col items-center text-center group">
                <div className="w-24 h-24 rounded-2xl bg-landing-surface-container-low flex items-center justify-center mb-8 shadow-startup group-hover:bg-landing-primary transition-all duration-300 group-hover:-translate-y-2">
                  <Link2 className="w-10 h-10 text-landing-primary group-hover:text-white" />
                </div>
                <div className="absolute -top-4 right-1/2 translate-x-12 bg-white px-2 py-1 border border-landing-outline-variant rounded-full text-[10px] font-bold text-landing-primary uppercase">
                  Step 02
                </div>
                <h3 className="text-xl font-bold mb-4">Connect AI</h3>
                <p className="text-landing-secondary leading-relaxed text-sm">
                  Paste the MCP URL into your AI assistant settings. Secure,
                  private, and instant.
                </p>
              </div>

              <div className="relative flex flex-col items-center text-center group">
                <div className="w-24 h-24 rounded-2xl bg-landing-surface-container-low flex items-center justify-center mb-8 shadow-startup group-hover:bg-landing-primary transition-all duration-300 group-hover:-translate-y-2">
                  <Zap className="w-10 h-10 text-landing-primary group-hover:text-white" />
                </div>
                <div className="absolute -top-4 right-1/2 translate-x-12 bg-white px-2 py-1 border border-landing-outline-variant rounded-full text-[10px] font-bold text-landing-primary uppercase">
                  Step 03
                </div>
                <h3 className="text-xl font-bold mb-4">Auto-Update</h3>
                <p className="text-landing-secondary leading-relaxed text-sm">
                  Your AI assistant tracks progress and closes cards as you push
                  code. Pure magic.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid */}
        <section id="features" className="py-32 max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-8 rounded-3xl shadow-startup border border-landing-outline-variant/10 hover:shadow-startup-hover hover:border-landing-primary/20 transition-all flex flex-col h-full min-h-[280px]">
              <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center mb-12">
                <Sparkles className="w-6 h-6 text-landing-primary" />
              </div>
              <h4 className="text-lg font-bold leading-tight mb-3">
                Auto-Generated Cards
              </h4>
              <p className="text-sm text-landing-secondary">
                Turns your natural language conversations into actionable
                project tasks automatically.
              </p>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-startup border border-landing-outline-variant/10 hover:shadow-startup-hover hover:border-landing-primary/20 transition-all flex flex-col h-full min-h-[280px] lg:translate-y-8">
              <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center mb-12">
                <GitCommit className="w-6 h-6 text-landing-primary" />
              </div>
              <h4 className="text-lg font-bold leading-tight mb-3">
                Commit Sync
              </h4>
              <p className="text-sm text-landing-secondary">
                Tasks are updated or closed as soon as your git commits are
                detected. No manual clicking.
              </p>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-startup border border-landing-outline-variant/10 hover:shadow-startup-hover hover:border-landing-primary/20 transition-all flex flex-col h-full min-h-[280px]">
              <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center mb-12">
                <Terminal className="w-6 h-6 text-landing-primary" />
              </div>
              <h4 className="text-lg font-bold leading-tight mb-3">
                Universal AI Support
              </h4>
              <p className="text-sm text-landing-secondary">
                Works seamlessly in your favorite AI desktop apps, IDE
                extensions, and web-based AI tools.
              </p>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-startup border border-landing-outline-variant/10 hover:shadow-startup-hover hover:border-landing-primary/20 transition-all flex flex-col h-full min-h-[280px] lg:translate-y-8">
              <div className="w-12 h-12 rounded-xl bg-orange-50 flex items-center justify-center mb-12">
                <Users className="w-6 h-6 text-landing-primary" />
              </div>
              <h4 className="text-lg font-bold leading-tight mb-3">
                Community First
              </h4>
              <p className="text-sm text-landing-secondary">
                Built for the developer community. No complex tiers, just a
                powerful tool to help you ship.
              </p>
            </div>
          </div>
        </section>

        {/* Visual Break */}
        <section className="max-w-7xl mx-auto px-6 md:px-12 pb-32">
          <div className="rounded-[3rem] overflow-hidden aspect-[21/9] relative group shadow-2xl bg-gradient-to-br from-landing-primary to-landing-primary-container">
            <div className="absolute inset-0 bg-landing-primary/20 mix-blend-multiply"></div>
            <div className="absolute inset-0 flex items-center justify-center px-6">
              <div className="bg-white/95 backdrop-blur-md px-8 md:px-16 py-8 md:py-10 rounded-3xl shadow-2xl text-center max-w-2xl transform group-hover:scale-105 transition-transform duration-700">
                <span className="font-headline italic text-3xl md:text-5xl block mb-4">
                  Focus on the code.
                </span>
                <p className="text-landing-secondary font-medium uppercase tracking-widest text-xs">
                  Let your AI assistant handle the rest.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-landing-primary-container/20 py-32 text-center relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(circle,_#dbc1b9_1.5px,_transparent_1.5px)] bg-[length:24px_24px] opacity-20"></div>
          <div className="max-w-3xl mx-auto px-6 relative z-10">
            <h2 className="font-headline italic text-5xl md:text-6xl mb-12">
              Ready to automate your board?
            </h2>
            <div className="flex flex-col sm:flex-row justify-center items-center gap-6">
              <Link
                to="/register"
                className="w-full sm:w-auto bg-landing-primary text-white px-12 py-5 rounded-full text-lg font-bold hover:shadow-2xl hover:shadow-landing-primary/30 transition-all hover:scale-105"
              >
                Get started free
              </Link>
              <button className="w-full sm:w-auto flex items-center justify-center gap-2 text-landing-on-background bg-white px-10 py-5 rounded-full border border-landing-outline-variant hover:border-landing-primary/50 transition-all font-bold">
                Support on Ko-fi{" "}
                <Heart className="w-5 h-5 text-landing-primary fill-landing-primary" />
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full bg-white border-t border-landing-outline-variant/10">
        <div className="flex flex-col md:flex-row justify-between items-center max-w-7xl mx-auto px-6 md:px-12 py-12">
          <div className="flex items-center gap-2 mb-8 md:mb-0">
            <div className="w-6 h-6 bg-landing-primary rounded flex items-center justify-center">
              <LayoutDashboard className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="font-headline italic text-lg font-bold">Boardy</div>
          </div>
          <div className="text-xs font-medium text-landing-secondary/60 mb-8 md:mb-0">
            © 2024 Boardy. Built for builders.
          </div>
          <div className="flex flex-wrap justify-center gap-8">
            <Link
              className="text-xs font-bold text-landing-secondary hover:text-landing-primary transition-all"
              to="/privacy"
            >
              Privacy
            </Link>
            <Link
              className="text-xs font-bold text-landing-secondary hover:text-landing-primary transition-all"
              to="/terms"
            >
              Terms
            </Link>
            <a
              className="text-xs font-bold text-landing-secondary hover:text-landing-primary transition-all"
              href="#"
            >
              Github
            </a>
            <a
              className="text-xs font-bold text-landing-secondary hover:text-landing-primary transition-all"
              href="#"
            >
              Donate
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
