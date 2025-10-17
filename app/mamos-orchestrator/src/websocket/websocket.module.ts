/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Module } from '@nestjs/common';
import { EventsGateway } from './events.gateway';
import { PrismaService } from '../prisma.service';

@Module({
  providers: [EventsGateway, PrismaService],
  exports: [EventsGateway],
})
export class WebsocketModule {}

