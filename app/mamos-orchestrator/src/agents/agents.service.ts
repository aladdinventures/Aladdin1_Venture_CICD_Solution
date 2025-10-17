/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { RegisterAgentDto, HeartbeatDto } from './dto/agent.dto';

@Injectable()
export class AgentsService {
  constructor(private prisma: PrismaService) {}

  async registerAgent(dto: RegisterAgentDto, token: string) {
    // Verify registration token
    const regToken = await this.prisma.registrationToken.findUnique({
      where: { token },
    });

    if (!regToken) {
      throw new BadRequestException('Invalid registration token');
    }

    if (regToken.used) {
      throw new BadRequestException('Registration token already used');
    }

    if (new Date() > regToken.expiresAt) {
      throw new BadRequestException('Registration token expired');
    }

    // Check if agent already exists
    const existingAgent = await this.prisma.agent.findUnique({
      where: { hostname: dto.hostname },
    });

    if (existingAgent) {
      // Update existing agent
      const agent = await this.prisma.agent.update({
        where: { hostname: dto.hostname },
        data: {
          os: dto.os,
          cpuCores: dto.cpuCores,
          ramTotal: dto.ramTotal,
          ramUsed: dto.ramUsed,
          status: 'online',
          lastHeartbeat: new Date(),
        },
      });

      // Mark token as used
      await this.prisma.registrationToken.update({
        where: { token },
        data: { used: true },
      });

      return agent;
    }

    // Create new agent
    const agent = await this.prisma.agent.create({
      data: {
        hostname: dto.hostname,
        os: dto.os,
        cpuCores: dto.cpuCores,
        ramTotal: dto.ramTotal,
        ramUsed: dto.ramUsed,
        status: 'online',
      },
    });

    // Mark token as used
    await this.prisma.registrationToken.update({
      where: { token },
      data: { used: true },
    });

    return agent;
  }

  async heartbeat(agentId: string, dto: HeartbeatDto) {
    const agent = await this.prisma.agent.findUnique({
      where: { id: agentId },
    });

    if (!agent) {
      throw new NotFoundException('Agent not found');
    }

    return this.prisma.agent.update({
      where: { id: agentId },
      data: {
        status: 'online',
        ramUsed: dto.ramUsed,
        lastHeartbeat: new Date(),
      },
    });
  }

  async getAllAgents() {
    return this.prisma.agent.findMany({
      orderBy: { registeredAt: 'desc' },
    });
  }

  async getAgentById(id: string) {
    const agent = await this.prisma.agent.findUnique({
      where: { id },
      include: {
        jobs: {
          orderBy: { createdAt: 'desc' },
          take: 10,
        },
      },
    });

    if (!agent) {
      throw new NotFoundException('Agent not found');
    }

    return agent;
  }

  async deleteAgent(id: string) {
    const agent = await this.prisma.agent.findUnique({
      where: { id },
    });

    if (!agent) {
      throw new NotFoundException('Agent not found');
    }

    await this.prisma.agent.delete({
      where: { id },
    });

    return { message: 'Agent deleted successfully' };
  }

  async createRegistrationToken(ttlSeconds: number = 3600) {
    const token = this.generateToken();
    const expiresAt = new Date(Date.now() + ttlSeconds * 1000);

    return this.prisma.registrationToken.create({
      data: {
        token,
        expiresAt,
      },
    });
  }

  async checkOfflineAgents() {
    const threshold = new Date(Date.now() - 60000); // 60 seconds
    await this.prisma.agent.updateMany({
      where: {
        lastHeartbeat: {
          lt: threshold,
        },
        status: 'online',
      },
      data: {
        status: 'offline',
      },
    });
  }

  private generateToken(): string {
    return (
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }
}

