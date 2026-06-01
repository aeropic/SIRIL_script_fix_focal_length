# SIRIL_script_fix_focal_length
a script to force the focal length field (FOCALLEN) in the .FIT file header

## the need

I get a CANON 2000D DSLR to acquire my astrophotographies. It is adapted without lens behing a Skywatcher 200x1000 telescope.
The acquired raw images come with a default 50 mm in the focal length of the lens. This value is then propataged by SIRIL into the stacked "result" .FIT file. Then when doing astrometry on the file, you have to modifiy the focla lenth to the real one... A mess !

## the solution
### first option
use the "preprocess_with_master_focalfixed.py" python script. Drop it into the SIRIL's script folder (for me C:\Users\ALAIN\AppData\Local\siril-scripts\Aeropic) and it will become available.
When you stack your images, just run this script!

If you want other preprocessing just translate the .ssf into .py file...

### second option

If you prefer using the standard preprocessing scripts (eg OSC_Preproceesing.ssf)
use this python script (fix_focal.py). Drop it into the SIRIL's script folder (for me C:\Users\ALAIN\AppData\Local\siril-scripts\Aeropic) and it will become available.

edit the processing script you use (eg OSC_Preproceesing.ssf found in the application directory for me : C:\Program Files\Siril\scripts) and add this line at the end just before the close instruction: "pyscript fix_focal.py"

#### extract of the OSC_Preprocessing script
  save ../result_$LIVETIME:%d$s
  
  cd ..
  
  pyscript fix_focal.py 
  
  close

## what does it do ?

It just changes the default value 50 mm into your focal length in the result file. To check it works, you can edit the file with notepad++ and see at the top :

<img width="1398" height="274" alt="focal" src="https://github.com/user-attachments/assets/94b3714d-0e3b-4537-bff4-952350edd44a" />

And when doing a plate solving, you don't have to bother with the value, it is ready :

<img width="581" height="780" alt="astro_focal" src="https://github.com/user-attachments/assets/b20007fc-6d0c-4ba4-965a-30afb93e83c4" />


