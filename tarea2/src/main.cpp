/* Copyright (c) 2017 
 Authors: Daniel Garcia Vaglio, Esteban Zamora Alvarado

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>
*/

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include "image_wrapper.hh"
#include <mutex>
#include <thread>
#include <vector>
#include <stdlib.h>

using namespace cv;
using namespace std;

int main(int argc, char** argv ){
  //Primer argumento cant de threads, segundo tamano de la ventana
  int cores=4, window_size=10;
  double std_dev=3;
  if (argc>2){
    cores= atoi(argv[1]);
    window_size= atoi(argv[2]);
    std_dev=window_size/2;
  }
  int interval; //interval for divinding the image
  mutex m; //no se esta ocupando, no se si para el gaussiano si
  char* imageName = "Highimgnoise.jpg";//FIXME: hardcodeado
  vector<thread> ths(cores);//vector con los threads

  //FIXME: utilizar constructor de copia, no estar abriendo el file, pero si se necesita
  //que sean Mats distintos, para no modificar la imagen original.
  Mat* imagex = new Mat(imread( imageName, 1 ));
  Mat* filteredx = new Mat(imread(imageName, 1));
  Mat* filteredp = new Mat(imread(imageName, 1));
  Mat* gauss_seqx= new Mat(imread(imageName, 1));

  //estos son wrappers (creo qeu esta mal escrito) para facilitarme al existencia
  Image_wrapper image(&m, imagex);
  Image_wrapper filtered(&m, filteredx);
  Image_wrapper parallel(&m, filteredp);
  Image_wrapper gauss_seq(&m, gauss_seqx);

  //hacer la parte secuencial
  auto begin = chrono::high_resolution_clock::now();
  //median_filter(&filtered, &image, window_size, 0, image.get_width());
  gaussian_filter(&gauss_seq, &image, std_dev, 0, image.get_width());
  auto end = chrono::high_resolution_clock::now();
  auto sequential=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();
  cout<<"sequantial: "<<sequential<< "ns" << endl;

  //hacer la parte en paralelo
  interval=image.get_width()/cores;
  begin = chrono::high_resolution_clock::now();
  for (int core=0; core<cores; core++){
    //a cada thrad se le asigna una parte de la imagen
    //ths[core]=thread(&median_filter, &parallel, &image, window_size, core*interval, (core+1)*interval);
    ths[core]=thread(&gaussian_filter, &parallel, &image, std_dev, core*interval, (core+1)*interval);
  }
  for (int core=0; core<cores; core++){
    //esperar a la ejecuccion de todos
    (ths[core]).join();
  }
  end = chrono::high_resolution_clock::now();
  auto parallel_t=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();
  cout<<"parallel: "<<parallel_t<< "ns" << endl;

  //comparacion final
  cout<<"Parallel is "<<sequential-parallel_t<<"ns faster"<<endl;
  cout<<"Parallel is "<<((double) sequential)/((double) parallel_t)<<" times faster"<<endl;
  
  //show de lso resultados
  namedWindow( imageName, CV_WINDOW_KEEPRATIO );
  //namedWindow( "Sequential", CV_WINDOW_KEEPRATIO );
  namedWindow( "Sequential_Gauss", CV_WINDOW_KEEPRATIO );
  namedWindow( "Parallel", CV_WINDOW_KEEPRATIO );
  
  imshow( imageName, *imagex );
  //imshow( "Sequential", *filteredx );
  imshow( "Sequential_Gauss", *gauss_seqx );
  imshow( "Parallel", *filteredp );
  
  waitKey(0);
  return 0;
}
