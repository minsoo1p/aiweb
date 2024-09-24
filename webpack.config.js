const path = require('path');

module.exports = {
  entry: './src/index.js',  // 메인 엔트리 포인트
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  mode: 'development',
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
      {
        test: /\.css$/,  // CSS 파일 로더
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  devServer: {
    contentBase: path.resolve(__dirname, 'dist'),
    compress: true,
    port: 9000,
  },
};
