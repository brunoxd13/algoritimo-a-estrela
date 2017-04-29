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
#include <math.h>

using namespace cv;
using namespace std;

int deepMedia = 7;
int height;

int MAX = 100;
double decaimento = 6;
int decaimento_slider = 0;

int top_slider = 0;
int posicao_vertical = 0;

int tamanho_faixa = 20;
int altura_slider = 0;


Mat image1, image2, alpha, beta;

char TrackbarName[50];

void updateScene() {
    Mat outputImagemBorrada, outputImagemOriginal;
    image1.convertTo(outputImagemOriginal, CV_32FC3);
    image2.convertTo(outputImagemBorrada, CV_32FC3);
    multiply(outputImagemOriginal, alpha, outputImagemOriginal);
    multiply(outputImagemBorrada, beta, outputImagemBorrada);
    Mat imageTiltShift;

    add(outputImagemOriginal, outputImagemBorrada, imageTiltShift);
    imageTiltShift.convertTo(imageTiltShift, CV_8UC3);
    imshow("tiltshift", imageTiltShift);
}

void calcWeighing() {
    int l1 = - tamanho_faixa/2;
    int l2 = -l1;

    alpha = Mat::zeros(image1.rows, image1.cols, CV_32F);
    beta = Mat::zeros(image1.rows, image1.cols, CV_32F);
    int i, j;
    for (i = 0; i < alpha.rows; i++) {
        int x = i - (posicao_vertical + tamanho_faixa/2);
        float alphaValue = 0.5f * (tanh((x - l1)/decaimento) - tanh((x - l2)/decaimento));
        for (j = 0; j < alpha.cols; j++) {
            alpha.at<float>(i, j) = alphaValue;
            beta.at<float>(i, j) = 1 - alphaValue;
        }
    }
    Mat auxA[] = {alpha, alpha, alpha};
    Mat auxB[] = {beta, beta, beta};
    merge(auxA, 3, alpha);
    merge(auxB, 3, beta);
    updateScene();
}

void on_trackbar_decaimento(int, void*){
    decaimento = (double) decaimento_slider;
    if (decaimento < 1) {
        decaimento = 1;
    }
    calcWeighing();
}

void on_trackbar_posicaoVertical(int, void *){
    posicao_vertical = top_slider*height/MAX;
    calcWeighing();
}

void on_trackbar_altura_regiao(int, void*) {
    tamanho_faixa = altura_slider*height/MAX;
    if (tamanho_faixa == 0) {
        tamanho_faixa = 1;
    }

    if (tamanho_faixa > height) {
        tamanho_faixa = height;
    }
    calcWeighing();
}

int main(int argvc, char** argv){
    image1 = imread("tilt/traffic_newyorkcity.jpg");
    height = image1.size().height;
    image2 = image1.clone();
    Mat aux, mask, mask1;
    float media[] = {1,1,1,
                     1,1,1,
                     1,1,1};

    mask = Mat(3, 3, CV_32F, media);
    scaleAdd(mask, 1/9.0, Mat::zeros(3,3,CV_32F), mask1);
    mask = mask1;
    image2.convertTo(aux, CV_32F);
    for (int i = 0; i < deepMedia; i++) {
        filter2D(aux, aux, aux.depth(), mask, Point(1, 1), 0);
    }
    aux=abs(aux);


    aux.convertTo(image2, CV_8UC3);

    namedWindow("tiltshift", 1);

    sprintf( TrackbarName, "Altura da região");
    createTrackbar( TrackbarName, "tiltshift",
                    &altura_slider,
                    MAX,
                    on_trackbar_altura_regiao);

    sprintf( TrackbarName, "Decaimento");
    createTrackbar( TrackbarName, "tiltshift",
                    &decaimento_slider,
                    MAX,
                    on_trackbar_decaimento);

    sprintf( TrackbarName, "Posição Vertical");
    createTrackbar( TrackbarName, "tiltshift",
                    &top_slider,
                    MAX,
                    on_trackbar_posicaoVertical );
    calcWeighing();
    waitKey(0);

    return 0;
}
