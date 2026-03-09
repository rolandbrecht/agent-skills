// Sample CommonJS file for testing parse-js.mjs
const fs = require('fs');
const path = require('path');

function loadConfig(filepath) {
  const raw = fs.readFileSync(filepath, 'utf8');
  return JSON.parse(raw);
}

function validateConfig(config) {
  if (!config.name) throw new Error('Missing name');
  return true;
}

class Logger {
  constructor(level) {
    this.level = level;
  }

  log(msg) {
    if (this.level === 'debug') {
      console.log(`[DEBUG] ${msg}`);
    }
  }
}

module.exports = {
  loadConfig,
  validateConfig,
  Logger,
};
