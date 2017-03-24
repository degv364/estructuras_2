#include "image_wrapper.hh"

using namespace std;
using namespace cv;

//IMAGE WRAPPER***********************************************************************************
Image_wrapper::Image_wrapper(mutex* m){
  this->m=m;
}

Image_wrapper::Image_wrapper(mutex* m, Mat* data){
  this->m=m;
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
  this->m->lock();
  this->get_data()->at<Vec3b>(y_t,x).val[color]=val;
  this->m->unlock();
}

void Image_wrapper::set_Mat(Mat* data){
  this->m->lock();
  this->data=data;
  this->m->unlock();
}

int Image_wrapper::get_neighbor_area(int x, int y, int r){
  neighbor ng(x, y, r, this);
  return ng.get_area();
}

Vec3b Image_wrapper::get_neighbor_mean(int x, int y, int r){
  //work with doubles to minimize errors
  neighbor ng(x, y, r, this);
  double result[3]={0,0,0};
  double area= (double) ng.get_area();
  Vec3b uchar_result;
  
  for (int xs=ng.get_x_start(); xs<ng.get_x_end(); xs++){
    for (int ys=ng.get_y_start(); ys<ng.get_y_end(); ys++){
      result[0]+=(( (double) this->get_color_value(xs,ys,0))/area);
      result[1]+=(( (double) this->get_color_value(xs,ys,1))/area);
      result[2]+=(( (double) this->get_color_value(xs,ys,2))/area);
    }
  }
  uchar_result.val[0]=(unsigned char) result[0];
  uchar_result.val[1]=(unsigned char) result[1];
  uchar_result.val[2]=(unsigned char) result[2];
  return uchar_result;
}

Vec3b Image_wrapper::get_neighbor_gauss(int cx, int cy, int r, double std_dev){
  //work with doubles to minimize errors
  neighbor ng(cx,cy,r, this);
  double result[3]={0,0,0};
  double gauss_val;
  double area= (double) ng.get_area();
  Vec3b uchar_result;
  int rx, ry; //relative x,y position respect to center at cx, cy

  double probe;

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




//NEIGHBOR******************************************************************
neighbor::neighbor(void){
  this->x_start=0;
  this->y_start=0;
  this->x_end=0;
  this->y_end=0;
  this->parent=0;
}

neighbor::neighbor(int x, int y, int r, Image_wrapper* parent){
  this->set_parent(parent);
  this->set_area(x,y,r);
}

Image_wrapper* neighbor::get_parent(void){
  return parent;
}

int neighbor::get_area(void){
  return (this->get_x_end()-this->get_x_start())*(this->get_y_end()-get_y_start());
}

int neighbor::get_x_start(void){
  return this->x_start;
}

int neighbor::get_x_end(void){
  return this->x_end;
}

int neighbor::get_y_start(void){
  return this->y_start;
}

int neighbor::get_y_end(void){
  return this->y_end;
}

void neighbor::set_parent(Image_wrapper* parent){
  this->parent=parent;
}

void neighbor::set_area(int x, int y, int r){
  //first check if there is a parent
  if (this->get_parent()!=0){
    //check center is inside image
    if (0<=x && x<=this->get_parent()->get_width() &&
	0<=y && y<=this->get_parent()->get_height()){

      this->set_x_start(truncate_value(x-r, 0, this->get_parent()->get_width()));
      this->set_y_start(truncate_value(y-r, 0, this->get_parent()->get_height()));
      this->set_x_end(truncate_value(x+r, 0, this->get_parent()->get_width()));
      this->set_y_end(truncate_value(y+r, 0, this->get_parent()->get_height()));
    }
  }
}

void neighbor::set_x_start(int x){
  this->x_start=x;
}

void neighbor::set_x_end(int x){
  this->x_end=x;
}

void neighbor::set_y_start(int y){
  this->y_start=y;
}

void neighbor::set_y_end(int y){
  this->y_end=y;
}

//INDEPENDENT FUNCTIONS*********************************************************

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

void median_filter(Image_wrapper* target, Image_wrapper* source, int window_size, int start, int end){
  //chack same size
  Vec3b mean;
  if (target->get_cols()==source->get_cols() && target->get_rows()==source->get_rows()){
    for (int x=start; x<=end; x++){
      for (int y=0; y<target->get_height(); y++){
	mean=source->get_neighbor_mean(x,y,window_size);
	target->set_b(mean.val[0], x, y);
	target->set_g(mean.val[1], x, y);
	target->set_r(mean.val[2], x, y);
      }
    }
  }
}

void gaussian_filter(Image_wrapper* target, Image_wrapper* source, double std_dev, int start, int end){
  int window_size=ceil(3*std_dev); //recomended convolution matrix of 6std_dev x 6std_dev
  Vec3b gaussian;
  if (target->get_cols()==source->get_cols() && target->get_rows()==source->get_rows()){
    for (int x=start; x<=end; x++){
      for (int y=0; y<target->get_height(); y++){
	gaussian=source->get_neighbor_gauss(x,y,window_size, std_dev);
	target->set_b(gaussian.val[0], x, y);
	target->set_g(gaussian.val[1], x, y);
	target->set_r(gaussian.val[2], x, y);
      }
    }
  }
  
}
