
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'node_modules/pdfjs-dist/build/pdf.worker.mjs',
          dest: '.'
        }
      ]
    })
  ],
    build: {
    manifest: true,
    rollupOptions: {
      input: 'static/main.js',
    },
    outDir: 'static/dist',
    emptyOutDir: true,
    // --- BUILD OPTIMIZATION SUGGESTIONS ---
    // 1. Code Splitting: Ensure dynamic imports are used for lazy loading components/routes.
    //    Vite/Rollup handles this automatically for static imports.
    // 2. Minification: Vite automatically minifies JS, CSS, and HTML in production.
    // 3. Asset Hashing: Vite handles asset hashing for cache busting.
    // 4. Bundle Analysis: Consider adding `rollup-plugin-visualizer` to analyze bundle size
    //    and identify large dependencies for optimization.
    // 5. Compression: Brotli/Gzip compression is typically handled by the web server (e.g., Nginx) or CDN.
  },
});
});
