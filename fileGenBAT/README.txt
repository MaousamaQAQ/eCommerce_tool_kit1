This project is used for packaging and uploading main and supplementary images, and requires three necessary files:

1. data.csv - used to store configuration information
2. Run.bat - the main file of this project
3. distributor.bat - image distributor

Usage instructions:
1. First, place the unzipped folder containing images into this project folder (you can use the existing "pic" folder for testing; before testing, remember to back up the four pic folders elsewhere). You can also directly place the images inside the project folder.
2. Check the first column of data.csv. This column is the ASIN, and the folders to be created later will be named using the ASIN.
3. Run Run.bat. At this time, the folder from step 1 containing the images will move all images into the project folder and delete the original folder; meanwhile, subfolders named after the ASIN values in the first column of data.csv will be created in the project folder.
4. Run.bat will print in the terminal:

--------------------------------------- 
Please place images into the corresponding folders,
then enter 0 (Full Rename) or 1 (Rename 1st image only)
--------------------------------------- 
Enter number and press Enter:

At this moment, do not type anything yet. We must first place the images into the corresponding subfolders. This can be done manually, but it is too troublesome, so I created distributor.bat. Now look at the second column of data.csv; this column contains the image names, meaning that images containing the names in the second column will be distributed by distributor.bat into the corresponding folders named with the ASIN in the first column. Now run distributor.bat. After it finishes, we may proceed to the next step in Run.bat.

5. If we want to upload both main and supplementary images, enter 0 to choose Mode 0; if we only want to upload one image (note: Mode 1 only supports one image per folder!), enter 1.
Details of Mode 0: In this mode, images in each subfolder will be renamed based on natural name sorting, such as:
The first image: Asin.MAIN.jpg
The second image: Asin.PT01.jpg
The third image: Asin.PT02.jpg
... (image formats may include jpg, jpeg, png, etc.)
Then the subfolder will be automatically packaged into a zip file.
Details of Mode 1: In this mode, only the first image in each subfolder will be renamed (therefore it is strongly recommended to put only one image into the folder, otherwise the second image will not be renamed and may fail to upload). The default renamed file is Asin.MAIN.jpg (image formats may include jpg, jpeg, png, etc.). If you wish to customise the name, rename Run.bat to Run.txt, press Ctrl+F to search for “:: PART C — 仅将第一张图片命名为 MAIN” (line 123). Below this section, there is a command: set "NEWNAME=!FOLDER!.MAIN" (line 141). You may change .MAIN to .PT01, .PT02, or any other allowed string (note that some symbols cannot be used in file or folder names). Then press Ctrl+S to save Run.txt and rename it back to Run.bat, and run it.
Then all images in the subfolder will be named as Asin + your customised content + .jpg.
Then the subfolder will be automatically packaged into a zip file.