/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { IsString, IsNumber, IsNotEmpty } from 'class-validator';

export class RegisterAgentDto {
  @IsString()
  @IsNotEmpty()
  hostname: string;

  @IsString()
  @IsNotEmpty()
  os: string;

  @IsNumber()
  cpuCores: number;

  @IsNumber()
  ramTotal: number;

  @IsNumber()
  ramUsed: number;
}

export class HeartbeatDto {
  @IsNumber()
  ramUsed: number;
}

export class CreateRegistrationTokenDto {
  @IsNumber()
  ttlSeconds?: number;
}

