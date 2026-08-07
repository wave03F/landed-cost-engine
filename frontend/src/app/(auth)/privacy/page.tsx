export default function PrivacyPage() {
  return (
    <div className="max-w-[700px] w-full bg-manifest-paper border border-steel-blue/30 rounded-sm p-8 text-on-surface text-sm leading-relaxed max-h-[90vh] overflow-y-auto">
      <h1 className="font-headline-lg text-headline-lg text-primary mb-6">Privacy Policy</h1>
      <p className="text-on-surface-variant text-[11px] mb-4">Last updated: August 2026</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">1. Data We Collect</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li><strong>Account data:</strong> Name, email address, profile picture (from Google/GitHub OAuth)</li>
        <li><strong>Calculation data:</strong> HTS codes, values, dates, and results you submit</li>
        <li><strong>Usage data:</strong> Timestamps, pages visited (no third-party tracking)</li>
      </ul>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">2. How We Use Your Data</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>Provide and improve the calculation service</li>
        <li>Maintain your calculation history (audit trail)</li>
        <li>Enforce rate limits and prevent abuse</li>
      </ul>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">3. Data We Do NOT Collect</h2>
      <ul className="list-disc pl-5 space-y-1">
        <li>Passwords (we use OAuth only)</li>
        <li>Payment/financial information</li>
        <li>Location data</li>
        <li>Cookies for advertising</li>
      </ul>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">4. Data Storage</h2>
      <p>Data is stored on Render.com servers (US region). Calculation logs are retained indefinitely for audit purposes. You may request deletion of your account and associated data.</p>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">5. Data Sharing</h2>
      <p>We do not sell, rent, or share your personal data with third parties. Data is only shared with:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li>Infrastructure providers (Render, Vercel) for service operation</li>
        <li>OAuth providers (Google, GitHub) for authentication only</li>
      </ul>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">6. Your Rights</h2>
      <p>You have the right to:</p>
      <ul className="list-disc pl-5 space-y-1">
        <li>Access your data</li>
        <li>Request correction of inaccurate data</li>
        <li>Request deletion of your account</li>
        <li>Export your calculation history</li>
      </ul>

      <h2 className="font-title-md text-title-md text-primary mt-6 mb-2">7. Contact</h2>
      <p>Data protection inquiries: <a href="mailto:honasas1101@gmail.com" className="text-brass hover:underline">honasas1101@gmail.com</a></p>
    </div>
  );
}
