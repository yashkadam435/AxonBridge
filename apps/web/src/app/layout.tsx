import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AxonBridge — Healthcare Automation Platform',
  description: 'HIPAA-compliant Universal Agentic Automation Layer for Healthcare. AI-powered middleware for HIS/EHR systems.',
  keywords: ['healthcare', 'automation', 'HIPAA', 'EHR', 'HIS', 'AI', 'clinical'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>{children}</body>
    </html>
  );
}
