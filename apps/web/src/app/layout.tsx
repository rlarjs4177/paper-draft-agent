// apps/web/src/app/layout.tsx
import "../styles/globals.css";
import React from "react";

export const metadata = {
  title: "Paper Draft Agent",
  description: "MVP",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
