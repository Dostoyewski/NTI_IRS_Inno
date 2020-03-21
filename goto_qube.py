from map import Qube

def goto_qube(qube_x,qube_y):
   dc = 0.1;
   a=0.2; #var koef for each hiegth 
   # kamera 640*360
   kam_x = 320;
   kam_y = 180;
   if qube_y>100:
   	pix_y = kam_y - qube_y;
   	real_metric_y = h + pix_y*a;
   else:
   	pix_y = kam_y - qube_y;
   	real_metric_x = h + pix_y*a;

   pix_x = kam_x - qube_x;
   real_metric_x = pix_x*a;

if __name__ == "__main__":
	v = [Qube(2, 3, 1) for i in range(10)]
	print(v)
