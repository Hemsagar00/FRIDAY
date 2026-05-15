# Skill: Deploy Website

## Trigger

Asked to deploy a website or web application.

## Steps

1. Check codebase structure (`find . -type f | head -30`)
2. Identify build system (package.json, Cargo.toml, requirements.txt, etc.)
3. Run tests if available (`npm test`, `pytest`, `cargo test`)
4. Execute build (`npm run build`, `cargo build --release`, etc.)
5. Verify build output exists
6. Deploy via appropriate method (Vercel, Netlify, VPS, etc.)
7. Return deployment URL

## Pitfalls

- Always run tests before deploying
- Check `.env` files are not committed
- Verify the correct branch is checked out
- Ensure NODE_ENV / environment variables are set

## Example

User: "Deploy my React app"

```
friday > tests pass ✅
friday > build succeeded ✅
friday > deploying to Vercel...
friday > deployed: https://myapp.vercel.app
```
