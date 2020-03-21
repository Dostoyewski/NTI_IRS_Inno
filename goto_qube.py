def goto_qube(qube_x,qube_y):
   dc = 0.1;
   a=0.2; #var koef for each hiegth 
   # kamera 640*200
   kam_x = 320;
   kam_y = 100;
   if qube_y>100:
   	pix_y = kam_y - qube_y;
   	real_metric_y = h + pix_y*a;
   else:
   	pix_y = kam_y - qube_y;
   	real_metric_x = h + pix_y*a;

   pix_x = kam_x - qube_x;
   real_metric_x = pix_x*a;
