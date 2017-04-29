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

int main(int argc, char** argv){
  Mat image, mask;
  int width, height;
  int nobjects;
  int BRANCO = 255;
  int PRETO = 0;
  int BACKGROUND = 1;
  int COM_BOLHA = 67;
  int SEM_BOLHA = 196;
  CvPoint p;
  p.x = 0;
  p.y = 0;
  image = imread(argv[1],CV_LOAD_IMAGE_GRAYSCALE);

  if(!image.data){
    std::cout << "imagem nao carregou corretamente\n";
    return(-1);
  }
  imshow("imageOriginal", image);
  width=image.size().width;
  height=image.size().height;

  //Aplica 255 em todos os pontos na borda da
  // imagem e aplica-se o floodfill para remover os elementos que tocam as bordas
  for (int i = 0; i < width; i++) {
    image.at<uchar>(i, height -1) = BRANCO;
    image.at<uchar>(i, 0) = BRANCO;
  }

  for (int i = 0; i < height; i++) {
    image.at<uchar>(0, i) = BRANCO;
    image.at<uchar>(width -1, i) = BRANCO;
  }
  //Aplica-se o floodfill no ponto (0, 0) removendo todos os elementos da borda
  floodFill(image, p, PRETO);

  //Aplica-se o floodfill em todo o background da imagem
  floodFill(image, p, BACKGROUND);


  //Procurando por Elementos, julgando inicialmente que nenhum tem bolhas
  int qtdTotal = 0;
  for (int i = 0; i < height; i++) {
    for (int j = 0; j < width; j++) {
      if (image.at<uchar>(i, j) == BRANCO) {
        p.x = j;
        p.y = i;
        floodFill(image, p, SEM_BOLHA);
        qtdTotal++;
      }
    }
  }

  //Procurando por Elementos que possuem bolhas
  int qtdComBolhas = 0;
  for (int i = 0; i < height; i++) {
    for (int j = 0; j < width; j++) {
      //Armazene a posição do elemento encontrado, independente se for rotulado com bolha ou sem bolha
      if (image.at<uchar>(i,j) == SEM_BOLHA || image.at<uchar>(i,j) == COM_BOLHA) {
        p.x = j;
        p.y = i;
      } else if (image.at<uchar>(i,j) == PRETO) {
        //Caso for encontrado um buraco (rotulo PRETO), rotule o ultimo elemento encontrado como "COM_BOLHA",
         //se ele não já tiver sido rotulado como um
        if (image.at<uchar>(p.y, p.x) == SEM_BOLHA) {
          floodFill(image, p, COM_BOLHA);
          qtdComBolhas++;
        }
        //Rotule o buraco encontrado como COM_BOLHA (poderia ser um rótulo diferente também)
        p.x = j;
        p.y = i;
        floodFill(image, p, COM_BOLHA);
      }
    }
  }

  imshow("image", image);
  imwrite("labeling.png", image);
  printf("Quantidade de elementos sem bolhas: %d, com bolhas: %d\n", qtdTotal - qtdComBolhas, qtdComBolhas);
  waitKey();
  return 0;
}
