import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OIL INDIA LIMITED · eRTMAC-NWIS | Nearby Wells Intelligence System",
  description: "Real-time look-ahead drilling hazard intelligence & spatial offset-well advisory system calibrated for Upper Assam Basin.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
      </head>
      <body className="min-h-screen bg-[#F8F9FA] text-[#1E242B] antialiased">
        {children}
      </body>
    </html>
  );
}
