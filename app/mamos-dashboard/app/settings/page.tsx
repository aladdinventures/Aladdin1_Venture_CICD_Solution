/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { healthApi, setAuthToken } from '@/lib/api';
import Navigation from '@/components/Navigation';

export default function SettingsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    } else if (status === 'authenticated' && session) {
      setAuthToken((session as any).accessToken);
      loadHealth();
    }
  }, [status, session, router]);

  const loadHealth = async () => {
    try {
      const res = await healthApi.check();
      setHealth(res.data);
    } catch (error) {
      console.error('Error loading health:', error);
    } finally {
      setLoading(false);
    }
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">System Health</h2>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`font-semibold ${health?.status === 'ok' ? 'text-green-600' : 'text-red-600'}`}>
                  {health?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Database:</span>
                <span className={`font-semibold ${health?.database === 'connected' ? 'text-green-600' : 'text-red-600'}`}>
                  {health?.database || 'Unknown'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Timestamp:</span>
                <span className="text-gray-900">{health?.timestamp ? new Date(health.timestamp).toLocaleString() : 'N/A'}</span>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">About MAMOS</h2>
            <div className="space-y-3 text-gray-600">
              <p><strong>Version:</strong> 1.0.0</p>
              <p><strong>Description:</strong> Manus Agent Management & Orchestration System</p>
              <p><strong>License:</strong> MIT</p>
              <p><strong>Copyright:</strong> © 2025 Saeed Alaediny</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

