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
#include <mutex>
#include <thread>
#include <vector>
#include <stdlib.h>
#include "image_wrapper.hh"
#include "experimentation.hh"
using namespace cv;
using namespace std;

int main(int argc, char** argv ){
  //Primer argumento cant de threads, segundo tamano de la ventana
  //Del tercer argumento en adelante se escriben los nombres de las
  //imagenes que se desean analizar.
  vector<vector<double>> result_times;
  int image_cant;
  int cores=4, window_size=10;
  double std_dev=3;
  vector<string> image_names(1);
  bool show=false, save=false, core_path=false, compare=false;
  image_names[0]="Highimgnoise.jpg";
  if (argc>5){
    cores= atoi(argv[1]);
    window_size= atoi(argv[2]);
    std_dev=window_size/2;
    //if arg is 1, become true. 
    show=     (1==atoi(argv[3]));
    save=     (1==atoi(argv[4]));
    core_path=(1==atoi(argv[5]));
    compare=  (1==atoi(argv[6]));
  }
  if (argc>7){
    //image names were specified
    image_cant=argc-7;
    image_names.resize(image_cant);
    for (int i=0; i<image_cant; i++){
      image_names[i]=string(argv[i+7]);
    }
  }
  result_times.resize(image_cant);
  for (int img=0; img<image_cant; img++){
    cout<<"Filtrando "<<image_names[img]<<" ..."<<endl;
    result_times[img]=experiment(img, cores, window_size, image_names[img],
				 show, save, compare);
    
  }
  
  
  return 0;
}
