import { fileURLToPath, URL } from 'node:url'
const fs = require('fs')

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: { 
    port: 3000,
    https: {
      key: fs.readFileSync('./certs/example.com+5-key.pem'),
      cert: fs.readFileSync('./certs/example.com+5.pem'),
    },
  }
})
