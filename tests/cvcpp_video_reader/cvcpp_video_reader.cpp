#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>



int main () {

	cv::VideoCapture cap("http://admin:gremio83@192.168.0.52/video/mjpg.cgi?.mjpeg");

	while (true) {
		cv::Mat image;
		cap >> image;

		cv::imshow("hey", image);
		cv::waitKey(10);
	}

}