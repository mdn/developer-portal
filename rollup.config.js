import { eslint } from 'rollup-plugin-eslint';
import { terser } from 'rollup-plugin-terser';
import autoprefixer from 'autoprefixer';
import commonjs from 'rollup-plugin-commonjs';
import postcss from 'rollup-plugin-postcss';
import postcssPresetEnv from 'postcss-preset-env';

export default {
  input: 'src/js/index.js',
  output: {
    file: 'dist/bundle.js',
    format: 'iife'
  },
  plugins: [
    eslint(),
    commonjs(),
    postcss({
      extract: true,
      plugins: [
        autoprefixer,
        postcssPresetEnv(),
      ],
    }),
    terser(),
  ],
};
