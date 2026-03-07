// Sample file with no exports for testing parse-js.mjs
const x = 42;
const y = x + 1;

function helper() {
  return x * y;
}

if (helper() > 100) {
  console.log('big number');
}
