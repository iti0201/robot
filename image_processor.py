import cv2
import numpy as np
import sys

class ImageProcessor:
    def __init__(self, publisher=None):
        self.width = None
        self.height = None
        if publisher is None:
            self.publisher = None
        else:
            self.publisher = publisher


    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def get_mask(self, image, hue, saturation):
        low = np.array([hue, saturation, 107])
        high = np.array([hue, 255, 255])
        return cv2.inRange(image, low, high)

    def process_mask(self, identifier, mask, image, color, outfile=None):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        return_value = []
        for contour in contours:
           if len(contour) > 5:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            #outfile = "temp.jpg"
            if outfile is not None:
                cv2.circle(image,(int(x), int(y)), int(radius), color, 2)
            return_value.append((identifier, (int(x), int(y)), int(radius)))
        return return_value

    def process_image(self, src, outfile=None) -> list:
        src = cv2.medianBlur(src, 17)
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        kernel = np.ones((47, 47), np.uint8)
        mask_red = cv2.morphologyEx(self.get_mask(hsv, 0, 130), cv2.MORPH_CLOSE, kernel)
        mask_blue = cv2.morphologyEx(self.get_mask(hsv, 110, 130), cv2.MORPH_CLOSE, kernel)
        return_value = self.process_mask("red sphere", mask_red, src, (255, 255, 255), outfile) + \
                       self.process_mask("blue sphere", mask_blue, src, (0, 255, 0), outfile)
        #outfile = "temp.jpg"
        if outfile is not None:
            cv2.imwrite(outfile, src)
        return return_value

    def get_objects(self, image, message=None):
        src = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        if src is None:
            return []
        result = self.process_image(src)
        if self.publisher is not None:
            if message is not None:
                message.data = str(result)
                self.publisher.publish(message)
        return result

    def read_image_from_file(self, filename):
        src = cv2.imread(cv2.samples.findFile(filename), cv2.IMREAD_COLOR)
        if src is None:
            print ('Error opening image!')
            return None
        return src

    def get_objects_from_file(self, filename, outfile=None):
        src = self.read_image_from_file(filename)
        if src is not None:
            return self.process_image(src, outfile)
        return []

def main(argv):
    if len(argv) < 4:
        print("Usage: opencv.py width height infile outfile")
        return None
    ip = ImageProcessor()
    ip.set_width(argv[0])
    ip.set_height(argv[1])
    print(ip.get_objects_from_file(argv[2], outfile=argv[3]))


if __name__ == "__main__":
    main(sys.argv[1:])
