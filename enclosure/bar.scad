leds=32;

// The dimensions here are super fiddly
pixel_size=[6.9, 6.9, 3.25];
pixel_wall=[1, 1, 0.20];
strip=[10.5, pixel_size[1] * leds - pixel_wall[1], pixel_size[2] + pixel_wall[2]];
housing=strip + [1, 1, 1];
smidge = 0.05;

print_diffuser();
//print_back();

module assembly() {
  color("red")
  translate([(housing[0]-strip[0])/2,0,(housing[2]-strip[2])+smidge*2])
    diffuser();
  translate([0,0,0])
  back();

}

module print_diffuser() {
  translate([0,0,strip[2]])
  rotate([180,0,180])
    diffuser();
}

module print_back() {
  back();
}

module diffuser() {
  difference() {
    cube(strip);
      for ( y = [ 0 : 1 : leds] )
        translate([(strip[0] - (pixel_size[0]-pixel_wall[0]))/2,y * pixel_size[1],-smidge])
          cube(pixel_size - pixel_wall + [0,0,smidge*2]);
  }
}

module back () {
difference() {
  cube(housing);
  translate([(housing[0] - strip[0])/2, 0, ((housing[2] - strip[2] )+ smidge)])
    cube(strip);
}
}
