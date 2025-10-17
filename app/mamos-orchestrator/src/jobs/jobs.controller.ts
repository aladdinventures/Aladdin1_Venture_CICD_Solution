/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  UseGuards,
} from '@nestjs/common';
import { JobsService } from './jobs.service';
import { CreateJobDto, UpdateJobDto } from './dto/job.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@Controller('jobs')
export class JobsController {
  constructor(private readonly jobsService: JobsService) {}

  @Post()
  @UseGuards(JwtAuthGuard)
  async create(@Body() dto: CreateJobDto) {
    return this.jobsService.createJob(dto);
  }

  @Get()
  async getAll(@Query('agentId') agentId?: string) {
    if (agentId) {
      return this.jobsService.getJobsByAgent(agentId);
    }
    return this.jobsService.getAllJobs();
  }

  @Get('pending/:agentId')
  async getPendingForAgent(@Param('agentId') agentId: string) {
    return this.jobsService.getPendingJobsForAgent(agentId);
  }

  @Get(':id')
  async getById(@Param('id') id: string) {
    return this.jobsService.getJobById(id);
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() dto: UpdateJobDto) {
    return this.jobsService.updateJob(id, dto);
  }

  @Delete(':id')
  @UseGuards(JwtAuthGuard)
  async delete(@Param('id') id: string) {
    return this.jobsService.deleteJob(id);
  }
}

