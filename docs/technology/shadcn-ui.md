# shadcn/ui

Web Core v0.1.0 includes shadcn/ui conventions with Radix primitives, Lucide icons, a neutral theme, and a reference `Button` component. shadcn/ui's approach gives the application editable component source instead of treating the UI library as a closed runtime dependency. `components.json` holds generator/theme configuration; generated components live under `src/components/ui/`.

The tradeoff is component ownership: teams can adapt the source, but must maintain those local changes and review upstream updates themselves. Accessibility still depends on correct composition and usage; adopting a component does not guarantee every interaction is accessible.

Reference: [shadcn/ui documentation](https://ui.shadcn.com/docs).
