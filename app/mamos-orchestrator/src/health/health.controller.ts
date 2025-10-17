/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Controller, Get } from '@nestjs/common';
import { PrismaService } from '../prisma.service';

@Controller('health')
export class HealthController {
  constructor(private prisma: PrismaService) {}

  @Get()
  async check() {
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      return {
        status: 'ok',
        timestamp: new Date().toISOString(),
        database: 'connected',
      };
    } catch (error) {
      return {
        status: 'error',
        timestamp: new Date().toISOString(),
        database: 'disconnected',
        error: error.message,
      };
    }
  }

  @Get('metrics')
  async metrics() {
    const agentCount = await this.prisma.agent.count();
    const onlineAgentCount = await this.prisma.agent.count({
      where: { status: 'online' },
    });
    const jobCount = await this.prisma.job.count();
    const pendingJobCount = await this.prisma.job.count({
      where: { status: 'pending' },
    });

    return {
      agents: {
        total: agentCount,
        online: onlineAgentCount,
        offline: agentCount - onlineAgentCount,
      },
      jobs: {
        total: jobCount,
        pending: pendingJobCount,
      },
      timestamp: new Date().toISOString(),
    };
  }
}

