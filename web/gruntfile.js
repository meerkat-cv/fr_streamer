module.exports = function(grunt) {
  'use strict';

//require('load-grunt-tasks')(grunt); // npm install --save-dev load-grunt-tasks

grunt.initConfig({
    connect: {
      server: {
        options: {
          protocol: 'https',
          hostname: '0.0.0.0',
          port: 8080,
          base: './',
          keepalive: true
        }
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.registerTask('default', ['connect']);
};