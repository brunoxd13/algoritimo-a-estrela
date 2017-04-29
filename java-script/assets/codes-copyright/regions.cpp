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
#include <cv.h>
#include <highgui.h>

using namespace cv;
using namespace std;

void usage(int qtdArgs, char** args);

int main(int qtdArg, char** args){
    usage(qtdArg, args);
    Mat image;

    image= imread(args[1], CV_LOAD_IMAGE_COLOR);

    int p1x = atoi(args[2]);
    int p1y = atoi(args[3]);
    int p2x = atoi(args[4]);
    int p2y = atoi(args[5]);

    if(!image.data)
        cout << "nao abriu a imagem" << endl;

    namedWindow("janela", WINDOW_AUTOSIZE);

    for(int i=p1x;i< p2x;i++) {
        for(int j=p1y; j< p2y;j++){
            Vec3b valor = image.at<Vec3b>(i,j);
            valor[0] = 255 - valor[0];
            valor[1] = 255 - valor[1];
            valor[2] = 255 - valor[2];
            image.at<Vec3b>(i,j) = valor;
        }
    }

    imshow("janela", image);
    waitKey();
    return 0;

}

void usage(int qtdArgs, char** args) {

    if (qtdArgs < 6) {
        printf("Uso: ./regions <nome_arquivo> X1 Y1 X2 Y2\n");
        exit(0);
    }

}