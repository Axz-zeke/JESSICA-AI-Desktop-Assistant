# Tailwind CSS and Dark-Mode Design Systems

## Semantic CSS Variables Architecture
Rather than hardcoding utility colors like `bg-gray-900`, enterprise design systems map functional tokens via CSS variables for smooth theming:

```css
:root {
  --background: 220 20% 98%;
  --foreground: 222 47% 11%;
  --primary: 221 83% 53%;
  --border: 214 32% 91%;
}

.dark {
  --background: 224 71% 4%;
  --foreground: 210 40% 98%;
  --primary: 217 91% 60%;
  --border: 217 33% 17%;
}
```

## Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: 'hsl(var(--background) / <alpha-value>)',
        foreground: 'hsl(var(--foreground) / <alpha-value>)',
        primary: 'hsl(var(--primary) / <alpha-value>)',
        border: 'hsl(var(--border) / <alpha-value>)',
      }
    }
  }
}
```
