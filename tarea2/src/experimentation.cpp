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

#include "image_wrapper.hh"
#include "experimentation.hh"

using namespace cv;
using namespace std;



void show_images(int index, Mat* control_mat, Mat* sec_mat, Mat* par_mat){
  string index_str = to_string(index); 
  namedWindow("Imagen original "+index_str, CV_WINDOW_KEEPRATIO);
  namedWindow("Imagen secuencial "+index_str, CV_WINDOW_KEEPRATIO);
  namedWindow("Imagen paralela "+index_str, CV_WINDOW_KEEPRATIO);
  imshow("Imagen original "+index_str, *control_mat);
  imshow("Imagen secuencial "+index_str, *sec_mat);
  imshow("Imagen paralela "+index_str, *par_mat);
  waitKey(0);
}

void save_images(string name, Mat* sec_mat, Mat* par_mat){
  imwrite(name+".secuencial.jpg", *sec_mat);
  imwrite(name+".paralelo.jpg", *par_mat);
}


vector<double> experiment(int index, int cores, int window_size, string imageName,
			  bool show, bool save){
  vector<double> result(2);
  int interval; // intervalo para dividir la imagen
  mutex m; // FIXME: tal vez no sea necesario
  vector<thread> ths(cores); //vector con los threads
  double std_dev=3;

  //FIXME: utilizar constructor de copia para no tener que
  //estar abiendo imagenes, pero si se necesita que sean
  // Mats distintos

  Mat* control_mat = new Mat(imread(imageName, 1));
  Mat* sec_mat = new Mat(imread(imageName, 1));
  Mat* par_mat = new Mat(imread(imageName, 1));
  Image_wrapper control(&m, control_mat); //imagen de control
  Image_wrapper sec(&m, sec_mat); //imagen para operaciones secuenciales
  Image_wrapper par(&m, par_mat); //imagen para operaciones paralelas

  //hacer la parte secuencial
  cout<<"Proceso secuencial..."<<endl;
  auto begin = chrono::high_resolution_clock::now();
  gaussian_filter(&sec, &control, std_dev, 0, sec.get_width());
  auto end = chrono::high_resolution_clock::now();
  auto sequential_t=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();

  //hacer la parte paralela
  cout<<"Proceso paralelo..."<<endl;
  interval=par.get_width()/cores;
  begin = chrono::high_resolution_clock::now();
  for (int core=0; core<cores; core++){
    //a cada thread se le asigna una parte de la imagen
    ths[core]=thread(&gaussian_filter, &par, &control, std_dev, core*interval, (core+1)*interval);
  }
  for (int core=0; core<cores; core++){
    //esperar a la ejecuccion de todos
    (ths[core]).join();
  }
  end = chrono::high_resolution_clock::now();
  auto parallel_t=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();

  
  if (show==true) {
    cout<<"Cierre las ventanas para continuar ..."<<endl;
    show_images(index, control_mat, sec_mat, par_mat);
  }
  if (save==true) {
    cout<<"Guardando resultados ..."<<endl;
    save_images(imageName, sec_mat, par_mat);
  }
  result[0]=sequential_t;
  result[1]=parallel_t;
  return result;
}
