### from Leica Ann/n axis to other real axis
def leica_Ann_to_axis(Ann,axis):
    try:
      # Ann = "J31_2" e.g.
      yy = ord(Ann[:1])  # point x axis,"J31_2" J's ascii 74
      # yy = A to Z except I (asc=73)
      if yy>=(73):
        yy -= 1

      xx, p = Ann.split('_') # "J31_2" 2
      xx = int(xx[1:])
      p = p.split('.')[0]
      p = int(p)
      ### axis(z50x,z50y,a15x,a15y) = 125.9,36.7,  160,13.5
      z50x=axis[0] # 125.9
      z50y=axis[1] # 36.7

      a15x=axis[2] # 160
      a15y=axis[3] # 13.5

      x_step = (a15x - z50x)/(50-15)
      y_step = (z50y - a15y)/(26-1)

      gapx_step = x_step/4.0
      gapy_step = y_step/4.0

      if p == 1:
        gapx =  gapx_step
        gapy = -gapy_step
      elif p == 2:
        gapx = -gapx_step
        gapy = -gapy_step
      elif p == 3:
        gapx =  gapx_step
        gapy =  gapy_step
      elif p == 4:
        gapx = -gapx_step
        gapy =  gapy_step
      else:
        gapx = 0
        gapy = 0

      #print(xx,yy)
      new_x = round(a15x - (xx-15)*x_step + gapx,1)
      new_y = round(a15y + (yy-65)*y_step + gapy,1)

      return new_x,new_y

    except:
      return 0.0, 0.0


if __name__ == "__main__":
    std_axis = [125.9, 36.7, 160, 13.5]
    test = leica_Ann_to_axis("J31_2", std_axis)
    # test = (144.2, 20.7)
    print(test)