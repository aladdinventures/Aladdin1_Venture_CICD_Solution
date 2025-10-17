/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

'use client';

import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { agentApi, jobApi, healthApi, setAuthToken } from '@/lib/api';
import { getSocket } from '@/lib/socket';
import Navigation from '@/components/Navigation';

export default function HomePage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [metrics, setMetrics] = useState<any>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login');
    } else if (status === 'authenticated' && session) {
      setAuthToken((session as any).accessToken);
      loadData();
      setupWebSocket();
    }
  }, [status, session, router]);

  const loadData = async () => {
    try {
      const [metricsRes, agentsRes, jobsRes] = await Promise.all([
        healthApi.metrics(),
        agentApi.getAll(),
        jobApi.getAll(),
      ]);

      setMetrics(metricsRes.data);
      setAgents(agentsRes.data);
      setJobs(jobsRes.data.slice(0, 5));
    } catch (error) {
      console.error('Error loading data:', error);
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

    socket.on('job:update', (job: any) => {
      setJobs((prev) => {
        const index = prev.findIndex((j) => j.id === job.id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = job;
          return updated;
        }
        return [job, ...prev.slice(0, 4)];
      });
    });
  };

  if (status === 'loading' || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

          {/* Metrics Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="text-sm font-medium text-gray-500">Total Agents</div>
              <div className="text-3xl font-semibold text-gray-900 mt-2">
                {metrics?.agents?.total || 0}
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="text-sm font-medium text-gray-500">Online Agents</div>
              <div className="text-3xl font-semibold text-green-600 mt-2">
                {metrics?.agents?.online || 0}
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="text-sm font-medium text-gray-500">Total Jobs</div>
              <div className="text-3xl font-semibold text-gray-900 mt-2">
                {metrics?.jobs?.total || 0}
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg p-5">
              <div className="text-sm font-medium text-gray-500">Pending Jobs</div>
              <div className="text-3xl font-semibold text-yellow-600 mt-2">
                {metrics?.jobs?.pending || 0}
              </div>
            </div>
          </div>

          {/* Recent Agents */}
          <div className="bg-white shadow rounded-lg mb-8">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Agents</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hostname</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">OS</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Heartbeat</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {agents.slice(0, 5).map((agent) => (
                    <tr key={agent.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{agent.hostname}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{agent.os}</td>
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
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Jobs */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Jobs</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Command</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Agent</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr key={job.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">{job.command}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.agent?.hostname || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          job.status === 'completed' ? 'bg-green-100 text-green-800' :
                          job.status === 'failed' ? 'bg-red-100 text-red-800' :
                          job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.createdAt).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

