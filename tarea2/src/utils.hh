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

#include <algorithm>
#include <vector>
#include <string>

#ifndef UTILS_H
#define UTILS_H

using namespace std;

//Clase para el parseo de los argumentos de línea de comandos.
class Cmd_parser{
private:
   //Vector de strings que contiene los argumentos dados ejecutar el programa
   vector<string> input_vec;

public:
   //Constructor de la clase Cmd_parser, que recibe el array de argumentos del main
   Cmd_parser(int& argc, char **argv);   

   //Se obtiene el valor del parámetro indicado por el string flag
   string get_opt(const string& flag);
   //Se obtiene el vector de parámetros indicados por el string flag
   vector<string> get_multiple_opt(const string& flag);
   //Se indica si existe cierto argumento (string flag) en la lista de argumentos
   bool opt_exists(const string& flag);
};

/*Estructura para almacenar los parámetros obtenidos del parseo de la
 * línea de comandos.
 */
struct Cmd_params{

   //Parámetros de interés para la ejecución del experimento
   int image_count=1, cores=4, window_size=10;
   double std_dev=3;
   vector<string> image_names = vector<string>(1);
   bool show=false, save=false, core_increase=false, compare=false;

   //Instancia de Cmd_parser para obtener los argumentos de línea de comandos
   Cmd_parser cmd_parse;

   //Constructor de la estructura Cmd_params
   Cmd_params(int& argc, char **argv);
};


#endif
