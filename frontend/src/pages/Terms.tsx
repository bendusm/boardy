import { Link } from "react-router-dom";
import { LayoutDashboard, ArrowLeft } from "lucide-react";

export default function TermsPage() {
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
          Terms of Service
        </h1>
        <p className="text-landing-secondary mb-8">
          Last updated: April 7, 2026
        </p>

        <div className="prose prose-lg max-w-none text-landing-on-background">
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">1. Acceptance of Terms</h2>
            <p className="text-landing-secondary">
              By creating an account or using Boardy ("the Service"), you agree
              to be bound by these Terms of Service ("Terms"). If you do not
              agree to these Terms, do not use the Service.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">2. Description of Service</h2>
            <p className="text-landing-secondary">
              Boardy is a Kanban board application with AI integration through
              the Model Context Protocol (MCP). The Service allows you to create
              boards, manage tasks, and connect AI assistants to automate task
              management.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">3. Account Registration</h2>
            <p className="text-landing-secondary mb-4">To use the Service, you must:</p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>Provide a valid email address</li>
              <li>Create a secure password (minimum 8 characters)</li>
              <li>Be at least 16 years of age</li>
              <li>Accept these Terms and our Privacy Policy</li>
            </ul>
            <p className="text-landing-secondary mt-4">
              You are responsible for maintaining the security of your account
              and password. Boardy cannot and will not be liable for any loss or
              damage from your failure to comply with this security obligation.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">4. User Content</h2>
            <p className="text-landing-secondary mb-4">
              "User Content" means any content you create, upload, or share
              through the Service, including boards, cards, comments, and
              attachments.
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>You retain ownership of your User Content</li>
              <li>
                You grant Boardy a license to store and display your User
                Content solely to provide the Service
              </li>
              <li>
                You are responsible for ensuring your User Content does not
                violate any laws or third-party rights
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">5. AI Integration (MCP)</h2>
            <p className="text-landing-secondary mb-4">
              The Service allows integration with AI assistants via MCP. When
              you connect an AI assistant:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>
                The AI assistant will have access to your board data (as
                authorized by you)
              </li>
              <li>
                Actions taken by the AI are marked as "created by claude" in the
                system
              </li>
              <li>
                You are responsible for reviewing and approving AI-generated
                content
              </li>
              <li>
                We are not responsible for actions taken by third-party AI
                assistants
              </li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">6. Prohibited Uses</h2>
            <p className="text-landing-secondary mb-4">You agree not to:</p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>Use the Service for any illegal purpose</li>
              <li>Upload malicious code or attempt to hack the Service</li>
              <li>
                Interfere with or disrupt the Service or servers connected to it
              </li>
              <li>
                Attempt to gain unauthorized access to other users' accounts
              </li>
              <li>Use the Service to send spam or unsolicited communications</li>
              <li>Violate any applicable laws or regulations</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">7. Service Availability</h2>
            <p className="text-landing-secondary">
              We strive to maintain high availability but do not guarantee
              uninterrupted access to the Service. We may suspend or terminate
              the Service for maintenance, updates, or other reasons. We will
              make reasonable efforts to notify users of planned downtime.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">8. Data and Privacy</h2>
            <p className="text-landing-secondary">
              Your use of the Service is also governed by our{" "}
              <Link
                to="/privacy"
                className="text-landing-primary hover:underline"
              >
                Privacy Policy
              </Link>
              , which describes how we collect, use, and protect your personal
              data.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">9. Account Termination</h2>
            <p className="text-landing-secondary mb-4">
              You may delete your account at any time through the Account
              Settings page. Upon deletion:
            </p>
            <ul className="list-disc pl-6 text-landing-secondary space-y-2">
              <li>All your personal data will be permanently deleted</li>
              <li>All boards you own will be deleted</li>
              <li>This action cannot be undone</li>
            </ul>
            <p className="text-landing-secondary mt-4">
              We reserve the right to suspend or terminate accounts that violate
              these Terms.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">10. Limitation of Liability</h2>
            <p className="text-landing-secondary">
              To the maximum extent permitted by law, Boardy shall not be liable
              for any indirect, incidental, special, consequential, or punitive
              damages, including loss of data, profits, or business
              opportunities, arising from your use of the Service.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">11. Disclaimer of Warranties</h2>
            <p className="text-landing-secondary">
              The Service is provided "as is" and "as available" without
              warranties of any kind, either express or implied, including but
              not limited to implied warranties of merchantability, fitness for
              a particular purpose, or non-infringement.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">12. Governing Law</h2>
            <p className="text-landing-secondary">
              These Terms shall be governed by and construed in accordance with
              the laws of Germany, without regard to its conflict of law
              provisions. Any disputes arising from these Terms shall be subject
              to the exclusive jurisdiction of the courts in Germany.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">13. Changes to Terms</h2>
            <p className="text-landing-secondary">
              We may modify these Terms at any time. We will notify you of
              material changes by posting the updated Terms on the Service and
              updating the "Last updated" date. Your continued use of the
              Service after such changes constitutes acceptance of the new
              Terms.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-4">14. Contact</h2>
            <p className="text-landing-secondary">
              If you have questions about these Terms, please contact us at:
              support@boardy.app
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
            © 2024 Boardy. Built for builders.
          </div>
        </div>
      </footer>
    </div>
  );
}
