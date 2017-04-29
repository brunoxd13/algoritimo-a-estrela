/**
 * Desenvolvido por José Victor Alves de Souza para a disciplina de Processamento Digital de Imagens
 * lecionada por Agostinho, DCA, UFRN.
 */
#include <iostream>
#include "opencv2/opencv.hpp"

using namespace std;
using namespace cv;

int top_slider = 70;
int top_slider_max = 200;

int raio_slider = 5;
int jitter = 3;
int step = 5;

int width, height;

struct Ponto {
    int x, y;
};

#define RAIO_MAX 10
#define JITTER_MAX 10
#define STEP_MAX 20

char TrackbarName[50];

Mat image, border, points;

void calcPontilhismo() {
  vector<int> yrange;
  vector<int> xrange;
  int width, height;
  int x, y;

  width=image.size().width;
  height=image.size().height;

  xrange.resize(height/step);
  yrange.resize(width/step);

  iota(xrange.begin(), xrange.end(), 0);
  iota(yrange.begin(), yrange.end(), 0);

  for(uint i=0; i<xrange.size(); i++){
    xrange[i]= xrange[i]*step+step/2;
  }

  for(uint i=0; i<yrange.size(); i++){
    yrange[i]= yrange[i]*step+step/2;
  }


  points = Mat(height, width, CV_8U, Scalar(255, 255, 255));

  random_shuffle(xrange.begin(), xrange.end());


  uchar cor;

  for(auto i : xrange){
    random_shuffle(yrange.begin(), yrange.end());
    for(auto j : yrange){
      x = i+rand()%(2*jitter)-jitter+1;
      y = j+rand()%(2*jitter)-jitter+1;
      cor = image.at<uchar>(x,y);
      circle(points,
             cv::Point(y,x),
             raio_slider,
             Scalar(cor,cor,cor),
             -1,
             CV_AA);
    }
  }


  vector<vector<Point>> contornos;
  vector<Vec4i> hierarquia;
  findContours(border, contornos, hierarquia, CV_RETR_TREE, CV_CHAIN_APPROX_NONE);
  for (int i = 0; i < contornos.size(); i++){
    for (int j = 0; j < contornos[i].size(); j++) {
      uchar cor = image.at<uchar>(contornos[i][j].y, contornos[i][j].x);
      circle(points, cv::Point(contornos[i][j].x, contornos[i][j].y),
      1,
      CV_RGB(cor, cor, cor),
      -1,
      CV_AA);
    }
  }

  imshow("cannypoints", points);


}

void on_trackbar_pontilhismo(int, void*) {

  if (jitter < 1) jitter = 1;
  if (raio_slider < 1) raio_slider = 1;
  if (step < 1) step = 1;
  calcPontilhismo();
  imshow("canny", border);

}

void on_trackbar_canny(int, void*){
  Canny(image, border, top_slider, 3*top_slider);
  on_trackbar_pontilhismo(top_slider, 0);

}

int main(int argc, char**argv){

  image= imread(argv[1],CV_LOAD_IMAGE_GRAYSCALE);
  
  width=image.size().width;
  height=image.size().height;

  sprintf( TrackbarName, "Threshold Canny");

  namedWindow("cannypoints",1);
  createTrackbar( TrackbarName, "cannypoints",
                &top_slider,
                top_slider_max,
                on_trackbar_canny );

  sprintf( TrackbarName, "Raio");
  createTrackbar( TrackbarName, "cannypoints",
                  &raio_slider,
                  RAIO_MAX,
                  on_trackbar_pontilhismo );

  sprintf( TrackbarName, "Jitter");
  createTrackbar( TrackbarName, "cannypoints",
                  &jitter,
                  JITTER_MAX,
                  on_trackbar_pontilhismo );

  sprintf( TrackbarName, "Step");
  createTrackbar( TrackbarName, "cannypoints",
                  &step,
                  STEP_MAX,
                  on_trackbar_pontilhismo );

  on_trackbar_canny(top_slider, 0 );

  waitKey();
  return 0;
}
