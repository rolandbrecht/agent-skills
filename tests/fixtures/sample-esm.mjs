// Sample ESM JavaScript file for testing parse-js.mjs
import path from 'path';
import { readFileSync } from 'fs';

export function greet(name) {
  return `Hello, ${name}!`;
}

export class Calculator {
  add(a, b) {
    return a + b;
  }

  subtract(a, b) {
    return a - b;
  }
}

export const VERSION = '1.0.0';

export default function main() {
  const calc = new Calculator();
  console.log(greet('world'));
  console.log(calc.add(1, 2));
}
