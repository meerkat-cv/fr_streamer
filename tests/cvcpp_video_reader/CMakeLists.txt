project( cvcpp_video_reader )
cmake_minimum_required(VERSION 2.8)  
find_package( OpenCV REQUIRED )
add_executable( cvcpp_video_reader
		  cvcpp_video_reader.cpp
		)
target_link_libraries(cvcpp_video_reader ${OpenCV_LIBS})
