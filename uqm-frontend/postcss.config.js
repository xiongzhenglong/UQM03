export default {
  plugins: {
    '@tailwindcss/postcss': {
      // 指定 Tailwind 配置文件的路径
      config: './tailwind.config.js',
    },
    autoprefixer: {},
  },
} 