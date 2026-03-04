/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: '#0d0d12',
                surface: '#171721',
                primary: '#8b5cf6',
                secondary: '#00FF41',
                text: '#f8fafc',
                muted: '#94a3b8',
                danger: '#fb7185',
                success: '#34d399'
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
