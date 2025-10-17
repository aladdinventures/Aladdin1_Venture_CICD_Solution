/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { IsString, IsNotEmpty, IsOptional, IsIn } from 'class-validator';

export class CreateJobDto {
  @IsString()
  @IsNotEmpty()
  command: string;

  @IsString()
  @IsNotEmpty()
  agentId: string;
}

export class UpdateJobDto {
  @IsString()
  @IsOptional()
  @IsIn(['pending', 'running', 'completed', 'failed'])
  status?: string;

  @IsString()
  @IsOptional()
  output?: string;

  @IsString()
  @IsOptional()
  error?: string;
}

