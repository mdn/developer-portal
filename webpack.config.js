const { resolve } = require('path');
const autoprefixer = require('autoprefixer');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

const config = {
  entry: {
    bundle: './src/js/index.js',
    head: './src/js/head-includes.js',
    admin_extras: './src/js/admin-extras.js',
  },
  output: {
    filename: 'js/[name].js',
    path: resolve(__dirname, 'dist'),
  },
  target: 'web',
  mode: process.env.NODE_ENV,
  module: {
    rules: [
      {
        test: /\.js$/,
        loader: 'buble-loader',
        exclude: /node_modules/,
        options: {
          objectAssign: 'Object.assign',
          transforms: { forOf: false },
        },
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: 'css-loader',
            options: { url: false },
          },
          {
            loader: 'postcss-loader',
            options: { plugins: [autoprefixer] },
          },
          'sass-loader',
        ],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: 'css/[name].css',
    }),
  ],
};

if (process.env.NODE_ENV === 'production') {
  config.plugins = [...config.plugins, new OptimizeCssAssetsPlugin()];
}

module.exports = config;
