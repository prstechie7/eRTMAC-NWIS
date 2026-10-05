import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OIL INDIA LIMITED · eRTMAC-NWIS | Nearby Wells Intelligence System",
  description: "Real-time look-ahead drilling hazard intelligence & spatial offset-well advisory system calibrated for Upper Assam Basin (SIH26121).",
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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;0,14..32,900;1,14..32,400&family=JetBrains+Mono:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800;900&display=swap"
          rel="stylesheet"
        />
        {/* Leaflet CSS for real satellite map rendering */}
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
      </head>
      <body className="min-h-screen antialiased" style={{ background: "var(--canvas)", color: "var(--text-primary)" }}>
        {children}
      </body>
    </html>
  );
}
