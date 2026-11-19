# UI: Next.js, Tailwind, Zod, Forms

## Next.js 16 App Router

The template is derived from a `create-next-app` scaffold (Next.js 16.4.5, React 19.3.0) with its App Router layout: `src/app/layout.tsx` (Geist fonts via `next/font/google`), `src/app/page.tsx` (+ `page.test.tsx`), `src/app/globals.css` (Tailwind and the shadcn neutral theme). Application identity lives in `src/lib/app-info.json` (`name`, `description`), written once by Copier with `to_json` so no answer is ever interpolated into code.

### Cache Components (`cache_components`, default on)

```ts title="next.config.ts (cache_components=true)"
const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: { rules: { "*.css": { loaders: ["@tailwindcss/turbopack"], as: "*.css" } } },
};
```

- Data fetching is **dynamic by default**; caching is opt-in with `use cache`.
- `partialPrefetching` requires `cacheComponents` (Next.js validation throws otherwise), so they are one switch.
- Requires the Node.js runtime; the `runtime` route segment config is rejected.
- Database data is request-time data: read it inside a `Suspense` boundary after `await connection()` from `next/server`.

With `--set cache_components=false` both lines are omitted.

!!! warning "Read the bundled docs"
    The generated `AGENTS.md` opens with Next.js's own agent block: *"This is NOT the Next.js you know … Read the relevant guide in `node_modules/next/dist/docs/` before writing any code."* It also points at `node_modules/next/dist/docs/01-app/02-guides/data-security.md` before writing data access or mutations.

## Styling: Tailwind CSS v4 and shadcn/ui

Tailwind 4.3.5 is wired through Turbopack (`@tailwindcss/turbopack` in `next.config.ts`; there is no PostCSS config). shadcn/ui components are copied into `src/components/ui/` (configured by `components.json`), built on `radix-ui` and `lucide-react`, styled with `class-variance-authority` and the `cn()` helper in `src/lib/utils.ts`. `Button` (with its test) is the reference component.

## Validation: Zod (`zod`)

`src/lib/schemas/` is the **contract module** shared by client and server: shapes and rules only, never keys or connection details, no framework, environment or database imports (a test checks the import graph).

| Schema | Feature | Used by |
|---|---|---|
| `appInfoSchema` (`app-info.ts`) | zod | validates `src/lib/app-info.json` |
| `exampleFormSchema` (`example-form.ts`) | forms | the example form (client) |
| `item.ts` | database | the repository (DB input and output) |
| `v1/*` (`app-info`, `validate-example`, `problem`, `items`, `session`) | rest_api, auth | route handlers and the OpenAPI document |

The rule from `AGENTS.md`: add a schema and a test for every new input shape, and `safeParse` at the trust boundary. Client-side validation is for user experience only; the server always re-validates.

## Forms: React Hook Form (`forms`)

`/forms-example` renders `src/components/forms/example-form.tsx`: React Hook Form with `zodResolver(exampleFormSchema)`, so the shared schema is the single source of the rules. Labels, `aria-invalid` and error messages are linked; tests run in a DOM environment (`// @vitest-environment jsdom`, Testing Library). The example **saves and sends nothing**: it demonstrates the pattern, not a feature.

## Calling the API from the browser

Use `authClient` from `@/lib/auth-client` for sign-up, sign-in and sign-out; it carries no secret. Same-origin `fetch` to `/api/v1/*` sends the session cookie automatically; state-changing requests carry the browser's `Origin`, which must be trusted. On the server, read the session with `sessionFromHeaders`.
