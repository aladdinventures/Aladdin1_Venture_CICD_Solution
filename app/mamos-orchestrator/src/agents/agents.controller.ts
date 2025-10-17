/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import {
  Controller,
  Get,
  Post,
  Delete,
  Body,
  Param,
  Headers,
  UseGuards,
} from '@nestjs/common';
import { AgentsService } from './agents.service';
import { RegisterAgentDto, HeartbeatDto, CreateRegistrationTokenDto } from './dto/agent.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('agents')
export class AgentsController {
  constructor(private readonly agentsService: AgentsService) {}

  @Post('register')
  async register(
    @Body() dto: RegisterAgentDto,
    @Headers('authorization') authorization: string
  ) {
    const token = authorization?.replace('Bearer ', '');
    return this.agentsService.registerAgent(dto, token);
  }

  @Post(':id/heartbeat')
  async heartbeat(@Param('id') id: string, @Body() dto: HeartbeatDto) {
    return this.agentsService.heartbeat(id, dto);
  }

  @Get()
  @UseGuards(JwtAuthGuard)
  async getAll() {
    return this.agentsService.getAllAgents();
  }

  @Get(':id')
  @UseGuards(JwtAuthGuard)
  async getById(@Param('id') id: string) {
    return this.agentsService.getAgentById(id);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  async delete(@Param('id') id: string) {
    return this.agentsService.deleteAgent(id);
  }

  @Post('tokens')
  @UseGuards(JwtAuthGuard)
  async createToken(@Body() dto: CreateRegistrationTokenDto) {
    return this.agentsService.createRegistrationToken(dto.ttlSeconds);
  }
}

