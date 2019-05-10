import { eslint } from 'rollup-plugin-eslint';
import { terser } from 'rollup-plugin-terser';
import autoprefixer from 'autoprefixer';
import babel from 'rollup-plugin-babel';
import commonjs from 'rollup-plugin-commonjs';
import postcss from 'rollup-plugin-postcss';
import postcssPresetEnv from 'postcss-preset-env';

export default {
  input: 'src/js/index.js',
  output: {
    file: 'dist/js/bundle.js',
    format: 'iife'
  },
  plugins: [
    eslint(),
    commonjs(),
    babel({
      exclude: 'node_modules/**',
    }),
    postcss({
      extract: 'dist/css/bundle.css',
      plugins: [
        autoprefixer,
        postcssPresetEnv(),
      ],
    }),
    terser(),
  ],
};
