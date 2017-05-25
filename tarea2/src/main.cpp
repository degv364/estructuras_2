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

int main(int argc, char** argv ){

   vector<vector<double>> exec_time;
  
   Cmd_params cmd(argc, argv);
   

   exec_time.resize(cmd.image_count);

   for (int img=0; img<cmd.image_count; img++){

      cout<<"Filtrando "<<cmd.image_names[img]<<" ..."<<endl;
      exec_time[img]=experiment(img,
				cmd.cores,
				cmd.window_size,
				cmd.std_dev,
				cmd.image_names[img],
				cmd.show,
				cmd.save,
				cmd.core_increase,
				cmd.compare);

      auto n=get_speed_up(exec_time[img]);
   }
  
  
   return 0;
}
