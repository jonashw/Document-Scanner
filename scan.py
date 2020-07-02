from datetime import datetime
import os
import cv2
import sys
import img2pdf
import glob
import subprocess
import pyperclip
from shutil import copyfile

storage_folder_path = "c:/users/jonashw/Box Sync/scans/"

today = datetime.today()
id = today.strftime('%Y-%m-%d_%H-%M-%S')
short_id = today.strftime('%Y%m%d%H%M%S')
pdf_out_file_path = os.path.join("c:/users/jonashw/scanning/scans", id + ".pdf")
batch_path = os.path.join("c:/users/jonashw/scanning/scans/batches",id)
capture_path = os.path.join(batch_path, "capture")
tailor_path = os.path.join(batch_path, "tailor")

def do_camera():
    cam = cv2.VideoCapture(3)#,cv2.CAP_DSHOW)
    w,h = 2560,1440#3840,2160#1920,1080
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cam.set(cv2.CAP_PROP_FORMAT, 0)
    w = cam.get(cv2.CAP_PROP_FRAME_WIDTH)
    h = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
    grab_mode = cam.get(cv2.CAP_PROP_MODE)
    format = cam.get(cv2.CAP_PROP_FORMAT)
    print("capturing with w={}, h={}, grab_mode={}, format={}".format(w,h,grab_mode, format))
    
    #ok = False
    #i = -100
    #while (not ok) and i < 10:
        #if i != 0:
            #print("setting grab_mode {}".format(grab_mode + i))
            #ok = cam.set(cv2.CAP_PROP_MODE, grab_mode + i)
        #i += 1
    #if ok:
        #gm = cam.get(cv2.CAP_PROP_MODE)
        #printf("Grab mode = {}", format(gm))

    cv2.namedWindow("test", cv2.WINDOW_NORMAL)

    img_counter = 0
    img_paths = []

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)
        cv2.resizeWindow("test",1280,720)
        cv2.moveWindow("test",1920,0)

        k = cv2.waitKey(1)
        if k%256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k%256 == 32:
            # SPACE pressed
            img_name = "capture_{}.png".format(img_counter)
            img_path = os.path.join(capture_path, img_name)
            img_paths.append(img_path)
            os.makedirs(capture_path, exist_ok=True)
            cv2.imwrite(img_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            print("{} written!".format(img_name))
            img_counter += 1

    cam.release()

    cv2.destroyAllWindows()
    return img_paths

capture_paths = do_camera()

if len(capture_paths) == 0:
    print("No images captured.  Exiting...")
    sys.exit()


os.system('cls')
raw_filename_from_user = str(input("\n*** File name? ***\n"))
filename_mantissa, _ = os.path.splitext(raw_filename_from_user)
dst_path = os.path.join(storage_folder_path, filename_mantissa + "_" + short_id +".pdf")
os.makedirs(storage_folder_path, exist_ok=True)


capture_arg = ' '.join(capture_paths)

os.makedirs(tailor_path, exist_ok=True)

subprocess.check_output(' '.join([
    'scantailor-cli',
    '-v',
    '--margins=0',
    '--layout=1',
    '--deskew=manual',
    '--rotate=90',
    '--threshold=0',
    '--content-detection=normal',
    '--alignment-vertical=bottom',
    '--alignment-horizontal=center',
    '--white-margins=true',
    '--color-mode=black_and_white',
    '--dpi=300',
    '--output-dpi=600',
    '--despeckle=cautious',
    '--tiff-compression=lzw',
    '--start-filter=1',
    '--end-filter=6',
    capture_arg,
    tailor_path
]))

with open(pdf_out_file_path,"wb") as f:
    infiles = glob.glob(os.path.join(tailor_path, "*.tif"))
    pdf = img2pdf.convert(infiles)
    f.write(pdf)

copyfile(pdf_out_file_path,dst_path)
pyperclip.copy(dst_path)