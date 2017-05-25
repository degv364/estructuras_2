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



vector<double> experiment(int index, int cores, int window_size, double std_dev,
			  string imageName, bool show, bool save, bool core_increase,
			  bool compare){
  int interval; // intervalo para dividir la imagen
  mutex m; // FIXME: tal vez no sea necesario
  vector<thread> threads(cores); //vector con los threads
  vector<double> times(2); //vector donde se guardan los resultados de tiempo
  vector<Mat*> mats(2); //vector donde se guardan las matrices
  vector<Image_wrapper*> images(2); //vector donde se guardan las imagenes

  //FIXME: utilizar constructor de copia para no tener que
  //estar abiendo imagenes, pero si se necesita que sean
  // Mats distintos
  cout<<"entering experiment"<<endl;
  //imagen de control
  Mat* control_mat = new Mat(imread(imageName, 1));
  Image_wrapper control(&m, control_mat);

  //imagen secuencial
  mats[0]= new Mat(imread(imageName, 1));
  images[0] = new Image_wrapper(&m, mats[0]);

  //si necesario, crear las imagenes para cada cantidad de cores
  if (core_increase){
    mats.resize(cores);
    images.resize(cores);

    for (int img=1; img < cores-1; img++){
      mats[img]= new Mat(imread(imageName, 1));
      images[img] = new Image_wrapper(&m, mats[img]);
    }
  }
  
  //create image for fully parallel
  mats.back()=new Mat(imread(imageName, 1));
  images.back()= new Image_wrapper(&m, mats.back());

  //------------------------------------------------------------------------
  //Parte secuencial
  //------------------------------------------------------------------------

  cout<<"Proceso secuencial..."<<endl;
  auto begin = chrono::high_resolution_clock::now();
  gaussian_filter(images[0], &control, std_dev, 0, images[0]->get_width());
  auto end = chrono::high_resolution_clock::now();
  times[0]=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();


  //------------------------------------------------------------------------
  //Parte paralelizada incremental
  //------------------------------------------------------------------------
  
  if (core_increase == true){

     times.resize(cores);
    //hacer el recorrrido por las cantidades de cores, en paralelo
    for (int core_i=2; core_i<cores; core_i++){
      cout<<"Proceso paralelo con "<<core_i<<" cores..."<<endl;
      interval=images[core_i-1]->get_width()/core_i;
      begin = chrono::high_resolution_clock::now();

      for (int core=0; core<core_i; core++){
	//a cada thread se le asigna una parte de la imagen
	threads[core] = thread(&gaussian_filter,
			       images[core_i-1],
			       &control,
			       std_dev,
			       core*interval,
			       (core+1)*interval);
      }
      for (int core=0; core<core_i; core++){
	//esperar a la ejecuccion de todos
	(threads[core]).join();
      }
      end = chrono::high_resolution_clock::now();
      times[core_i-1]=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();
    }
  }
  
  //hacer la parte paralela, contodos los cores
  cout<<"Proceso paralelo con "<<cores<<" cores..."<<endl;
  interval=images.back()->get_width()/cores;
  begin = chrono::high_resolution_clock::now();
  for (int core=0; core<cores; core++){
    //a cada thread se le asigna una parte de la imagen
    threads[core]=thread(&gaussian_filter, images.back(), &control, std_dev, core*interval, (core+1)*interval);
  }
  for (int core=0; core<cores; core++){
    //esperar a la ejecuccion de todos
    (threads[core]).join();
  }
  end = chrono::high_resolution_clock::now();
  times.back()=chrono::duration_cast<chrono::nanoseconds>(end-begin).count();

  //el procesamiento de varios cores es para obtener tiempos, entonces esta parte puede
  //quedar igual
  if (show==true) {
    cout<<"Cierre las ventanas para continuar ..."<<endl;
    show_images(index, control_mat, mats[0], mats.back());
  }
  if (save==true) {
    cout<<"Guardando resultados ..."<<endl;
    save_images(imageName, mats[0], mats.back());
  }
  if (compare==true){
    cout<<"Comparando ambos resultados ..."<<endl;
    if (images[0]->compare(images.back())) cout<<"Resultados iguales!"<<endl;
    else cout<<"**ERROR**"<<endl;
  }

  
  return times;
}

vector<double> get_speed_up(vector<double> times){
  vector<double> result(times.size());
  for (unsigned int i=0; i<times.size(); i++){
    result[i]=times[0]/times[i];
    cout<<i+1<<" "<<result[i]<<endl;
  }
  return result;
}
