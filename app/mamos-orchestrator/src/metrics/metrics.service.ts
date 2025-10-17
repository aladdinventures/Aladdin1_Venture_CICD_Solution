// Copyright (c) 2025 Saeed Alaediny
// This file is part of MAMOS (Manus Agent Management & Orchestration System)

import { Injectable } from '@nestjs/common';
import { Registry, Counter, Gauge, Histogram, collectDefaultMetrics } from 'prom-client';

@Injectable()
export class MetricsService {
  private readonly registry: Registry;

  // Counters
  public readonly httpRequestsTotal: Counter;
  public readonly jobsCreatedTotal: Counter;
  public readonly jobsCompletedTotal: Counter;
  public readonly jobsFailedTotal: Counter;

  // Gauges
  public readonly activeAgents: Gauge;
  public readonly pendingJobs: Gauge;
  public readonly runningJobs: Gauge;

  // Histograms
  public readonly httpRequestDuration: Histogram;
  public readonly jobExecutionDuration: Histogram;

  constructor() {
    this.registry = new Registry();

    // Collect default metrics (CPU, memory, etc.)
    collectDefaultMetrics({ register: this.registry });

    // HTTP Requests
    this.httpRequestsTotal = new Counter({
      name: 'http_requests_total',
      help: 'Total number of HTTP requests',
      labelNames: ['method', 'route', 'status_code'],
      registers: [this.registry],
    });

    this.httpRequestDuration = new Histogram({
      name: 'http_request_duration_seconds',
      help: 'Duration of HTTP requests in seconds',
      labelNames: ['method', 'route', 'status_code'],
      registers: [this.registry],
    });

    // Jobs
    this.jobsCreatedTotal = new Counter({
      name: 'jobs_created_total',
      help: 'Total number of jobs created',
      registers: [this.registry],
    });

    this.jobsCompletedTotal = new Counter({
      name: 'jobs_completed_total',
      help: 'Total number of jobs completed successfully',
      registers: [this.registry],
    });

    this.jobsFailedTotal = new Counter({
      name: 'jobs_failed_total',
      help: 'Total number of jobs that failed',
      registers: [this.registry],
    });

    this.pendingJobs = new Gauge({
      name: 'pending_jobs',
      help: 'Number of pending jobs',
      registers: [this.registry],
    });

    this.runningJobs = new Gauge({
      name: 'running_jobs',
      help: 'Number of running jobs',
      registers: [this.registry],
    });

    this.jobExecutionDuration = new Histogram({
      name: 'job_execution_duration_seconds',
      help: 'Duration of job execution in seconds',
      labelNames: ['command_id', 'status'],
      registers: [this.registry],
    });

    // Agents
    this.activeAgents = new Gauge({
      name: 'active_agents',
      help: 'Number of active agents',
      registers: [this.registry],
    });
  }

  getRegistry(): Registry {
    return this.registry;
  }

  async getMetrics(): Promise<string> {
    return this.registry.metrics();
  }
}

