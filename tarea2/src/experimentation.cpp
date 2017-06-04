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



vector<pair<int,double>> experiment(int index, int cores, int window_size, double std_dev,
			  string imageName, bool show, bool save, bool core_increase,
			  bool compare){
   
  int interval; //Ancho de cada franja de la imagen asignada a un thread

  //Vector de threads para las pruebas paralelizadas
  vector<thread> threads(cores);

  //Vector que almacena el número de threads y el tiempo de ejecución por prueba
  vector<pair<int,double>> core_num_time;

  //Vectores que almacenan la información asociada a las imágenes
  vector<Mat*> mats; 
  vector<Image_wrapper*> images;

  //Imagen de control (original)
  Mat* control_mat = new Mat(imread(imageName, 1));
  Image_wrapper control(control_mat);

  
  //------------------------------------------------------------------------
  //Parte secuencial
  //------------------------------------------------------------------------

  //Imagen secuencial  
  core_num_time.push_back(make_pair(1,double()));
  mats.push_back(new Mat(control_mat->rows, control_mat->cols, control_mat->type()));
  images.push_back(new Image_wrapper(mats[0]));
  
  cout<<"Proceso secuencial..."<<endl;
  auto begin = chrono::high_resolution_clock::now(); //Inicio del tiempo de la prueba

  //Ejecución del filtro gaussiano para la prueba secuencial
  gaussian_filter(images[0], &control, window_size, std_dev, 0, images[0]->get_width());

  auto end = chrono::high_resolution_clock::now(); //Fin del tiempo de la prueba

  //Se guarda el tiempo de ejecución de la prueba secuencial
  core_num_time[0].second =
     chrono::duration_cast<chrono::nanoseconds>(end-begin).count();


  //------------------------------------------------------------------------
  //Parte paralelizada
  //------------------------------------------------------------------------

  //Inicializar pruebas paralelizadas
  for(int num_cores=2; num_cores <= cores; num_cores++){
     if((num_cores<cores && core_increase) || (num_cores==cores)){
	core_num_time.push_back(make_pair(num_cores,double()));
     }
  }
  int num_tests = core_num_time.size();

  //FIXME: Change to smart_ptr
  for (int img=1; img < num_tests; img++){ 
     mats.push_back(new Mat(control_mat->rows, control_mat->cols, control_mat->type()));
     images.push_back(new Image_wrapper(mats[img]));
  }

  //Se itera sobre todas las pruebas, cada una con distinta cantidad de threads
  for (int test=1; test<num_tests; test++){
     int num_cores = core_num_time[test].first;
     
     cout<<"Proceso paralelo con "<<num_cores<<" threads..."<<endl;
     interval = images[test]->get_width()/num_cores; //Se establece el ancho de cada franja

     begin = chrono::high_resolution_clock::now(); //Inicio del tiempo de la prueba
     for (int core_id=0; core_id < num_cores; core_id++){
	//Ejecución del filtro gaussiano, a cada thread se le asigna una franja de la imagen
	threads[core_id] = thread(&gaussian_filter,
				  images[test],
				  &control,
				  window_size,
				  std_dev,
				  core_id*interval,
				  (core_id+1)*interval);
     }
     //Se espera a que terminen de ejecutarse todos los threads para continuar
     for (int core_id=0; core_id < num_cores; core_id++){
	threads[core_id].join();
     }
     end = chrono::high_resolution_clock::now(); //Fin del tiempo de la prueba

     //Se guarda el tiempo de ejecución para la prueba
     core_num_time[test].second =
	chrono::duration_cast<chrono::nanoseconds>(end-begin).count();
  }


  //------------------------------------------------------------------------
  //Visualización y comparación de imágenes
  //------------------------------------------------------------------------
  
  if (show) {
    cout<<"Cierre las ventanas para continuar ..."<<endl;
    show_images(index, control_mat, mats[0], mats.back());
  }
  if (save) {
    cout<<"Guardando resultados ..."<<endl;
    save_images(imageName, mats[0], mats.back());
  }
  if (compare) {
    cout<<"Comparando ambos resultados ..."<<endl;
    if (images[0]->compare(images.back())) cout<<"Resultados iguales!"<<endl;
    else cout<<"Error: Resultados distintos"<<endl;
  }
  
  return core_num_time;
}

vector<double> get_speed_up(vector<pair<int,double>> core_num_time){
   vector<double> result(core_num_time.size());

   for (unsigned int test=0; test < core_num_time.size(); test++){
      result[test]=core_num_time[0].second/core_num_time[test].second;
      cout<<"Num_cores: "<<core_num_time[test].first<<" => Speedup: "<<result[test]<<endl;
   }
   return result;
}
