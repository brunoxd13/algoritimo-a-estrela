/*
   Copyright 2016 -  José Victor Alves de Souza - https://github.com/dudevictor/

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
 */
#include <iostream>
#include <opencv2/opencv.hpp>

using namespace cv;
using namespace std;

int main(int argc, char** argv){
    Mat image;
    VideoCapture cap;
    vector<Mat> channels;

    image= imread(argv[1], CV_LOAD_IMAGE_COLOR);
    imshow("original", image);

    Mat imagemYCrCb;
    cvtColor(image, imagemYCrCb, CV_BGR2YCrCb);

    split(imagemYCrCb, channels);
    equalizeHist(channels[0], channels[0]);
    merge(channels, imagemYCrCb);
    Mat result;
    cvtColor(imagemYCrCb, result, CV_YCrCb2BGR);
    namedWindow("image", WINDOW_AUTOSIZE);
    imshow("image", result);
    waitKey();
    return 0;
}

