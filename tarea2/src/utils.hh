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
#include <string>

#ifndef UTILS_H
#define UTILS_H

using namespace std;

class Cmd_parser{
private:
   vector<string> input_vec;

public:
   Cmd_parser(int& argc, char **argv){
      for(int i=1; i < argc; i++){
	 input_vec.push_back(std::string(argv[i]));
      }
   }
   
   string get_opt(const string& flag){
      string value = "";
      auto itr = find(input_vec.begin(), input_vec.end(), flag); 
      if(itr != input_vec.end() && ++itr != input_vec.end()){
	 value = *itr;
      }
      return value;
   }

   vector<string> get_multiple_opt(const string& flag){
      vector<string> values_vec;
      
      auto itr = input_vec.begin();
      auto end = input_vec.end();
      
      while(itr != end){
	 itr = find(itr, end, flag);

	 if(itr != end && ++itr != end){
	    values_vec.push_back(*itr);
	 }
      }
      return values_vec;
   }
   
   bool opt_exists(const string& flag){
      auto itr = find(input_vec.begin(), input_vec.end(), flag);
      return itr!=input_vec.end();
   }

};


struct Cmd_params{

   int image_count=1, cores=4, window_size=10;
   double std_dev=3;
   vector<string> image_names = vector<string>(1);
   bool show=false, save=false, core_increase=false, compare=false;

   Cmd_parser cmd_parse;
   
   Cmd_params(int& argc, char **argv)
      : cmd_parse(argc,argv)
   {
      show = cmd_parse.opt_exists("--show");
      save = cmd_parse.opt_exists("--save");
      core_increase = cmd_parse.opt_exists("--core_increase");
      compare = cmd_parse.opt_exists("--compare");

      if(cmd_parse.opt_exists("--cores"))
	 cores = stoi(cmd_parse.get_opt("--cores"));
  
      if(cmd_parse.opt_exists("--window_size"))
	 window_size = stoi(cmd_parse.get_opt("--window_size"));
  
      if(cmd_parse.opt_exists("--std_dev"))
	 std_dev = stod(cmd_parse.get_opt("--std_dev"));

      if(cmd_parse.opt_exists("--img")){
	 image_names = cmd_parse.get_multiple_opt("--img");
	 image_count = image_names.size();
      }
      else {
	 image_names[0]="Highimgnoise.jpg";
      }
   }
};


#endif
