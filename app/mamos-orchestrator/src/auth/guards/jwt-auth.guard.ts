/**
 * Copyright (c) 2025 Saeed Alaediny
 * This file is part of MAMOS (Manus Agent Management & Orchestration System)
 */

import { Injectable } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

