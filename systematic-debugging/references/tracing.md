# Boundary Tracing Patterns

When an issue spans multiple components (Frontend → API → Database, or CI → Build → Sign), the first step of systematic debugging is to inject boundary logs to prove *where* the data mutation occurs.

Do not guess which layer is failing. Inject telemetry around the boundaries, trigger the bug, and observe the logs.

## 1. API Boundary (Frontend / Backend)

When a frontend request fails or returns unexpected data, log the exact payload leaving the client and the exact payload entering the server.

**Frontend (e.g., fetch wrapper):**

```javascript
// Before sending
console.log('[BOUNDARY: FRONTEND OUT]', { 
  url, 
  method, 
  headers: req.headers, 
  body: JSON.parse(req.body) 
});

const res = await fetch(url, req);

// After receiving
console.log('[BOUNDARY: FRONTEND IN]', {
  status: res.status,
  body: await res.clone().json()
});
```

**Backend (e.g., Express middleware):**

```javascript
app.use((req, res, next) => {
  // What exactly did the server receive?
  console.log('[BOUNDARY: BACKEND IN]', {
    path: req.path,
    query: req.query,
    body: req.body,
    authHeader: !!req.header('Authorization')
  });
  
  // Intercept the response
  const originalSend = res.send;
  res.send = function (data) {
    console.log('[BOUNDARY: BACKEND OUT]', {
      status: res.statusCode,
      data: typeof data === 'string' ? data.slice(0, 100) : data
    });
    originalSend.call(this, data);
  };
  next();
});
```

## 2. Database Boundary

When an object has the wrong state, log exactly what the ORM/Query builder is sending to the database and what it receives back.

**Python (SQLAlchemy example):**

```python
import logging
# Enable SQLAlchemy query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Or manually wrap the specific failing query:
print(f"[BOUNDARY: DB OUT] Query Params: {user_id}, {new_status}")
result = db.execute(query)
print(f"[BOUNDARY: DB IN] Rows affected: {result.rowcount}, Data: {result.fetchall()}")
```

## 3. Environment / CI Boundary

When a script works locally but fails in CI, the issue is almost always environmental state (missing env vars, wrong paths, mismatched dependency versions).

**Bash script wrapper:**

```bash
echo "=== [BOUNDARY: SCRIPT START] ==="
echo "PWD: $(pwd)"
echo "NODE_ENV: ${NODE_ENV:-UNSET}"
echo "SECRET_KEY: ${SECRET_KEY:+SET (Length: ${#SECRET_KEY})}${SECRET_KEY:-UNSET}"
echo "Node version: $(node -v)"
echo "================================"
```

## How to use this data

Once you run the system with these logs, you map the flow:

1. `FRONTEND OUT` has `status: "active"`
2. `BACKEND IN` has `status: "active"`
3. `DB OUT` has `status: null`

**Conclusion:** The bug is definitively isolated inside the backend controller/ORM layer. You can stop looking at the frontend and database, and strictly investigate the controller logic.
