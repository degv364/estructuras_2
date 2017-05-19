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

#ifndef EXPERIMENTATION_H_
#define EXPERIMENTATION_H_

//Mostrar las imagenes generadas y la original
void show_images(int index, Mat* control_mat, Mat* sec_mat, Mat* par_mat);

//Guardar las imagenes generadas
void save_images(string name, Mat* sec_mat, Mat* par_mat);

//Aplicar el filtro gaussiano de manera secuencial y paralela a una imagen
vector<double> experiment(int index, int cores, int window_size, string imageName,
			  bool show, bool save, bool core_path, bool compare);

//Analisis de speedup
vector<double> get_speed_up(vector<double> times);

#endif
