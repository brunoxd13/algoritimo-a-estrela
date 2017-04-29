#include <iostream>
#include <opencv2/opencv.hpp>
#include <math.h>

using namespace cv;
using namespace std;

int height;

int dft_M, dft_N;

float MAX = 100.0;
float yl = 0;
float max_yl = 100;
int yl_slider = 0;

int d0_slider = 0;
float max_d0 = 256;
float d0 = 0;

float yh = 0;
float max_yh = 100;
int yh_slider = 0;


Mat image, imageDft, padded;

char TrackbarName[50];

// troca os quadrantes da imagem da DFT
void deslocaDFT(Mat& image ){
    Mat tmp, A, B, C, D;

    // se a imagem tiver tamanho impar, recorta a regiao para
    // evitar cópias de tamanho desigual
    image = image(Rect(0, 0, image.cols & -2, image.rows & -2));
    int cx = image.cols/2;
    int cy = image.rows/2;

    // reorganiza os quadrantes da transformada
    // A B   ->  D C
    // C D       B A
    A = image(Rect(0, 0, cx, cy));
    B = image(Rect(cx, 0, cx, cy));
    C = image(Rect(0, cy, cx, cy));
    D = image(Rect(cx, cy, cx, cy));

    // A <-> D
    A.copyTo(tmp);  D.copyTo(A);  tmp.copyTo(D);

    // C <-> B
    C.copyTo(tmp);  B.copyTo(C);  tmp.copyTo(B);
}

void calcHomomorphicFilter() {
    Mat filter = Mat(padded.size(), CV_32FC2, Scalar(0));
    Mat tmp = Mat(dft_M, dft_N, CV_32F);

    for (int i = 0; i < dft_M; i++) {
        for (int j = 0; j < dft_N; j++) {
            float d2 = pow(i - dft_M/2.0, 2) + pow(j - dft_N/2.0, 2);
            float exp = - (d2/pow(d0, 2));
            float valor = (yh - yl)*(1 - expf(exp) ) + yl;
            tmp.at<float> (i,j) = valor;
        }
    }

    Mat comps[] = {tmp, tmp};
    merge(comps, 2, filter);

    Mat dftClone = imageDft.clone();

    mulSpectrums(dftClone,filter,dftClone,0);

    deslocaDFT(dftClone);

    idft(dftClone, dftClone);

    vector<Mat> planos;

    split (dftClone, planos);

    normalize(planos[0], planos[0], 0, 1, CV_MINMAX);

    char bufferd0[20], bufferyh[20], bufferyl[20];
    sprintf(bufferd0, "D0: %f", d0);
    sprintf(bufferyh, "Yh: %f", yh);
    sprintf(bufferyl, "Yl: %f", yl);
    putText(planos[0], bufferd0,cv::Point(0,10), CV_FONT_HERSHEY_SIMPLEX, 0.35, cv::Scalar(255),1,8,false);
    putText(planos[0], bufferyh,cv::Point(0,20), CV_FONT_HERSHEY_SIMPLEX, 0.35, cv::Scalar(255),1,8,false);
    putText(planos[0], bufferyl,cv::Point(0,30), CV_FONT_HERSHEY_SIMPLEX, 0.35, cv::Scalar(255),1,8,false);
    imshow("Filtro Homomorfico", planos[0]);
    imshow("Original", image);
}

void on_trackbar_yl(int, void*){
    yl = (float) yl_slider;
    yl = max_yl*yl/MAX;
    calcHomomorphicFilter();
}

void on_trackbar_d0(int, void *){
    d0 = d0_slider*max_d0/MAX;
    calcHomomorphicFilter();
}

void on_trackbar_yh(int, void*) {
    yh = yh_slider*max_yh/MAX;

    calcHomomorphicFilter();
}

int main(int argvc, char** argv){
    image = imread("homomorfica.png");
    cvtColor(image, image, CV_BGR2GRAY);

    height = image.size().height;

    // identifica os tamanhos otimos para
    // calculo do FFT
    dft_M = getOptimalDFTSize(image.rows);
    dft_N = getOptimalDFTSize(image.cols);

    // realiza o padding da imagem
    Mat_<float> zeros;
    copyMakeBorder(image, padded, 0,
                   dft_M - image.rows, 0,
                   dft_N - image.cols,
                   BORDER_CONSTANT, Scalar::all(0));

    // parte imaginaria da matriz complexa (preenchida com zeros)
    zeros = Mat_<float>::zeros(padded.size());

    // prepara a matriz complexa para ser preenchida
    imageDft = Mat(padded.size(), CV_32FC2, Scalar(0));

    copyMakeBorder(image, padded, 0,
                   dft_M - image.rows, 0,
                   dft_N - image.cols,
                   BORDER_CONSTANT, Scalar::all(0));

    Mat_<float> realInput = Mat_<float>(padded);

    // insere as duas componentes no array de matrizes
    vector<Mat> planos;
    planos.push_back(realInput);
    planos.push_back(zeros);

    // combina o array de matrizes em uma unica
    // componente complexa
    merge(planos, imageDft);

    // calcula o dft
    dft(imageDft, imageDft);
    deslocaDFT(imageDft);

    namedWindow("Filtro Homomorfico", 1);

    sprintf( TrackbarName, "Yh");
    createTrackbar( TrackbarName, "Filtro Homomorfico",
                    &yh_slider,
                    MAX,
                    on_trackbar_yh);

    sprintf( TrackbarName, "YL");
    createTrackbar( TrackbarName, "Filtro Homomorfico",
                    &yl_slider,
                    MAX,
                    on_trackbar_yl);

    sprintf( TrackbarName, "D0");
    createTrackbar( TrackbarName, "Filtro Homomorfico",
                    &d0_slider,
                    MAX,
                    on_trackbar_d0 );
    calcHomomorphicFilter();
    waitKey(0);

    return 0;
}
