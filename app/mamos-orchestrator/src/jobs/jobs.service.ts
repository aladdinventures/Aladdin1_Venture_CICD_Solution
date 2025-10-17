/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { PrismaService } from '../prisma.service';
import { CreateJobDto, UpdateJobDto } from './dto/job.dto';

@Injectable()
export class JobsService {
  // Whitelist of allowed commands for security
  private readonly commandWhitelist = [
    'echo',
    'ls',
    'pwd',
    'date',
    'whoami',
    'hostname',
    'uptime',
    'df',
    'free',
  ];

  constructor(private prisma: PrismaService) {}

  async createJob(dto: CreateJobDto) {
    // Validate command against whitelist
    const command = dto.command.trim().split(' ')[0];
    if (!this.commandWhitelist.includes(command)) {
      throw new BadRequestException(
        `Command '${command}' is not whitelisted. Allowed commands: ${this.commandWhitelist.join(', ')}`
      );
    }

    // Verify agent exists
    const agent = await this.prisma.agent.findUnique({
      where: { id: dto.agentId },
    });

    if (!agent) {
      throw new NotFoundException('Agent not found');
    }

    if (agent.status !== 'online') {
      throw new BadRequestException('Agent is not online');
    }

    return this.prisma.job.create({
      data: {
        command: dto.command,
        agentId: dto.agentId,
      },
      include: {
        agent: true,
      },
    });
  }

  async getAllJobs() {
    return this.prisma.job.findMany({
      include: {
        agent: true,
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getJobById(id: string) {
    const job = await this.prisma.job.findUnique({
      where: { id },
      include: {
        agent: true,
      },
    });

    if (!job) {
      throw new NotFoundException('Job not found');
    }

    return job;
  }

  async getJobsByAgent(agentId: string) {
    return this.prisma.job.findMany({
      where: { agentId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async getPendingJobsForAgent(agentId: string) {
    return this.prisma.job.findMany({
      where: {
        agentId,
        status: 'pending',
      },
      orderBy: { createdAt: 'asc' },
    });
  }

  async updateJob(id: string, dto: UpdateJobDto) {
    const job = await this.prisma.job.findUnique({
      where: { id },
    });

    if (!job) {
      throw new NotFoundException('Job not found');
    }

    const updateData: any = {};

    if (dto.status) {
      updateData.status = dto.status;

      if (dto.status === 'running' && !job.startedAt) {
        updateData.startedAt = new Date();
      }

      if ((dto.status === 'completed' || dto.status === 'failed') && !job.completedAt) {
        updateData.completedAt = new Date();
      }
    }

    if (dto.output !== undefined) {
      updateData.output = dto.output;
    }

    if (dto.error !== undefined) {
      updateData.error = dto.error;
    }

    return this.prisma.job.update({
      where: { id },
      data: updateData,
      include: {
        agent: true,
      },
    });
  }

  async deleteJob(id: string) {
    const job = await this.prisma.job.findUnique({
      where: { id },
    });

    if (!job) {
      throw new NotFoundException('Job not found');
    }

    await this.prisma.job.delete({
      where: { id },
    });

    return { message: 'Job deleted successfully' };
  }
}

