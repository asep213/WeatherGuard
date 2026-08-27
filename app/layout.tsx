import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WeatherGuard | Keputusan cuaca yang lebih aman",
  description: "Impact-based weather intelligence untuk pertanian, maritim, dan BPBD.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}