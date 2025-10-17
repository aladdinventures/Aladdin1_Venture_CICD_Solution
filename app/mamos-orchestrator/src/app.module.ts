/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Module } from '@nestjs/common';
import { AgentsModule } from './agents/agents.module';
import { JobsModule } from './jobs/jobs.module';
import { AuthModule } from './auth/auth.module';
import { HealthModule } from './health/health.module';
import { WebsocketModule } from './websocket/websocket.module';
import { MetricsModule } from './metrics/metrics.module';
import { PrismaService } from './prisma.service';

@Module({
  imports: [AgentsModule, JobsModule, AuthModule, HealthModule, WebsocketModule, MetricsModule],
  providers: [PrismaService],
  exports: [PrismaService],
})
export class AppModule {}

