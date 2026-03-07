#!/usr/bin/env node

/**
 * parse-js.mjs — Parse a JavaScript/TypeScript file and emit AST or symbol list.
 *
 * Usage:
 *   node parse-js.mjs <file>              # Full JSON AST to stdout
 *   node parse-js.mjs <file> --symbols    # Flat list of exported symbols with line numbers
 *
 * Requirements: Node.js v14+
 * Dependencies: acorn, acorn-walk (auto-installed to a temp dir if missing)
 */

import { existsSync, readFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { execSync } from 'child_process';
import { createRequire } from 'module';

// --- Args ---
const args = process.argv.slice(2);
if (args.length < 1) {
  console.error('Usage: node parse-js.mjs <file> [--symbols]');
  process.exit(1);
}

const file = args[0];
const mode = args.includes('--symbols') ? 'symbols' : 'ast';

if (!existsSync(file)) {
  console.error(`Error: File not found: ${file}`);
  process.exit(1);
}

// --- Ensure acorn is available ---
const depsDir = join(tmpdir(), 'ast-skill-deps');
const acornPath = join(depsDir, 'node_modules', 'acorn');

if (!existsSync(acornPath)) {
  console.error(`Installing acorn to ${depsDir}...`);
  mkdirSync(depsDir, { recursive: true });
  execSync('npm init -y --silent 2>/dev/null || npm init -y --silent 2>nul', { cwd: depsDir, stdio: 'pipe' });
  execSync('npm install --silent acorn acorn-walk', { cwd: depsDir, stdio: 'pipe' });
}

const require = createRequire(join(depsDir, 'node_modules', '_'));
const acorn = require('acorn');
const walk = require('acorn-walk');

// --- Parse ---
const code = readFileSync(file, 'utf8');
let ast;
try {
  ast = acorn.parse(code, {
    ecmaVersion: 'latest',
    sourceType: 'module',
    locations: true,
    allowImportExportEverywhere: true,
    allowReturnOutsideFunction: true,
  });
} catch (e) {
  console.error('Parse error:', e.message);
  process.exit(1);
}

// --- Full AST mode ---
if (mode === 'ast') {
  console.log(JSON.stringify(ast, null, 2));
  process.exit(0);
}

// --- Symbol extraction mode ---
const symbols = [];

// Named exports: export function foo() / export class Bar / export const baz
walk.simple(ast, {
  ExportNamedDeclaration(node) {
    if (node.declaration) {
      const decl = node.declaration;
      if (decl.type === 'FunctionDeclaration' && decl.id) {
        symbols.push({ name: decl.id.name, type: 'function', line: decl.loc.start.line });
      } else if (decl.type === 'ClassDeclaration' && decl.id) {
        symbols.push({ name: decl.id.name, type: 'class', line: decl.loc.start.line });
      } else if (decl.type === 'VariableDeclaration') {
        for (const d of decl.declarations) {
          if (d.id && d.id.name) {
            symbols.push({ name: d.id.name, type: decl.kind, line: d.loc.start.line });
          }
        }
      }
    }
    // export { a, b, c }
    if (node.specifiers) {
      for (const spec of node.specifiers) {
        symbols.push({ name: (spec.exported || spec.local).name, type: 're-export', line: node.loc.start.line });
      }
    }
  },
  ExportDefaultDeclaration(node) {
    const decl = node.declaration;
    const name = (decl.id && decl.id.name) || 'default';
    symbols.push({ name, type: 'default-export', line: node.loc.start.line });
  },
});

// CommonJS: module.exports = { ... }
walk.simple(ast, {
  AssignmentExpression(node) {
    if (
      node.left.type === 'MemberExpression' &&
      node.left.object.name === 'module' &&
      node.left.property.name === 'exports'
    ) {
      if (node.right.type === 'ObjectExpression') {
        for (const prop of node.right.properties) {
          if (prop.key) {
            symbols.push({ name: prop.key.name || prop.key.value, type: 'cjs-export', line: prop.loc.start.line });
          }
        }
      } else {
        symbols.push({ name: 'module.exports', type: 'cjs-default', line: node.loc.start.line });
      }
    }
  },
});

if (symbols.length === 0) {
  console.log('No exported symbols found.');
} else {
  const maxName = Math.max(...symbols.map((s) => s.name.length));
  for (const s of symbols) {
    console.log(s.name.padEnd(maxName + 2) + s.type.padEnd(16) + 'line ' + s.line);
  }
}
