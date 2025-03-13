import { defineConfig } from 'vite';

export default defineConfig({
    server: {
        port: 5173
    },
    build: {
        rollupOptions: {
            input: {
                main: 'index.html',
                optimize: 'optimize.html',
                result: 'result.html',
                destination: 'destination.html'
            }
        }
    }
});
