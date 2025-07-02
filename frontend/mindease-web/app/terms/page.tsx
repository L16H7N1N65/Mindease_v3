// app/terms/page.tsx
export const metadata = {
  title: "Terms of Service",
};

export default function TermsPage() {
  return (
    <main className="prose max-w-3xl mx-auto py-16 px-4">
      <h1>MindEase Terms of Service</h1>
      <p>Last Updated: April 2025</p>
      <p>
        These Terms of Service (the “Terms”) govern your access to and use of
        MindEase’s websites and services (“MindEase,” “we,” or “us”). By
        accessing or using any MindEase service, you agree to be bound by these
        Terms.
      </p>

      <h2>1. Who May Use MindEase</h2>
      <p>
        You must be at least 16 years old to use our Services. If you’re under
        the age of majority in your country (in France, 18), a parent or legal
        guardian must agree to these Terms on your behalf.
      </p>

      <h2>2. Your Account</h2>
      <p>
        To access certain features, you’ll need to register for an account. You
        agree to provide accurate information, keep it up to date, and secure
        your password. You’re responsible for all activity under your account
        and must notify us immediately at <a href="mailto:support@mindease.com">support@mindease.com</a> if you suspect unauthorized use.
      </p>

      <h2>3. Subscriptions & Payments</h2>
      <p>
        MindEase offers both free and paid subscription tiers. Paid
        subscriptions (MindEase Premium) renew automatically until canceled.
        You authorize us to charge your chosen payment method at each renewal,
        including VAT or other taxes. To avoid renewal, cancel at least 24 hours
        before your period ends via your MindEase profile.
      </p>

      <h2>4. Trial & Promotional Offers</h2>
      <p>
        Trial periods or other promotional pricing apply only to new
        subscribers and convert automatically to paid subscriptions unless
        canceled beforehand. Full terms of each promotion will be disclosed
        where offered.
      </p>

      <h2>5. User Content & Conduct</h2>
      <p>
        You retain ownership of any content you post (messages, journal
        entries, etc.), but grant MindEase a worldwide, royalty‑free license to
        use it in connection with providing the Services. You agree not to:
      </p>
      <ul>
        <li>Post anything illegal, infringing, harmful or abusive.</li>
        <li>Reverse‑engineer, scrape or interfere with the Service.</li>
        <li>Impersonate others or misrepresent your affiliation.</li>
      </ul>

      <h2>6. Privacy & Data</h2>
      <p>
        Your privacy is critically important. Our{" "}
        <a href="/privacy">Privacy Policy</a> explains how we collect, use,
        store, and disclose data about you.
      </p>

      <h2>7. Disclaimers & Limitation of Liability</h2>
      <p>
        MindEase provides cognitive‑behavioral tools and AI‑powered support for
        informational purposes only. We are not a licensed medical provider and
        do not offer diagnosis or treatment. Always seek qualified professional
        help for medical or mental‑health emergencies. To the fullest extent
        permitted by law, MindEase disclaims all warranties and limits its
        liability to direct damages up to the amount you paid us in the prior
        year.
      </p>

      <h2>8. Governing Law & Dispute Resolution</h2>
      <p>
        These Terms are governed by French law and the regulations of the
        European Economic Area. Any dispute arising under these Terms shall be
        resolved by the courts of Grenoble, France, unless mandatory local law
        provides otherwise.
      </p>

      <h2>9. Changes to These Terms</h2>
      <p>
        We may update these Terms from time to time. We’ll notify you of
        material changes by email or via an in‑app notice at least 30 days
        before they take effect. Continued use of the Services after the
        effective date constitutes your acceptance.
      </p>

      <h2>10. Contact Us</h2>
      <p>
        If you have questions about these Terms, reach out at{" "}
        <a href="mailto:support@mindease.com">support@mindease.com</a> or:
      </p>
      <address>
        MindEase SAS<br />
        12 Rue des Alpes<br />
        38000 Grenoble, France
      </address>
    </main>
  );
}
