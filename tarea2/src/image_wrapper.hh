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

/* Función que devuelve un entero que no se pase de los límites, en caso de estar dentro 
 * se devuelve el entero original, si está afuera devuelve el límite (inferior o superior)
 */
int truncate_value(int target, int low_limit, int up_limit);

/* Función que devuelve el valor en la distribución de Gauss según su ubicación 
 * y la desviación estándar
 */
double gauss(int x, int y, double dev_std);

/* Clase que establece una interfaz con la matriz de la imagen para encapsular y simplificar 
 * el acceso a las regiones de la misma.
 */
class Image_wrapper{
private:
  Mat* data;
  unsigned char get_color_value(int x, int y, int color);
  void set_color_value(unsigned char val, int x, int y, int color);
  
public:
  //Image_wrapper(mutex* m);
  Image_wrapper(Mat* data);

  ~Image_wrapper(void);

  Mat* get_data(void);
  //esto retorna la cantidad de rows y columns
  int get_rows(void);
  int get_cols(void);
  //returns height and width defined with the coordinate system for the wrappers
  int get_height(void);
  int get_width(void);

  int get_neighborhood_area(int x, int y, int r); //retorna el area de un neighborhood del punto (x,y), y de
					      //"radio" r. El lado del cuadrado es 2r.
  

  unsigned char get_b(int x,int y);// value of the color at the x,y coordinate
  unsigned char get_g(int x,int y);
  unsigned char get_r(int x,int y);


   Vec3b get_neighborhood_gauss(int cx, int cy, int r, double std_dev); //return the gauss-average of the neighborhood

  void set_b(unsigned char val,int x, int y );
  void set_g(unsigned char val,int x, int y );
  void set_r(unsigned char val,int x, int y );

  void set_Mat(Mat* data);

  //Compare if two images are tha same (pixel-wise)
  bool compare(Image_wrapper* other);
  
};

/* Clase que define a un vecindario alrededor de un punto de la imagen. Es inteligente en el 
 * sentido de que sus extremos los define de manera que siempre retorne regiones dentro de 
 * la imagen.
 */
class neighborhood{
private:
  int x_start, y_start;
  int x_end, y_end;
  Image_wrapper* parent;
  void set_x_start(int x);
  void set_y_start(int y);
  void set_x_end(int x);
  void set_y_end(int y);
public:
  neighborhood(void);
  neighborhood(int x, int y, int r, Image_wrapper* parent);

  //Image wrapper que representa la imagen a la cual está asociada el vecindario
  Image_wrapper* get_parent(void);
				  

  int get_area(void); //calcula el area
  
  int get_x_start(void);
  int get_y_start(void);
  int get_y_end(void);
  int get_x_end(void);

  void set_parent(Image_wrapper* parent);
  void set_area(int x, int y, int r); //x,y position of the center and radius r
  
};

//Apply the gaussian filter
void gaussian_filter(Image_wrapper* target, Image_wrapper* source, double std_dev, int start, int end);

#endif
