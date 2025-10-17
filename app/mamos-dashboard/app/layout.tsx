/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'MAMOS - Agent Management & Orchestration System',
  description: 'Manage and orchestrate distributed agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

