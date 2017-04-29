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
int main(int qtdArg, char** args) {
    usage(qtdArg, args);
    Mat image;

    image= imread(args[1], CV_LOAD_IMAGE_COLOR);
    int width = image.size().width;
    int height = image.size().height;


    Mat A(image, Rect(0, 0, width/2, height/2));
    Mat B(image, Rect(width/2, 0, width/2, height/2));
    Mat C(image, Rect(0, height/2, width/2, height/2));
    Mat D(image, Rect(width/2, height/2, width/2, height/2));

    Mat saida = Mat::zeros(image.size(), image.type());
    Mat aux;

    aux = saida.colRange(0, width/2).rowRange(0, height/2);
    D.clone().copyTo(aux);

    aux = saida.colRange(width/2, width).rowRange(0, height/2);
    C.copyTo(aux);

    aux = saida.colRange(0, width/2).rowRange(height/2, height);
    B.copyTo(aux);

    aux = saida.colRange(width/2, width).rowRange(height/2, height);
    A.copyTo(aux);

    if(!image.data)
        cout << "nao abriu a imagem" << endl;

    namedWindow("janela", WINDOW_AUTOSIZE);

    imshow("janela", saida);
    waitKey();
    return 0;

}

void usage(int qtdArgs, char** args) {

    if (qtdArgs < 2) {
        printf("Uso: ./trocaregioes <nome_arquivo>\n");
        exit(0);
    }

}
