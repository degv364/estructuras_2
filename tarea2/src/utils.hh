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

//Clase para parseo de los argumentos de linea de comandos.

class Cmd_parser{
private:
   vector<string> input_vec;

public:
   Cmd_parser(int& argc, char **argv);   

   string get_opt(const string& flag);
   vector<string> get_multiple_opt(const string& flag);
   bool opt_exists(const string& flag);
};


struct Cmd_params{

   int image_count=1, cores=4, window_size=10;
   double std_dev=3;
   vector<string> image_names = vector<string>(1);
   bool show=false, save=false, core_increase=false, compare=false;
   
   Cmd_parser cmd_parse;
   
   Cmd_params(int& argc, char **argv);
};


#endif
