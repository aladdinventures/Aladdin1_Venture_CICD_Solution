// Copyright (c) 2025 Saeed Alaediny
// This file is part of MAMOS (Manus Agent Management & Orchestration System)

import { Module, Global } from '@nestjs/common';
import { MetricsService } from './metrics.service';
import { MetricsController } from './metrics.controller';

@Global()
@Module({
  providers: [MetricsService],
  controllers: [MetricsController],
  exports: [MetricsService],
})
export class MetricsModule {}

