const path = require('path');

module.exports = {
    mode: 'production',
    entry: './src/index.js',
    output: {
        filename: 'alpine.js',
        path: path.resolve(__dirname, '../static/js/'),
    },
};

