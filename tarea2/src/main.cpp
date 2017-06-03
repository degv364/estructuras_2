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

#include "utils.hh"
#include "image_wrapper.hh"
#include "experimentation.hh"

using namespace cv;
using namespace std;

/* Función principal del programa en donde se itera por la lista de imágenes indicada para
 * ejecutar el experimento en cada una de estas, el cual consiste en un conjunto de pruebas
 * en donde se evalúa el filtro gaussiano para distintas cantidades de threads. 
 */

int main(int argc, char** argv ){
  //Vector donde se guardan los tiempos de ejecución y la cantidad de threads de cada prueba
  vector<vector<pair<int,double>>> exec_time;
  //Vector para almacenar el Speedup para cada prueba
  vector<double> speedup;
  //Obtención de los parámetros indicados por los argumentos de la terminal
  Cmd_params cmd(argc, argv);
  
  exec_time.resize(cmd.image_count);

  //Iterar por todas las imágenes, para ejecutar el experimento con cada una
  for (int img=0; img < cmd.image_count; img++){
    
    cout<<"Filtrando "<<cmd.image_names[img]<<" ..."<<endl;
    //Ejecución del experimento con los parámetros indicados
    exec_time[img]=experiment(img,
			      cmd.cores,
			      cmd.window_size,
			      cmd.std_dev,
			      cmd.image_names[img],
			      cmd.show,
			      cmd.save,
			      cmd.core_increase,
			      cmd.compare);

    //Se obtiene el Speedup para todas las pruebas de la imagen correspondiente
    speedup = get_speed_up(exec_time[img]);
  }
  
  return 0;
}
