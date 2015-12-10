#include <cv.h>
#include <highgui.h>



int main () {

	cv::VideoCapture cap(0);

	while (true) {
		cv::Mat image;
		cap >> image;

		cv::imshow("hey", image);
		cv::waitKey(10);
	}

}