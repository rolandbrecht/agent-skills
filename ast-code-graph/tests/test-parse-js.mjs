/**
 * Tests for ast-code-graph/scripts/parse-js.mjs
 *
 * Run: node --test tests/test-parse-js.mjs
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SCRIPT = join(__dirname, '..', 'scripts', 'parse-js.mjs');
const FIXTURES = join(__dirname, 'fixtures');

function run(file, ...flags) {
  const result = execFileSync('node', [SCRIPT, join(FIXTURES, file), ...flags], {
    encoding: 'utf8',
    timeout: 30000,
  });
  return result.trim();
}

describe('parse-js.mjs', () => {
  describe('--symbols mode', () => {
    it('should extract ESM named exports', () => {
      const output = run('sample-esm.mjs', '--symbols');
      assert.ok(output.includes('greet'), 'should find greet function');
      assert.ok(output.includes('Calculator'), 'should find Calculator class');
      assert.ok(output.includes('VERSION'), 'should find VERSION const');
      assert.ok(output.includes('function'), 'should identify function type');
      assert.ok(output.includes('class'), 'should identify class type');
    });

    it('should extract ESM default export', () => {
      const output = run('sample-esm.mjs', '--symbols');
      assert.ok(output.includes('default-export'), 'should find default export');
    });

    it('should extract CommonJS exports', () => {
      const output = run('sample-cjs.js', '--symbols');
      assert.ok(output.includes('loadConfig'), 'should find loadConfig');
      assert.ok(output.includes('validateConfig'), 'should find validateConfig');
      assert.ok(output.includes('Logger'), 'should find Logger');
      assert.ok(output.includes('cjs-export'), 'should identify CJS export type');
    });

    it('should report no exports when file has none', () => {
      const output = run('sample-no-exports.js', '--symbols');
      assert.ok(output.includes('No exported symbols found'), 'should report no exports');
    });

    it('should include line numbers', () => {
      const output = run('sample-esm.mjs', '--symbols');
      assert.ok(/line \d+/.test(output), 'should include line numbers');
    });
  });

  describe('AST mode (default)', () => {
    it('should produce valid JSON AST', () => {
      const output = run('sample-esm.mjs');
      const ast = JSON.parse(output);
      assert.equal(ast.type, 'Program', 'root node should be Program');
      assert.ok(Array.isArray(ast.body), 'should have body array');
      assert.ok(ast.body.length > 0, 'body should not be empty');
    });

    it('should include location info', () => {
      const output = run('sample-esm.mjs');
      const ast = JSON.parse(output);
      const firstNode = ast.body[0];
      assert.ok(firstNode.loc, 'nodes should have loc');
      assert.ok(firstNode.loc.start.line >= 1, 'loc should have valid line number');
    });

    it('should parse CommonJS files', () => {
      const output = run('sample-cjs.js');
      const ast = JSON.parse(output);
      assert.equal(ast.type, 'Program');
    });
  });

  describe('error handling', () => {
    it('should fail on missing file', () => {
      assert.throws(() => {
        execFileSync('node', [SCRIPT, 'nonexistent.js'], {
          encoding: 'utf8',
          stdio: 'pipe',
        });
      }, 'should throw on missing file');
    });

    it('should fail with no arguments', () => {
      assert.throws(() => {
        execFileSync('node', [SCRIPT], {
          encoding: 'utf8',
          stdio: 'pipe',
        });
      }, 'should throw with no args');
    });
  });
});
