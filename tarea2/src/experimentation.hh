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

/* Función que muestra la imagen original (control) y las generadas por el
 * algoritmo (secuencial y paralelo)
 */

void show_images(int index, Mat* control_mat, Mat* sec_mat, Mat* par_mat);

//Función que guarda las imágenes generadas (secuencial y paralelo) en archivos
void save_images(string name, Mat* sec_mat, Mat* par_mat);

//Función que aplica el filtro gaussiano a una imagen de manera secuencial y paralelizada
vector<pair<int,double>> experiment(int index, int cores, int window_size, double std_dev,
			  string imageName, bool show, bool save, bool core_path, bool compare);

/*Función que calcula la razón de tiempo de cada prueba con respecto a la 
 * ejecución secuencial del algoritmo
 */
vector<double> get_speed_up(vector<pair<int,double>> times);

#endif
