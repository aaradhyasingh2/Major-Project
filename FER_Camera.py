
import cv2, sys, numpy, os
import numpy as np

size = 2
fn_haar = 'haarcascade_frontalface_default.xml'
fn_dir = 'criminals'



thresss = 110





# Part 1: Create fisherRecognizer
print('Training...')



pred = []

faces_name = []

# Create a list of images and a list of corresponding names
(images, lables, names, id) = ([], [], {}, 0)

# Get the folders containing the training data
for (subdirs, dirs, files) in os.walk(fn_dir):

    # Loop through each folder named after the subject in the photos
    for subdir in dirs:
        names[id] = subdir
        subjectpath = os.path.join(fn_dir, subdir)

        # Loop through each photo in the folder
        for filename in os.listdir(subjectpath):

            # Skip non-image formates
            f_name, f_extension = os.path.splitext(filename)
            if(f_extension.lower() not in
                    ['.png','.jpg','.jpeg','.gif','.pgm']):
                print("Skipping "+filename+", wrong file type")
                continue
            path = subjectpath + '/' + filename
            lable = id

            # Add to training data
            images.append(cv2.imread(path, 0))
            lables.append(int(lable))
        id += 1
(im_width, im_height) = (112, 92)

# Create a Numpy array from the two lists above
(images, lables) = [numpy.array(lis) for lis in [images, lables]]

# OpenCV trains a model from the images
# NOTE FOR OpenCV2: remove '.face'
#model = cv2.face.createFisherFaceRecognizer()
#model = cv2.face.FisherFaceRecognizer_create()
model = cv2.face.LBPHFaceRecognizer_create()
#model = cv2.face.LBPHFaceRecognizer_create()
#model = cv2.face.EigenFaceRecognizer_create()
model.train(images, lables)




# Part 2: Use fisherRecognizer on camera stream
haar_cascade = cv2.CascadeClassifier(fn_haar)
webcam = cv2.VideoCapture(0)

confirmation_count = 0

print('Ready...')




class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,test_img=self.video.read()# captures frame and returns boolean value and captured image  
          
        
        gray_img= cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)  
        mini = cv2.resize(gray_img, (int(gray_img.shape[1] / size), int(gray_img.shape[0] / size)))

        try:
            faces = haar_cascade.detectMultiScale(mini)
            

            for i in range(len(faces)):
                face_i = faces[i]

                # Coordinates of face after scaling back by `size`
                (x, y, w, h) = [v * size for v in face_i]
                face = gray_img[y:y + h, x:x + w]
                face_resize = cv2.resize(face, (im_width, im_height))

                # Try to recognize the face
                prediction = model.predict(face_resize)
                cv2.rectangle(test_img, (x, y), (x + w, y + h), (0, 255, 0), 3)

                # [1]
                # Write the name of recognized face
                #cv2.putText(frame,'%s - %.0f' % (names[prediction[0]],prediction[1]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
                if prediction[1]< thresss:
                    cv2.putText(test_img,'%s - %.0f' % (names[prediction[0]],prediction[1]),(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 255, 0))
                
                else:
                    cv2.putText(test_img,'not recognized',(x-10, y-10), cv2.FONT_HERSHEY_PLAIN,1,(0, 0, 255))
                
        except:
            pass

        resized_img = cv2.resize(test_img, (1000, 600))

        _, jpeg = cv2.imencode('.jpg', resized_img)

        return jpeg.tobytes()