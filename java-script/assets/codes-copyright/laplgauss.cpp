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

void printmask(Mat &m){
    for(int i=0; i<m.size().height; i++){
        for(int j=0; j<m.size().width; j++){
            cout << m.at<float>(i,j) << ",";
        }
        cout << endl;
    }
}

void menu(){
    cout << "\npressione a tecla para ativar o filtro: \n"
            "a - calcular modulo\n"
            "m - media\n"
            "g - gauss\n"
            "v - vertical\n"
            "h - horizontal\n"
            "l - laplaciano\n"
            "b - Gaussiano Laplaciano\n"
            "esc - sair\n";
}

Mat applyMask(Mat cap, Mat mask, int absolut) {
    Mat frame, frame32f, frameFiltered, result;
    cvtColor(cap, frame, CV_BGR2GRAY);
    flip(frame, frame, 1);
    imshow("original", frame);
    frame.convertTo(frame32f, CV_32F);
    filter2D(frame32f, frameFiltered, frame32f.depth(), mask, Point(1,1), 0);
    if(absolut){
        frameFiltered=abs(frameFiltered);
    }
    frameFiltered.convertTo(result, CV_8U);

    return result;
}

Mat applyGausLaplace(Mat cap, Mat maskGaus, Mat maskLap, int absolut) {
    Mat frame, frame32f, frameFilteredGaus, frameFilteredLaplace, result;
    cvtColor(cap, frame, CV_BGR2GRAY);
    flip(frame, frame, 1);
    imshow("original", frame);
    frame.convertTo(frame32f, CV_32F);
    filter2D(frame32f, frameFilteredGaus, frame32f.depth(), maskGaus, Point(1,1), 0);
    //Apply Laplace
    filter2D(frameFilteredGaus, frameFilteredLaplace, frameFilteredGaus.depth(), maskLap, Point(1,1), 0);
    if(absolut){
        frameFilteredLaplace=abs(frameFilteredLaplace);
    }
    frameFilteredLaplace.convertTo(result, CV_8U);

    return result;
}

int main(int argvc, char** argv){
    VideoCapture video;
    float media[] = {1,1,1,
                     1,1,1,
                     1,1,1};
    float gauss[] = {1,2,1,
                     2,4,2,
                     1,2,1};
    float horizontal[]={-1,0,1,
                        -2,0,2,
                        -1,0,1};
    float vertical[]={-1,-2,-1,
                      0,0,0,
                      1,2,1};
    float laplacian[]={0,-1,0,
                       -1,4,-1,
                       0,-1,0};

    Mat mask(3,3,CV_32F), mask1;
    Mat result, result1;
    double width, height, min, max;
    int absolut;
    char key, lastKey;

    video.open(0);
    if(!video.isOpened())
        return -1;
    width=video.get(CV_CAP_PROP_FRAME_WIDTH);
    height=video.get(CV_CAP_PROP_FRAME_HEIGHT);
    std::cout << "largura=" << width << "\n";;
    std::cout << "altura =" << height<< "\n";;

    namedWindow("filtroespacial",1);

    mask = Mat(3, 3, CV_32F, media);
    scaleAdd(mask, 1/9.0, Mat::zeros(3,3,CV_32F), mask1);
    swap(mask, mask1);
    absolut=1; // calcs abs of the image

    menu();
    Mat cap;
    for(;;){
        video >> cap;
        if (lastKey == 'b') {
            Mat maskLaplacian = Mat(3, 3, CV_32F, laplacian);
            result = applyGausLaplace(cap, mask, maskLaplacian, absolut);
        } else {
            result = applyMask(cap, mask, absolut);
        }
        imshow("filtroespacial", result);
        key = (char) waitKey(10);
        if( key == 27 ) break; // esc pressed!
        switch(key){
            case 'a':
                menu();
                absolut=!absolut;
                break;
            case 'm':
                menu();
                mask = Mat(3, 3, CV_32F, media);
                scaleAdd(mask, 1/9.0, Mat::zeros(3,3,CV_32F), mask1);
                mask = mask1;
                printmask(mask);
                break;
            case 'g':
            case 'b':
                menu();
                mask = Mat(3, 3, CV_32F, gauss);
                scaleAdd(mask, 1/16.0, Mat::zeros(3,3,CV_32F), mask1);
                mask = mask1;
                printmask(mask);
                break;
            case 'h':
                menu();
                mask = Mat(3, 3, CV_32F, horizontal);
                printmask(mask);
                break;
            case 'v':
                menu();
                mask = Mat(3, 3, CV_32F, vertical);
                printmask(mask);
                break;
            case 'l':
                menu();
                mask = Mat(3, 3, CV_32F, laplacian);
                printmask(mask);
                break;
            default:
                break;
        }
        if (key != -1) {
            lastKey = key;
        }
    }
    return 0;
}