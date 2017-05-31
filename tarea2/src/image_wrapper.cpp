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

using namespace std;
using namespace cv;


//---------------------------------------------------------------
//Implementación de la clase Image_wrapper
//---------------------------------------------------------------

Image_wrapper::Image_wrapper(Mat* data){
  this->set_Mat(data);
}

Image_wrapper::~Image_wrapper(void){
  delete this->data;
}

Mat* Image_wrapper::get_data(void){
  return this->data;
}

int Image_wrapper::get_rows(void){
  return this->get_data()->rows;
}

int Image_wrapper::get_cols(void){
  return this->get_data()->cols;
}

int Image_wrapper::get_height(void){
  return this->get_data()->rows;
}

int Image_wrapper::get_width(void){
  return this->get_data()->cols;
}

unsigned char Image_wrapper::get_b(int x, int y){
  return this->get_color_value(x,y,0);
}

unsigned char Image_wrapper::get_g(int x, int y){
  return this->get_color_value(x,y,1);
}


unsigned char Image_wrapper::get_r(int x, int y){
  return this->get_color_value(x,y,2);
}

unsigned char Image_wrapper::get_color_value(int x, int y, int color){
  int y_t=(this->get_height())-y-1;
  return this->get_data()->at<Vec3b>(y_t,x).val[color];
}

void Image_wrapper::set_b(unsigned char val, int x, int y){
  this->set_color_value(val, x, y, 0);
}


void Image_wrapper::set_g(unsigned char val, int x, int y){
  this->set_color_value(val, x, y, 1);
}


void Image_wrapper::set_r(unsigned char val, int x, int y){
  this->set_color_value(val, x, y, 2);
}

void Image_wrapper::set_color_value(unsigned char val, int x, int y, int color){
  int y_t=(this->get_height())-y-1;
  this->get_data()->at<Vec3b>(y_t,x).val[color]=val;
}

void Image_wrapper::set_Mat(Mat* data){
  this->data=data;
}

int Image_wrapper::get_neighborhood_area(int x, int y, int r){
  neighborhood ng(x, y, r, this);
  return ng.get_area();
}


Vec3b Image_wrapper::get_neighborhood_gauss(int cx, int cy, int r, double std_dev){
  neighborhood ng(cx,cy,r, this);
  double result[3]={0,0,0};
  double gauss_val;
  Vec3b uchar_result;
  int rx, ry; //Posición relativa (x,y) con respecto al centro (cx,cy)

  double probe;

  //Se recorre el vecindario para calcular el valor del filtro
  for (int nx=ng.get_x_start(); nx<ng.get_x_end(); nx++){
    for (int ny=ng.get_y_start(); ny<ng.get_y_end(); ny++){
      rx=nx-cx;
      ry=ny-cy;
      gauss_val=gauss(rx, ry, std_dev);
      probe+=gauss_val;
      result[0]+=((double) this->get_b(nx,ny))*gauss_val;
      result[1]+=((double) this->get_g(nx,ny))*gauss_val;
      result[2]+=((double) this->get_r(nx,ny))*gauss_val;
    }
  }
  uchar_result.val[0]=(unsigned char) (result[0]/probe);
  uchar_result.val[1]=(unsigned char) (result[1]/probe);
  uchar_result.val[2]=(unsigned char) (result[2]/probe);
  return uchar_result;
}

bool Image_wrapper::compare(Image_wrapper* other){
  if (this->get_width()==other->get_width() &&
      this->get_height()==other->get_height()){
    
    for (int x = 0; x < this->get_width(); x++){
      for (int y = 0; y < this->get_height(); y++){
	if (this->get_r(x,y) != other->get_r(x,y)) return false;
	if (this->get_g(x,y) != other->get_g(x,y)) return false;
	if (this->get_b(x,y) != other->get_b(x,y)) return false;
      }
    }
  }
  else return false;
  return true;
}


//---------------------------------------------------------------
//Implementación de la clase neighborhood
//---------------------------------------------------------------

neighborhood::neighborhood(void){
  this->x_start=0;
  this->y_start=0;
  this->x_end=0;
  this->y_end=0;
  this->parent=0;
}

neighborhood::neighborhood(int x, int y, int r, Image_wrapper* parent){
  this->set_parent(parent);
  this->set_area(x,y,r);
}

Image_wrapper* neighborhood::get_parent(void){
  return parent;
}

int neighborhood::get_area(void){
  return (this->get_x_end()-this->get_x_start())*(this->get_y_end()-get_y_start());
}

int neighborhood::get_x_start(void){
  return this->x_start;
}

int neighborhood::get_x_end(void){
  return this->x_end;
}

int neighborhood::get_y_start(void){
  return this->y_start;
}

int neighborhood::get_y_end(void){
  return this->y_end;
}

void neighborhood::set_parent(Image_wrapper* parent){
  this->parent=parent;
}

void neighborhood::set_area(int x, int y, int r){
  //Se verifica si hay un image_wrapper válido asociado (parent)
  if (this->get_parent()!=0){
     //Se verifica si el centro está dentro de la imagen
    if (0<=x && x<=this->get_parent()->get_width() &&
	0<=y && y<=this->get_parent()->get_height()){

      //Se calculan los límites del vecindario para que estén dentro de la imagen
      this->set_x_start(truncate_value(x-r, 0, this->get_parent()->get_width()));
      this->set_x_end(truncate_value(x+r, 0, this->get_parent()->get_width()));
      this->set_y_start(truncate_value(y-r, 0, this->get_parent()->get_height()));
      this->set_y_end(truncate_value(y+r, 0, this->get_parent()->get_height()));
    }
  }
}

void neighborhood::set_x_start(int x){
  this->x_start=x;
}

void neighborhood::set_x_end(int x){
  this->x_end=x;
}

void neighborhood::set_y_start(int y){
  this->y_start=y;
}

void neighborhood::set_y_end(int y){
  this->y_end=y;
}

//---------------------------------------------------------------
//Funciones independientes
//---------------------------------------------------------------

int truncate_value(int target, int low_limit, int up_limit){
  if (up_limit>low_limit){
    if (target>up_limit) return up_limit;
    else if (target<low_limit) return low_limit;
    else return target;
  }
  else return 0;
}

double gauss(int x, int y, double dev_std){
  const double pi = 3.1415926535897;
  double var=pow(dev_std, 2);
  double den=1/(2*pi*var);
  double exponent=-((x^2)+ (y^2))/(2*var);
  return den*exp(exponent);
}


void gaussian_filter(Image_wrapper* target, Image_wrapper* source, double std_dev, int start, int end){
  int window_size = ceil(3*std_dev); //Ventana del filtro recomendada de 6std_dev x 6std_dev
  Vec3b gaussian;
  
  if (target->get_cols()==source->get_cols() && target->get_rows()==source->get_rows()){
     //Se calculan los valores de la imagen filtrada para la franja vertical indicada
     //por los límites start y end 
     for (int x=start; x<=end; x++){
      for (int y=0; y<target->get_height(); y++){
	gaussian=source->get_neighborhood_gauss(x, y, window_size, std_dev);
	target->set_b(gaussian.val[0], x, y);
	target->set_g(gaussian.val[1], x, y);
	target->set_r(gaussian.val[2], x, y);
      }
    }
  }
  
}
