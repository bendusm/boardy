import { Link } from "react-router-dom";
import { LayoutDashboard, ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
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
          Privacy Policy
        </h1>
        <p className="text-landing-secondary mb-8">
          Last updated: April 7, 2026
        </p>

        <div className="prose prose-lg max-w-none text-landing-on-background">
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">1. Data Controller</h2>
            <p className="text-landing-secondary mb-4">
              The data controller responsible for your personal data is:
            </p>
            <div className="text-landing-secondary mb-4 pl-4 border-l-2 border-landing-outline-variant/30">
              <p className="font-semibold">boardy.ALIVIK</p>
              <p>Michael Bendus</p>
              <p>Dockenhudener Strasse 23</p>
              <p>22587 Hamburg</p>
              <p>Germany</p>
              <p className="mt-2">Email: contact@alivik.io</p>
              <p>VAT ID: DE369941265</p>
            </div>
            <p className="text-landing-secondary">
              If you have any questions about this Privacy Policy or our data
              practices, please contact us at the email address above.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">2. Data We Collect</h2>
            <p className="text-landing-secondary mb-4">
              We collect and process the following personal data:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                <strong>Account Information:</strong> Email address (required
                for registration)
              </li>
              <li>
                <strong>Authentication Data:</strong> Hashed passwords (we never
                store plaintext passwords)
              </li>
              <li>
                <strong>User Content:</strong> Boards, columns, cards, comments,
                and attachments you create
              </li>
              <li>
                <strong>Usage Data:</strong> Timestamps of account creation and
                last activity
              </li>
              <li>
                <strong>Technical Data:</strong> IP address (for rate limiting
                and security only)
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">
              3. Legal Basis for Processing
            </h2>
            <p className="text-landing-secondary mb-4">
              We process your personal data based on the following legal
              grounds:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                <strong>Contract:</strong> Processing necessary to provide the
                Boardy service you requested
              </li>
              <li>
                <strong>Consent:</strong> Where you have given explicit consent
                (e.g., accepting our Terms of Service)
              </li>
              <li>
                <strong>Legitimate Interests:</strong> For security purposes,
                fraud prevention, and service improvement
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">4. Data Retention</h2>
            <p className="text-landing-secondary mb-4">
              We retain your personal data for as long as your account is
              active. When you delete your account:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>All your personal data is permanently deleted</li>
              <li>All boards you own are deleted along with their content</li>
              <li>This process is irreversible</li>
            </ul>
            <p className="text-landing-secondary mt-4">
              We may retain anonymized, aggregated data for analytics purposes.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">5. Third-Party Services</h2>
            <p className="text-landing-secondary mb-4">
              We use the following third-party services:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                <strong>Cloudflare:</strong> For DDoS protection, CDN, and SSL
                certificates (Privacy Policy:{" "}
                <a
                  href="https://www.cloudflare.com/privacypolicy/"
                  className="text-landing-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  cloudflare.com/privacypolicy
                </a>
                )
              </li>
              <li>
                <strong>Cloudflare R2:</strong> For file storage (attachments)
              </li>
              <li>
                <strong>Hetzner:</strong> For server hosting in the EU (Germany)
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">6. Your Rights (GDPR)</h2>
            <p className="text-landing-secondary mb-4">
              Under the General Data Protection Regulation (GDPR), you have the
              following rights:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                <strong>Right of Access:</strong> Request a copy of your
                personal data
              </li>
              <li>
                <strong>Right to Rectification:</strong> Request correction of
                inaccurate data
              </li>
              <li>
                <strong>Right to Erasure:</strong> Request deletion of your data
                ("right to be forgotten")
              </li>
              <li>
                <strong>Right to Data Portability:</strong> Export your data in
                a machine-readable format
              </li>
              <li>
                <strong>Right to Object:</strong> Object to processing based on
                legitimate interests
              </li>
              <li>
                <strong>Right to Restrict Processing:</strong> Request
                limitation of processing
              </li>
            </ul>
            <p className="text-landing-secondary mt-4">
              To exercise these rights, visit your{" "}
              <Link
                to="/account"
                className="text-landing-primary hover:underline"
              >
                Account Settings
              </Link>{" "}
              or contact us at contact@alivik.io.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">7. Cookies</h2>
            <p className="text-landing-secondary mb-4">
              We use only essential cookies required for the service to
              function:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                <strong>Session Cookie:</strong> Maintains your login session
                (httpOnly, secure)
              </li>
              <li>
                <strong>CSRF Token:</strong> Protects against cross-site request
                forgery attacks
              </li>
            </ul>
            <p className="text-landing-secondary mt-4">
              We do not use tracking cookies, analytics cookies, or advertising
              cookies.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">8. Data Security</h2>
            <p className="text-landing-secondary mb-4">
              We implement appropriate technical and organizational measures to
              protect your data:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>HTTPS encryption for all data in transit</li>
              <li>Bcrypt hashing for passwords</li>
              <li>Rate limiting to prevent brute-force attacks</li>
              <li>CSRF protection on all state-changing requests</li>
              <li>OAuth 2.1 with PKCE for third-party integrations</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">9. International Transfers</h2>
            <p className="text-landing-secondary">
              Your data is stored and processed in the European Union (Germany).
              We do not transfer your personal data outside the EU/EEA.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">10. Complaints</h2>
            <p className="text-landing-secondary">
              If you believe we have violated your data protection rights, you
              have the right to lodge a complaint with a supervisory authority.
              In Germany, this is the Bundesbeauftragte für den Datenschutz und
              die Informationsfreiheit (BfDI).
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">11. Changes to This Policy</h2>
            <p className="text-landing-secondary">
              We may update this Privacy Policy from time to time. We will
              notify you of any material changes by posting the new Privacy
              Policy on this page and updating the "Last updated" date.
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
