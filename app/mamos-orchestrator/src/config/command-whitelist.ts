// Copyright (c) 2025 Saeed Alaediny
// This file is part of MAMOS (Manus Agent Management & Orchestration System)

export const COMMAND_WHITELIST = {
  echo: {
    id: 'echo',
    name: 'Echo',
    description: 'Print text to console',
    platforms: ['linux', 'windows', 'darwin'],
    executable: 'echo',
  },
  uname: {
    id: 'uname',
    name: 'System Info (uname)',
    description: 'Display system information',
    platforms: ['linux', 'darwin'],
    executable: 'uname',
  },
  uptime: {
    id: 'uptime',
    name: 'Uptime',
    description: 'Show system uptime',
    platforms: ['linux', 'darwin'],
    executable: 'uptime',
  },
  ver: {
    id: 'ver',
    name: 'Version (Windows)',
    description: 'Display Windows version',
    platforms: ['windows'],
    executable: 'ver',
  },
};

export function isCommandAllowed(commandId: string): boolean {
  return commandId in COMMAND_WHITELIST;
}

export function getCommandInfo(commandId: string) {
  return COMMAND_WHITELIST[commandId] || null;
}

