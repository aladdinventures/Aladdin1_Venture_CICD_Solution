/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { agentApi, setAuthToken } from '@/lib/api';
import { getSocket } from '@/lib/socket';
import Navigation from '@/components/Navigation';

export default function AgentsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [newToken, setNewToken] = useState('');

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    } else if (status === 'authenticated' && session) {
      setAuthToken((session as any).accessToken);
      loadAgents();
      setupWebSocket();
    }
  }, [status, session, router]);

  const loadAgents = async () => {
    try {
      const res = await agentApi.getAll();
      setAgents(res.data);
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocket = () => {
    const socket = getSocket();
    socket.on('agent:update', (agent: any) => {
      setAgents((prev) => {
        const index = prev.findIndex((a) => a.id === agent.id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = agent;
          return updated;
        }
        return [...prev, agent];
      });
    });
  };

  const handleCreateToken = async () => {
    try {
      const res = await agentApi.createToken(3600);
      setNewToken(res.data.token);
      setShowTokenModal(true);
    } catch (error) {
      console.error('Error creating token:', error);
    }
  };

  const handleDeleteAgent = async (id: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) return;
    
    try {
      await agentApi.delete(id);
      setAgents((prev) => prev.filter((a) => a.id !== id));
    } catch (error) {
      console.error('Error deleting agent:', error);
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
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Agents</h1>
            <button
              onClick={handleCreateToken}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Create Registration Token
            </button>
          </div>

          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hostname</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">OS</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">CPU Cores</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">RAM (GB)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Heartbeat</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {agents.map((agent) => (
                  <tr key={agent.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{agent.hostname}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{agent.os}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{agent.cpuCores}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(agent.ramUsed / 1024).toFixed(1)} / {(agent.ramTotal / 1024).toFixed(1)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        agent.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {agent.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(agent.lastHeartbeat).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <button
                        onClick={() => handleDeleteAgent(agent.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Token Modal */}
      {showTokenModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Registration Token Created</h3>
            <p className="text-sm text-gray-500 mb-4">
              Copy this token and use it to register new agents. It will expire in 1 hour.
            </p>
            <div className="bg-gray-100 p-3 rounded font-mono text-sm break-all mb-4">
              {newToken}
            </div>
            <button
              onClick={() => setShowTokenModal(false)}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

