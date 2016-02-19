(function (global, $) {
    'use strict';

    var WS_Recognition = {};

    WS_Recognition.init = function () {
    	this.w = 640;
    	this.h = 480;
    	var self = this;

        $(document).ready(function () {
            self.bind();
            self.startVideo();
            $("[name='start_cam']").bootstrapSwitch();
            self.connectWS();
        });
    };

    WS_Recognition.bind = function () {
        this.video = $("#videoElement");

    	var self = this;
        $("[name='start_cam']").on('switchChange.bootstrapSwitch', function (event, state) {
        	if (state == false) {
        		self.videoStream.getVideoTracks()[0].stop();	
        		self.videoRunning = false;
        	}
        	else if (state == true) {
        		self.startVideo();
        	}
   		});

   		this.bindProcess();
    };

    WS_Recognition.startVideo = function () {
    	
	    var self = this;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia || navigator.oGetUserMedia;

        if (navigator.getUserMedia) {
            navigator.getUserMedia({
                video: true
            }, handleVideo, videoError);
        }

        function handleVideo(stream) {
        	self.videoRunning = true;
        	self.videoStream = stream;
        	self.video[0].src = window.URL.createObjectURL(stream);
        }

        function videoError(e) {
            console.log('Error from video');
        }
    };

    WS_Recognition.drawFace = function (ctx, face, color) {
    	if (face) {
            var w = (face['bottom_right']['x'] - face['top_left']['x']),
                h = (face['bottom_right']['y'] - face['top_left']['y']);
            ctx.beginPath();
            ctx.rect(face['top_left']['x'], face['top_left']['y'], w, h);
            ctx.lineWidth=4;
            ctx.strokeStyle=color;
            ctx.stroke();
        }

    }


    WS_Recognition.drawRecognition = function(ctx, data, minConfidence) {
    	var people_list = data["people"];
    	for (var i = 0; i < people_list.length; ++i) {
            var name = people_list[i]["recognition"]["predictedLabel"] || "?";
            
            var color = '#3a3a3a';
            if (people_list[i]["recognition"]["confidence"] > minConfidence)
                color = '#488efe';


            this.drawFace(ctx, people_list[i], color);

            if (people_list[i]["recognition"]["confidence"] > minConfidence) {
                ctx.font = "20px Arial";
                var width = ctx.measureText(name).width;
                ctx.fillStyle = color;
                ctx.fillRect(people_list[i]['top_left']['x']-2, people_list[i]['top_left']['y']-27, width+10, 26);

                ctx.fillStyle = "white";
                ctx.fillText(name, people_list[i]['top_left']['x']+2, people_list[i]['top_left']['y']-6);
            }

            var conf_string = 'Conf: '+Math.round(people_list[i]["recognition"]["confidence"]*100)/100;
            var width = ctx.measureText(conf_string).width;
            ctx.fillStyle = color;
            ctx.fillRect(people_list[i]['top_left']['x']-2, people_list[i]['bottom_right']['y']-27, width+10, 26);

            ctx.fillStyle = "white";
            ctx.fillText(conf_string, people_list[i]['top_left']['x']+2, people_list[i]['bottom_right']['y']-6);
        }
    }


    WS_Recognition.bindProcess = function() {
    	var self = this;

    	this.video[0].addEventListener('play', function() {
		   var canvas = document.getElementById("videoCanvas"),
    		   ctx = canvas.getContext('2d');
    		   

		   setInterval(function() {

		      if (self.video[0].paused || self.video[0].ended || !self.videoRunning) return;

		      ctx.fillRect(0, 0, self.w, self.h);
			  ctx.drawImage(self.video[0], 0, 0, self.w, self.h);

			  // get the image from video, put in a jpeg and send to server
		      if (self.connected) {
		      	canvas.toBlob(function(blob) {
      				self.frSocket.send(blob);
    			}, 'image/jpeg');

		      	self.drawRecognition(ctx, self.recognition_data, 40);
		      }


		   }, 80);
		}, false);
    }

    WS_Recognition.connectWS = function() {
    	this.frSocket = new WebSocket("ws://localhost:4444/recognize?api_key=27fe4653692be12294b02336e1950c99");

    	var self = this;
    	this.frSocket.onopen = function(event) {
    		self.connected = true;
    	}


    	this.frSocket.onmessage = function (event) {
 			 self.recognition_data = JSON.parse(event.data);
		}

    }


    global.ws_recognition = WS_Recognition;
    global.ws_recognition.init();
    


}(window, jQuery));
