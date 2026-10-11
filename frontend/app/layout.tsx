import type { Metadata } from "next";
import { Big_Shoulders, Hanken_Grotesk } from "next/font/google";
import { Toaster } from "sonner";

import { AppHeader } from "@/components/app-header";
import { CaptionFontFaces } from "@/components/style/caption-font-faces";

import "./globals.css";

const display = Big_Shoulders({
  variable: "--font-big-shoulders",
  subsets: ["latin"],
  axes: ["opsz"],
  adjustFontFallback: false, // no metric overrides exist for this family
});

const sans = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Shortz",
  description: "Turn long videos into captioned vertical shorts.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body className="min-h-dvh">
        <CaptionFontFaces />
        <AppHeader />
        {children}
        <Toaster theme="dark" position="bottom-center" toastOptions={{ className: "!bg-raise !border-line !text-text" }} />
      </body>
    </html>
  );
}
