export default function TermsPage() {
  return (
    <div className="max-w-[700px] w-full bg-manifest-paper border border-steel-blue/30 rounded-sm p-8 text-on-surface text-sm leading-relaxed max-h-[90vh] overflow-y-auto">
      <h1 className="font-headline-lg text-headline-lg text-primary mb-6">Terms of Service</h1>
      <p className="text-on-surface-variant text-[11px] mb-4">Last updated: August 2026</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">1. Service Description</h2>
      <p>Landed Cost Ledger ("the Service") provides estimated US import duty calculations based on publicly available tariff data. The Service is provided for informational purposes only.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">2. Disclaimer</h2>
      <p>The calculations provided are <strong>estimates only</strong> and do not constitute legal, customs brokerage, or financial advice. You should consult a licensed customs broker for official filings with US Customs and Border Protection (CBP).</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">3. Accuracy</h2>
      <p>While we strive to maintain accurate tariff data, rates may change without notice. The Service may not reflect the latest Federal Register amendments, executive orders, or USTR notices.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">4. User Accounts</h2>
      <p>You may sign in using Google or GitHub OAuth. We access only your name and email address. You are responsible for maintaining the security of your account.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">5. Acceptable Use</h2>
      <p>You agree not to: abuse the API with excessive requests, attempt to circumvent rate limits, reverse-engineer the service, or use it for unlawful purposes.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">6. Limitation of Liability</h2>
      <p>The Service is provided "as is" without warranty. We are not liable for any damages arising from reliance on the calculations provided.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">7. Changes</h2>
      <p>We may modify these terms at any time. Continued use of the Service constitutes acceptance of the updated terms.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">8. Contact</h2>
      <p>Questions about these terms: <a href="mailto:honasas1101@gmail.com" className="text-brass hover:underline">honasas1101@gmail.com</a></p>
    </div>
  );
}
