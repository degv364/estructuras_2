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
#include <opencv2/imgproc/imgproc.hpp>
#include <mutex>
#include <math.h>
#include <iostream>

using namespace std;
using namespace cv;

#ifndef WRAPPER
#define WRAPPER

//devuelve un entero que no se pase de lso limites, en caso de estar dentro, devuelve a wrapper, si
//esta afuera, devuelve el limite
int truncate_value(int target, int low_limit, int up_limit);

//devuleve el valor en la distribucion de Gauss segun su ibcacion, y una dev_std
double gauss(int x, int y, double dev_std);

//clase que utiliza por dentro a Mat. basicamente para disminuir las instrucciones de tomar pixeles
//y sus valores, y que 0,0 sea la esquina inferior izquierda, de manera que la imagen se comporte
//como el primer cuadrante.
class Image_wrapper{
private:
  mutex* m;//this mutex is not required for median filter, but maybe it is required for the gausian...
  Mat* data;
  unsigned char get_color_value(int x, int y, int color);
  void set_color_value(unsigned char val, int x, int y, int color);
  
public:
  Image_wrapper(mutex* m);
  Image_wrapper(mutex* m, Mat* data);

  ~Image_wrapper(void);

  Mat* get_data(void);
  //esto retorna la cantidad de rows y columns
  int get_rows(void);
  int get_cols(void);
  //returns height and width defined with the coordinate system for the wrappers
  int get_height(void);
  int get_width(void);

  int get_neighbor_area(int x, int y, int r); //retorna el area de un neighbor del punto (x,y), y de
					      //"radio" r. No es un radio, pero el lado del cuadrado
					      //es 2r.
  

  unsigned char get_b(int x,int y);// value of the color at the x,y coordinate
  unsigned char get_g(int x,int y);
  unsigned char get_r(int x,int y);

  Vec3b get_neighbor_mean(int x, int y, int r); //return vec with the average of the neighbor
  Vec3b get_neighbor_gauss(int cx, int cy, int r, double std_dev); //return the gauss-average of the neighbor

  void set_b(unsigned char val,int x, int y );//value of the colot at x,y
  void set_g(unsigned char val,int x, int y );
  void set_r(unsigned char val,int x, int y );

  void set_Mat(Mat* data);

  //Compare if two images are tha same (pixel-wise)
  bool compare(Image_wrapper* other);
  
};

//define a un vecindario al rededor de un punto. es inteligente  en el sentido que sus bordes lso
//define de manera que siempre retorne cosas dentro de la imagen

class neighbor{
private:
  int x_start, y_start;
  int x_end, y_end;
  Image_wrapper* parent;
  void set_x_start(int x);
  void set_y_start(int y);
  void set_x_end(int x);
  void set_y_end(int y);
public:
  neighbor(void);
  neighbor(int x, int y, int r, Image_wrapper* parent);

  Image_wrapper* get_parent(void);//se llama parent porque el neighbor esta siempre asociado a algun
				  //wrapper, pero esto no es herencia

  int get_area(void); //calcula el area
  
  int get_x_start(void);
  int get_y_start(void);
  int get_y_end(void);
  int get_x_end(void);

  void set_parent(Image_wrapper* parent);
  void set_area(int x, int y, int r); //x,y position of the center and radius r
  
};
//Apply to every point in the range defined by start->end the average of the values in the
//neighbor. target and source must be two different wrappers. Window size defines radius r
void median_filter(Image_wrapper* target, Image_wrapper* source, int window_size, int start, int end);

//Aply the gaussian filter
void gaussian_filter(Image_wrapper* target, Image_wrapper* source, double std_dev, int start, int end);

#endif
