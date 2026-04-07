import { Link } from "react-router-dom";
import { LayoutDashboard, ArrowLeft } from "lucide-react";

export default function ImprintPage() {
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
      <main className="max-w-3xl mx-auto px-6 py-16">
        <h1 className="font-headline italic text-4xl md:text-5xl mb-8">
          Impressum
        </h1>
        <p className="text-landing-secondary mb-8">
          Legal Disclosure according to TMG §5
        </p>

        <div className="prose prose-lg max-w-none text-landing-on-background">
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Service Provider</h2>
            <div className="text-landing-secondary">
              <p className="font-semibold text-lg">boardy.ALIVIK</p>
              <p>Represented by: Michael Bendus</p>
            </div>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Address</h2>
            <p className="text-landing-secondary">
              Dockenhudener Strasse 23
              <br />
              22587 Hamburg
              <br />
              Germany
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Contact</h2>
            <p className="text-landing-secondary">
              Email:{" "}
              <a
                href="mailto:contact@alivik.io"
                className="text-landing-primary hover:underline"
              >
                contact@alivik.io
              </a>
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">VAT Identification Number</h2>
            <p className="text-landing-secondary">
              VAT ID according to §27a UStG: DE369941265
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">
              Responsible for Content
            </h2>
            <p className="text-landing-secondary">
              Responsible for content according to §18 Abs. 2 MStV:
              <br />
              Michael Bendus
              <br />
              Dockenhudener Strasse 23
              <br />
              22587 Hamburg
              <br />
              Germany
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">EU Dispute Resolution</h2>
            <p className="text-landing-secondary mb-4">
              The European Commission provides a platform for online dispute
              resolution (OS):{" "}
              <a
                href="https://ec.europa.eu/consumers/odr/"
                className="text-landing-primary hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                https://ec.europa.eu/consumers/odr/
              </a>
            </p>
            <p className="text-landing-secondary">
              We are not willing or obliged to participate in dispute resolution
              proceedings before a consumer arbitration board.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Liability for Content</h2>
            <p className="text-landing-secondary">
              As a service provider, we are responsible for our own content on
              these pages according to general laws pursuant to §7 Abs.1 TMG.
              According to §§8 to 10 TMG, however, we are not obligated as a
              service provider to monitor transmitted or stored third-party
              information or to investigate circumstances that indicate illegal
              activity. Obligations to remove or block the use of information
              under general law remain unaffected. However, liability in this
              regard is only possible from the point in time at which knowledge
              of a specific infringement of the law is obtained. Upon becoming
              aware of corresponding infringements, we will remove this content
              immediately.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Liability for Links</h2>
            <p className="text-landing-secondary">
              Our offer contains links to external third-party websites over
              whose content we have no influence. Therefore, we cannot assume
              any liability for this external content. The respective provider
              or operator of the pages is always responsible for the content of
              the linked pages. The linked pages were checked for possible legal
              violations at the time of linking. Illegal content was not
              recognizable at the time of linking. However, permanent monitoring
              of the content of the linked pages is not reasonable without
              concrete evidence of an infringement. Upon becoming aware of legal
              violations, we will remove such links immediately.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">Copyright</h2>
            <p className="text-landing-secondary">
              The content and works created by the site operators on these pages
              are subject to German copyright law. Duplication, processing,
              distribution, or any form of commercialization of such material
              beyond the scope of the copyright law requires the prior written
              consent of its respective author or creator. Downloads and copies
              of this site are only permitted for private, non-commercial use.
              Insofar as the content on this site was not created by the
              operator, the copyrights of third parties are respected. In
              particular, third-party content is marked as such. Should you
              nevertheless become aware of a copyright infringement, please
              inform us accordingly. Upon becoming aware of legal violations, we
              will remove such content immediately.
            </p>
          </section>
        </div>
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
          <div className="text-xs font-medium text-landing-secondary/60">
            © {new Date().getFullYear()} boardy.ALIVIK. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
