import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

// One widget per build: vite-plugin-singlefile inlines every chunk into the HTML,
// which only works with a single entry. `npm run build` runs this once per widget.
const widget = process.env.WIDGET
if (!widget) throw new Error('Set WIDGET=card|stats|types|team|search')

export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    outDir: '../src/widgets/html',
    emptyOutDir: false,
    rollupOptions: { input: `${widget}.html` },
  },
})
